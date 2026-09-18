from __future__ import annotations

from datetime import date

import numpy as np

from draft_model.contracts import BacktestFold, BacktestResult, DataMode, FeatureRow, Role
from draft_model.modeling import fit, predict


def _rank(values: list[float]) -> np.ndarray:
    order = np.argsort(np.asarray(values), kind="stable")
    ranks = np.empty(len(values), dtype=float)
    ranks[order] = np.arange(len(values), dtype=float)
    return ranks


def rank_correlation(left: list[float], right: list[float]) -> float:
    if len(left) < 2 or len(set(left)) < 2 or len(set(right)) < 2:
        return 0.0
    return float(np.corrcoef(_rank(left), _rank(right))[0, 1])


def run_backtest(rows: list[FeatureRow]) -> BacktestResult:
    folds: list[BacktestFold] = []
    for year in range(2015, 2024):
        for role in Role:
            train = [r for r in rows if r.role == role and r.draft_year < year]
            test = [r for r in rows if r.role == role and r.draft_year == year]
            if len(train) < 4 or not test:
                continue
            model = fit(train, role)
            predictions = [predict(model, row) for row in test]
            actual = [float(row.outcome_war) for row in test if row.outcome_war is not None]
            projected = [p.projected_war for p in predictions]
            absolute = [abs(a - p) for a, p in zip(actual, projected, strict=True)]
            covered = [p.lower_war <= a <= p.upper_war for a, p in zip(actual, predictions, strict=True)]
            brier = [
                (p.probability_two_war - float(a >= 2.0)) ** 2
                for a, p in zip(actual, predictions, strict=True)
            ]
            actual_busts = [a < 2.0 for a in actual]
            caught_busts = [
                actual_bust and prediction.projected_war < 2.0
                for actual_bust, prediction in zip(actual_busts, predictions, strict=True)
            ]
            bust_hit_rate = sum(caught_busts) / max(sum(actual_busts), 1)
            benchmark = [row.values[-2] if role == Role.HITTER else row.values[-1] for row in test]
            folds.append(
                BacktestFold(
                    draft_year=year,
                    role=role,
                    train_size=len(train),
                    test_size=len(test),
                    rank_correlation=round(rank_correlation(projected, actual), 4),
                    mean_absolute_error=round(float(np.mean(absolute)), 4),
                    interval_coverage=round(float(np.mean(covered)), 4),
                    brier_score=round(float(np.mean(brier)), 4),
                    bust_flag_hit_rate=round(bust_hit_rate, 4),
                    benchmark_rank_correlation=round(rank_correlation(benchmark, actual), 4),
                )
            )
    return BacktestResult(
        data_mode=DataMode.DEMO,
        as_of=date(2023, 5, 31),
        folds=folds,
        limitations=[
            "All players, observations, outcomes, and benchmark scores are synthetic fixtures.",
            "Metrics validate execution only and are not estimates of baseball performance.",
            "Two-player test cohorts are intentionally tiny and unsuitable for inference.",
        ],
    )
