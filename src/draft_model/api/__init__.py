from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query

from draft_model import __version__
from draft_model.contracts import DEMO_LABEL, BacktestResult, BoardResponse, ReadinessResponse
from draft_model.service import backtest as run_backtest
from draft_model.service import board as build_board
from draft_model.service import readiness as get_readiness

app = FastAPI(title="DRAFT — Decision Regression for Amateur Future Talent", version=__version__)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "label": DEMO_LABEL, "version": __version__}


@app.get("/v1/board", response_model=BoardResponse)
def board(data_mode: str = Query(default="demo"), draft_year: int = Query(default=2026)) -> BoardResponse:
    try:
        return build_board(data_mode, draft_year)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/backtest", response_model=BacktestResult)
def backtest(data_mode: str = Query(default="demo")) -> BacktestResult:
    try:
        return run_backtest(data_mode)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/v1/readiness", response_model=ReadinessResponse)
def readiness() -> ReadinessResponse:
    return get_readiness()
