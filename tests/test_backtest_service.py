from __future__ import annotations

from draft_model.contracts import DEMO_LABEL, Role
from draft_model.service import backtest, board


def test_backtest_covers_every_requested_cohort_and_role() -> None:
    result = backtest()
    assert len(result.folds) == 18
    assert {(fold.draft_year, fold.role) for fold in result.folds} == {
        (year, role) for year in range(2015, 2024) for role in Role
    }
    assert all(fold.train_size >= 6 and fold.test_size == 2 for fold in result.folds)
    assert all(0.0 <= fold.bust_flag_hit_rate <= 1.0 for fold in result.folds)
    assert result.label == DEMO_LABEL


def test_backtest_is_deterministic() -> None:
    assert backtest().model_dump_json() == backtest().model_dump_json()


def test_board_is_ranked_and_labeled() -> None:
    result = board()
    scores = [prediction.projected_war for prediction in result.predictions]
    assert scores == sorted(scores, reverse=True)
    assert len(result.predictions) == 4
    assert all(prediction.label == DEMO_LABEL for prediction in result.predictions)


def test_empirical_mode_works_when_available() -> None:
    try:
        result = backtest("empirical")
        assert result.data_mode.value == "empirical"
        assert result.label == "EMPIRICAL (NCAA DATA) / LIMITED COHORT"
        assert len(result.folds) == 4
        assert all(fold.train_size >= 1 for fold in result.folds)
        assert all(0.0 <= fold.bust_flag_hit_rate <= 1.0 for fold in result.folds)
        print(f"Empirical backtest folds: {len(result.folds)}")
        for fold in result.folds:
            print(f"  {fold.draft_year} {fold.role.value}: train={fold.train_size} test={fold.test_size} rho={fold.rank_correlation}")
    except ValueError as exc:
        if "ncaa_bbStats is required" in str(exc):
            pass
        else:
            raise
