from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from draft_model.cli import main
from draft_model.contracts import IdentityMatch, IdentityResolution
from draft_model.outcomes.lahman import MlbDebutLabel, OutcomeResolution
from draft_model.outcomes.preflight import audit_empirical_labels


def _write_models(path: Path, models: list[IdentityMatch] | list[MlbDebutLabel]) -> None:
    payload = [model.model_dump(mode="json") for model in models]
    path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _identity(player_id: str, resolution: IdentityResolution) -> IdentityMatch:
    matched = resolution in {
        IdentityResolution.MATCHED_EXACT_ID,
        IdentityResolution.MATCHED_NAME_DOB,
    }
    candidate = "11111111-1111-4111-8111-111111111111"
    return IdentityMatch(
        player_id=player_id,
        register_package_id="register-fixture",
        resolution=resolution,
        matched_uuid=candidate if matched else None,
        candidate_uuids=[candidate] if matched else [],
        method="fixture",
        evidence=["synthetic fixture"],
    )


def _outcome(player_id: str, year: int, resolution: OutcomeResolution) -> MlbDebutLabel:
    resolved = resolution in {
        OutcomeResolution.RESOLVED_DEBUT,
        OutcomeResolution.RESOLVED_NO_DEBUT,
    }
    return MlbDebutLabel(
        player_id=player_id,
        lahman_player_id=f"lahman-{player_id}" if resolved else None,
        draft_year=year,
        horizon_complete_seasons=2,
        outcome_data_through_year=2025,
        resolution=resolution,
        debut_date="2024-05-01" if resolution == OutcomeResolution.RESOLVED_DEBUT else None,
        debut_within_horizon=(resolution == OutcomeResolution.RESOLVED_DEBUT) if resolved else None,
    )


def test_preflight_reports_year_level_identity_and_outcome_coverage(tmp_path: Path) -> None:
    identities = [
        _identity("player_a", IdentityResolution.MATCHED_EXACT_ID),
        _identity("player_b", IdentityResolution.CONFLICT),
        _identity("player_c", IdentityResolution.MATCHED_NAME_DOB),
        _identity("player_d", IdentityResolution.UNRESOLVED),
    ]
    outcomes = [
        _outcome("player_a", 2022, OutcomeResolution.RESOLVED_DEBUT),
        _outcome("player_b", 2022, OutcomeResolution.RESOLVED_NO_DEBUT),
        _outcome("player_c", 2023, OutcomeResolution.CENSORED),
        _outcome("player_d", 2023, OutcomeResolution.UNRESOLVED_IDENTITY),
    ]
    identity_path = tmp_path / "identities.json"
    outcome_path = tmp_path / "outcomes.json"
    _write_models(identity_path, identities)
    _write_models(outcome_path, outcomes)
    audit = audit_empirical_labels(identity_path, outcome_path)
    assert audit.status == "no_go"
    assert not audit.label_pipeline_complete
    assert audit.total_players == 4
    assert audit.eligible_labels == 1
    assert audit.eligible_rate == 0.25
    assert [year.draft_year for year in audit.years] == [2022, 2023]
    assert audit.years[0].identity_conflicts == 1
    assert audit.years[1].outcomes_censored == 1
    assert audit.years[1].outcomes_unresolved == 1


def test_preflight_rejects_mismatched_player_universes(tmp_path: Path) -> None:
    identity_path = tmp_path / "identities.json"
    outcome_path = tmp_path / "outcomes.json"
    _write_models(identity_path, [_identity("player_a", IdentityResolution.MATCHED_EXACT_ID)])
    _write_models(
        outcome_path,
        [_outcome("player_b", 2023, OutcomeResolution.RESOLVED_NO_DEBUT)],
    )
    with pytest.raises(ValueError, match="player universes differ"):
        audit_empirical_labels(identity_path, outcome_path)


def test_complete_label_pipeline_still_reports_global_no_go(tmp_path: Path) -> None:
    identity_path = tmp_path / "identities.json"
    outcome_path = tmp_path / "outcomes.json"
    _write_models(identity_path, [_identity("player_a", IdentityResolution.MATCHED_EXACT_ID)])
    _write_models(
        outcome_path,
        [_outcome("player_a", 2023, OutcomeResolution.RESOLVED_NO_DEBUT)],
    )
    audit = audit_empirical_labels(identity_path, outcome_path)
    assert audit.label_pipeline_complete
    assert audit.status == "no_go"


def test_preflight_cli_output_is_deterministic(tmp_path: Path) -> None:
    identity_path = tmp_path / "identities.json"
    outcome_path = tmp_path / "outcomes.json"
    _write_models(identity_path, [_identity("player_a", IdentityResolution.MATCHED_EXACT_ID)])
    _write_models(outcome_path, [_outcome("player_a", 2023, OutcomeResolution.RESOLVED_DEBUT)])
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    arguments = [
        "audit-empirical-labels",
        "--identities",
        str(identity_path),
        "--outcomes",
        str(outcome_path),
    ]
    assert main([*arguments, "--output", str(first)]) == 0
    assert main([*arguments, "--output", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()


def _make_package(root: Path, package_id: str, filename: str, payload: bytes) -> Path:
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
        "files": [{
            "path": filename,
            "sha256": hashlib.sha256(payload).hexdigest(),
            "bytes": len(payload),
            "media_type": "text/csv",
        }],
    }
    manifest_path = root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_verify_empirical_labels_cli_runs_end_to_end(tmp_path: Path) -> None:
    cohort = (
        b"player_id,name_first,name_last,birth_date,mlbam_id,bbref_id,fangraphs_id,draft_year,lahman_player_id\n"
        b"player_a,Juan,Soto,1998-10-25,101,,,2023,11111111-1111-4111-8111-111111111111\n"
        b"player_b,No,Match,,202,,,2023,22222222-2222-4222-8222-222222222222\n"
    )
    register = (
        b"key_uuid,key_mlbam,key_bbref,key_fangraphs,name_first,name_last,"
        b"birth_year,birth_month,birth_day\n"
        b"11111111-1111-4111-8111-111111111111,101,,,Juan,Soto,1998,10,25\n"
        b"22222222-2222-4222-8222-222222222222,999,,,Different,Player,2000,1,1\n"
    )
    people = b"playerID,debut\n11111111-1111-4111-8111-111111111111,2024-04-15\n"
    cohort_manifest = _make_package(tmp_path / "cohort", "cohort", "cohort.csv", cohort)
    register_manifest = _make_package(tmp_path / "register", "register", "register.csv", register)
    lahman_manifest = _make_package(tmp_path / "lahman", "lahman", "People.csv", people)
    output_dir = tmp_path / "output"
    assert main([
        "verify-empirical-labels",
        "--cohort-manifest", str(cohort_manifest),
        "--cohort-file", "cohort.csv",
        "--register-manifest", str(register_manifest),
        "--register-file", "register.csv",
        "--lahman-manifest", str(lahman_manifest),
        "--people-file", "People.csv",
        "--outcome-through-year", "2025",
        "--output-dir", str(output_dir),
    ]) == 0
    identity = json.loads((output_dir / "identity-matches.json").read_text())
    outcome = json.loads((output_dir / "mlb-debut-labels.json").read_text())
    audit = json.loads((output_dir / "label-audit.json").read_text())
    assert len(identity) == 2
    assert len(outcome) == 2
    assert audit["label_pipeline_complete"] is False
    assert audit["eligible_labels"] == 1
