# DRAFT — Decision Regression for Amateur Future Talent: Agent Instructions

## Mission and Truth Boundary

Build a public, reproducible amateur-to-professional baseball projection system for hitters and pitchers. The system must ingest normalized college, summer-league, and showcase observations; derive age, competition, performance, and scouting features; produce uncertainty-aware projections; run a leakage-safe 2015-2023 backtest; compare eligible outputs with THE BOARD and MLB Pipeline; and expose equivalent CLI and API workflows.

The repository currently contains planning documents only. No real source datasets, licenses, benchmark snapshots, implementation, or empirical results have been verified. Treat all bundled phase-1 records as clearly labeled synthetic/demo fixtures. Never describe demo metrics as real-world performance or empirical findings.

## Instruction Precedence

Follow, in order: explicit user instructions, the nearest scoped `AGENTS.md`, root `AGENTS.md`, then `ROADMAP.md`. Use `ROADMAP.md` for temporary sequencing and decisions; keep this file limited to durable engineering rules.

## Architecture Boundaries

Implement the planned Python system with these boundaries:

- `src/draft_model/contracts/`: canonical schemas, identifiers, enums, validation, and provenance types. Other modules depend on contracts; contracts do not depend on them.
- `src/draft_model/ingest/`: source adapters and normalization only. Preserve raw source fields and provenance; do not model here.
- `src/draft_model/features/`: cutoff-aware hitter and pitcher feature construction. Feature functions accept an explicit `as_of` date.
- `src/draft_model/outcomes/`: professional outcome labels and horizon definitions. Do not treat Lahman as complete minor-league or WAR coverage.
- `src/draft_model/modeling/`: deterministic training, prediction, calibration, and uncertainty. Consume canonical tables, not source-specific records.
- `src/draft_model/backtest/`: temporal folds, benchmark alignment, metrics, and leakage assertions.
- `src/draft_model/artifacts/`: board and report generation. Generated output must identify data mode (`demo` or `empirical`), cutoff, model version, and limitations.
- `src/draft_model/api/` and `src/draft_model/cli.py`: thin interfaces over shared application services; no duplicate business logic.
- `tests/`: mirrors module boundaries. `tests/fixtures/demo/` is the only bundled phase-1 dataset and must visibly identify itself as synthetic.

Keep raw or licensed data out of Git. Use ignored local paths and manifests containing source, retrieval time, license status, coverage, and checksum.

## Commands

The following commands were implemented and verified locally on 2026-09-17 with Python 3.12:

- `make setup`: create/install the development environment.
- `make lint`: run formatting and static lint checks.
- `make typecheck`: run static type checks.
- `make test`: run unit and integration tests.
- `make backtest DATA_MODE=demo`: run deterministic temporal evaluation on bundled demo fixtures.
- `make board DATA_MODE=demo`: generate the demo board and 1,500-2,000-word methodology/results writeup.
- `make api`: run the local API.
- `draft-model --help`: show the CLI contract.
- `draft-model readiness`: show the machine-readable empirical no-go/readiness decision.
- `draft-model validate-source-package MANIFEST`: validate rights metadata, local file boundaries,
  byte sizes, and checksums without enabling empirical mode.
- `draft-model export-prospective-schemas --output-dir DIR`: export deterministic collection schemas
  for a future consented 2026-forward dataset.
- `draft-model derive-lahman-debut-outcomes ...`: derive fixed-horizon MLB debut labels from a
  validated cohort package and pinned Lahman package without enabling empirical modeling.
- `draft-model resolve-chadwick-identities ...`: resolve conservative exact-ID or full-name/DOB
  matches from validated local cohort and Chadwick packages.
- `draft-model audit-empirical-labels ...`: join derived identity/outcome outputs by canonical player
  ID and report unresolved, conflicting, censored, and eligible label coverage without enabling modeling.

When command names change, update both this file and the command smoke tests in the same change.

## Quality Gates

Every change must satisfy all implemented relevant gates before integration:

- Formatting, lint, type checking, unit tests, integration tests, and command smoke tests pass.
- Repeated demo runs with the same seed and inputs produce byte-stable canonical outputs, except explicitly isolated runtime metadata.
- Schema and feature changes include contract tests and fixture updates.
- Every feature is computable using only records available at its fold cutoff; tests must fail on post-cutoff timestamps and future-derived fields.
- Hitter and pitcher paths each have end-to-end coverage, including uncertainty output and invalid-input behavior.
- API and CLI outputs conform to the same versioned response schema.
- Generated artifacts clearly display `DEMO / NOT EMPIRICAL` when demo fixtures are used.
- No secrets, restricted raw data, unapproved scraped content, or unverified benchmark snapshots enter Git.

Do not bypass failing checks, weaken assertions to accommodate a result, hand-edit generated metrics, or hard-code expected model quality. Fix causes and record material methodological changes.

## Reproducibility, Leakage, and Provenance

- Pin runtime and dependency versions; record random seeds, configuration, code revision when available, input checksums, and schema/model versions in every run manifest.
- Define the prediction timestamp and outcome horizon explicitly. Join observations by stable player identity and `available_at <= as_of`, not merely season.
- Fit imputers, encoders, scalers, feature selection, model parameters, and calibration inside each training fold only.
- Keep 2015-2023 draft classes as temporal evaluation cohorts; never randomly split player rows across train and test.
- Quarantine records with unknown historical availability from empirical backtests. Missing timestamps must not be inferred silently.
- Benchmark only against archived, pre-draft snapshots whose publication date, terms, and player matching are documented. A current-date board is not a historical benchmark.
- Report sample sizes, missingness, exclusions, point estimates, uncertainty intervals, and calibration. Separate demo validation from empirical evaluation in paths and labels.
- Use Lahman only for the MLB outcomes it actually supplies after coverage validation. Do not represent it as a complete minor-league dataset or authoritative WAR source.

## Evidence and Reporting

Support claims with tests, run manifests, generated tables, or cited source documentation. Label statements as verified fact, proposal, inference, or unknown. The public writeup must distinguish model methodology, demo behavior, empirical findings, and unresolved limitations; in phase 1, the empirical findings section must state that no empirical claims are available.

Progress reports must name roadmap work IDs, files changed, checks run, data mode, unresolved decisions, and any impact on reproducibility, leakage risk, model quality, reliability, security/privacy, licensing, or delivery.

## Coordination Protocol

1. Select ready work from `ROADMAP.md` by dependency order and claim one exclusive file/component ownership area.
2. Use one writer per file. Parallelize only work in the same declared concurrency wave with non-overlapping ownership.
3. Integrate contracts and fixtures before dependent ingest, features, models, or interfaces. Rebase or reread shared contracts before integration; do not silently resolve semantic conflicts.
4. At each integration checkpoint, run all available relevant gates plus the demo vertical slice. Record command status truthfully.
5. Escalate instead of guessing when licensing/ToS, historical availability, identity matching, target definitions, benchmark comparability, or data coverage changes architecture or validity.
6. Update `ROADMAP.md` when a decision is made, a gate changes, or evidence invalidates sequencing. Do not mark an item complete without its stated exit evidence.
