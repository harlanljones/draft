# DRAFT — Decision Regression for Amateur Future Talent Roadmap

## Executive Assessment

The product goal is valuable and technically plausible, but an empirical public model is not currently evidence-ready. The repository began empty, and no source datasets, usage rights, archived pre-draft benchmark boards, identity map, empirical outcome definition, or quality baselines exist. Licensing/terms of service and historical pre-draft availability are unresolved. Lahman can contribute selected MLB outcomes only after validation; it is not complete minor-league history or a canonical WAR dataset. A current-date THE BOARD or MLB Pipeline ranking cannot be asserted or used as a historical benchmark without live, archived evidence.

Phase 1 therefore delivers a complete, reproducible vertical slice using bundled, conspicuously labeled synthetic/demo fixtures. It proves schemas, temporal controls, modeling, uncertainty, interfaces, artifacts, and tests without claiming baseball validity. Empirical ingestion and benchmark comparison remain gated on provenance, rights, timestamp, coverage, and target decisions.

## Current State

- Phase 1 is implemented as a Python 3.12 package with contracts, demo generators, normalization, features, models, backtests, artifacts, CLI, API, and tests.
- `make lint`, `make typecheck`, `make test`, `make backtest DATA_MODE=demo`, `make board DATA_MODE=demo`, and reproducibility verification pass locally on 2026-09-17.
- No real data, source agreements, verified publisher snapshots, or empirical results exist. Empirical mode fails closed.
- D-001 and the phase-1 portion of D-005 are recorded under `docs/decisions/`; empirical uncertainty semantics remain open.

## Objective

Deliver a public, deterministic reference system that can normalize amateur observations, construct cutoff-safe hitter and pitcher features, train and evaluate uncertainty-aware projections across temporal draft cohorts, compare compatible archived rankings, publish a board and a 1,500-2,000-word writeup, and serve the same results through an API and CLI. Phase 1 must run end to end on demo fixtures and make it impossible to confuse demo outputs with empirical evidence.

## Scope

- Versioned canonical contracts for player identity, observations, scouting grades, source provenance, availability time, outcomes, predictions, uncertainty, boards, and run manifests.
- Adapter boundary for college, summer, and showcase data, with demo adapters exercising each source class.
- Separate hitter and pitcher feature/model paths with shared temporal and provenance controls.
- Age, competition/context, performance, and scouting features represented in demo form.
- Deterministic 2015-2023 temporal cohort runner, fold-local preprocessing, uncertainty/calibration outputs, and leakage tests.
- Optional benchmark contract and demo benchmark fixtures shaped like archived THE BOARD and MLB Pipeline snapshots, never represented as those publishers' real data.
- Shared services exposed by a CLI and read-only API.
- Reproducible `make backtest` and `make board` workflows, generated machine-readable artifacts, board, model card, and 1,500-2,000-word report.

## Non-Goals

- Claiming predictive accuracy, player evaluation quality, causal effects, production readiness, or current prospect rankings from demo data.
- Scraping, redistributing, or publishing third-party data before rights and ToS review.
- Inferring historical availability from current pages or undated records.
- Treating Lahman as complete minor-league coverage or an authoritative WAR source.
- Live draft-room updates, fantasy advice, betting use, private scouting workflows, or production authentication in phase 1.
- Optimizing model complexity before trustworthy empirical baselines exist.

## Assumptions

- Demo fixtures may be bundled if invented, non-identifying, small, and prominently labeled.
- Draft year is the evaluation cohort; each prediction has an explicit pre-draft `as_of` timestamp and a fixed outcome horizon.
- One simple deterministic tabular baseline per role is sufficient to prove the architecture; model choice is not evidence of optimality.
- The API is read-only and local/development grade in phase 1.
- Empirical adapters can be added without changing canonical contracts once source rights and field availability are established.

## Decision Status

| ID | Decision | Required evidence | Gate/owner |
|---|---|---|---|
| D-001 | Accepted for phase 1: Python 3.12, Pydantic, NumPy, FastAPI, pytest, Ruff, and mypy | `docs/decisions/001-toolchain.md`; passing local gates | Complete for M0 |
| D-002 | Constrained proposal: MLB debut within two complete post-draft seasons for an all-2015-2023 Lahman pilot; longer horizons use narrower mature cohorts | `docs/decisions/002-empirical-outcome.md`; domain utility review still required | Proposed; empirical run blocked |
| D-003 | Source dispositions recorded; only Lahman outcomes and Chadwick identity aid are conditionally available in narrow licensed roles | `docs/sources/registry.md`, `docs/decisions/003-source-disposition.md`, research report | Complete as no-go inventory; counsel/permissions remain external gates |
| D-004 | Fail-closed identity policy selected; numeric thresholds await lawful cohort inventory and adjudicated sample | `docs/decisions/004-identity-policy.md` | Design complete; joins blocked |
| D-005 | Demo semantics accepted; empirical semantics remain open | `docs/decisions/005-demo-uncertainty.md`; empirical target decision | Complete for M2 / open for M5 |
| D-006 | No-go for the proposed full empirical 2015-2023 backtest; limited pilot conditional on four readiness prerequisites | `docs/decisions/006-empirical-readiness.md` | Complete as no-go decision |
| D-007 | Separate code, source, derived database, labels, models, and artifact licensing | `docs/decisions/007-public-licensing.md`; code license and counsel review remain open | Policy complete; publication blocked |

## Success Metrics

Targets below are phase-1 engineering gates unless marked empirical. No model-quality baseline is available.

| Metric | Baseline | Target/threshold | Measurement | Owner | Cadence |
|---|---|---|---|---|---|
| Demo vertical-slice completion | 0; repository empty | Hitter and pitcher demo workflows both pass from ingest through board/API/CLI | CI command smoke tests and artifact assertions | Integration owner | Every integration checkpoint |
| Reproducibility | TBD until first implementation | Two clean runs with identical seed/input yield identical canonical artifacts | Checksum comparison excluding isolated runtime metadata | Reproducibility owner | Every release candidate |
| Temporal leakage violations | No detector exists | 0 accepted post-cutoff records; injected violations fail tests | Adversarial fixture and fold audit | Backtest owner | Every backtest change |
| Provenance completeness | 0 manifests | 100% of input rows resolve to source, retrieval/availability metadata, rights status, and checksum; demo rows identify synthetic origin | Schema validation and manifest audit | Data-contract owner | Every ingest run |
| Schema/API/CLI parity | No interfaces exist | 100% contract tests pass for shared output schema | Golden contract tests | Interface owners | Every interface change |
| Demo-label integrity | No artifacts exist | 100% demo artifacts and responses contain an unambiguous non-empirical label | Snapshot/schema tests | Artifact owner | Every artifact build |
| Test/lint/type quality | No toolchain exists | All adopted gates pass; coverage threshold TBD after M0 instrumentation | CI reports | Technical lead | Every change |
| Backtest cohort coverage | No data | Demo: all 2015-2023 cohorts execute for both roles; empirical: TBD after source audit | Fold manifest | Backtest owner | Every backtest run |
| Predictive discrimination/error | TBD; no real data | Demo: execution only, no quality target; empirical target TBD after naive baseline | Fold metrics with sample sizes and intervals | Modeling owner | Each model version |
| Calibration | TBD; target semantics unresolved | Demo: metric emitted/tested; empirical threshold TBD after D-002/D-005 | Reliability curves and proper scoring metric | Modeling owner | Each model version |
| Benchmark comparison coverage | 0 verified snapshots | Demo contract passes; empirical cohort/player overlap target TBD after archive audit | Dated snapshot inventory and match report | Benchmark owner | Each benchmark refresh |
| Public report length and truthfulness | No report | 1,500-2,000 words; limitations and data mode present; no demo-as-empirical claims | Word-count and required-section tests plus review | Documentation owner | Every board release |
| API reliability/performance | No API | Functional/error contract passes; latency target TBD after representative payload exists | Integration test and later benchmark | API owner | Every release candidate |

## Milestones and Exit Gates

### M0: Foundation and Decisions

Exit when D-001 is recorded; package skeleton, pinned environment, CI, `Makefile`, configuration, demo-data policy, and planned command smoke tests exist; adopted lint/type/test commands pass. Establish initial test coverage and runtime baselines without inventing thresholds.

### M1: Contracts, Provenance, and Demo Corpus

Exit when canonical schemas validate all three amateur source classes, both player roles, scouting inputs, outcomes, benchmark snapshots, and run manifests; synthetic identities and values are visibly labeled; invalid timestamps/provenance fail tests; no real source content is bundled.

### M2: Leakage-Safe Modeling Core

Exit when cutoff-aware features, fold-local preprocessing, deterministic hitter/pitcher baselines, selected uncertainty semantics, and 2015-2023 demo temporal folds pass unit and adversarial leakage tests. Every prediction traces to input and model manifests.

### M3: Interfaces and Artifacts

Exit when API and CLI invoke shared services; planned `make backtest DATA_MODE=demo` and `make board DATA_MODE=demo` work from a clean setup; generated board, metrics, manifest, model card, and 1,500-2,000-word report are deterministic and marked `DEMO / NOT EMPIRICAL`.

### M4: Phase-1 Release Gate

Exit when all adopted checks pass twice from clean environments, artifact checksums match, threat/license scans find no secrets or restricted data, traceability is complete, and an independent review confirms no empirical claims. This is the phase-1 completion point.

### M5: Empirical Readiness Decision (Not Phase-1 Completion)

Decision exit reached on 2026-09-17 with a documented no-go for the full empirical backtest and a conditional limited-pilot contract. This does not authorize empirical execution. Reopening requires a lawful cohort, lawful pre-cutoff predictors, validated outcome/identity joins, mature labels, source-specific rights records, measured coverage, and approved empirical thresholds.

## Work Plan

Exclusive ownership means one writer at a time for the listed files/components. Exact filenames may be refined at M0, but IDs and boundaries remain stable.

| ID | Depends on | Suggested role | Exclusive ownership | Deliverable and measurable exit |
|---|---|---|---|---|
| W-001 | None | Technical lead | `pyproject.toml`, lockfile, `Makefile`, CI, package skeleton | D-001 recorded; clean setup plus adopted lint/type/test smoke checks pass |
| W-002 | W-001 | Data-contract engineer | `contracts/`, schema docs | Versioned contracts cover required entities; valid/invalid contract tests pass |
| W-003 | W-002 | Fixture engineer | `tests/fixtures/demo/`, demo generators | Synthetic college/summer/showcase, hitters/pitchers, 2015-2023 outcomes and mock benchmark shapes validate; every record is demo-labeled |
| W-004 | W-002, W-003 | Ingest engineer | `ingest/`, ingest tests | Three demo adapters normalize without loss of raw provenance; manifests/checksums pass |
| W-005 | W-002, W-003 | Feature engineer | `features/`, feature tests | Role-specific age/competition/performance/scouting features honor `as_of`; future-row injection fails |
| W-006 | W-002, W-003 | Outcome engineer | `outcomes/`, outcome tests | Demo targets/horizons/censoring contract implemented; Lahman limitations documented in source registry |
| W-007 | W-004, W-005, W-006 | Modeling engineer | `modeling/`, model tests | Deterministic role baselines and D-005 uncertainty output train/predict with fold-local transforms |
| W-008 | W-007 | Backtest engineer | `backtest/`, backtest tests | All demo 2015-2023 cohorts run; leakage assertions, sample sizes, intervals/calibration, and naive comparison emit |
| W-009 | W-002, W-003 | Benchmark engineer | `benchmarks/`, benchmark tests | Dated benchmark contract, demo comparison, unmatched-player accounting; no publisher data or current-board claim |
| W-010 | W-008, W-009 | Application-service engineer | shared orchestration/services, response schemas | One service produces board/backtest responses for both interfaces with stable schema |
| W-011 | W-010 | CLI engineer | `cli.py`, CLI tests, CLI command wiring | CLI help, validation, backtest, and board smoke tests pass in demo mode |
| W-012 | W-010 | API engineer | `api/`, API tests, API command wiring | Read-only health/metadata/board/backtest endpoints pass success and error contract tests |
| W-013 | W-010 | Artifact/documentation engineer | `artifacts/`, templates, generated-output tests | Deterministic board, metrics, manifest, model card, and 1,500-2,000-word report generated with mandatory demo disclaimer |
| W-014 | W-011, W-012, W-013 | Integration/release engineer | integration tests, root docs, CI release workflow | M4 gates pass twice cleanly; checksums agree; no empirical claims/restricted data detected |
| W-015 | W-002 | Data steward/researcher | source registry and decision records only; no raw data | Complete 2026-09-17: each proposed source is evidenced and classified; no restricted data collected |
| W-016 | W-015 | Domain + modeling reviewers | target/identity/benchmark decision records | Complete as no-go 2026-09-17: constrained outcome, identity, licensing, benchmark, and four-part readiness policies recorded; empirical execution remains blocked |
| W-017 | W-016 | Application-service engineer | readiness contracts, service, CLI/API endpoints, tests | Machine-readable no-go status exposes every empirical prerequisite and source disposition identically through CLI and API |
| W-018 | W-016 | Data acquisition lead | expanded source registry, acquisition report, permission-request package | Complete 2026-09-17: ranked MLB/MLBAM, 6-4-3, SIS, institutional, TrackMan, and Prep paths with exact rights and file requirements; no data collected |
| W-019 | W-018 | Project owner + data acquisition lead | permission correspondence and non-secret rights records | Skipped by project owner on 2026-09-17; no outreach sent and empirical source gates remain failed |
| W-020 | W-018 | Data-contract engineer | source package contracts, local validator, CLI, tests, format documentation | Complete 2026-09-17: rights, availability, paths, symlinks, sizes, and checksums fail closed before adapter access; validation never implies model readiness |
| W-021 | W-020 | Data-contract engineer | prospective contracts, deterministic JSON Schemas, CLI, tests, collection guidance | Complete 2026-09-17: 2026-forward provenance, player, roster, game, batting, pitching, measurement, consent, correction, and release fields validate without weakening the empirical no-go gate |
| W-022 | W-020 | Outcome engineer | validated Lahman adapter, outcome contracts, CLI, tests, documentation | Complete 2026-09-17: fixed-horizon MLB debut labels preserve resolved, unresolved, and censored states; immature cohorts and identity contradictions fail safely; no real data is bundled |
| W-023 | W-020 | Identity engineer | validated Chadwick matcher, identity contracts, CLI, tests, documentation | Complete 2026-09-17: exact external IDs precede full-name/DOB fallback; conflicting, ambiguous, partial, and missing identities remain quarantined with evidence; no professional activity fields enter features |
| W-024 | W-022, W-023 | Evaluation engineer | empirical label preflight contracts, CLI, tests, documentation | Complete 2026-09-17: identity and outcome universes join by canonical player ID; checksums and year-level conflict/unresolved/censoring coverage emit; complete labels never override failed predictor/readiness gates |
| W-025 | W-022, W-023, W-024 | Integration engineer | synthetic pipeline CLI, end-to-end integration test | Complete 2026-09-17: identity, outcome, and audit run in sequence from three validated packages; CLI command writes all intermediate outputs and the combined audit |

## Traceability

| Requirement or critical gap | Work IDs | Acceptance evidence |
|---|---|---|
| Normalized college/summer/showcase ingest | W-002, W-003, W-004 | Contract and adapter tests with provenance preservation |
| Age/competition/scouting features | W-005 | Cutoff-aware feature tests and documented formulas |
| Hitters and pitchers | W-003, W-005, W-006, W-007, W-008 | Both roles complete every demo fold and emit uncertainty |
| Uncertainty and calibration | W-007, W-008 | Versioned uncertainty schema, intervals/scores, calibration artifact |
| Leakage-safe 2015-2023 backtest | W-003, W-005, W-008 | Temporal fold manifests and adversarial post-cutoff failures |
| THE BOARD/MLB Pipeline benchmarks | W-009, W-015, W-016 | Demo-shaped contract first; empirical use only with dated licensed snapshots and match audit |
| API and CLI | W-010, W-011, W-012 | Shared-schema contract and smoke tests |
| `make backtest` and `make board` | W-001, W-011, W-013, W-014 | Clean-environment command tests |
| 1,500-2,000-word writeup | W-013 | Automated word count, required sections, demo disclaimer, human truth review |
| No existing real datasets or empirical baseline | W-003, W-013, W-014 | Demo watermark tests and release review |
| Licensing/ToS and historical availability unresolved | W-015, W-016 | Source decision records; empirical pipeline remains disabled until approval |
| Lahman coverage limitations | W-006, W-015, W-016 | Coverage audit and explicit non-claim in model card/report |
| No unsupported current-date board | W-009, W-013, W-014 | Snapshot-date requirement and prohibited-claim review |

## Dependencies, Critical Path, and Concurrency

Dependency graph:

```text
W-001 -> W-002 -> W-003 -> {W-004, W-005, W-006, W-009}
{W-004, W-005, W-006} -> W-007 -> W-008
{W-008, W-009} -> W-010 -> {W-011, W-012, W-013} -> W-014
W-002 -> W-015 -> W-016 -> W-018 -> {W-019 skipped, W-020 local package gate}
```

Critical path for phase 1: `W-001 -> W-002 -> W-003 -> W-005 -> W-007 -> W-008 -> W-010 -> W-013 -> W-014`. W-004 and W-006 remain mandatory gates even if they are not duration-dominant.

Concurrency waves:

| Wave | Ready work | Integration gate |
|---|---|---|
| 0 | W-001 | Toolchain and command contract pass |
| 1 | W-002 | Schema review and contract tests pass |
| 2 | W-003 and W-015 (non-overlapping fixture vs source-registry ownership) | Demo corpus validates; source audit cannot introduce data |
| 3 | W-004, W-005, W-006, W-009 | Canonical-schema compatibility suite passes |
| 4 | W-007; W-016 may proceed separately if W-015 is complete | Determinism and uncertainty contracts pass |
| 5 | W-008 | Full temporal/leakage suite passes |
| 6 | W-010 | Shared service/schema integration passes |
| 7 | W-011, W-012, W-013 | CLI/API/artifact parity and demo labels pass |
| 8 | W-014 | M4 clean-release gate passes twice |

## Integration Checks

- IC-1 after W-002/W-003: validate all demo files and deliberate invalid cases against canonical contracts.
- IC-2 after Wave 3: normalize every source class and build both role feature sets at multiple cutoffs; assert row-level provenance and no future inputs.
- IC-3 after W-008/W-009: execute all 2015-2023 demo folds, benchmark alignment, determinism checks, and injected leakage failures.
- IC-4 after Wave 7: compare CLI and API canonical JSON for the same configuration; generate board/report; assert word count, schemas, manifests, and all demo warnings.
- IC-5 at W-014: run setup, lint, typecheck, tests, backtest, board, CLI, and API smoke tests from two clean environments; compare canonical checksums and scan tracked files/artifacts for secrets, restricted data, publisher impersonation, and empirical-claim language.

## Risks, Triggers, and Mitigations

| Risk | Trigger | Mitigation/decision response |
|---|---|---|
| Source use violates license or ToS | No explicit permission, redistribution restriction, or prohibited automation | Do not ingest; retain adapter contract only; seek permission or choose a compatible source |
| Historical leakage | Missing/derived `available_at`, current page used for old cohort, fold-global fit | Quarantine record/source; require timestamp evidence; fail closed in validators and fold tests |
| Outcome invalidity or censoring | Recent cohorts lack mature horizon; source omits minors/WAR or changes definition | Narrow horizon/cohorts, model censoring, source authoritative outcomes, or issue no-go under D-002/D-006 |
| Identity collisions | Ambiguous names, school changes, draft re-entry, conflicting IDs exceed D-004 threshold | Stable source IDs, probabilistic candidates plus manual review; exclude unresolved joins and report them |
| Benchmark incomparability | Snapshot is post-draft/current, ranks cover a different population/date, low match rate | Require publication cutoff and overlap report; compare only compatible subsets; withhold headline comparison |
| Demo results mistaken for findings | Artifact lacks label or prose implies baseball performance | Schema-required `data_mode`; watermark filenames/content/responses; automated phrase checks and independent release review |
| Small or biased empirical samples | Fold/role/source sample size or missingness breaches thresholds established in W-016 | Publish stratified coverage and intervals; simplify claims/model or stop evaluation |
| Reproducibility drift | Dependency, seed, source, locale, or serialization changes checksum | Lock dependencies; canonical sorting/serialization; manifests; clean rerun gate |
| Uncertainty is misleading | Intervals/calibration do not match target semantics or are unstable by cohort | Resolve D-005; report method and sample size; prefer simple calibrated outputs; no unsupported rank certainty |
| Interface divergence | CLI and API produce different fields/results | Shared service and response contract; parity golden tests |
| Scope expansion delays vertical slice | Live ingestion, UI, or complex models requested before M4 | Hold non-goals; complete demo tracer bullet first; route additions through a decision record |

## Phase-1 Deliverable Layout (Proposed)

```text
src/draft_model/{contracts,ingest,features,outcomes,modeling,backtest,benchmarks,artifacts,api}/
src/draft_model/cli.py
tests/fixtures/demo/
tests/{unit,integration}/
artifacts/demo/              # generated, clearly labeled outputs
docs/decisions/              # toolchain, targets, uncertainty, source approvals
docs/sources/                # provenance and rights registry, never raw restricted data
Makefile
pyproject.toml
```

This layout is implemented, with generated demo artifacts ignored by Git and reproducible from the documented commands.

## Phase-1 Status (2026-09-17)

W-001 through W-014 are complete for the explicitly synthetic phase-1 scope, with local gate evidence in `GATES.md`. W-015 and W-016 are complete as an evidence-backed no-go assessment in `reports/Baseball source feasibility.md`; they do not authorize empirical execution. Lahman and Chadwick are conditionally usable only in their narrow licensed roles. Empirical execution remains blocked on a lawful cohort, authorized pre-cutoff predictors, identity validation, measured coverage, and publication review. Generated demo metrics are execution fixtures and provide no model-quality baseline.

W-017 operationalizes that decision through a versioned readiness response shared by `draft-model readiness` and `/v1/readiness`. Re-evaluating a source or gate requires updating its evidence record, decision documentation, service response, and contract tests together.

W-018 integrates the broader source search in `reports/Open amateur baseball data.md`. The preferred
path is an MLB/MLBAM cohort delivery plus 6-4-3 Charts predictors, with SIS evaluated for historical
gaps. W-019 is intentionally blocked until the project owner approves external outreach; trial tokens,
consumer subscriptions, undocumented endpoints, and repository mirrors remain ineligible inputs.
