# Empirical Source Registry

Status as of 2026-09-17. This engineering inventory is not legal advice. `Available` means an
affirmative public license appears to support the narrow stated use subject to its conditions;
it does not mean counsel has approved it. Free access, robots rules, an export button, or an
archive capture never upgrades a source.

Full evidence and primary-source citations are in
[`reports/Baseball source feasibility.md`](../../reports/Baseball%20source%20feasibility.md) and
[`reports/Open amateur baseball data.md`](../../reports/Open%20amateur%20baseball%20data.md).

| Source | Status | Permitted project role | Blocking evidence |
|---|---|---|---|
| NCAA.com / stats.ncaa.org | Unavailable without written permission | None | Terms reserve statistics and restrict repurposing, duplication, exploitation, and derivative use; no immutable pre-draft export verified. |
| School athletics pages | Unresolved per school and operator | None by default | Rights, archives, identifiers, and serving operators vary. Sample SIDEARM, PrestoSports, and StatBroadcast terms do not grant this workflow; StatBroadcast expressly restricts automated/ML use. |
| Cape Cod Baseball League | Unavailable without written permission | None | Terms prohibit automated scripts and do not grant retention, modeling, or redistribution; dated 2015-2023 exports were not verified. |
| Northwoods League / Pointstreak | Unavailable without written permission | None | Northwoods restricts mining, extraction, and publication; operator rights and complete dated coverage remain unresolved. |
| Perfect Game | Unavailable without separate agreement | None | Terms restrict non-interface access, reproduction, distribution, and derivative works; mutable profiles can contain post-cutoff information. |
| Baseball-Reference | Unavailable without written permission | None | Sports Reference terms expressly restrict predictive ML and bulk reuse; nominal draft-preview pages contain later outcomes and are not frozen snapshots. |
| SABR Lahman 2025 | Available conditionally under CC BY-SA 3.0 | Pinned MLB debut and counting-outcome pilot only | Does not provide WAR, complete minor-league records, signing data, or a draft cohort. Attribution, ShareAlike treatment, checksum, and coverage validation are required. |
| FanGraphs THE BOARD | Conditional on permission and publisher-supplied dated files | Disabled benchmark only | Public terms do not grant the required corpus/reuse. Product launched in 2018 and older tabs can be retroactive; current historical rows are not point-in-time evidence. |
| MLB Pipeline | Unavailable under public terms; conditional after permission | Disabled benchmark only | MLB terms restrict automation and reuse. Dated list articles exist, but complete immutable payloads and publication rights are unverified. |
| Chadwick Register | Available conditionally under ODC-By 1.0 | Pinned, validated identity aid only | Not a draft cohort or ground truth. Full UUID, commit, attribution, match evidence, and measured precision/recall are required; outcome-revealing fields cannot become features. |
| Retrosheet | Available with required attribution | Optional MLB outcome validation | Its affirmative use notice supports this narrow role, but its scope is MLB events and rosters rather than amateur cohorts, minor leagues, or predictors. |
| MLB/MLBAM publisher-supplied draft file | Conditional on negotiated delivery and rights | Preferred complete selected-player cohort | The undocumented endpoint demonstrates deep 2015-2023 pick payloads, including non-MLB players, but current terms do not authorize bulk/model use. Current person fields can leak later outcomes. |
| 6-4-3 Charts | Conditional on research license | Preferred college predictor panel for documented 2017+ coverage | Private APIs and trial access are documented, but price, complete coverage, historical first-availability timestamps, sublicensing authority, and public prediction rights require a contract. |
| Sports Info Solutions | Conditional on custom license | Candidate 2015-2023 predictor and identity feed | College/historical feeds and universal IDs are advertised, but exact years, completeness, timestamps, price, retention, and public-output rights are not public. |
| Conference or university native exports | Unresolved per institution and vendor | Fragmented cohort/predictor pilot | Export workflows exist, but custody, vendor rights, historical coverage, identifiers, corrections, and downstream publication rights vary. Records disclosure does not settle reuse rights. |
| TrackMan College Data Sharing Network | Conditional research partnership | Supplemental 2021-2023 pitch/batted-ball evidence | Prior academic delivery proves access can be negotiated but also withheld supporting rows. Selection, privacy, device, linkage, retention, and identified prediction rights require review. |
| Prep Baseball | Conditional on bespoke agreement | Supplemental 2020+ showcase measurements | Consumer access does not grant data rights. Historical completeness, consent/publicity authority, immutable timestamps, device protocols, and public prediction rights require a separate license. |
| Public anonymized TrackMan scrimmage fixture | Available only under its repository terms | Development and schema fixture | Useful for measurement-contract testing, but anonymization, 21 scrimmages, and absent cohort identities make it unusable for model training or backtesting. |

## Required Rights Record

Every future source request and approval must record:

- operator and party authorized to grant rights;
- terms URL/version, review date, reviewer, and correspondence reference;
- approved acquisition mechanism, years/files, rate limits, and retention;
- permission for transformation, ML training, trained artifacts, normalized features, predictions,
  aggregate metrics, quotations, raw redistribution, and derived redistribution;
- upstream licensors, attribution, ShareAlike or database-license obligations, revocation, and deletion;
- original publication time, retrieval time, checksum, correction history, stable IDs, fields, and
  measured year/role coverage.

Silence, credentials, membership, or technical access leaves the source disabled.

## Empirical Readiness Rule

An empirical run requires all four independent prerequisites:

1. A lawful left-hand cohort that retains players who did not reach MLB.
2. Lawful amateur predictors with verified `available_at <= as_of` evidence.
3. Validated outcome and identity joins with unresolved records quarantined.
4. A mature, preregistered outcome horizon.

Benchmark permission is optional for model fitting but mandatory for publisher comparisons. No
proposed source combination currently satisfies the first two prerequisites.

## Acquisition Priority

1. Request a frozen 2015-2023 Rule 4 selection delivery and explicit ML/public-output rights from
   MLB/MLBAM. This is the best identified route to a cohort retaining unsigned and never-MLB players.
2. Request a sample, dictionary, coverage matrix, timestamp semantics, and research license from
   6-4-3 Charts for 2017-2023 college and available summer-league predictors.
3. Ask Sports Info Solutions to document whether it can fill 2015-2016 and broader competition gaps.
4. Pilot one conference or public-university native export to measure fragmentation and rights.
5. Pursue TrackMan, Prep Baseball, and a summer league only as supplemental sources after the cohort
   and core statistics gates pass.

Use [`permission-request.md`](permission-request.md) for every approach. No endpoint, trial, consumer
subscription, repository mirror, or delivered sample enters empirical mode before its rights record
passes all required fields.
