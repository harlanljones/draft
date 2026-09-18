from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

from draft_model.contracts import Observation, Prospect, Role, SourceKind

DEMO_SEED = 20260917


def _observation(
    player_id: str,
    year: int,
    role: Role,
    variant: int,
    source: SourceKind,
    sequence: int,
) -> Observation:
    quality = ((year * 7 + variant * 11 + sequence * 5) % 19) / 18
    competition = {SourceKind.COLLEGE: 0.78, SourceKind.SUMMER: 0.86, SourceKind.SHOWCASE: 0.58}[source]
    observed = date(year, 3 + sequence, 10 + variant)
    common: dict[str, Any] = {
        "observation_id": f"demo-{player_id}-{source}-{sequence}",
        "player_id": player_id,
        "source_kind": source,
        "source_name": f"Synthetic {source.value.title()} Fixture",
        "observed_on": observed,
        "available_at": date(year, observed.month, observed.day + 2),
        "synthetic": True,
        "competition_strength": competition,
        "raw_fields": {"fixture": "invented", "quality_index": quality},
    }
    if role == Role.HITTER:
        pa = 90 if source != SourceKind.SHOWCASE else 28
        return Observation.model_validate(
            common
            | {
                "plate_appearances": pa,
                "hits": round(pa * (0.20 + 0.10 * quality)),
                "home_runs": round(pa * (0.015 + 0.055 * quality)),
                "walks": round(pa * (0.06 + 0.07 * quality)),
                "strikeouts": round(pa * (0.28 - 0.12 * quality)),
            }
        )
    innings = 42 if source != SourceKind.SHOWCASE else 12
    return Observation.model_validate(
        common
        | {
            "innings_pitched": innings,
            "strikeouts": round(innings * (0.65 + quality)),
            "walks": round(innings * (0.50 - 0.25 * quality)),
            "strike_percentage": 0.57 + 0.11 * quality,
            "fastball_velocity": 87.0
            + 9.0 * quality
            - (1.0 if source == SourceKind.SHOWCASE else 0.0),
        }
    )


def load_demo_prospects() -> list[Prospect]:
    prospects: list[Prospect] = []
    for year in range(2012, 2027):
        for role in Role:
            for variant in range(2):
                level = "high_school" if variant else "college"
                player_id = f"demo-{year}-{role.value}-{variant}"
                primary = SourceKind.SHOWCASE if variant else SourceKind.COLLEGE
                observations = [_observation(player_id, year, role, variant, primary, 0)]
                if not variant:
                    observations.append(
                        _observation(player_id, year, role, variant, SourceKind.SUMMER, 1)
                    )
                age = 18 if variant else 20 + (year + (1 if role == Role.PITCHER else 0)) % 3
                quality = ((year * 7 + variant * 11) % 19) / 18
                role_bonus = 0.3 if role == Role.HITTER else 0.0
                outcome = None
                outcome_available = None
                if year <= 2023:
                    outcome = round(-0.8 + quality * 6.5 - max(age - 20, 0) * 0.45 + role_bonus, 3)
                    outcome_available = date(year + 7, 12, 31)
                prospects.append(
                    Prospect(
                        player_id=player_id,
                        name=f"Demo {role.value.title()} {year}-{variant + 1}",
                        role=role,
                        draft_year=year,
                        birth_date=date(year - age, 7, 1),
                        level=level,
                        tool_grade=round(40 + quality * 25 + (3 if variant else 0), 1),
                        observations=observations,
                        outcome_war=outcome,
                        outcome_available_at=outcome_available,
                    )
                )
    return prospects


def demo_checksum(prospects: list[Prospect]) -> str:
    payload = [p.model_dump(mode="json") for p in prospects]
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()
