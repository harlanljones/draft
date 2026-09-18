from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from draft_model.cli import main
from draft_model.contracts import SourcePackageManifest
from draft_model.ingest.packages import canonical_manifest, validate_source_package


def _manifest(path: str, payload: bytes, **rights: bool) -> dict[str, object]:
    return {
        "schema_version": "1.0",
        "package_id": "fixture-1",
        "source": "Authorized Synthetic Package Fixture",
        "data_mode": "empirical",
        "retrieved_at": "2026-09-17",
        "source_available_at": "2026-09-16",
        "availability_evidence": "Fixture agreement records first publication time.",
        "license_name": "Synthetic test grant",
        "license_url": "https://example.invalid/test-grant",
        "attribution": "Synthetic package fixture",
        "rights": {
            "agreement_reference": "fixture-agreement-1",
            "reviewed_by": "test reviewer",
            "reviewed_at": "2026-09-17",
            "allows_retention": rights.get("allows_retention", True),
            "allows_model_training": rights.get("allows_model_training", True),
            "allows_derived_publication": rights.get("allows_derived_publication", True),
            "allows_public_predictions": rights.get("allows_public_predictions", True),
            "allows_raw_redistribution": rights.get("allows_raw_redistribution", False),
        },
        "files": [
            {
                "path": path,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "bytes": len(payload),
                "media_type": "text/csv",
            }
        ],
    }


def _write_package(tmp_path: Path, manifest: dict[str, object], payload: bytes) -> Path:
    data_path = tmp_path / "data.csv"
    data_path.write_bytes(payload)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return manifest_path


def test_valid_local_source_package_and_cli(tmp_path: Path) -> None:
    payload = b"player_id,value\nfixture,1\n"
    manifest_path = _write_package(tmp_path, _manifest("data.csv", payload), payload)
    result = validate_source_package(manifest_path)
    assert result.valid
    assert result.files_verified == 1
    assert result.total_bytes == len(payload)
    assert not result.raw_redistribution_allowed
    output = tmp_path / "validation.json"
    assert main(["validate-source-package", str(manifest_path), "--output", str(output)]) == 0
    assert json.loads(output.read_text(encoding="utf-8"))["valid"] is True


def test_source_package_rejects_checksum_drift(tmp_path: Path) -> None:
    original = b"original\n"
    manifest_path = _write_package(tmp_path, _manifest("data.csv", original), b"modified\n")
    with pytest.raises(ValueError, match="checksum mismatch"):
        validate_source_package(manifest_path)


def test_source_package_rejects_missing_required_rights(tmp_path: Path) -> None:
    payload = b"fixture\n"
    manifest = _manifest("data.csv", payload, allows_public_predictions=False)
    manifest_path = _write_package(tmp_path, manifest, payload)
    with pytest.raises(ValidationError, match="public predictions"):
        validate_source_package(manifest_path)


def test_source_package_rejects_path_traversal() -> None:
    with pytest.raises(ValidationError, match="normalized relative paths"):
        SourcePackageManifest.model_validate(_manifest("../data.csv", b"fixture\n"))


def test_source_package_rejects_symlink(tmp_path: Path) -> None:
    payload = b"fixture\n"
    target = tmp_path / "target.csv"
    target.write_bytes(payload)
    (tmp_path / "data.csv").symlink_to(target)
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(_manifest("data.csv", payload)), encoding="utf-8")
    with pytest.raises(ValueError, match="cannot be a symlink"):
        validate_source_package(manifest_path)


def test_manifest_canonicalization_is_stable() -> None:
    manifest = SourcePackageManifest.model_validate(_manifest("data.csv", b"fixture\n"))
    assert canonical_manifest(manifest) == canonical_manifest(manifest)
