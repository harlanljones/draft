from __future__ import annotations

import csv
import re
import unicodedata
import uuid
from collections import defaultdict
from datetime import date
from pathlib import Path

from draft_model.contracts import (
    IdentityMatch,
    IdentityResolution,
    SourcePackageManifest,
)
from draft_model.ingest.packages import validated_package_file

COHORT_FIELDS = {
    "player_id",
    "name_first",
    "name_last",
    "birth_date",
    "mlbam_id",
    "bbref_id",
    "fangraphs_id",
}
REGISTER_FIELDS = {
    "key_uuid",
    "key_mlbam",
    "key_bbref",
    "key_fangraphs",
    "name_first",
    "name_last",
    "birth_year",
    "birth_month",
    "birth_day",
}


def _read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"missing required columns in {path.name}: {', '.join(sorted(missing))}")
        return [dict(row) for row in reader]


def _normalize_name(value: str) -> str:
    normalized = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"[^\w]+", "", normalized)


def _register_birth_date(row: dict[str, str]) -> date | None:
    values = (row["birth_year"].strip(), row["birth_month"].strip(), row["birth_day"].strip())
    if not all(values):
        return None
    return date(*(int(value) for value in values))


def resolve_chadwick_identities(
    *,
    cohort_manifest: Path,
    cohort_file: str,
    register_manifest: Path,
    register_file: str,
) -> list[IdentityMatch]:
    cohort_path = validated_package_file(cohort_manifest, cohort_file)
    register_path = validated_package_file(register_manifest, register_file)
    register_package = SourcePackageManifest.model_validate_json(
        register_manifest.read_text(encoding="utf-8")
    )
    cohort_rows = _read_csv(cohort_path, COHORT_FIELDS)
    register_rows = _read_csv(register_path, REGISTER_FIELDS)

    external_indexes: dict[str, dict[str, set[str]]] = {
        field: defaultdict(set) for field in ("key_mlbam", "key_bbref", "key_fangraphs")
    }
    name_dob_index: dict[tuple[str, str, date], set[str]] = defaultdict(set)
    seen_uuids: set[str] = set()
    for row in register_rows:
        try:
            register_uuid = str(uuid.UUID(row["key_uuid"].strip()))
        except ValueError as exc:
            raise ValueError(f"invalid Chadwick key_uuid: {row['key_uuid']!r}") from exc
        if register_uuid in seen_uuids:
            raise ValueError(f"duplicate Chadwick key_uuid: {register_uuid}")
        seen_uuids.add(register_uuid)
        for field, index in external_indexes.items():
            value = row[field].strip()
            if value:
                index[value].add(register_uuid)
        birth_date = _register_birth_date(row)
        first = _normalize_name(row["name_first"])
        last = _normalize_name(row["name_last"])
        if birth_date is not None and first and last:
            name_dob_index[(first, last, birth_date)].add(register_uuid)

    matches: list[IdentityMatch] = []
    seen_project_ids: set[str] = set()
    id_mapping = {
        "mlbam_id": "key_mlbam",
        "bbref_id": "key_bbref",
        "fangraphs_id": "key_fangraphs",
    }
    for row in cohort_rows:
        project_id = row["player_id"].strip()
        if not project_id or project_id in seen_project_ids:
            raise ValueError(f"blank or duplicate player_id: {project_id!r}")
        seen_project_ids.add(project_id)
        evidence: list[str] = []
        exact_candidates: set[str] = set()
        for cohort_field, register_field in id_mapping.items():
            value = row[cohort_field].strip()
            if value:
                candidates = external_indexes[register_field].get(value, set())
                evidence.append(f"{cohort_field}={value}:matches={len(candidates)}")
                exact_candidates.update(candidates)

        resolution = IdentityResolution.UNRESOLVED
        method = "none"
        candidates = exact_candidates
        if len(exact_candidates) == 1:
            resolution = IdentityResolution.MATCHED_EXACT_ID
            method = "unique_external_id"
        elif len(exact_candidates) > 1:
            resolution = IdentityResolution.CONFLICT
            method = "conflicting_or_ambiguous_external_ids"
        else:
            birth_value = row["birth_date"].strip()
            first = _normalize_name(row["name_first"])
            last = _normalize_name(row["name_last"])
            if birth_value and first and last:
                birth_date = date.fromisoformat(birth_value)
                candidates = name_dob_index.get((first, last, birth_date), set())
                evidence.append(f"full_name_birth_date:matches={len(candidates)}")
                if len(candidates) == 1:
                    resolution = IdentityResolution.MATCHED_NAME_DOB
                    method = "unique_normalized_full_name_and_birth_date"
                elif len(candidates) > 1:
                    resolution = IdentityResolution.CONFLICT
                    method = "ambiguous_normalized_full_name_and_birth_date"
            else:
                evidence.append("full_name_birth_date:incomplete")

        ordered_candidates = sorted(candidates)
        matched_uuid = ordered_candidates[0] if resolution in {
            IdentityResolution.MATCHED_EXACT_ID,
            IdentityResolution.MATCHED_NAME_DOB,
        } else None
        matches.append(
            IdentityMatch(
                player_id=project_id,
                register_package_id=register_package.package_id,
                resolution=resolution,
                matched_uuid=matched_uuid,
                candidate_uuids=ordered_candidates,
                method=method,
                evidence=evidence,
            )
        )
    return sorted(matches, key=lambda match: match.player_id)
