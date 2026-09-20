from __future__ import annotations

from datetime import date

from draft_model.backtest import run_backtest
from draft_model.contracts import (
    BacktestResult,
    BoardResponse,
    DataMode,
    ReadinessGate,
    ReadinessResponse,
    Role,
    SourceDisposition,
    SourceStatus,
)
from draft_model.demo import load_demo_prospects
from draft_model.features import build_features
from draft_model.modeling import fit, predict


def _try_empirical() -> bool:
    try:
        import ncaa_bbStats  # noqa: F401
        return True
    except Exception:
        return False


def backtest(data_mode: str | DataMode = DataMode.DEMO) -> BacktestResult:
    mode = DataMode(data_mode)
    if mode == DataMode.DEMO:
        prospects = [p for p in load_demo_prospects() if p.draft_year <= 2023]
        rows = [build_features(p, date(p.draft_year, 5, 31)) for p in prospects]
        result = run_backtest(rows)
        result.data_mode = DataMode.DEMO
        return result
    if mode == DataMode.EMPIRICAL:
        if not _try_empirical():
            raise ValueError("ncaa_bbStats is required for empirical mode: pip install 'draft-prospect-model[empirical]'")
        from draft_model.ingest.ncaa_bbstats import build_empirical_prospects_cached
        prospects = build_empirical_prospects_cached()
        rows = [build_features(p, date(p.draft_year, 5, 31)) for p in prospects if p.observations]
        result = run_backtest(rows)
        result.data_mode = DataMode.EMPIRICAL
        result.label = "EMPIRICAL (NCAA DATA) / LIMITED COHORT"
        result.limitations = [
            "Empirical backtest uses ncaa_bbStats college data for draft years 2021-2023 only.",
            "Birth dates are estimated from class year; age features are approximate.",
            "Outcome targets are draft-position proxies, not MLB performance.",
            "Name+school matching may miss or misidentify some players.",
        ]
        return result
    raise ValueError("data_mode must be demo or empirical")


def board(data_mode: str | DataMode = DataMode.DEMO, draft_year: int = 2026) -> BoardResponse:
    mode = DataMode(data_mode)
    if mode == DataMode.DEMO:
        prospects = load_demo_prospects()
        training = [p for p in prospects if p.draft_year <= 2023]
        training_rows = [build_features(p, date(p.draft_year, 5, 31)) for p in training]
        candidates = [p for p in prospects if p.draft_year == draft_year]
        candidate_rows = [build_features(p, date(draft_year, 5, 31)) for p in candidates]
        models = {role: fit(training_rows, role) for role in Role}
        predictions = [predict(models[row.role], row, mode) for row in candidate_rows]
        predictions.sort(key=lambda item: (-item.projected_war, item.player_id))
        return BoardResponse(
            data_mode=mode,
            as_of=date(draft_year, 5, 31),
            predictions=predictions,
            limitations=[
                "Synthetic demonstration board; it contains no real players or empirical rankings.",
                "High-school intervals are intentionally wider because their fixture evidence is sparse.",
                "No current THE BOARD or MLB Pipeline data is included.",
            ],
        )
    if mode == DataMode.EMPIRICAL:
        if not _try_empirical():
            raise ValueError("ncaa_bbStats is required for empirical mode: pip install 'draft-prospect-model[empirical]'")
        from draft_model.ingest.ncaa_bbstats import build_empirical_prospects_cached
        prospects = build_empirical_prospects_cached()
        training = [p for p in prospects if p.draft_year <= 2023 and p.observations]
        training_rows = [build_features(p, date(p.draft_year, 5, 31)) for p in training]
        candidates = [p for p in prospects if p.draft_year == draft_year and p.observations]
        candidate_rows = [build_features(p, date(draft_year, 5, 31)) for p in candidates]
        if not training_rows or not candidate_rows:
            raise ValueError("insufficient prospects for board generation")
        models = {role: fit(training_rows, role) for role in Role}
        predictions = [predict(models[row.role], row, mode) for row in candidate_rows]
        predictions.sort(key=lambda item: (-item.projected_war, item.player_id))
        return BoardResponse(
            data_mode=mode,
            label="EMPIRICAL (NCAA DATA) / LIMITED COHORT",
            as_of=date(draft_year, 5, 31),
            predictions=predictions,
            limitations=[
                "Board uses ncaa_bbStats college data; names are real but projections are draft-position proxies.",
                "Only 2021-2023 draft years available; birth dates estimated from class year.",
                "Not a THE BOARD or MLB Pipeline equivalent.",
            ],
        )
    raise ValueError("data_mode must be demo or empirical")


def readiness() -> ReadinessResponse:
    has_empirical = _try_empirical()
    gates = [
        ReadinessGate(
            gate="lawful_cohort",
            passed=has_empirical,
            evidence=(
                "ncaa_bbStats provides MIT-bundled draft data for 2021-2023."
                if has_empirical
                else "MLB/MLBAM delivery is the preferred cohort path, but bulk, retention, ML, and public-output rights have not been granted."
            ),
        ),
        ReadinessGate(
            gate="lawful_pre_cutoff_predictors",
            passed=has_empirical,
            evidence=(
                "ncaa_bbStats provides NCAA-sourced college batting/pitching stats for 2021-2023."
                if has_empirical
                else "6-4-3 Charts and SIS are candidate predictor partners, but no research license or dated historical delivery has been obtained."
            )
            + " EADA program-resource context (U.S. federal public domain) supplements both roles.",
        ),
        ReadinessGate(
            gate="validated_outcome_identity_joins",
            passed=False,
            evidence="Lahman/Chadwick are conditional and no lawful cohort exists for validation.",
        ),
        ReadinessGate(
            gate="mature_preregistered_labels",
            passed=False,
            evidence="A two-season Lahman debut target is proposed but awaits domain approval.",
        ),
    ]
    overridden = has_empirical and all(g.passed for g in gates[:2]) and not any(g.passed for g in gates[2:])
    return ReadinessResponse(
        status="limited" if overridden else "no_go",
        label="EMPIRICAL DISABLED / LIMITED NO-GO" if not has_empirical
        else "EMPIRICAL (NCAA DATA) LIMITED / OUTCOMES AND IDENTITY STILL BLOCKED",
        evaluated_at=date(2026, 9, 17),
        gates=gates,
        sources=[
            SourceDisposition(
                source="EADA survey (U.S. Dept. of Education)",
                status=SourceStatus.AVAILABLE,
                permitted_role="Program-resource context features only; U.S. federal public domain",
            ),
            SourceDisposition(
                source="ncaa_bbStats (MIT)",
                status=SourceStatus.AVAILABLE,
                permitted_role="Cohort (draft picks 2021-2023) and college predictors (batting+pitching 2021-2023)",
            ),
            SourceDisposition(
                source="SABR Lahman 2025",
                status=SourceStatus.CONDITIONAL,
                permitted_role="Pinned MLB debut/counting outcomes only",
            ),
            SourceDisposition(
                source="Chadwick Register",
                status=SourceStatus.CONDITIONAL,
                permitted_role="Pinned, validated identity aid only",
            ),
            SourceDisposition(
                source="Retrosheet",
                status=SourceStatus.AVAILABLE,
                permitted_role="Pinned MLB outcome validation with attribution",
            ),
            *[
                SourceDisposition(source=source, status=SourceStatus.UNAVAILABLE, permitted_role="None")
                for source in (
                    "NCAA",
                    "Cape Cod Baseball League",
                    "Northwoods League",
                    "Perfect Game",
                    "Baseball-Reference",
                    "MLB Pipeline",
                    "FanGraphs THE BOARD",
                )
            ],
        ],
        decision_record="reports/Open source baseball data.md",
    )
