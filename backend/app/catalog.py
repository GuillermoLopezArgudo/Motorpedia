"""Catálogo estático de marcas (nombres reales, sin modelos inventados)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "brands_catalog.json"


@lru_cache(maxsize=1)
def load_brand_catalog() -> list[str]:
    raw = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    names: list[str] = []
    seen: set[str] = set()
    for item in raw:
        name = str(item).strip()
        key = name.casefold()
        if not name or key in seen:
            continue
        seen.add(key)
        names.append(name)
    return sorted(names, key=str.casefold)
