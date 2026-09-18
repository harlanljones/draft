# Lahman MLB Debut Outcomes

W-022 implements the constrained D-002 outcome proposal without enabling empirical mode. It accepts
only files declared by two validated local source packages: a lawful cohort and a pinned Lahman
release. No real data is bundled.

```bash
draft-model derive-lahman-debut-outcomes \
  --cohort-manifest data/empirical/cohort/manifest.json \
  --cohort-file cohort.csv \
  --lahman-manifest data/empirical/lahman/manifest.json \
  --people-file People.csv \
  --outcome-through-year 2025 \
  --horizon 2 \
  --output data/empirical/derived/mlb-debut-labels.json
```

The cohort file requires `player_id`, `draft_year`, and `lahman_player_id`. `People.csv` requires
Lahman's `playerID` and `debut`. The default target asks whether a player debuted by the end of two
complete post-draft seasons. It is not WAR, minor-league value, signing success, or affiliated-ball
participation.

## Resolution States

- `resolved_debut`: a validated Lahman identity debuted by the fixed deadline.
- `resolved_no_debut`: a validated Lahman identity did not debut by the fixed deadline.
- `unresolved_identity`: the cohort lacks a Lahman ID or the ID is absent from the pinned release.
- `censored`: the pinned outcome release does not cover the full horizon.

Unresolved players are never converted to non-debuts. Immature cohorts are censored even when a
positive debut is already visible, preserving a uniform confirmatory horizon. A debut before the
recorded draft year is treated as an identity/data error.

Package validation establishes rights metadata and file integrity only. Before these labels can be
used, the global readiness gate still requires a lawful cohort, measured identity accuracy, cohort
coverage, domain approval of the two-season target, and release-license review.
