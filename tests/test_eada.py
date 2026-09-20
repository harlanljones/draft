from __future__ import annotations

from datetime import date

from draft_model.contracts import DEMO_LABEL, Observation, Prospect, Role, SourceKind
from draft_model.features import build_features
from draft_model.ingest.eada import (
    EADA_LICENSE_NAME,
    EADA_SOURCE_NAME,
    build_eada_index,
    eada_context,
    eada_publication_cutoff,
    latest_usable_eada_year,
)

EADA_ROWS = [
    {
        "institution_name": "State University",
        "season": "2021",
        "budget_pct": "0.9",
        "log_budget_per_player": "8.5",
        "roster_size": "40.0",
    },
    {
        "institution_name": "State University",
        "season": "2022",
        "budget_pct": "0.8",
        "log_budget_per_player": "8.6",
        "roster_size": "38.0",
    },
]

INDEX = build_eada_index(EADA_ROWS)


def observation(raw_fields: dict) -> Observation:
    return Observation(
        observation_id="obs-1",
        player_id="p1",
        source_kind=SourceKind.COLLEGE,
        source_name="test",
        observed_on=date(2023, 5, 15),
        available_at=date(2023, 5, 15),
        synthetic=True,
        competition_strength=0.5,
        plate_appearances=100,
        hits=30,
        home_runs=5,
        walks=10,
        strikeouts=20,
        raw_fields=raw_fields,
    )


def prospect(obs: Observation) -> Prospect:
    return Prospect(
        player_id="p1",
        name="Test Player",
        role=Role.HITTER,
        draft_year=2023,
        birth_date=date(2002, 6, 1),
        level="college",
        tool_grade=55.0,
        observations=[obs],
    )


def test_eada_publication_cutoff_is_conservative() -> None:
    # Academic year 2021 data is treated as published only at the end of 2022.
    assert eada_publication_cutoff(2021) == date(2022, 12, 31)


def test_latest_usable_year_respects_cutoff() -> None:
    # A 2023 draft (as_of May 2023) can use 2021 but not 2022 EADA data.
    assert latest_usable_eada_year(2023, date(2023, 5, 15)) == 2021


def test_context_never_returns_unpublished_year() -> None:
    # 2022 academic-year data is not published until 2023-12-31: the 2021
    # record must be selected instead, never the newer one.
    context = eada_context("State University", 2023, date(2023, 5, 15), index=INDEX)
    assert context is not None
    assert context["eada_year"] == 2021.0
    assert context["budget_pct"] == 0.9


def test_context_falls_back_to_older_published_year() -> None:
    # Early in 2023 nothing newer than 2021 is usable; ask for 2022 and the
    # walk-back must land on 2021, not return 2022.
    context = eada_context("State University", 2024, date(2023, 5, 15), index=INDEX)
    assert context is not None
    assert context["eada_year"] == 2021.0


def test_context_none_for_unknown_school() -> None:
    assert eada_context("Nowhere College", 2023, date(2023, 5, 15), index=INDEX) is None


def test_eada_provenance_constants_carry_license() -> None:
    assert EADA_LICENSE_NAME.startswith("Public domain")
    assert "ed.gov" in EADA_SOURCE_NAME or "EADA" in EADA_SOURCE_NAME


def test_feature_includes_program_resources() -> None:
    obs = observation(
        {
            "eada_source": EADA_SOURCE_NAME,
            "eada_license": EADA_LICENSE_NAME,
            "eada_budget_pct": 0.9,
        }
    )
    row = build_features(prospect(obs), date(2023, 5, 15))
    assert "program_resources" in row.feature_names
    assert row.values[row.feature_names.index("program_resources")] == 0.9


def test_feature_neutral_without_eada_context() -> None:
    row = build_features(prospect(observation({})), date(2023, 5, 15))
    assert row.values[row.feature_names.index("program_resources")] == 0.5
    assert DEMO_LABEL  # sanity: demo labeling constants remain importable
