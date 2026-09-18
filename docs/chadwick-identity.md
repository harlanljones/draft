# Chadwick Identity Resolution

W-023 implements the fail-closed D-004 identity policy over separately validated local cohort and
Chadwick Register packages. No Register data is bundled.

```bash
draft-model resolve-chadwick-identities \
  --cohort-manifest data/empirical/cohort/manifest.json \
  --cohort-file cohort.csv \
  --register-manifest data/empirical/chadwick/manifest.json \
  --register-file register.csv \
  --output data/empirical/derived/identity-matches.json
```

The cohort requires canonical `player_id`, first and last name, full birth date, and nullable MLBAM,
Baseball-Reference, and FanGraphs IDs. The Register input is allowlisted to full Chadwick UUID,
those external IDs, name, and birth components. Professional activity ranges, debut/final dates,
and the mere presence of downstream fields never become model features.

## Precedence

1. Unique exact external-ID matches are accepted.
2. Multiple UUIDs implied by supplied IDs produce `conflict`.
3. Without an exact match, normalized full name plus complete birth date may match only one UUID.
4. Ambiguous name/DOB candidates produce `conflict`.
5. Name-only, partial-DOB, missing, or absent matches remain `unresolved`.

Every result records the pinned Register package ID, candidate UUIDs, method, and evidence counts.
The full UUID is used; short Chadwick keys are not accepted. Duplicate or malformed UUID rows fail
the run rather than relying on file order.

This adapter does not establish match quality. Before empirical labels are accepted, an independent
stratified sample must measure precision, unresolved rate, conflicts, duplicate-person rate, and
drift across pinned Register versions. Thresholds must be fixed before the final join.
