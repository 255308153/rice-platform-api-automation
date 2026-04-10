from __future__ import annotations

import json
from pathlib import Path

import jsonschema


def load_schema(file_name: str) -> dict:
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / file_name
    return json.loads(schema_path.read_text(encoding="utf-8"))


def validate_with_schema(payload: dict, file_name: str) -> None:
    schema = load_schema(file_name)
    jsonschema.validate(instance=payload, schema=schema)
