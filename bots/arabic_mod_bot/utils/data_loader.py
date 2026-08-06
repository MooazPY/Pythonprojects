"""Load bundled filter data (word lists, scam domains) from JSON files."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger("arabic_mod_bot.data_loader")

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json_list(filename: str, fallback: list[str]) -> list[str]:
    path = _DATA_DIR / filename
    if not path.exists():
        logger.warning("Data file missing: %s — using built-in fallback.", path)
        return list(fallback)
    try:
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"{filename} must contain a JSON array")
        return [str(item).strip() for item in data if str(item).strip()]
    except (json.JSONDecodeError, OSError, ValueError) as exc:
        logger.error("Failed to load %s: %s — using fallback.", path, exc)
        return list(fallback)


def load_bad_words(fallback: list[str]) -> list[str]:
    return _load_json_list("arabic_bad_words.json", fallback)


def load_scam_domains(fallback: set[str]) -> set[str]:
    items = _load_json_list("scam_domains.json", list(fallback))
    return set(items)
