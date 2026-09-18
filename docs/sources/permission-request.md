# Empirical Data Permission Request

Use one completed copy per source. This is a negotiation checklist, not legal language. Do not send
it until the project owner approves the recipient and requested scope.

## Request Header

- Source/operator:
- Contact and authority to grant rights:
- Requested datasets and years:
- Requested delivery mechanism:
- Pilot size and deadline:
- Project contact:

## Purpose

We are building a public, reproducible research system that evaluates amateur baseball projections.
The repository publishes code, manifests, methodology, aggregate diagnostics, and, only when
authorized, identified player predictions. We will not redistribute raw records unless separately
permitted. We need a written agreement because technical access or consumer terms are insufficient.

## Requested Files

- One small redacted sample and complete data dictionary before a full delivery.
- Cohort, roster, game, player-game, event, measurement, and correction tables that exist for the
  requested years.
- Stable source IDs and documented crosswalks for players, organizations, teams, games, and events.
- Original observation/event time, first availability time, correction time, revision number,
  source system, collection method, and file checksum.
- A year/team/role/field coverage and missingness matrix, including known outages and exclusions.
- Definitions for signed status, roles, innings/outs, pitches/strikes, devices, and derived fields.

## Requested Rights

Please state explicitly whether the project may:

- receive data through a publisher delivery or named API under documented rate limits;
- retain encrypted working copies, backups, and immutable reproducibility snapshots;
- share access with named collaborators and reproducibility reviewers;
- normalize, link, quality-check, and use the records for statistical and ML training;
- retain trained parameters and reproducibility evidence after contract termination;
- publish code, schemas, source manifests, checksums, non-reconstructable features, model parameters,
  identified predictions, uncertainty intervals, rankings, aggregate metrics, and limited examples;
- redistribute normalized or raw rows, if any subset is permitted;
- cite the source and use its name solely for factual attribution.

Please identify upstream licensors or fields that you cannot sublicense. Those fields can be excluded.

## Governance

- Required security, access, retention, deletion, incident, correction, and takedown procedures:
- Required attribution and license notices:
- Privacy, consent, minors, biometric, video, medical, academic, NIL, or publicity restrictions:
- Publication review scope and response time:
- Revocation and post-termination reproducibility terms:
- Pilot and full-delivery pricing, including extraction and collaborator fees:

## Acceptance Evidence

The project enables an adapter only after receiving a signed or otherwise authoritative grant,
sample validation, dictionary, checksums, timestamp evidence, measured coverage, and confirmation
that public derived outputs are permitted. Silence, a trial token, credentials, an invoice, or file
delivery without use rights leaves the source disabled.

## Source-Specific Addenda

### MLB/MLBAM Cohort

Request every 2015-2023 Rule 4 selection, passed/forfeited picks where represented, unsigned players,
and re-drafted players. Ask for pick announcement time, round and overall pick, team, school/class,
role at selection, DOB provenance, MLBAM/BIS IDs, signed-status semantics, signing date, licensable
bonus/slot fields, corrections, and universe completeness. Exclude mutable current-player fields.

### 6-4-3 Charts and SIS Predictors

Request college roster, schedule, box-score, player-game and play-by-play coverage first. Inventory
summer, pitch, batted-ball, fielding, baserunning, and device fields separately. Require each provider
to identify exact start years, historical `available_at` semantics, missing teams/games, and fields
controlled by schools, leagues, TrackMan, Synergy, D1Baseball, or other parties.

### Institutions and Leagues

Request one existing native CSV, JSON, XML, or database export for one season before expanding.
Identify the actual system of record and vendor. Exclude protected academic, medical, eligibility,
contact, and financial fields. A public-records production still requires downstream rights review.
