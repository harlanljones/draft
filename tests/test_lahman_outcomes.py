from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from draft_model.cli import main
from draft_model.outcomes.lahman import OutcomeResolution, derive_mlb_debut_labels


def _package(root: Path, package_id: str, filename: str, payload: bytes) -> Path:
    root.mkdir()
    (root / filename).write_bytes(payload)
    manifest = {
        "schema_version": "1.0",
        "package_id": package_id,
        "source": f"Synthetic {package_id}",
        "data_mode": "empirical",
        "retrieved_at": "2026-09-17",
        "source_available_at": "2025-12-31",
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
        b"player_id,draft_year,lahman_player_id\n"
        b"player_a,2023,known1\n"
        b"player_b,2023,known2\n"
        b"player_c,2023,missing\n"
        b"player_d,2023,\n"
        b"player_e,2024,known3\n"
    )
    people = b"playerID,debut\nknown1,2024-06-01\nknown2,\nknown3,2025-07-01\n"
    return (
        _package(tmp_path / "cohort", "cohort-fixture", "cohort.csv", cohort),
        _package(tmp_path / "lahman", "lahman-fixture", "People.csv", people),
    )


def test_lahman_labels_preserve_unresolved_and_censored_states(tmp_path: Path) -> None:
    cohort_manifest, lahman_manifest = _fixtures(tmp_path)
    labels = derive_mlb_debut_labels(
        cohort_manifest=cohort_manifest,
        cohort_file="cohort.csv",
        lahman_manifest=lahman_manifest,
        people_file="People.csv",
        outcome_data_through_year=2025,
    )
    by_player = {label.player_id: label for label in labels}
    assert by_player["player_a"].resolution == OutcomeResolution.RESOLVED_DEBUT
    assert by_player["player_a"].debut_within_horizon is True
    assert by_player["player_b"].resolution == OutcomeResolution.RESOLVED_NO_DEBUT
    assert by_player["player_b"].debut_within_horizon is False
    assert by_player["player_c"].resolution == OutcomeResolution.UNRESOLVED_IDENTITY
    assert by_player["player_c"].debut_within_horizon is None
    assert by_player["player_d"].resolution == OutcomeResolution.UNRESOLVED_IDENTITY
    assert by_player["player_e"].resolution == OutcomeResolution.CENSORED
    assert by_player["player_e"].debut_within_horizon is None


def test_lahman_adapter_requires_declared_files(tmp_path: Path) -> None:
    cohort_manifest, lahman_manifest = _fixtures(tmp_path)
    with pytest.raises(ValueError, match="not declared"):
        derive_mlb_debut_labels(
            cohort_manifest=cohort_manifest,
            cohort_file="other.csv",
            lahman_manifest=lahman_manifest,
            people_file="People.csv",
            outcome_data_through_year=2025,
        )


def test_lahman_adapter_rejects_pre_draft_debut(tmp_path: Path) -> None:
    cohort = b"player_id,draft_year,lahman_player_id\nplayer_a,2023,known1\n"
    people = b"playerID,debut\nknown1,2022-06-01\n"
    cohort_manifest = _package(tmp_path / "cohort", "cohort-fixture", "cohort.csv", cohort)
    lahman_manifest = _package(tmp_path / "lahman", "lahman-fixture", "People.csv", people)
    with pytest.raises(ValueError, match="debut predates draft year"):
        derive_mlb_debut_labels(
            cohort_manifest=cohort_manifest,
            cohort_file="cohort.csv",
            lahman_manifest=lahman_manifest,
            people_file="People.csv",
            outcome_data_through_year=2025,
        )


def test_lahman_outcome_cli_is_deterministic(tmp_path: Path) -> None:
    cohort_manifest, lahman_manifest = _fixtures(tmp_path)
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    arguments = [
        "derive-lahman-debut-outcomes",
        "--cohort-manifest",
        str(cohort_manifest),
        "--cohort-file",
        "cohort.csv",
        "--lahman-manifest",
        str(lahman_manifest),
        "--people-file",
        "People.csv",
        "--outcome-through-year",
        "2025",
    ]
    assert main([*arguments, "--output", str(first)]) == 0
    assert main([*arguments, "--output", str(second)]) == 0
    assert first.read_bytes() == second.read_bytes()
