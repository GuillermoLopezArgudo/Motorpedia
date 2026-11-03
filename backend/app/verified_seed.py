"""Aplica fichas verificadas propias (JSON) sobre motores del catálogo.

Sustituye plantillas orientativas cuando hay coincidencia marca/modelo/año/motor.
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session, joinedload

from app.models import Brand, CarModel, Engine, ModelYear, TechSheet, WorkshopItem
from app.seed import seed_categories

VERIFIED_PATH = Path(__file__).resolve().parent.parent / "data" / "verified_workshop.json"


def load_verified_catalog() -> list[dict]:
    if not VERIFIED_PATH.exists():
        return []
    return json.loads(VERIFIED_PATH.read_text(encoding="utf-8"))


def apply_verified_content(db: Session) -> dict:
    categories = seed_categories(db)
    catalog = load_verified_catalog()
    sheets_updated = 0
    engines_touched = 0
    items_written = 0

    engines = (
        db.query(Engine)
        .options(
            joinedload(Engine.model_year)
            .joinedload(ModelYear.model)
            .joinedload(CarModel.brand)
        )
        .all()
    )

    for entry in catalog:
        brand_cf = str(entry["brand"]).casefold()
        model_cf = str(entry["model"]).casefold()
        y0 = int(entry["year_from"])
        y1 = int(entry["year_to"])
        match = str(entry["engine_match"]).casefold()
        want_hp = entry.get("power_hp")

        matched = []
        for engine in engines:
            year = engine.model_year
            model = year.model
            brand = model.brand
            if brand.name.casefold() != brand_cf:
                continue
            if model.name.casefold() != model_cf:
                continue
            if year.year < y0 or year.year > y1:
                continue
            if match not in engine.name.casefold():
                continue
            if want_hp is not None and engine.power_hp not in (None, want_hp):
                # Permitir etiqueta "1.4 T-Jet 165 CV" aunque power_hp esté en el nombre
                if f"{want_hp}" not in engine.name:
                    continue
            matched.append(engine)

        for engine in matched:
            engines_touched += 1
            sheet = db.query(TechSheet).filter(TechSheet.engine_id == engine.id).first()
            if not sheet:
                sheet = TechSheet(engine_id=engine.id)
                db.add(sheet)
            for key, value in (entry.get("sheet") or {}).items():
                setattr(sheet, key, value)
            sheet.is_verified = True
            sheets_updated += 1

            # Sustituir ítems de taller por los verificados
            db.query(WorkshopItem).filter(WorkshopItem.engine_id == engine.id).delete()
            for raw in entry.get("items") or []:
                slug = raw["category"]
                cat = categories.get(slug)
                if not cat:
                    continue
                payload = {k: v for k, v in raw.items() if k != "category"}
                db.add(
                    WorkshopItem(
                        engine_id=engine.id,
                        category_id=cat.id,
                        is_recommended=True,
                        is_verified=True,
                        **payload,
                    )
                )
                items_written += 1

    db.commit()
    return {
        "engines_touched": engines_touched,
        "sheets_updated": sheets_updated,
        "items_written": items_written,
        "entries": len(catalog),
    }
