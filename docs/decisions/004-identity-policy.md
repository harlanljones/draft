# D-004: Empirical Identity Policy

Status: accepted as a fail-closed design; thresholds await a lawful pilot inventory.

Use an immutable project player ID and preserve every source-native ID. Chadwick's full UUID at a
pinned commit may assist linkage but is not ground truth. Store the commit, match method, evidence,
score and margin, reviewer, review date, and supersession history.

Matching order is trusted exact source IDs, licensed crosswalks, normalized identity plus full birth
date and school/team/year evidence, then conservative candidate scoring and manual review. Name-only
matches never auto-resolve. Ambiguous, many-to-one, conflicting, and unmatched records are
quarantined; unmatched never means non-debut.

Retrospective Chadwick linkage may be disclosed and used for outcomes, but professional activity,
MLB debut/final-game fields, and the presence of professional IDs cannot enter pre-draft features.
Before labels are accepted, a stratified independently adjudicated sample must measure precision,
unresolved rate, conflicts, duplicates, and identity drift. Numeric thresholds are set from that
inventory before the final join, not invented in advance.
