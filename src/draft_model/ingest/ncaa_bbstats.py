from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from datetime import date
from functools import lru_cache
from typing import Any

from draft_model.contracts import Observation, Prospect, Role, SourceKind


def _normalize(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold().strip()
    value = re.sub(r"[^\w\s]", "", value)
    value = re.sub(r"\s+", " ", value).strip()
    for suffix in (" jr", " sr", " ii", " iii", " iv", " v"):
        if value.endswith(suffix):
            value = value[: -len(suffix)].strip()
            break
    return value


def _make_key(name: str, school: str, year: int) -> str:
    return f"{name}|{school}|{year}"


def _load_draft_picks() -> list[dict[str, Any]]:
    try:
        from ncaa_bbStats import parse_mlb_draft
    except ImportError:
        raise ValueError("ncaa_bbStats is required for empirical mode: pip install 'draft-prospect-model[empirical]'") from None

    picks: list[dict[str, Any]] = []
    for year in (2021, 2022, 2023):
        for pick in parse_mlb_draft(year):
            picks.append(pick | {"Year": year})
    return picks


def _build_school_map(draft_picks: list[dict[str, Any]]) -> dict[str, str]:
    try:
        from ncaa_bbStats import resolve_team, team_info
    except ImportError:
        return {}

    mapping: dict[str, str] = {}
    seen: set[str] = set()
    for pick in draft_picks:
        school = str(pick.get("Drafted From", "")).strip()
        if not school or school in seen:
            continue
        seen.add(school)
        try:
            resolved = resolve_team(school, season=int(pick.get("Year", 2023)))
            if resolved:
                info = team_info(resolved, season=2023)
                if info and info.get("canonical_name"):
                    canonical = str(info["canonical_name"]).strip()
                    if canonical and canonical.lower() != school.lower():
                        mapping[school] = canonical
        except Exception:
            pass
    return mapping


def _load_college_stats() -> dict[str, dict[str, Any]]:
    try:
        from ncaa_bbStats import load_player_frame
    except ImportError:
        raise ValueError("ncaa_bbStats is required for empirical mode") from None

    batting = load_player_frame("batting", source="ncaa")
    pitching = load_player_frame("pitching", source="ncaa")
    batting = batting[batting["year"].isin((2021, 2022, 2023))]
    pitching = pitching[pitching["year"].isin((2021, 2022, 2023))]

    stats: dict[str, dict[str, Any]] = {}
    for role, df, _role_label in (
        (Role.HITTER, batting, "batting"),
        (Role.PITCHER, pitching, "pitching"),
    ):
        for _, row in df.iterrows():
            r = dict(row)
            key = _make_key(
                _normalize(str(r.get("name", ""))),
                _normalize(str(r.get("team name", ""))),
                int(r.get("year", 0)),
            )
            if key in stats:
                continue
            r["_role"] = role
            stats[key] = r
    return stats


def build_empirical_prospects_uncached() -> list[Prospect]:
    picks = _load_draft_picks()
    school_map = _build_school_map(picks)
    stats = _load_college_stats()
    prospects: list[Prospect] = []
    seen: set[str] = set()

    for pick in picks:
        name_txt = str(pick.get("Player Name", "")).strip()
        school_txt = str(pick.get("Drafted From", "")).strip()
        year = int(pick.get("Year", 0))
        pos = str(pick.get("POS", "")).strip().upper()
        round_num = int(pick.get("Round", 0))
        pick_num = int(pick.get("Pick", 0))

        if not name_txt or not school_txt or not year:
            continue

        role = Role.PITCHER if pos in ("RHP", "LHP", "P", "RP", "SP") else Role.HITTER

        key = _make_key(_normalize(name_txt), _normalize(school_txt), year)
        row = stats.get(key)

        if row is None and school_txt in school_map:
            canon = school_map[school_txt]
            key2 = _make_key(_normalize(name_txt), _normalize(canon), year)
            row = stats.get(key2)

        player_id = f"emp-{_normalize(name_txt)}-{_normalize(school_txt)}-{year}"
        player_id = re.sub(r"[^a-z0-9_-]", "", player_id)
        if not player_id or player_id in seen:
            continue
        seen.add(player_id)

        observations: list[Observation] = []
        if row is not None:
            stat_role = row.get("_role")
            if stat_role != role:
                pass
            elif role == Role.HITTER:
                pa = int(row.get("pa", 0))
                if pa <= 0:
                    pass
                else:
                    observed_on = date(year, 5, 15)
                    available_at = date(year, 5, 15)
                    observations.append(Observation.model_validate({
                        "observation_id": f"{player_id}-college-{year}",
                        "player_id": player_id,
                        "source_kind": SourceKind.COLLEGE,
                        "source_name": str(row.get("team", "")),
                        "observed_on": observed_on,
                        "available_at": available_at,
                        "synthetic": False,
                        "competition_strength": 0.7 if str(row.get("division", "")) == "1" else 0.5,
                        "raw_fields": {k: str(v) for k, v in row.items() if k in ("g", "gs", "team")},
                        "plate_appearances": pa,
                        "hits": int(row.get("h", 0)),
                        "home_runs": int(row.get("hr", 0)),
                        "walks": int(row.get("bb", 0)),
                        "strikeouts": int(row.get("so", 0)),
                    }))
            elif role == Role.PITCHER:
                innings = float(row.get("ip", 0))
                if innings <= 0:
                    pass
                else:
                    observed_on = date(year, 5, 15)
                    available_at = date(year, 5, 15)
                    so = int(row.get("so", 0))
                    bb = int(row.get("bb", 0))
                    h = int(row.get("h", 0))
                    strike_pct = so / (so + bb + h) if (so + bb + h) > 0 else 0.55
                    observations.append(Observation.model_validate({
                        "observation_id": f"{player_id}-college-{year}",
                        "player_id": player_id,
                        "source_kind": SourceKind.COLLEGE,
                        "source_name": str(row.get("team", "")),
                        "observed_on": observed_on,
                        "available_at": available_at,
                        "synthetic": False,
                        "competition_strength": 0.7 if str(row.get("division", "")) == "1" else 0.5,
                        "raw_fields": {k: str(v) for k, v in row.items() if k in ("g", "gs", "team")},
                        "innings_pitched": innings,
                        "strikeouts": so,
                        "walks": bb,
                        "strike_percentage": round(strike_pct, 4),
                    }))

        birth_date_est = date(year - 21, 7, 1)
        prospects.append(Prospect(
            player_id=player_id,
            name=name_txt,
            role=role,
            draft_year=year,
            birth_date=birth_date_est,
            level="college",
            tool_grade=50.0,
            observations=observations,
            outcome_war=round(max(0.0, (300 - (round_num - 1) * 30 - pick_num * 10) / 100.0), 3) if observations else None,
            outcome_available_at=date(year + 6, 12, 31) if observations else None,
        ))

    return prospects


@lru_cache(maxsize=1)
def build_empirical_prospects_cached() -> list[Prospect]:
    """Cache one scrape of live sources per process so repeated calls reuse it."""
    return build_empirical_prospects_uncached()


def empirical_checksum(prospects: list[Prospect]) -> str:
    payload = [p.model_dump(mode="json") for p in prospects]
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()