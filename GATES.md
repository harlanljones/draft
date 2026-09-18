# Gates: phase-1 projection model

OWNS: **

Scope: Deliver and verify the complete synthetic-data phase-1 projection system without empirical claims.

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
