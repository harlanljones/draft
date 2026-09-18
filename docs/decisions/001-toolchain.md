# D-001: Phase-1 Toolchain

Status: accepted for the synthetic vertical slice on 2026-09-17.

- Python 3.12 with a `src` package layout.
- Pydantic contracts, NumPy deterministic ridge regression, FastAPI, and Uvicorn.
- Ruff, mypy, and pytest are pinned development gates; Make targets fall back to syntax/unit checks only to keep source inspection possible before setup.
- The published package interface is `draft-model`; direct module execution remains supported.

This decision does not approve empirical sources or settle empirical outcome semantics.
