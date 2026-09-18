from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from draft_model.artifacts.prospective import export_prospective_schemas
from draft_model.cli import main
from draft_model.contracts.prospective import (
    ProspectiveBattingLine,
    ProspectiveGame,
    ProspectiveMeasurement,
    ProspectivePitchingLine,
    ProspectiveProvenance,
    ProspectiveReleaseManifest,
)


def _provenance() -> dict[str, object]:
    return {
        "source_package_id": "fixture-package",
        "source_record_id": "fixture-record",
        "observed_at": "2026-04-01T18:00:00Z",
        "available_at": "2026-04-01T21:00:00Z",
        "received_at": "2026-04-02T01:00:00Z",
        "collector": "Synthetic fixture operator",
        "method": "Synthetic fixture export",
    }


def test_provenance_rejects_naive_and_out_of_order_timestamps() -> None:
    naive = _provenance() | {"observed_at": "2026-04-01T18:00:00"}
    with pytest.raises(ValidationError, match="include a timezone"):
        ProspectiveProvenance.model_validate(naive)
    reversed_flow = _provenance() | {"available_at": "2026-03-31T21:00:00Z"}
    with pytest.raises(ValidationError, match="observed_at <= available_at"):
        ProspectiveProvenance.model_validate(reversed_flow)


def test_game_rejects_identical_teams() -> None:
    with pytest.raises(ValidationError, match="teams must differ"):
        ProspectiveGame.model_validate(
            {
                "game_id": "game-1",
                "game_date": "2026-04-01",
                "home_team_id": "team-1",
                "away_team_id": "team-1",
                "competition_level": "college",
                "venue": "Synthetic Park",
                "provenance": _provenance(),
            }
        )


def test_batting_rejects_impossible_components() -> None:
    with pytest.raises(ValidationError, match="hit components cannot exceed"):
        ProspectiveBattingLine.model_validate(
            {
                "record_id": "bat-1",
                "player_id": "player_1",
                "game_id": "game-1",
                "plate_appearances": 4,
                "at_bats": 3,
                "singles": 2,
                "doubles": 2,
                "triples": 0,
                "home_runs": 0,
                "walks": 1,
                "hit_by_pitch": 0,
                "strikeouts": 0,
                "sacrifice_flies": 0,
                "stolen_bases": 0,
                "caught_stealing": 0,
                "provenance": _provenance(),
            }
        )


def test_pitching_uses_outs_and_validates_pitch_counts() -> None:
    with pytest.raises(ValidationError, match="strikes require pitches"):
        ProspectivePitchingLine.model_validate(
            {
                "record_id": "pitch-1",
                "player_id": "player_1",
                "game_id": "game-1",
                "outs_recorded": 6,
                "batters_faced": 8,
                "hits_allowed": 1,
                "runs": 0,
                "earned_runs": 0,
                "walks": 1,
                "hit_batters": 0,
                "strikeouts": 3,
                "home_runs_allowed": 0,
                "pitches": None,
                "strikes": 20,
                "provenance": _provenance(),
            }
        )


def test_measurement_requires_device_and_protocol_metadata() -> None:
    with pytest.raises(ValidationError, match="protocol"):
        ProspectiveMeasurement.model_validate(
            {
                "measurement_id": "measurement-1",
                "player_id": "player_1",
                "metric": "fastball_velocity",
                "value": 92.1,
                "unit": "mph",
                "device_make": "Synthetic",
                "device_model": "Fixture",
                "hardware_version": "1",
                "software_version": "1",
                "calibration": "Fixture calibration",
                "attempt": 1,
                "operator": "Fixture operator",
                "environment": {"setting": "test"},
                "provenance": _provenance(),
            }
        )


def test_release_manifest_is_empirical_append_only_and_timestamped() -> None:
    with pytest.raises(ValidationError, match="append-only"):
        ProspectiveReleaseManifest.model_validate(
            {
                "release_id": "release-1",
                "data_mode": "empirical",
                "cutoff": "2026-05-31T23:59:59Z",
                "source_package_ids": ["fixture-package"],
                "protocol_registration": "https://example.invalid/protocol",
                "consent_version": "fixture-v1",
                "append_only": False,
                "correction_log": "corrections.jsonl",
                "limitations": ["Synthetic contract test"],
            }
        )


def test_schema_export_is_deterministic_and_available_from_cli(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    first_files = export_prospective_schemas(first)
    second_files = export_prospective_schemas(second)
    assert len(first_files) == 8
    assert [path.name for path in first_files] == [path.name for path in second_files]
    assert [path.read_bytes() for path in first_files] == [path.read_bytes() for path in second_files]
    cli_output = tmp_path / "cli"
    assert main(["export-prospective-schemas", "--output-dir", str(cli_output)]) == 0
    release_schema = json.loads((cli_output / "release_manifest.schema.json").read_text())
    assert release_schema["properties"]["append_only"]
