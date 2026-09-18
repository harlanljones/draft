from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from draft_model.cli import main
from draft_model.contracts import IdentityResolution
from draft_model.ingest.chadwick import resolve_chadwick_identities

UUID_1 = "11111111-1111-4111-8111-111111111111"
UUID_2 = "22222222-2222-4222-8222-222222222222"
UUID_3 = "33333333-3333-4333-8333-333333333333"
UUID_4 = "44444444-4444-4444-8444-444444444444"
UUID_5 = "55555555-5555-4555-8555-555555555555"


def _package(root: Path, package_id: str, filename: str, payload: bytes) -> Path:
    root.mkdir()
    (root / filename).write_bytes(payload)
    manifest = {
        "schema_version": "1.0",
        "package_id": package_id,
        "source": f"Synthetic {package_id}",
        "data_mode": "empirical",
        "retrieved_at": "2026-09-17",
        "source_available_at": "2026-09-16",
        "availability_evidence": "Synthetic test evidence",
        "license_name": "Synthetic test grant",
        "license_url": "https://example.invalid/grant",
        "attribution": "Synthetic test fixture",
        "rights": {
            "agreement_reference": f"{package_id}-agreement",
            "reviewed_by": "test reviewer",
            "reviewed_at": "2026-09-17",
            "allows_retention": True,
            "allows_model_training": True,
            "allows_derived_publication": True,
            "allows_public_predictions": True,
            "allows_raw_redistribution": False,
        },
        "files": [
            {
                "path": filename,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "media_type": "text/csv",
            }
        ],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def _fixtures(tmp_path: Path) -> tuple[Path, Path]:
    cohort = (
        b"player_id,name_first,name_last,birth_date,mlbam_id,bbref_id,fangraphs_id\n"
        b"player_exact,Wrong,Name,,101,,\n"
        b"player_conflict,Any,Name,,101,bb,\n"
        b"player_name,Alex,Doe,2005-01-02,,,\n"
        b"player_ambiguous,Shared,Person,2004-03-04,,,\n"
        b"player_name_only,Alex,Doe,,,,\n"
        b"player_missing,Missing,Person,,999,,\n"
    )
    header = (
        "key_uuid,key_mlbam,key_bbref,key_fangraphs,name_first,name_last,"
        "birth_year,birth_month,birth_day\n"
    )
    register = (
        header
        + f"{UUID_1},101,aa,1,First,One,2000,1,1\n"
        + f"{UUID_2},202,bb,2,Second,Two,2001,1,1\n"
        + f"{UUID_3},303,cc,3,Alex,Doe,2005,1,2\n"
        + f"{UUID_4},404,dd,4,Shared,Person,2004,3,4\n"
        + f"{UUID_5},405,ee,5,Shared,Person,2004,3,4\n"
    ).encode()
    return (
        _package(tmp_path / "cohort", "cohort-fixture", "cohort.csv", cohort),
        _package(tmp_path / "register", "register-fixture", "register.csv", register),
    )


def test_identity_resolution_is_conservative(tmp_path: Path) -> None:
    cohort_manifest, register_manifest = _fixtures(tmp_path)
    matches = resolve_chadwick_identities(
        cohort_manifest=cohort_manifest,
        cohort_file="cohort.csv",
        register_manifest=register_manifest,
        register_file="register.csv",
    )
    by_player = {match.player_id: match for match in matches}
    assert by_player["player_exact"].resolution == IdentityResolution.MATCHED_EXACT_ID
    assert by_player["player_exact"].matched_uuid == UUID_1
    assert by_player["player_name"].resolution == IdentityResolution.MATCHED_NAME_DOB
    assert by_player["player_name"].matched_uuid == UUID_3
    assert by_player["player_conflict"].resolution == IdentityResolution.CONFLICT
    assert by_player["player_conflict"].matched_uuid is None
    assert by_player["player_conflict"].candidate_uuids == [UUID_1, UUID_2]
    assert by_player["player_ambiguous"].resolution == IdentityResolution.CONFLICT
    assert by_player["player_name_only"].resolution == IdentityResolution.UNRESOLVED
    assert by_player["player_missing"].resolution == IdentityResolution.UNRESOLVED


def test_duplicate_register_uuid_fails(tmp_path: Path) -> None:
    cohort = (
        b"player_id,name_first,name_last,birth_date,mlbam_id,bbref_id,fangraphs_id\n"
        b"player_a,A,B,,101,,\n"
    )
    register = (
        b"key_uuid,key_mlbam,key_bbref,key_fangraphs,name_first,name_last,birth_year,birth_month,birth_day\n"
        + f"{UUID_1},101,,,A,B,2000,1,1\n".encode()
        + f"{UUID_1},102,,,C,D,2001,1,1\n".encode()
    )
    cohort_manifest = _package(tmp_path / "cohort", "cohort-fixture", "cohort.csv", cohort)
    register_manifest = _package(
        tmp_path / "register", "register-fixture", "register.csv", register
    )
    with pytest.raises(ValueError, match="duplicate Chadwick key_uuid"):
        resolve_chadwick_identities(
            cohort_manifest=cohort_manifest,
            cohort_file="cohort.csv",
            register_manifest=register_manifest,
            register_file="register.csv",
        )


def test_identity_cli_output_is_deterministic(tmp_path: Path) -> None:
    cohort_manifest, register_manifest = _fixtures(tmp_path)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    arguments = [
        "resolve-chadwick-identities",
        "--cohort-manifest",
        str(cohort_manifest),
        "--cohort-file",
        "cohort.csv",
        "--register-manifest",
        str(register_manifest),
        "--register-file",
        "register.csv",
    ]
    assert main([*arguments, "--output", str(first)]) == 0
    assert main([*arguments, "--output", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()
