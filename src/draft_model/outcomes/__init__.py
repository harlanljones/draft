from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OutcomeDefinition:
    name: str
    horizon_years: int
    description: str


DEMO_OUTCOME = OutcomeDefinition(
    name="synthetic_cumulative_war_like_value",
    horizon_years=7,
    description=(
        "Invented continuous fixture target used only to exercise temporal modeling; "
        "it is not sourced from Lahman and is not an empirical WAR value."
    ),
)
