from __future__ import annotations

from datetime import date

import pytest

from draft_model.contracts import Role
from draft_model.demo import load_demo_prospects
from draft_model.features import build_features
from draft_model.modeling import fit, predict


def test_feature_builder_fails_on_post_cutoff_input() -> None:
    prospect = load_demo_prospects()[0]
    with pytest.raises(ValueError, match="post-cutoff"):
        build_features(prospect, date(prospect.draft_year, 3, 1))


def test_role_specific_features_do_not_use_era() -> None:
    prospects = load_demo_prospects()
    hitter = next(p for p in prospects if p.role == Role.HITTER)
    pitcher = next(p for p in prospects if p.role == Role.PITCHER)
    hitter_row = build_features(hitter, date(hitter.draft_year, 5, 31))
    pitcher_row = build_features(pitcher, date(pitcher.draft_year, 5, 31))
    assert "offense" in hitter_row.feature_names
    assert "velocity" in pitcher_row.feature_names
    assert "era" not in pitcher_row.feature_names


def test_high_school_predictions_are_wider() -> None:
    prospects = load_demo_prospects()
    historical = [p for p in prospects if p.role == Role.HITTER and p.draft_year <= 2023]
    training = [build_features(p, date(p.draft_year, 5, 31)) for p in historical]
    model = fit(training, Role.HITTER)
    candidates = [p for p in prospects if p.role == Role.HITTER and p.draft_year == 2026]
    rows = [build_features(p, date(2026, 5, 31)) for p in candidates]
    predictions = {row.high_school: predict(model, row) for row in rows}
    assert predictions[True].uncertainty_width > predictions[False].uncertainty_width


def test_model_fit_is_deterministic() -> None:
    prospects = [p for p in load_demo_prospects() if p.role == Role.PITCHER and p.draft_year <= 2023]
    rows = [build_features(p, date(p.draft_year, 5, 31)) for p in prospects]
    first = fit(rows, Role.PITCHER)
    second = fit(rows, Role.PITCHER)
    assert first.coefficients.tolist() == second.coefficients.tolist()
