from __future__ import annotations

import json
from pathlib import Path

from draft_model.contracts.prospective import PROSPECTIVE_SCHEMA_MODELS


def export_prospective_schemas(output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for model in PROSPECTIVE_SCHEMA_MODELS:
        name = model.__name__.removeprefix("Prospective")
        filename = "".join((f"_{char.lower()}" if char.isupper() else char) for char in name).lstrip("_")
        path = output_dir / f"{filename}.schema.json"
        payload = model.model_json_schema()
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        written.append(path)
    return sorted(written)
