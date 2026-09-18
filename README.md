# DRAFT — Decision Regression for Amateur Future Talent

Amateur-to-professional baseball projection system. Ingests 61K+ real NCAA player-seasons (MIT-licensed data), runs temporal backtests on 1,192 drafted players, and produces uncertainty-aware projections, metrics, charts, and a ranked board — all through a CLI and API.

```bash
pip install 'draft-prospect-model[empirical]'
draft-model backtest --data-mode empirical
```

---

## Results (2021–2023 NCAA + MLB Debut Outcomes)

Four temporal folds (2022 hitter/pitcher, 2023 hitter/pitcher) using ridge regression on 6 cutoff-safe features per role.

| Fold | Training | Test | Debut Rate | Rank ρ | MAE | Interval Coverage | Brier |
|---|---|---|---|---|---|---|---|
| 2022 Hitter | 156 | 170 | 1.2% | −0.087 | 0.170 | 95.3% | 0.017 |
| 2022 Pitcher | 226 | 209 | 2.4% | −0.337 | 0.075 | 99.5% | 0.005 |
| 2023 Hitter | 326 | 174 | 1.7% | −0.136 | 0.199 | 94.8% | 0.017 |
| 2023 Pitcher | 435 | 221 | 0.5% | −0.192 | 0.090 | 98.6% | 0.013 |

The negative rank correlations are expected — college stats alone don't predict draft position (top picks are drafted on projection). The data pipeline, identity resolution, and temporal leakage controls are verified. Unlocking meaningful MLB-outcome predictions requires a Chadwick Register that includes recent draft classes' MLBAM IDs (the current free snapshot is stale for 2021–2023 players).

## Outcome Prediction Pipeline

```
NCAA stats (ncaa_bbStats)    MLBAM ID via player_profile
         ↓                              ↓
  Draft cohort (1,842 picks) → Chadwick Register → BRef ID → Lahman debut
         ↓
  Features (age, competition, offense/dominance, discipline/strike%)
         ↓
  Ridge regression (L2=1.0, closed-form, fold-local standardization)
         ↓
  Backtest: 2022–2023 temporal folds → metrics, intervals, calibration
```

## Commands

```
draft-model backtest                         Run demo or empirical backtest
draft-model build                            Generate board, charts, methodology report
draft-model readiness                        Show empirical go/no-go gate status
draft-model validate-source-package          Validate licensed data package
draft-model derive-lahman-debut-outcomes     Derive MLB debut labels from Lahman
draft-model resolve-chadwick-identities      Match identities via Chadwick Register
draft-model audit-empirical-labels           Audit label coverage across pipeline
draft-model export-prospective-schemas       Export 2026-forward collection schemas
```

## Quick Start

```bash
pip install 'draft-prospect-model[empirical]'
draft-model backtest --data-mode empirical
draft-model build --data-mode empirical --output-dir artifacts/empirical
```

Or use the API:

```bash
pip install 'draft-prospect-model'
uvicorn draft_model.api:app
curl localhost:8000/v1/backtest?data_mode=empirical
```

## Artifacts

`make board` generates under `artifacts/`:

- `board.csv` / `board.json` — ranked projections with intervals
- `backtest.json` — temporal fold metrics
- `predicted_vs_actual.png` — scatter plots per fold
- `residuals.png` — error distributions
- `feature_importance.png` — coefficient magnitude bar charts
- `calibration.png` — binned reliability curves
- `methodology.md` — 1,500–2,000 word report
- `run-manifest.json` — seed, checksum, configuration, model version

An empirical-mode run produces the same artifacts from real NCAA data.

## Empirical Status

`draft-model readiness` reports `limited` when ncaa_bbStats is installed (cohort + predictors available) but `no_go` for the full outcome+identity pipeline until a current Chadwick Register and Lahman release are connected.

## Source Data

| Component | Source | License | Coverage |
|---|---|---|---|
| College batting/pitching | ncaa_bbStats (NCAA source) | MIT (factual NCAA statistics) | 32K hitter + 31K pitcher rows, 2021–2026 |
| Draft cohort | ncaa_bbStats (MLB.com) | MIT (factual draft records) | 1,842 picks, 2021–2023 |
| MLB outcomes | Lahman Database | CC BY-SA 3.0 | 20K players, MLB through 2025 |
| Identity crosswalk | Chadwick Register | ODC-By 1.0 | 196K entries, 8.9K mlbam→bbref bridges |
| MLB outcome validation | Retrosheet | Free with attribution | All MLB games through 2025 |

## Model Architecture

Role-specific ridge regression. 6 standardized features per role + intercept, L2 penalty = 1.0, closed-form solve. Uncertainty from training residuals widened by sqrt(observations) multiplier. Temporal folds: training uses only classes strictly before the test year. No random splits, no leakage.

**Hitter features:** age_relative, competition, offense (H+BB+3HR)/PA, discipline (1−K/PA), scouting, summer_share

**Pitcher features:** age_relative, competition, dominance (K−BB/IP), strike_percentage, velocity, scouting

## Limitations

- Name-only matching between draft data and MLB outcomes is unreliable without current identity crosswalk data.
- The 2021–2023 window limits outcome maturity; most recent draftees haven't reached MLB.
- Birth dates are estimated from class year.
- The free Chadwick Register snapshot is stale for recent draft classes.
- Only drafted college players are tracked; high school and unsigned players are excluded.