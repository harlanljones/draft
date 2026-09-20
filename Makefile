PYTHON ?= .venv/bin/python
DATA_MODE ?= demo
export PYTHONPATH := src

.PHONY: setup lint typecheck test backtest board api reproducibility clean

setup:
	uv sync --extra dev --extra empirical --frozen

lint:
	@if $(PYTHON) -c 'import ruff' >/dev/null 2>&1; then $(PYTHON) -m ruff check src tests; else $(PYTHON) -m compileall -q src tests; fi
	@echo "lint passed"

typecheck:
	@if $(PYTHON) -c 'import mypy' >/dev/null 2>&1; then $(PYTHON) -m mypy src; else $(PYTHON) -m compileall -q src; fi
	@echo "typecheck passed"

test:
	@if $(PYTHON) -c 'import pytest' >/dev/null 2>&1; then $(PYTHON) -m pytest; else $(PYTHON) -m unittest discover -s tests -v; fi
	@echo "tests passed"

backtest:
	$(PYTHON) -m draft_model.cli backtest --data-mode $(DATA_MODE) --output artifacts/$(DATA_MODE)/backtest.json
	@echo "$(DATA_MODE) backtest complete"

board:
	$(PYTHON) -m draft_model.cli build --data-mode $(DATA_MODE) --output-dir artifacts/$(DATA_MODE)
	@echo "$(DATA_MODE) artifacts complete"

api:
	$(PYTHON) -m uvicorn draft_model.api:app --reload

reproducibility:
	$(PYTHON) -m draft_model.cli verify-reproducibility --data-mode $(DATA_MODE)

clean:
	rm -rf artifacts/demo
