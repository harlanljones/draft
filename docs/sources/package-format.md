# Local Source Package Format

`draft-model validate-source-package MANIFEST` validates a locally supplied empirical package before
an adapter can inspect its rows. Raw or licensed files belong under ignored local paths such as
`data/empirical/`; never commit them.

Validation proves only that:

- the manifest is schema-valid and explicitly empirical;
- retention, model training, derived publication, and public prediction rights are affirmatively
  recorded with a reviewer and agreement reference;
- every declared file is a regular, non-symlinked file beneath the package directory;
- byte sizes and SHA-256 checksums match;
- availability evidence, license, attribution, source, and retrieval dates are present.

It does not approve source authority, legal interpretation, identity matching, cohort coverage,
outcomes, feature semantics, or empirical execution. The `/v1/readiness` gates remain separate.

## Example Shape

```json
{
  "schema_version": "1.0",
  "package_id": "provider-2026-01",
  "source": "Provider name",
  "data_mode": "empirical",
  "retrieved_at": "2026-09-17",
  "source_available_at": "2026-05-31",
  "availability_evidence": "Reference to authoritative publication evidence",
  "license_name": "Executed data-use agreement",
  "license_url": "internal-reference://agreement-id",
  "attribution": "Required attribution text",
  "rights": {
    "agreement_reference": "non-secret-record-id",
    "reviewed_by": "reviewer name or role",
    "reviewed_at": "2026-09-17",
    "allows_retention": true,
    "allows_model_training": true,
    "allows_derived_publication": true,
    "allows_public_predictions": true,
    "allows_raw_redistribution": false
  },
  "files": [
    {
      "path": "players.csv",
      "sha256": "0000000000000000000000000000000000000000000000000000000000000000",
      "bytes": 12345,
      "media_type": "text/csv"
    }
  ]
}
```

The all-zero checksum is illustrative and will fail unless it matches the actual file. Generate and
record checksums through the controlled acquisition process; do not hand-edit them to satisfy the
validator.
