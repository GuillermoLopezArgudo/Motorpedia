"""Arranque automático del catálogo + contenido (idempotente)."""

from __future__ import annotations

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.content_seed import seed_baseline_content
from app.models import Brand, Engine, TechSheet, WorkshopItem
from app.seed import seed_categories
from app.vehicle_import import import_vehicle_tree, load_vehicles_catalog


def bootstrap_catalog(db: Session) -> dict:
    seed_categories(db)

    catalog = load_vehicles_catalog()
    brand_count = db.query(func.count(Brand.id)).scalar() or 0
    engine_count = db.query(func.count(Engine.id)).scalar() or 0
    sheet_count = db.query(func.count(TechSheet.id)).scalar() or 0
    item_count = db.query(func.count(WorkshopItem.id)).scalar() or 0

    imported = {
        "brands_created": 0,
        "models_created": 0,
        "years_created": 0,
        "engines_created": 0,
    }
    # Si faltan marcas del catálogo UE o no hay motores, importar árbol
    if brand_count < len(catalog) or engine_count < 50:
        imported = import_vehicle_tree(db)

    content = {"sheets_created": 0, "items_created": 0}
    # Si hay motores sin ficha o sin ítems, rellenar plantillas
    engines_without_sheet = (
        db.query(func.count(Engine.id))
        .outerjoin(TechSheet, TechSheet.engine_id == Engine.id)
        .filter(TechSheet.id.is_(None))
        .scalar()
        or 0
    )
    if engines_without_sheet > 0 or item_count == 0:
        content = seed_baseline_content(db)

    return {
        "ready": True,
        "brands": db.query(func.count(Brand.id)).scalar() or 0,
        "engines": db.query(func.count(Engine.id)).scalar() or 0,
        "sheets": db.query(func.count(TechSheet.id)).scalar() or 0,
        "items": db.query(func.count(WorkshopItem.id)).scalar() or 0,
        "imported": imported,
        "content": content,
        "message": "Catálogo listo. Elige marca → modelo → año → motor para ver toda la info.",
    }
