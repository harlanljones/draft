from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path

from draft_model.artifacts import build_artifacts, verify_reproducibility
from draft_model.artifacts.prospective import export_prospective_schemas
from draft_model.ingest.chadwick import resolve_chadwick_identities
from draft_model.ingest.packages import validate_source_package
from draft_model.outcomes.lahman import derive_mlb_debut_labels
from draft_model.outcomes.preflight import audit_empirical_labels, run_empirical_pipeline
from draft_model.service import backtest, readiness


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="draft-model", description="Amateur projection reference system")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backtest_parser = subparsers.add_parser("backtest", help="run temporal evaluation")
    backtest_parser.add_argument("--data-mode", default="demo", choices=["demo", "empirical"])
    backtest_parser.add_argument("--output", type=Path, required=True)

    build_parser = subparsers.add_parser("build", help="generate board and report artifacts")
    build_parser.add_argument("--data-mode", default="demo", choices=["demo", "empirical"])
    build_parser.add_argument("--output-dir", type=Path, required=True)

    verify_parser = subparsers.add_parser("verify-reproducibility", help="compare two clean builds")
    verify_parser.add_argument("--data-mode", default="demo", choices=["demo", "empirical"])

    readiness_parser = subparsers.add_parser("readiness", help="show empirical readiness decision")
    readiness_parser.add_argument("--output", type=Path)

    package_parser = subparsers.add_parser(
        "validate-source-package", help="validate a local licensed source package"
    )
    package_parser.add_argument("manifest", type=Path)
    package_parser.add_argument("--output", type=Path)

    schema_parser = subparsers.add_parser(
        "export-prospective-schemas", help="export 2026-forward collection JSON Schemas"
    )
    schema_parser.add_argument("--output-dir", type=Path, required=True)

    outcome_parser = subparsers.add_parser(
        "derive-lahman-debut-outcomes", help="derive fixed-horizon MLB debut labels"
    )
    outcome_parser.add_argument("--cohort-manifest", type=Path, required=True)
    outcome_parser.add_argument("--cohort-file", required=True)
    outcome_parser.add_argument("--lahman-manifest", type=Path, required=True)
    outcome_parser.add_argument("--people-file", required=True)
    outcome_parser.add_argument("--outcome-through-year", type=int, required=True)
    outcome_parser.add_argument("--horizon", type=int, default=2)
    outcome_parser.add_argument("--output", type=Path, required=True)

    identity_parser = subparsers.add_parser(
        "resolve-chadwick-identities", help="resolve conservative Chadwick identity matches"
    )
    identity_parser.add_argument("--cohort-manifest", type=Path, required=True)
    identity_parser.add_argument("--cohort-file", required=True)
    identity_parser.add_argument("--register-manifest", type=Path, required=True)
    identity_parser.add_argument("--register-file", required=True)
    identity_parser.add_argument("--output", type=Path, required=True)

    preflight_parser = subparsers.add_parser(
        "audit-empirical-labels", help="audit identity and outcome label coverage"
    )
    preflight_parser.add_argument("--identities", type=Path, required=True)
    preflight_parser.add_argument("--outcomes", type=Path, required=True)
    preflight_parser.add_argument("--output", type=Path, required=True)

    pipeline_parser = subparsers.add_parser(
        "verify-empirical-labels", help="run full identity-label-pipeline from manifests"
    )
    pipeline_parser.add_argument("--cohort-manifest", type=Path, required=True)
    pipeline_parser.add_argument("--cohort-file", required=True)
    pipeline_parser.add_argument("--register-manifest", type=Path, required=True)
    pipeline_parser.add_argument("--register-file", required=True)
    pipeline_parser.add_argument("--lahman-manifest", type=Path, required=True)
    pipeline_parser.add_argument("--people-file", required=True)
    pipeline_parser.add_argument("--outcome-through-year", type=int, required=True)
    pipeline_parser.add_argument("--output-dir", type=Path, required=True)

    eada_parser = subparsers.add_parser(
        "ingest-eada",
        help="download and derive first-party EADA program-resource context",
        description=(
            "Download official U.S. Department of Education EADA archives "
            "(public domain), derive program-resource context rows, and write "
            "a combined context CSV plus provenance manifest under the output "
            "directory. The derived file is gitignored local data."
        ),
    )
    eada_parser.add_argument(
        "--academic-end-years",
        type=int,
        nargs="+",
        required=True,
        help="academic years' END year, e.g. 2023 for the 2022-23 survey",
    )
    eada_parser.add_argument("--download-dir", type=Path, default=Path("data/empirical/eada"))
    eada_parser.add_argument(
        "--output-dir", type=Path, default=Path("data/empirical/derived")
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "backtest":
            result = backtest(args.data_mode)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
            return 0
        if args.command == "build":
            build_artifacts(args.output_dir, args.data_mode)
            return 0
        if args.command == "readiness":
            payload = readiness().model_dump_json(indent=2) + "\n"
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(payload, encoding="utf-8")
            else:
                print(payload, end="")
            return 0
        if args.command == "validate-source-package":
            payload = validate_source_package(args.manifest).model_dump_json(indent=2) + "\n"
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(payload, encoding="utf-8")
            else:
                print(payload, end="")
            return 0
        if args.command == "export-prospective-schemas":
            export_prospective_schemas(args.output_dir)
            return 0
        if args.command == "derive-lahman-debut-outcomes":
            labels = derive_mlb_debut_labels(
                cohort_manifest=args.cohort_manifest,
                cohort_file=args.cohort_file,
                lahman_manifest=args.lahman_manifest,
                people_file=args.people_file,
                outcome_data_through_year=args.outcome_through_year,
                horizon_complete_seasons=args.horizon,
            )
            outcome_payload = [label.model_dump(mode="json") for label in labels]
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(outcome_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            return 0
        if args.command == "resolve-chadwick-identities":
            matches = resolve_chadwick_identities(
                cohort_manifest=args.cohort_manifest,
                cohort_file=args.cohort_file,
                register_manifest=args.register_manifest,
                register_file=args.register_file,
            )
            identity_payload = [match.model_dump(mode="json") for match in matches]
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(identity_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            return 0
        if args.command == "audit-empirical-labels":
            audit = audit_empirical_labels(args.identities, args.outcomes)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(audit.model_dump_json(indent=2) + "\n", encoding="utf-8")
            return 0
        if args.command == "verify-empirical-labels":
            pipeline_result = run_empirical_pipeline(
                cohort_manifest=args.cohort_manifest,
                cohort_file=args.cohort_file,
                register_manifest=args.register_manifest,
                register_file=args.register_file,
                lahman_manifest=args.lahman_manifest,
                people_file=args.people_file,
                outcome_data_through_year=args.outcome_through_year,
                output_dir=args.output_dir,
            )
            audit_path = args.output_dir / "label-audit.json"
            audit_path.write_text(pipeline_result.audit.model_dump_json(indent=2) + "\n", encoding="utf-8")
            print(f"verify-empirical-labels complete: identity={pipeline_result.identity_path}, outcome={pipeline_result.outcome_path}, audit={audit_path}")
            return 0
        if args.command == "ingest-eada":
            from draft_model.ingest.eada_file import (
                build_context_rows,
                download_eada_file,
                extract_schools_workbook,
                write_context_csv,
            )

            all_rows: list[dict[str, object]] = []
            manifests: list[dict[str, object]] = []
            for end_year in sorted(set(args.academic_end_years)):
                provenance = download_eada_file(end_year, args.download_dir)
                workbook = extract_schools_workbook(
                    args.download_dir / provenance["file"],
                    args.download_dir / "extracted" / str(end_year),
                )
                rows, unmatched = build_context_rows(workbook, end_year)
                all_rows.extend(rows)
                manifests.append(
                    provenance
                    | {"eada_year": end_year, "rows": len(rows), "unmatched_schools": len(unmatched)}
                )
                print(f"EADA {end_year - 1}-{end_year}: {len(rows)} programs, {len(unmatched)} unmatched")
            args.output_dir.mkdir(parents=True, exist_ok=True)
            write_context_csv(all_rows, args.output_dir / "eada-context.csv")
            manifest = {
                "schema_version": "1.0",
                "source": "EADA survey (U.S. Department of Education)",
                "license_name": "Public domain (U.S. federal government work)",
                "license_url": "https://ope.ed.gov/athletics/#/datafile/list",
                "derived_sha256": hashlib.sha256(
                    (args.output_dir / "eada-context.csv").read_bytes()
                ).hexdigest(),
                "files": manifests,
            }
            (args.output_dir / "eada-context-manifest.json").write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            print(f"wrote {args.output_dir / 'eada-context.csv'} ({len(all_rows)} rows)")
            return 0
        if not verify_reproducibility(args.data_mode):
            print("reproducibility failed")
            return 1
        print("reproducibility passed")
        return 0
    except ValueError as exc:
        print(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
