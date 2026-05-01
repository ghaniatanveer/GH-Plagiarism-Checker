from __future__ import annotations

import re
from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def clamp_percentage(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 2)
