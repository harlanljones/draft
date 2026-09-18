# Prospective 2026-Forward Dataset

This is the fallback when lawful point-in-time historical inputs cannot be acquired. It creates new
evidence prospectively; it does not repair or substitute for the 2015-2023 empirical backtest.

Run:

```bash
draft-model export-prospective-schemas --output-dir schemas/prospective
```

The deterministic JSON Schemas cover provenance, players, rosters, games, batting lines, pitching
lines, measurements, and release manifests. Generated schemas may be shared with prospective data
partners. Actual records remain in validated, ignored local source packages until release rights,
consent, privacy, and readiness gates pass.

## Evidence Flow

Every event or measurement records timezone-aware `observed_at`, `available_at`, and `received_at`.
The contract requires that order and retains source package, source record, collector, method, and
supersession evidence. `available_at` means when the predictor could actually have been used, not
merely when a game occurred. Corrections create superseding records; releases are append-only.

## Statistical Records

Batting stores raw counting components rather than rates and rejects hit totals above at-bats or
at-bats above plate appearances. Pitching stores integer outs rather than ambiguous decimal innings,
retains batters faced, and validates earned-run and pitch/strike relationships. Derived rates belong
in cutoff-aware feature code, not source tables.

Measurements retain value, unit, device make/model, hardware/software versions, calibration,
protocol, attempt, operator, environment, and provenance. A maximum velocity without those fields is
not interchangeable with a tracked distribution.

## Consent and Privacy

The player contract records consent version and whether identified public release is allowed. That
flag alone is not publication approval. Institutional agreements must separately cover source
authority, minors, privacy, publicity/NIL, cross-source linkage, measurements, video, withdrawal,
corrections, commercial reuse, and public player-level predictions. Medical, academic, contact,
eligibility, and financial data are outside the public schema.

Recruitment and coverage reports must distinguish eligible, approached, consented, declined,
withdrawn, linked, and released populations. The first season validates collection, timestamps,
identity, missingness, and measurement reliability; it is not model-quality evidence. Expansion
requires multiple materially different competition contexts and temporal holdouts by school, league,
or season rather than random player rows.

## Release Gate

A release manifest is explicitly empirical, timezone-cutoff, append-only, linked to validated source
packages, protocol registration, consent version, correction log, and limitations. Passing schema
validation does not pass the global empirical readiness decision. `draft-model readiness` remains the
authoritative stop/go response.
