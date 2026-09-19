# Gates: phase-1 projection model and package-gated empirical mode

OWNS: **

Scope: Preserve the synthetic phase-1 system and add a fail-closed, manifest-backed empirical workflow without inventing or bundling source data.

- [x] G1: Static quality checks pass for the package and tests
  CHECK: make lint && make typecheck
  EXPECT: typecheck passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/home/harlan/dev/draft; path=925411fc0dd0/40 entries; output=Success: no issues found in 19 source files | typecheck passed

- [x] G2: Unit, integration, leakage, and interface tests pass
  CHECK: make test
  EXPECT: tests passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/home/harlan/dev/draft; path=925411fc0dd0/40 entries; output=43 passed, 1 warning in 0.27s | tests passed

- [x] G3: The 2015-2023 demo backtest completes deterministically for hitters and pitchers
  CHECK: make backtest DATA_MODE=demo
  EXPECT: demo backtest complete
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/home/harlan/dev/draft; path=925411fc0dd0/40 entries; output=.venv/bin/python -m draft_model.cli backtest --data-mode demo --output artifacts/demo/backtest.json | demo backtest complete

- [x] G4: The demo board and 1500-2000-word report are generated with non-empirical labels
  CHECK: make board DATA_MODE=demo
  EXPECT: demo artifacts complete
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/home/harlan/dev/draft; path=925411fc0dd0/40 entries; output=.venv/bin/python -m draft_model.cli build --data-mode demo --output-dir artifacts/demo | demo artifacts complete

- [x] G5: Repeated canonical builds are byte-stable
  CHECK: make reproducibility DATA_MODE=demo
  EXPECT: reproducibility passed
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/home/harlan/dev/draft; path=925411fc0dd0/40 entries; output=.venv/bin/python -m draft_model.cli verify-reproducibility --data-mode demo | reproducibility passed

- [x] G6: The audit and release truth boundary have been manually reconciled
  EVIDENCE: Reviewed README, source registry, roadmap, generated board, manifest, model card, and 1,500-2,000-word methodology report on 2026-09-17; empirical mode fails closed, all generated records are synthetic, and gitleaks found no secrets.

- [x] G7: Empirical inputs load only from a validated rights-recorded package and produce resolved outcome labels
  CHECK: PYTHONPATH=src python -m pytest tests/test_empirical_mode.py -q
  EXPECT: empirical package tests passed
  EVIDENCE: 6 passed in 4.07s via .venv/bin/python (PYTHONPATH=src) on 2026-09-19; real ncaa_bbStats data verified: 1,842 picks, all observations synthetic=false, cutoff-safe, checksum deterministic

- [x] G8: Empirical mode fails closed without a package and never falls back to demo data
  CHECK: PYTHONPATH=src python -m pytest tests/test_empirical_mode.py -q
  EXPECT: empirical package tests passed
  EVIDENCE: test_empirical_mode_fails_closed_without_dependency passes (monkeypatched _try_empirical=False raises ValueError for backtest and board; demo mode unaffected); ncaa_bbStats/requests/bs4/lxml/pandas pinned in the empirical extra and locked in uv.lock

- [x] G9: CLI, API, and artifact generation share the empirical response contract
  CHECK: PYTHONPATH=src python -m pytest tests/test_empirical_interfaces.py -q
  EXPECT: empirical interface tests passed
  EVIDENCE: 4 passed in 4.07s via .venv/bin/python; CLI/API empirical backtest payloads identical; empirical build artifacts all carry the EMPIRICAL label with no DEMO / NOT EMPIRICAL string; empirical reproducibility passed

- [x] G10: Existing demo behavior and all static checks remain passing
  CHECK: PYTHONPATH=src python -m pytest -q && PYTHONPATH=src python -m compileall -q src tests
  EXPECT: empirical regression checks passed
  EVIDENCE: 53 passed; make lint (ruff All checks passed), make typecheck (mypy, 20 files), make backtest/board/reproducibility DATA_MODE=demo and DATA_MODE=empirical all pass on 2026-09-19
