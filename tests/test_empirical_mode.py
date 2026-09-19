from __future__ import annotations

from datetime import date

import pytest

from draft_model.contracts import DataMode, SourceKind
from draft_model.features import build_features

ncaa = pytest.importorskip("ncaa_bbStats", reason="ncaa_bbStats not installed")  # noqa: F841

from draft_model.ingest.ncaa_bbstats import (  # noqa: E402
    build_empirical_prospects_cached,
    empirical_checksum,
)
from draft_model.service import backtest, board  # noqa: E402


@pytest.fixture(scope="module")
def prospects() -> list:
    return build_empirical_prospects_cached()


def test_empirical_prospects_are_real_and_cutoff_safe(prospects) -> None:
    assert len(prospects) > 1000
    with_observations = [p for p in prospects if p.observations]
    assert len(with_observations) > 500
    for prospect in with_observations:
        assert all(not o.synthetic for o in prospect.observations)
        assert all(o.source_kind == SourceKind.COLLEGE for o in prospect.observations)
        # every observation is available at or before its draft-year cutoff
        for observation in prospect.observations:
            assert observation.available_at <= date(prospect.draft_year, 5, 31)
        assert prospect.outcome_war is not None
        assert prospect.outcome_available_at is not None
    # players without matched college stats carry no observations and no outcome
    unmatched = [p for p in prospects if not p.observations]
    assert all(p.outcome_war is None for p in unmatched)


def test_empirical_features_respect_cutoff(prospects) -> None:
    matched = [p for p in prospects if p.observations]
    assert matched
    rows = [build_features(p, date(p.draft_year, 5, 31)) for p in matched]
    assert len(rows) == len(matched)
    # post-cutoff construction must fail rather than silently proceed
    with pytest.raises(ValueError, match="post-cutoff"):
        build_features(matched[0], date(matched[0].draft_year, 4, 30))


def test_empirical_checksum_is_deterministic(prospects) -> None:
    assert empirical_checksum(prospects) == empirical_checksum(prospects)


def test_empirical_backtest_covers_2022_and_2023_folds(prospects) -> None:
    result = backtest("empirical")
    assert result.data_mode == DataMode.EMPIRICAL
    assert result.label == "EMPIRICAL (NCAA DATA) / LIMITED COHORT"
    assert {(f.draft_year, f.role) for f in result.folds} == {
        (2022, role) for role in ("hitter", "pitcher")
    } | {(2023, role) for role in ("hitter", "pitcher")}
    for fold in result.folds:
        assert fold.train_size >= 100
        assert fold.test_size >= 100
        assert -1.0 <= fold.rank_correlation <= 1.0
        assert 0.0 <= fold.interval_coverage <= 1.0
        assert 0.0 <= fold.brier_score <= 1.0
    assert any("not MLB performance" in item for item in result.limitations)


def test_empirical_board_returns_ranked_real_players(prospects) -> None:
    result = board("empirical", draft_year=2023)
    assert result.data_mode == DataMode.EMPIRICAL
    assert "EMPIRICAL" in result.label
    assert result.predictions
    scores = [p.projected_war for p in result.predictions]
    assert scores == sorted(scores, reverse=True)
    assert all(p.data_mode == DataMode.EMPIRICAL for p in result.predictions)
    assert all(not p.player_id.startswith("demo-") for p in result.predictions)


def test_empirical_mode_fails_closed_without_dependency(monkeypatch) -> None:
    import draft_model.service as service

    monkeypatch.setattr(service, "_try_empirical", lambda: False)
    with pytest.raises(ValueError, match="ncaa_bbStats is required"):
        backtest("empirical")
    with pytest.raises(ValueError, match="ncaa_bbStats is required"):
        board("empirical", draft_year=2023)
    # demo mode is untouched by the unavailable dependency
    demo = backtest("demo")
    assert demo.label == "DEMO / NOT EMPIRICAL"
