from __future__ import annotations

from typing import Any

from draft_model.contracts import Observation, SourceKind


def normalize_observation(source_kind: SourceKind, raw: dict[str, Any]) -> Observation:
    """Normalize a source-shaped record while retaining its original fields."""
    canonical = {
        "observation_id": raw["observation_id"],
        "player_id": raw["player_id"],
        "source_kind": source_kind,
        "source_name": raw["source_name"],
        "observed_on": raw["observed_on"],
        "available_at": raw["available_at"],
        "synthetic": raw.get("synthetic", False),
        "competition_strength": raw["competition_strength"],
        "plate_appearances": raw.get("plate_appearances", 0),
        "hits": raw.get("hits", 0),
        "home_runs": raw.get("home_runs", 0),
        "walks": raw.get("walks", 0),
        "strikeouts": raw.get("strikeouts", 0),
        "innings_pitched": raw.get("innings_pitched", 0.0),
        "strike_percentage": raw.get("strike_percentage"),
        "fastball_velocity": raw.get("fastball_velocity"),
        "raw_fields": raw,
    }
    return Observation.model_validate(canonical)
