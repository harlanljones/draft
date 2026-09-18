# Empirical Label Preflight

W-024 joins the derived Chadwick identity and Lahman outcome outputs by canonical `player_id` and
measures whether labels are technically eligible. It does not train a model or enable empirical mode.

```bash
draft-model audit-empirical-labels \
  --identities data/empirical/derived/identity-matches.json \
  --outcomes data/empirical/derived/mlb-debut-labels.json \
  --output data/empirical/derived/label-audit.json
```

The command validates both versioned JSON arrays, records their SHA-256 checksums, rejects duplicate
IDs, and requires exactly matching player universes. It reports each draft year's:

- total players;
- resolved, conflicting, and unresolved identities;
- resolved, unresolved, and censored outcomes;
- labels eligible only where identity and outcome are both resolved.

`label_pipeline_complete` is true only when every player has an eligible label. The overall `status`
remains `no_go` even then because lawful pre-draft predictors, source coverage, preregistered identity
thresholds, target utility, and publication review are independent gates. A high eligible rate is a
coverage measurement, not evidence of model quality or legal readiness.
