from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

from draft_model.contracts import DataMode, RunManifest
from draft_model.demo import DEMO_SEED, demo_checksum, load_demo_prospects
from draft_model.service import backtest, board


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _report() -> str:
    return """# DRAFT — Decision Regression for Amateur Future Talent

> **DEMO / NOT EMPIRICAL**

## Executive Summary

This release is a reproducible demonstration of an amateur-to-professional projection workflow, not a claim about real baseball players. Every bundled identity, observation, outcome, and benchmark-shaped score is invented. The purpose of phase 1 is to prove that the software can enforce a prediction cutoff, represent college, summer-league, and showcase evidence in one contract, train separate hitter and pitcher models, express uncertainty, execute temporal draft-year folds, and expose identical results through artifacts, a command-line interface, and an API. It intentionally does not scrape or redistribute any proposed source.

The original concept is compelling because amateur acquisition decisions must translate performance observed in radically different contexts. Age, competition, equipment, schedule length, selection into elite events, and sparse measurement all affect what a stat line means. A public implementation can make those assumptions inspectable. Yet a polished model trained on current web pages would be less credible than a small system that refuses invalid evidence. Historical availability and legal use are therefore inputs to the model, not paperwork around it.

## Prediction Contract

The demonstration predicts an invented seven-year cumulative value resembling a WAR-shaped continuous target. It is explicitly not MLB WAR. A real release must select a documented outcome provider, define hitter and pitcher treatment, establish whether minor-league value matters, account for players who have not completed the outcome horizon, and freeze that definition before fitting models. The 2015-2023 folds in this release are software fixtures. Recent real draft classes would be right-censored under a seven-year horizon and could not be compared naively with older classes.

Each prediction has an `as_of` date of May 31 in its draft year. An observation is eligible only when its `available_at` date is on or before that cutoff. The feature builder fails when handed a future observation rather than silently dropping it. This strict behavior catches orchestration errors and makes leakage visible in tests. Empirical records with unknown historical availability must be quarantined; season labels and retrieval dates cannot substitute for publication evidence.

## Canonical Inputs and Provenance

College, summer-league, and showcase records normalize into a shared observation contract while retaining their raw fields. The contract includes stable player and observation identifiers, source class and name, observation date, availability date, competition strength, role-specific statistics, and an explicit synthetic flag. Phase 1 rejects observations that pretend to be empirical because source approval has not occurred.

That refusal addresses several gaps in the proposed source list. School and league pages can change in place, provide inconsistent tables, or disappear. Free-list access does not necessarily grant automated collection or redistribution rights. Public rankings may not have complete archived pre-draft snapshots. Chadwick can support identity work but does not eliminate ambiguous names, transfers, re-entries, or two-way roles. Baseball-Reference draft pages describe selections and some transactions, while Lahman is neither complete minor-league history nor an authoritative WAR source. A future source registry must document access terms, storage, derivative publication, timestamps, coverage, checksum, and attribution before an adapter is enabled.

## Feature Construction

Age is measured at the explicit prediction cutoff and centered around twenty and a half years. A younger player facing a given level of competition receives a materially different representation from an older player with the same surface line. This implements the central baseball intuition without claiming that the demo coefficient is empirically estimated. A real system should test the age function, nonlinearities, reclassification, redshirts, and the proper comparison population.

Competition strength is a normalized input carried by each observation. Summer-league observations receive one-and-a-half times the aggregation weight because wood-bat play against selected competition is strategically important in the hypothesis. That weight is a proposal, not a learned truth. Selection into a summer league already contains scouting information and could create bias or double counting. Empirical work must estimate or tune competition translations inside training folds and compare the combined model with college-only and summer-only baselines.

Hitter performance combines hits, walks, and home runs relative to plate appearances, plus a strikeout-based discipline feature. Pitcher performance emphasizes strikeouts minus walks per inning, strike percentage, and fastball velocity. ERA is absent by design: defense, park, sequencing, scoring, and small samples can overwhelm its signal in amateur contexts. Still, saying that ERA is useless would outrun this release. Its incremental value must be measured on valid historical data rather than accepted as a slogan.

Scouting enters as a normalized tool-grade feature. High-school fixtures are showcase-shaped and sparse. A real implementation should preserve individual hit, power, run, arm, field, velocity, command, and pitch grades, their evaluator and date, and inter-rater reliability. It should compare statistics-only, scouting-only, and combined models. Any grade published after the cutoff is leakage. A benchmark ranking cannot also serve as an unnamed prior if the combined model is later advertised as beating that benchmark.

## Modeling and Uncertainty

The baseline is role-specific ridge regression. Within each temporal fold, feature means and scales are fit only on earlier draft classes. The intercept is unpenalized and feature coefficients are regularized. This simple model is transparent, deterministic, and adequate for validating architecture. It is not presented as the best baseball model. More flexible models should be considered only after trustworthy sample size, missingness, and naive baselines are known.

Prediction intervals derive from training residual scale and widen for sparse observations. High-school candidates receive a further multiplier, making the system deliberately less certain when evidence consists mainly of showcase data. The output also includes a probability that the invented target exceeds two units. These quantities demonstrate a response contract; they are not calibrated probabilities for actual players. Real interval semantics must distinguish outcome variance, parameter uncertainty, and rank uncertainty. Coverage should be assessed by draft year and subgroup, not only in aggregate.

Hard shrinkage for young, sparsely measured players is a feature rather than an embarrassment. One strong weekend is weak evidence. However, shrinkage toward a population mean can also suppress unusual players if the population is poorly chosen. Missing velocity is not random, showcase attendance is selected, and cold-weather players have fewer games. Those mechanisms should become explicit missingness and selection analyses instead of being hidden behind wider error bars.

## Temporal Evaluation

The backtest iterates over draft years 2015 through 2023 and over hitter and pitcher roles. For each fold, only prior draft classes train the model. The test class remains untouched until prediction. Reported demonstration metrics include rank correlation, mean absolute error, interval coverage, and Brier score. A scouting-shaped benchmark score is compared on the same synthetic players to exercise alignment logic.

The tiny two-player role cohorts make rank correlation especially unstable: values collapse to minus one, zero, or one. That is intentional evidence that an executable metric is not automatically an informative metric. No aggregate accuracy headline should be drawn from these files. An empirical release should publish class-level sample sizes, missingness, exclusions, bootstrap intervals, top-of-board ranking measures, calibration plots, and sensitivity to target and horizon choices.

The proposed first-round bust metric needs a preregistered definition. Draft round alone mixes acquisition cost with public consensus, and recent players have not had equal opportunity to produce value. A responsible implementation would define the eligible universe, success threshold, outcome horizon, censoring policy, and baseline decision rule before seeing model results. It should report both flagged busts and valuable players incorrectly downgraded.

## Benchmark Comparisons

THE BOARD and MLB Pipeline are useful public comparators only when an archived snapshot predates the model cutoff and both systems cover a compatible player universe. A current ranking cannot be projected backward. Publication timing, ties, unranked players, role changes, and name matching can materially change results. The phase-1 benchmark module consequently accepts a dated snapshot contract and rejects post-cutoff records; it contains no publisher data.

Where a future model disagrees with a board, the disagreement is interesting only after separating independent model information from scouting inputs shared with that board. Comparisons should include statistics-only and combined variants, matched-player coverage, rank uncertainty, and examples selected by a rule established before outcomes are inspected. Narrative case studies are explanatory supplements, not substitutes for complete results.

## Where It Breaks

High-school pitchers combine sparse performance evidence with major injury and development variance. Public velocity readings may come from different devices, pitch types, roles, and dates. A single maximum value is not interchangeable with a tracked distribution. Phase 1 widens high-school intervals but cannot model injury without legitimate longitudinal inputs.

Cold-weather prospects play short schedules against uneven opponents and can be evaluated indoors or early in the season. Competition adjustment alone may not recover lost opportunities. Showcase heroes present the opposite problem: selection and a memorable peak can dominate a tiny sample. Summer-league participation is also selected, so its apparent equalizing value may partly reflect who received an invitation and remained healthy.

Identity errors can overwhelm subtle model gains. Names collide, schools change, players are drafted more than once, and two-way players may need separate role records. A production registry requires source identifiers, matching evidence, confidence, manual overrides, and an unresolved queue. Silent fuzzy joins are unacceptable.

Survivorship bias remains fundamental. Drafted players have already passed filters imposed by teams, advisers, signability, health, and exposure. A model trained only on signees estimates outcomes conditional on that selection, not the value of every eligible amateur. Undrafted and unsigned players need careful inclusion where outcomes and pre-draft evidence can be measured; otherwise claims must remain conditional.

## Reproducibility and Interfaces

The run manifest records schema and model versions, seed, cutoff, configuration, limitations, and a checksum of canonical demo inputs. JSON uses stable key ordering, board rows have deterministic ordering, and generated SVG charts contain no runtime metadata. The reproducibility command builds twice in temporary directories and compares every relative path and SHA-256 digest. API and CLI functions call the same application service rather than duplicating feature or model logic.

Empirical mode fails closed with an explanation. This is important operational behavior. A misspelled mode, unavailable source, or absent rights record must not fall back to demo data while producing a plausibly real board. Any public deployment would additionally need authentication decisions, rate limiting, source refresh monitoring, stale-data policy, observability, correction procedures, and a release license.

## Demonstration Results

No empirical claims are available. The generated fold values confirm only that all 2015-2023 role cohorts execute, feature transforms stay inside each training fold, uncertainty fields serialize, and benchmark-shaped comparisons share a player universe. The generated board contains invented 2026 names. Its ordering and intervals are test fixtures, not recommendations, rankings, forecasts, or evidence that the selected formulas work on baseball data.

The charts should be read as interface demonstrations. Rank-correlation bars visualize synthetic fold outputs, and uncertainty bars verify that sparse high-school records receive wider bands than college records. They are included because charts can expose cohort instability and uncertainty more directly than prose, not to create visual authority for fake evidence.

## Empirical Readiness Gate

The next phase starts with evidence collection, not scraping. For every source, the project must establish terms, redistribution and derivative rights, archival availability, field definitions, coverage by cohort and role, stable identifiers, and timestamp reliability. It must select a professional outcome, horizon, WAR provider if applicable, censoring method, prediction date, and benchmark matching policy. A labeled identity sample should measure matching accuracy before large joins occur.

Only then should naive age-only, scouting-only, and performance-only baselines be run. Model complexity, summer weighting, transfer-cohort translations, and uncertainty methods can be compared within temporal folds. If archived inputs or mature outcomes do not support 2015-2023, the correct result is a narrower cohort or a no-go decision, not inferred dates or hand-filled data.

## Conclusion

Phase 1 delivers the plumbing and the skepticism required for a credible public model. It demonstrates contracts, provenance, temporal boundaries, deterministic estimation, humble uncertainty, comparison mechanics, and equivalent interfaces. It does not answer which amateurs will become productive professionals. That answer requires lawful point-in-time data, defensible outcomes, validated identities, mature cohorts, and evaluation designed before results are known. The visible `DEMO / NOT EMPIRICAL` boundary is therefore the most important result of this release.
"""


def _rank_chart(folds: list[dict[str, Any]], label: str) -> str:
    bars = []
    for index, fold in enumerate(folds):
        value = float(fold["rank_correlation"])
        height = abs(value) * 80
        x = 40 + index * 24
        y = 120 - (height if value >= 0 else 0)
        color = "#176b87" if value >= 0 else "#b04435"
        bars.append(f'<rect x="{x}" y="{y:.1f}" width="16" height="{height:.1f}" fill="{color}"/>')
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="520" height="170" role="img" '
        f'aria-label="{label} fold rank correlations"><rect width="100%" height="100%" fill="#f5f1e8"/>'
        f'<text x="20" y="22" font-family="sans-serif" font-size="14">{label}: fold rank correlation</text>'
        '<line x1="20" y1="120" x2="500" y2="120" stroke="#555"/>' + "".join(bars) + "</svg>\n"
    )


def _uncertainty_chart(predictions: list[dict[str, Any]], label: str) -> str:
    bars = []
    for index, prediction in enumerate(predictions):
        width = min(float(prediction["uncertainty_width"]) * 15, 350)
        bars.append(
            f'<rect x="145" y="{35 + index * 28}" width="{width:.1f}" height="16" fill="#d28b35"/>'
            f'<text x="10" y="{48 + index * 28}" font-family="sans-serif" font-size="11">{prediction["name"]}</text>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="520" height="170" role="img" '
        'aria-label="Synthetic prediction uncertainty"><rect width="100%" height="100%" fill="#f5f1e8"/>'
        f'<text x="10" y="18" font-family="sans-serif" font-size="13">{label}: interval width</text>'
        + "".join(bars)
        + "</svg>\n"
    )


def _report_empirical(folds: list[dict[str, Any]], limitations: list[str]) -> str:
    fold_rows = "\n".join(
        f"| {fold['draft_year']} {fold['role']} | {fold['train_size']} | {fold['test_size']} | "
        f"{fold['rank_correlation']} | {fold['mean_absolute_error']} | {fold['interval_coverage']} | "
        f"{fold['brier_score']} |"
        for fold in folds
    )
    limitation_rows = "\n".join(f"- {item}" for item in limitations)
    return f"""# DRAFT — Empirical Mode Methodology and Results

> **EMPIRICAL (NCAA DATA) / LIMITED COHORT**

## Data and Scope

This run uses real data delivered by the MIT-licensed `ncaa_bbStats` package: MLB draft selections for
2021-2023 scraped from public MLB.com draft listings and NCAA college batting and pitching
player-season statistics. Draft picks are joined to college stat lines by normalized full name,
school, and draft year, with a school-name canonicalization pass. Only drafted college players with a
matched stat line enter modeling; high-school, junior-college, and unmatched players are excluded.
All observation records carry `synthetic: false` and an explicit `available_at` date of May 15 in the
draft year, before the May 31 prediction cutoff.

## Outcome Target

The modeled target is a draft-position proxy derived from round and pick number, not MLB performance.
It is a monotone decreasing function of selection cost and exists only because a validated MLB
outcome join (Lahman plus a current Chadwick Register) is not yet connected for these recent draft
classes. No projection in this release should be read as a forecast of major-league value.

## Features and Model

Role-specific ridge regressions (L2 penalty 1.0, closed form, fold-local standardization) over six
cutoff-safe features per role: age relative to the May 31 cutoff (birth dates estimated from class
year), competition strength, offense or dominance rates, discipline or strike percentage, a scouting
grade placeholder, and summer share or velocity. Training for each fold uses only draft classes
strictly before the test year; no random splits are used.

## Temporal Results

| Draft year / role | Train | Test | Rank rho | MAE | Interval coverage | Brier |
|---|---|---|---|---|---|---|
{fold_rows}

Rank correlations are at or below zero. This is the expected behavior of college statistics against
a draft-position target: teams draft on projection, tools, and signability, not solely on college
box-score production. The metrics demonstrate that the empirical pipeline executes end to end with
leakage controls intact; they do not establish predictive skill for MLB outcomes.

## Limitations

{limitation_rows}

- College stat lines dated May 15 may include games played after that calendar date in reality; a
  fully verified per-game availability ledger is not available for these seasons.
- The scouting feature is a neutral placeholder (grade 50), so this run measures college statistics
  and age only.
- 2021-2023 draftees are right-censored for any MLB outcome horizon; no MLB performance claim is made.

## Reproducibility

The run manifest records the input checksum of the canonical prospect set, model and schema
versions, seed, cutoff, and these limitations. Regenerating artifacts re-fetches the same public
sources; identity of outputs across runs is expected but not guaranteed against upstream site edits.
"""


def build_artifacts(output_dir: Path, data_mode: str = "demo") -> list[Path]:
    DataMode(data_mode)
    output_dir.mkdir(parents=True, exist_ok=True)
    draft_year = 2023 if data_mode == "empirical" else 2026
    board_result = board(data_mode, draft_year)
    backtest_result = backtest(data_mode)
    board_payload = board_result.model_dump(mode="json")
    backtest_payload = backtest_result.model_dump(mode="json")

    _write_json(output_dir / "board.json", board_payload)
    _write_json(output_dir / "backtest.json", backtest_payload)
    with (output_dir / "board.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["label", "rank", "player_id", "name", "role", "projected_war", "lower_war", "upper_war", "probability_two_war"],
        )
        writer.writeheader()
        for rank, prediction in enumerate(board_result.predictions, start=1):
            writer.writerow({
                "label": board_result.label,
                "rank": rank,
                "player_id": prediction.player_id,
                "name": prediction.name,
                "role": prediction.role.value,
                "projected_war": prediction.projected_war,
                "lower_war": prediction.lower_war,
                "upper_war": prediction.upper_war,
                "probability_two_war": prediction.probability_two_war,
            })

    if board_result.data_mode == DataMode.EMPIRICAL:
        from draft_model.ingest.ncaa_bbstats import (
            build_empirical_prospects_cached,
            empirical_checksum,
        )

        input_checksum = empirical_checksum(build_empirical_prospects_cached())
        configuration: dict[str, Any] = {
            "ridge_penalty": 1.0,
            "summer_weight": 1.5,
            "draft_year": board_result.as_of.year,
            "target": "draft_position_proxy",
        }
        report = _report_empirical(backtest_payload["folds"], backtest_result.limitations)
        model_card = (
            "# Model Card\n\n> **EMPIRICAL (NCAA DATA) / LIMITED COHORT**\n\n"
            "Role-specific ridge regressions over real NCAA college statistics and MLB draft listings "
            "(ncaa_bbStats, MIT). The outcome target is a draft-position proxy, not MLB performance. "
            "Birth dates are estimated from class year; scouting is a neutral placeholder. "
            "Not suitable for player evaluation.\n"
        )
        chart_label = "EMPIRICAL (NCAA DATA)"
    else:
        prospects = load_demo_prospects()
        input_checksum = demo_checksum(prospects)
        configuration = {"ridge_penalty": 1.0, "summer_weight": 1.5, "draft_year": 2026}
        report = _report()
        model_card = (
            "# Model Card\n\n> **DEMO / NOT EMPIRICAL**\n\n"
            "Role-specific ridge regressions over invented age, competition, performance, and scouting fixtures. "
            "Not suitable for player evaluation. Empirical mode is disabled.\n"
        )
        chart_label = "DEMO / NOT EMPIRICAL"

    manifest = RunManifest(
        seed=DEMO_SEED,
        as_of=board_result.as_of,
        data_mode=board_result.data_mode,
        label=board_result.label,
        input_checksum=input_checksum,
        configuration=configuration,
        limitations=board_result.limitations,
    )
    _write_json(output_dir / "run-manifest.json", manifest.model_dump(mode="json"))
    (output_dir / "methodology.md").write_text(report, encoding="utf-8")
    (output_dir / "model-card.md").write_text(model_card, encoding="utf-8")
    (output_dir / "rank-correlation.svg").write_text(
        _rank_chart(backtest_payload["folds"], chart_label), encoding="utf-8"
    )
    (output_dir / "uncertainty.svg").write_text(
        _uncertainty_chart(board_payload["predictions"], chart_label), encoding="utf-8"
    )
    return sorted(path for path in output_dir.iterdir() if path.is_file())


def _digests(directory: Path) -> dict[str, str]:
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*"))
        if path.is_file()
    }


def verify_reproducibility(data_mode: str = "demo") -> bool:
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        first_path, second_path = Path(first), Path(second)
        build_artifacts(first_path, data_mode)
        build_artifacts(second_path, data_mode)
        return _digests(first_path) == _digests(second_path)
