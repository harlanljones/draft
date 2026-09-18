from __future__ import annotations

import hashlib
import json
from pathlib import Path

from draft_model.contracts import PackageValidationResult, SourcePackageManifest


def validate_source_package(manifest_path: Path) -> PackageValidationResult:
    if manifest_path.is_symlink():
        raise ValueError("source package manifest cannot be a symlink")
    manifest = SourcePackageManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    root = manifest_path.parent.resolve(strict=True)
    total_bytes = 0

    for entry in manifest.files:
        candidate = manifest_path.parent / entry.path
        if candidate.is_symlink():
            raise ValueError(f"source package file cannot be a symlink: {entry.path}")
        resolved = candidate.resolve(strict=True)
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise ValueError(f"source package path escapes package root: {entry.path}")
        payload = resolved.read_bytes()
        if len(payload) != entry.bytes:
            raise ValueError(f"source package size mismatch: {entry.path}")
        checksum = hashlib.sha256(payload).hexdigest()
        if checksum != entry.sha256:
            raise ValueError(f"source package checksum mismatch: {entry.path}")
        total_bytes += len(payload)

    return PackageValidationResult(
        package_id=manifest.package_id,
        source=manifest.source,
        valid=True,
        files_verified=len(manifest.files),
        total_bytes=total_bytes,
        raw_redistribution_allowed=manifest.rights.allows_raw_redistribution,
        limitations=[
            "Package validation does not approve identity matches, coverage, outcomes, or modeling.",
            "The empirical readiness gates remain authoritative and must pass separately.",
        ],
    )


def canonical_manifest(manifest: SourcePackageManifest) -> str:
    return json.dumps(manifest.model_dump(mode="json"), sort_keys=True, separators=(",", ":")) + "\n"


def validated_package_file(manifest_path: Path, relative_path: str) -> Path:
    validate_source_package(manifest_path)
    manifest = SourcePackageManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    if relative_path not in {entry.path for entry in manifest.files}:
        raise ValueError(f"file is not declared by source package: {relative_path}")
    return (manifest_path.parent / relative_path).resolve(strict=True)
