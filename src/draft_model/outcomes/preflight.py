from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path

from pydantic import BaseModel

from draft_model.contracts import (
    CohortYearAudit,
    EmpiricalLabelAudit,
    IdentityMatch,
    IdentityResolution,
)
from draft_model.ingest.chadwick import resolve_chadwick_identities
from draft_model.outcomes.lahman import MlbDebutLabel, OutcomeResolution, derive_mlb_debut_labels


def _load_models[ModelT: BaseModel](
    path: Path, model: type[ModelT]
) -> tuple[list[ModelT], str]:
    payload = path.read_bytes()
    parsed = json.loads(payload)
    if not isinstance(parsed, list):
        raise ValueError(f"derived input must be a JSON array: {path}")
    models = [model.model_validate(item) for item in parsed]
    return models, hashlib.sha256(payload).hexdigest()


def _unique_by_player[ModelT: BaseModel](models: list[ModelT]) -> dict[str, ModelT]:
    result: dict[str, ModelT] = {}
    for model in models:
        player_id = getattr(model, "player_id", None)
        if not isinstance(player_id, str) or not player_id or player_id in result:
            raise ValueError(f"blank or duplicate player_id in derived input: {player_id!r}")
        result[player_id] = model
    return result


def audit_empirical_labels(identity_path: Path, outcome_path: Path) -> EmpiricalLabelAudit:
    identities, identity_checksum = _load_models(identity_path, IdentityMatch)
    outcomes, outcome_checksum = _load_models(outcome_path, MlbDebutLabel)
    identities_by_id = _unique_by_player(identities)
    outcomes_by_id = _unique_by_player(outcomes)
    if identities_by_id.keys() != outcomes_by_id.keys():
        missing_identity = sorted(outcomes_by_id.keys() - identities_by_id.keys())
        missing_outcome = sorted(identities_by_id.keys() - outcomes_by_id.keys())
        raise ValueError(
            "identity and outcome player universes differ: "
            f"missing_identity={missing_identity}, missing_outcome={missing_outcome}"
        )

    matched_resolutions = {
        IdentityResolution.MATCHED_EXACT_ID,
        IdentityResolution.MATCHED_NAME_DOB,
    }
    resolved_outcomes = {
        OutcomeResolution.RESOLVED_DEBUT,
        OutcomeResolution.RESOLVED_NO_DEBUT,
    }
    by_year: dict[int, list[str]] = defaultdict(list)
    for player_id, outcome in outcomes_by_id.items():
        by_year[outcome.draft_year].append(player_id)

    year_audits: list[CohortYearAudit] = []
    for year, player_ids in sorted(by_year.items()):
        year_identities = [identities_by_id[player_id] for player_id in player_ids]
        year_outcomes = [outcomes_by_id[player_id] for player_id in player_ids]
        eligible = sum(
            identity.resolution in matched_resolutions and outcome.resolution in resolved_outcomes
            for identity, outcome in zip(year_identities, year_outcomes, strict=True)
        )
        year_audits.append(
            CohortYearAudit(
                draft_year=year,
                total_players=len(player_ids),
                identity_resolved=sum(
                    identity.resolution in matched_resolutions for identity in year_identities
                ),
                identity_conflicts=sum(
                    identity.resolution == IdentityResolution.CONFLICT for identity in year_identities
                ),
                identity_unresolved=sum(
                    identity.resolution == IdentityResolution.UNRESOLVED
                    for identity in year_identities
                ),
                outcomes_resolved=sum(
                    outcome.resolution in resolved_outcomes for outcome in year_outcomes
                ),
                outcomes_unresolved=sum(
                    outcome.resolution == OutcomeResolution.UNRESOLVED_IDENTITY
                    for outcome in year_outcomes
                ),
                outcomes_censored=sum(
                    outcome.resolution == OutcomeResolution.CENSORED for outcome in year_outcomes
                ),
                eligible_labels=eligible,
            )
        )

    total = len(identities)
    eligible_total = sum(year.eligible_labels for year in year_audits)
    pipeline_complete = total > 0 and eligible_total == total
    return EmpiricalLabelAudit(
        label_pipeline_complete=pipeline_complete,
        total_players=total,
        eligible_labels=eligible_total,
        eligible_rate=round(eligible_total / total, 6) if total else 0.0,
        identity_input_sha256=identity_checksum,
        outcome_input_sha256=outcome_checksum,
        years=year_audits,
        limitations=[
            "A complete label pipeline does not establish lawful or complete amateur predictors.",
            "Identity and coverage thresholds require preregistration before empirical use.",
            "The global empirical readiness response remains authoritative.",
        ],
    )


class PipelineOutputs(BaseModel):
    identity_path: Path
    outcome_path: Path
    audit: EmpiricalLabelAudit


def run_empirical_pipeline(
    *,
    cohort_manifest: Path,
    cohort_file: str,
    register_manifest: Path,
    register_file: str,
    lahman_manifest: Path,
    people_file: str,
    outcome_data_through_year: int,
    output_dir: Path,
    horizon_complete_seasons: int = 2,
) -> PipelineOutputs:
    output_dir.mkdir(parents=True, exist_ok=True)
    identity_path = output_dir / "identity-matches.json"
    outcome_path = output_dir / "mlb-debut-labels.json"
    matches = resolve_chadwick_identities(
        cohort_manifest=cohort_manifest,
        cohort_file=cohort_file,
        register_manifest=register_manifest,
        register_file=register_file,
    )
    identity_payload = [match.model_dump(mode="json") for match in matches]
    identity_path.write_text(
        json.dumps(identity_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    labels = derive_mlb_debut_labels(
        cohort_manifest=cohort_manifest,
        cohort_file=cohort_file,
        lahman_manifest=lahman_manifest,
        people_file=people_file,
        outcome_data_through_year=outcome_data_through_year,
        horizon_complete_seasons=horizon_complete_seasons,
    )
    outcome_payload = [label.model_dump(mode="json") for label in labels]
    outcome_path.write_text(
        json.dumps(outcome_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    audit = audit_empirical_labels(identity_path, outcome_path)
    return PipelineOutputs(
        identity_path=identity_path, outcome_path=outcome_path, audit=audit
    )
