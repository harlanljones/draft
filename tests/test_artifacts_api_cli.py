from __future__ import annotations

import json
import re
from pathlib import Path

from fastapi.testclient import TestClient

from draft_model.api import app
from draft_model.artifacts import build_artifacts, verify_reproducibility
from draft_model.cli import main
from draft_model.contracts import DEMO_LABEL


def test_artifact_set_and_report_truth_boundary(tmp_path: Path) -> None:
    files = build_artifacts(tmp_path)
    assert {path.name for path in files} == {
        "backtest.json",
        "board.csv",
        "board.json",
        "methodology.md",
        "model-card.md",
        "rank-correlation.svg",
        "run-manifest.json",
        "uncertainty.svg",
    }
    report = (tmp_path / "methodology.md").read_text(encoding="utf-8")
    word_count = len(re.findall(r"\b[\w’-]+\b", report))
    assert 1500 <= word_count <= 2000
    assert "No empirical claims are available" in report
    assert DEMO_LABEL in report
    assert all(DEMO_LABEL in path.read_text(encoding="utf-8") for path in files)


def test_canonical_artifacts_are_reproducible() -> None:
    assert verify_reproducibility()


def test_cli_and_api_share_response_contract(tmp_path: Path) -> None:
    output = tmp_path / "backtest.json"
    assert main(["backtest", "--data-mode", "demo", "--output", str(output)]) == 0
    cli_payload = json.loads(output.read_text(encoding="utf-8"))
    api_payload = TestClient(app).get("/v1/backtest").json()
    assert cli_payload == api_payload


def test_api_health_and_invalid_mode() -> None:
    client = TestClient(app)
    assert client.get("/health").json()["label"] == DEMO_LABEL
    response = client.get("/v1/board", params={"data_mode": "empirical", "draft_year": 2023})
    assert response.status_code == 200
    assert "EMPIRICAL" in response.json()["label"]


def test_cli_and_api_share_readiness_contract(tmp_path: Path) -> None:
    output = tmp_path / "readiness.json"
    assert main(["readiness", "--output", str(output)]) == 0
    cli_payload = json.loads(output.read_text(encoding="utf-8"))
    api_payload = TestClient(app).get("/v1/readiness").json()
    assert cli_payload == api_payload
    assert cli_payload["status"] in ("no_go", "limited")
    if cli_payload["status"] == "no_go":
        assert all(not gate["passed"] for gate in cli_payload["gates"])
    else:
        assert cli_payload["gates"][0]["passed"] is True
        assert cli_payload["gates"][1]["passed"] is True
        assert cli_payload["gates"][2]["passed"] is False
        assert cli_payload["gates"][3]["passed"] is False
    assert {source["status"] for source in cli_payload["sources"]} == {
        "available",
        "conditional",
        "unavailable",
    }
    dispositions = {source["source"]: source["status"] for source in cli_payload["sources"]}
    assert dispositions["ncaa_bbStats (MIT)"] == "available"
    assert dispositions["SABR Lahman 2025"] == "conditional"
    assert dispositions["MLB Pipeline"] == "unavailable"
