from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("ncaa_bbStats", reason="ncaa_bbStats not installed")

from draft_model.api import app  # noqa: E402
from draft_model.artifacts import build_artifacts, verify_reproducibility  # noqa: E402
from draft_model.cli import main  # noqa: E402


def test_cli_and_api_share_empirical_backtest_contract(tmp_path: Path) -> None:
    output = tmp_path / "backtest.json"
    assert main(["backtest", "--data-mode", "empirical", "--output", str(output)]) == 0
    cli_payload = json.loads(output.read_text(encoding="utf-8"))
    api_payload = TestClient(app).get("/v1/backtest", params={"data_mode": "empirical"}).json()
    assert cli_payload == api_payload
    assert cli_payload["data_mode"] == "empirical"
    assert "EMPIRICAL" in cli_payload["label"]
    assert len(cli_payload["folds"]) == 4


def test_api_and_cli_share_empirical_board_contract(tmp_path: Path) -> None:
    api_payload = (
        TestClient(app)
        .get("/v1/board", params={"data_mode": "empirical", "draft_year": 2023})
        .json()
    )
    assert "EMPIRICAL" in api_payload["label"]
    assert api_payload["predictions"]
    # CLI parity: the shared service produces identical board JSON
    from draft_model.service import board as build_board

    assert build_board("empirical", 2023).model_dump(mode="json") == api_payload


def test_empirical_build_artifacts_are_labeled_and_reproducible(tmp_path: Path) -> None:
    files = build_artifacts(tmp_path, "empirical")
    expected = {
        "backtest.json",
        "board.csv",
        "board.json",
        "methodology.md",
        "model-card.md",
        "rank-correlation.svg",
        "run-manifest.json",
        "uncertainty.svg",
    }
    assert {path.name for path in files} == expected
    for path in files:
        content = path.read_text(encoding="utf-8")
        assert "EMPIRICAL" in content
        assert "DEMO / NOT EMPIRICAL" not in content
    assert verify_reproducibility("empirical")


def test_empirical_readiness_reports_limited_status() -> None:
    client = TestClient(app)
    payload = client.get("/v1/readiness").json()
    assert payload["status"] == "limited"
    assert payload["gates"][0]["passed"] is True
    assert payload["gates"][1]["passed"] is True
    assert payload["gates"][2]["passed"] is False
    assert payload["gates"][3]["passed"] is False
