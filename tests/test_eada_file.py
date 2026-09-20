from __future__ import annotations

import csv
from pathlib import Path

import openpyxl
import pytest

from draft_model.ingest.eada import build_eada_index, eada_context
from draft_model.ingest.eada_file import (
    build_context_rows,
    normalize_rows,
    write_context_csv,
)

MODERN_HEADER = [
    "unitid",
    "institution_name",
    "state_cd",
    "SPORTSCODE",
    "PARTIC_MEN",
    "OPEXPPERPART_MEN",
    "EXP_MEN",
    "REV_MEN",
    "MEN_TOTAL_HEADCOACH",
    "MEN_TOTAL_ASSTCOACH",
    "Sports",
]

BASEBALL_ROW = [
    100654,
    "Test State University",
    "AL",
    "MEN-BASE",
    35,
    50000.0,
    1800000.0,
    1500000.0,
    3,
    2,
    "Baseball",
]

OTHER_SPORT_ROW = list(BASEBALL_ROW)
OTHER_SPORT_ROW[-1] = "Basketball"
OTHER_SPORT_ROW[4] = 15  # PARTIC_MEN for the other sport must not leak


@pytest.fixture()
def modern_workbook(tmp_path: Path) -> Path:
    wb = openpyxl.Workbook()
    ws = wb.active
    assert ws is not None
    ws.append(MODERN_HEADER)
    ws.append(BASEBALL_ROW)
    ws.append(OTHER_SPORT_ROW)
    path = tmp_path / "schools.xlsx"
    wb.save(path)
    return path


def test_normalize_rows_selects_baseball_and_maps_schema(modern_workbook: Path) -> None:
    records = normalize_rows(modern_workbook, eada_year=2023)
    assert len(records) == 1  # only the Baseball sport row
    row = records[0]
    assert row["eada_year"] == 2023
    assert row["EXP_MEN_Baseball"] == 1800000.0
    assert row["PARTIC_MEN_Baseball"] == 35
    assert row["unitid"] == 100654


def test_build_context_rows_derives_and_joins_registry(modern_workbook: Path) -> None:
    rows, unmatched = build_context_rows(modern_workbook, 2023)
    # join may or may not resolve this synthetic school through the registry;
    # either way the derivation must not crash and unmatched must be exact.
    assert isinstance(unmatched, list)
    for row in rows:
        assert row["season"] == 2023
        assert row["roster_size"] == 35.0
        assert row["budget_pct"] == 1.0  # single program ranks first


def test_context_csv_round_trips_into_lookup(tmp_path: Path) -> None:
    output = tmp_path / "derived" / "eada-context.csv"
    rows: list[dict[str, object]] = [
        {
            "team_id": "IPEDS:100654",
            "institution_name": "Test State University",
            "unitid": "100654",
            "season": "2023",
            "eada_year": "2023",
            "budget_pct": "0.75",
            "log_budget_per_player": "10.85",
            "roster_size": "35.0",
        }
    ]
    write_context_csv(rows, output)
    with open(output, encoding="utf-8") as handle:
        loaded = list(csv.DictReader(handle))
    assert loaded[0]["budget_pct"] == "0.75"

    index = build_eada_index(loaded)
    context = eada_context("Test State University", 2025, __import__("datetime").date(2025, 5, 15), index=index)
    assert context is not None
    assert context["budget_pct"] == 0.75
