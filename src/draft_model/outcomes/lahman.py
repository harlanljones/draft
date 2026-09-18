from __future__ import annotations

import csv
from datetime import date
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from draft_model.contracts import SCHEMA_VERSION
from draft_model.ingest.packages import validated_package_file


class OutcomeResolution(StrEnum):
    RESOLVED_DEBUT = "resolved_debut"
    RESOLVED_NO_DEBUT = "resolved_no_debut"
    UNRESOLVED_IDENTITY = "unresolved_identity"
    CENSORED = "censored"


class MlbDebutLabel(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str = SCHEMA_VERSION
    player_id: str
    lahman_player_id: str | None
    draft_year: int
    horizon_complete_seasons: int
    outcome_data_through_year: int
    resolution: OutcomeResolution
    debut_date: date | None
    debut_within_horizon: bool | None


def _read_csv(path: Path, required_fields: set[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        actual = set(reader.fieldnames or [])
        missing = required_fields - actual
        if missing:
            raise ValueError(f"missing required columns in {path.name}: {', '.join(sorted(missing))}")
        return [dict(row) for row in reader]


def derive_mlb_debut_labels(
    *,
    cohort_manifest: Path,
    cohort_file: str,
    lahman_manifest: Path,
    people_file: str,
    outcome_data_through_year: int,
    horizon_complete_seasons: int = 2,
) -> list[MlbDebutLabel]:
    if horizon_complete_seasons < 1:
        raise ValueError("horizon_complete_seasons must be positive")
    cohort_path = validated_package_file(cohort_manifest, cohort_file)
    people_path = validated_package_file(lahman_manifest, people_file)
    cohort = _read_csv(cohort_path, {"player_id", "draft_year", "lahman_player_id"})
    people_rows = _read_csv(people_path, {"playerID", "debut"})

    people: dict[str, date | None] = {}
    for row in people_rows:
        player_id = row["playerID"].strip()
        if not player_id:
            raise ValueError("Lahman playerID cannot be blank")
        if player_id in people:
            raise ValueError(f"duplicate Lahman playerID: {player_id}")
        people[player_id] = date.fromisoformat(row["debut"]) if row["debut"].strip() else None

    labels: list[MlbDebutLabel] = []
    seen_project_ids: set[str] = set()
    for row in cohort:
        project_id = row["player_id"].strip()
        if not project_id or project_id in seen_project_ids:
            raise ValueError(f"blank or duplicate cohort player_id: {project_id!r}")
        seen_project_ids.add(project_id)
        draft_year = int(row["draft_year"])
        lahman_id = row["lahman_player_id"].strip() or None
        deadline_year = draft_year + horizon_complete_seasons

        resolution = OutcomeResolution.UNRESOLVED_IDENTITY
        debut: date | None = None
        within_horizon: bool | None = None
        if outcome_data_through_year < deadline_year:
            resolution = OutcomeResolution.CENSORED
        elif lahman_id is not None and lahman_id in people:
            debut = people[lahman_id]
            if debut is not None and debut.year < draft_year:
                raise ValueError(f"debut predates draft year for {project_id}")
            within_horizon = debut is not None and debut.year <= deadline_year
            resolution = (
                OutcomeResolution.RESOLVED_DEBUT
                if within_horizon
                else OutcomeResolution.RESOLVED_NO_DEBUT
            )

        labels.append(
            MlbDebutLabel(
                player_id=project_id,
                lahman_player_id=lahman_id,
                draft_year=draft_year,
                horizon_complete_seasons=horizon_complete_seasons,
                outcome_data_through_year=outcome_data_through_year,
                resolution=resolution,
                debut_date=debut,
                debut_within_horizon=within_horizon,
            )
        )
    return sorted(labels, key=lambda label: label.player_id)
