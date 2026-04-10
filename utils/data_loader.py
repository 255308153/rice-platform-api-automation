from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml_cases(file_name: str) -> list[dict[str, Any]]:
    file_path = Path(__file__).resolve().parents[1] / "testdata" / file_name
    with file_path.open("r", encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or []
    if not isinstance(data, list):
        raise ValueError(f"YAML 数据格式错误，期望 list，实际为: {type(data)}")
    return data
