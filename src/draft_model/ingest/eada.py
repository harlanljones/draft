"""EADA program-resource context (U.S. Dept. of Education, public domain).

The Equity in Athletics Disclosure Act survey is a U.S. federal government
work and therefore public domain — the only source in this project whose
underlying data rights are unambiguous. Its permitted role is narrow:
program-resource context features keyed by school and college season. It is
never a player-level predictor, a cohort, or an outcome source.

Cutoff discipline: EADA data for academic year Y is conservatively treated
as unavailable until December 31 of Y+1 (the Department's release cadence is
slower in some cycles). For a draft in year D this makes Y = D - 2 the
newest usable academic year, and no exception is provided.
"""

from __future__ import annotations

import csv
from datetime import date
from functools import lru_cache
from typing import Any

from draft_model.ingest.ncaa_bbstats import _normalize

EADA_SOURCE_NAME = "EADA survey (U.S. Department of Education)"
EADA_LICENSE_NAME = "Public domain (U.S. federal government work)"
EADA_LICENSE_URL = "https://ope.ed.gov/athletics/#/datafile/list"
EADA_REGISTRY_NOTE = (
    "U.S. federal public domain; program-resource context features only. "
    "Not a player cohort, predictor, or outcome source."
)

# Numeric context fields exposed as features; all are ncaa_bbStats-derived
# computations on public-domain EADA inputs, redistributed under the
# package's MIT license with the underlying federal data unambiguously open.
EADA_CONTEXT_FIELDS = ("budget_pct", "log_budget_per_player", "roster_size")


def eada_publication_cutoff(academic_year: int) -> date:
    """Conservative publication date for EADA data covering ``academic_year``."""
    return date(academic_year + 1, 12, 31)


def latest_usable_eada_year(draft_year: int, as_of: date) -> int:
    """Newest academic year whose EADA release is on or before ``as_of``."""
    year = draft_year - 1
    while year >= 2000 and eada_publication_cutoff(year) > as_of:
        year -= 1
    return year


def _load_packaged_rows() -> list[dict[str, str]]:
    try:
        from ncaa_bbStats.program_store import data_path
    except ImportError:
        raise ValueError(
            "ncaa_bbStats is required for EADA context: pip install 'draft-prospect-model[empirical]'"
        ) from None
    path = data_path("program_finance", "eada_features.csv")
    with open(path, encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_eada_index(rows: list[dict[str, Any]]) -> dict[tuple[str, int], dict[str, float]]:
    """Index EADA records by normalized institution name and academic year.

    Matching is by normalized name; unmatched schools simply yield no context
    and the feature falls back to its neutral value. Records missing every
    context field are dropped rather than emitted as empty context.
    """
    index: dict[tuple[str, int], dict[str, float]] = {}
    for row in rows:
        name = str(row.get("institution_name", "")).strip()
        season_raw = str(row.get("season", "")).strip()
        if not name or not season_raw.isdigit():
            continue
        context: dict[str, float] = {}
        for field in EADA_CONTEXT_FIELDS:
            text = row.get(field)
            if text is None or text == "":
                continue
            try:
                context[field] = float(str(text))
            except ValueError:
                continue
        if context:
            key = (_normalize(name), int(season_raw))
            if key not in index:
                index[key] = context
    return index


@lru_cache(maxsize=1)
def _packaged_index() -> dict[tuple[str, int], dict[str, float]]:
    return build_eada_index([dict(r) for r in _load_packaged_rows()])


def eada_context(
    school: str,
    draft_year: int,
    as_of: date,
    index: dict[tuple[str, int], dict[str, float]] | None = None,
) -> dict[str, float] | None:
    """Program-resource context for a school's newest published EADA year.

    Returns None when the school has no published record usable at ``as_of``.
    Never raises for missing schools — absence is expected and must fall back
    to a neutral feature value, not an inferred one.
    """
    lookup = index if index is not None else _packaged_index()
    year = latest_usable_eada_year(draft_year, as_of)
    while year >= 2000:
        context = lookup.get((_normalize(school), year))
        if context is not None:
            return context | {"eada_year": float(year)}
        year = latest_usable_eada_year(year - 1, as_of)
    return None
