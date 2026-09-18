from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from draft_model.benchmarks import BenchmarkSnapshot
from draft_model.contracts import Observation, SourceKind
from draft_model.ingest import normalize_observation


def test_observation_rejects_impossible_availability() -> None:
    with pytest.raises(ValidationError, match="available_at cannot precede"):
        Observation(
            observation_id="demo-invalid",
            player_id="demo-player",
            source_kind=SourceKind.COLLEGE,
            source_name="Synthetic College Fixture",
            observed_on=date(2026, 4, 2),
            available_at=date(2026, 4, 1),
            synthetic=True,
            competition_strength=0.7,
        )


@pytest.mark.parametrize("source", list(SourceKind))
def test_normalizer_preserves_raw_source_fields(source: SourceKind) -> None:
    raw = {
        "observation_id": f"demo-{source.value}",
        "player_id": "demo-player",
        "source_name": f"Synthetic {source.value}",
        "observed_on": "2026-04-01",
        "available_at": "2026-04-02",
        "synthetic": True,
        "competition_strength": 0.8,
        "source_specific_note": "invented",
    }
    result = normalize_observation(source, raw)
    assert result.source_kind == source
    assert result.raw_fields["source_specific_note"] == "invented"


def test_benchmark_snapshot_must_precede_cutoff() -> None:
    snapshot = BenchmarkSnapshot(
        publisher_shape="synthetic-public-board-shape",
        published_at=date(2026, 6, 2),
        player_id="demo-player",
        rank=1,
        synthetic=True,
    )
    with pytest.raises(ValueError, match="after the prediction cutoff"):
        snapshot.assert_eligible(date(2026, 5, 31))
