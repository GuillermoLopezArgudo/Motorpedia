"""Importa estructura marca/modelo/años desde catálogo local (sin inventar motores/piezas)."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Brand, CarModel, ModelYear

VEHICLES_PATH = Path(__file__).resolve().parent.parent / "data" / "vehicles_eu.json"


def load_vehicles_catalog() -> list[dict]:
    return json.loads(VEHICLES_PATH.read_text(encoding="utf-8"))


def import_vehicle_tree(
    db: Session,
    *,
    brand_names: list[str] | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
) -> dict:
    catalog = load_vehicles_catalog()
    wanted = None
    if brand_names:
        wanted = {n.strip().casefold() for n in brand_names if n.strip()}

    brands_created = 0
    models_created = 0
    years_created = 0
    brands_touched: list[str] = []

    for entry in catalog:
        brand_name = str(entry["brand"]).strip()
        if wanted is not None and brand_name.casefold() not in wanted:
            continue

        brand = db.query(Brand).filter(Brand.name == brand_name).first()
        if not brand:
            brand = Brand(name=brand_name)
            db.add(brand)
            db.flush()
            brands_created += 1
        brands_touched.append(brand_name)

        for model_entry in entry.get("models") or []:
            model_name = str(model_entry["name"]).strip()
            y0 = int(model_entry["year_from"])
            y1 = int(model_entry["year_to"])
            if year_from is not None:
                y0 = max(y0, year_from)
            if year_to is not None:
                y1 = min(y1, year_to)
            if y1 < y0:
                continue

            model = (
                db.query(CarModel)
                .filter(CarModel.brand_id == brand.id, CarModel.name == model_name)
                .first()
            )
            if not model:
                model = CarModel(brand_id=brand.id, name=model_name)
                db.add(model)
                db.flush()
                models_created += 1

            existing_years = {
                y.year
                for y in db.query(ModelYear).filter(ModelYear.model_id == model.id).all()
            }
            for year in range(y0, y1 + 1):
                if year in existing_years:
                    continue
                db.add(ModelYear(model_id=model.id, year=year))
                years_created += 1
                existing_years.add(year)

    db.commit()
    return {
        "brands_touched": sorted(set(brands_touched), key=str.casefold),
        "brands_created": brands_created,
        "models_created": models_created,
        "years_created": years_created,
        "note": (
            "Estructura importada (marca/modelo/año). "
            "Motores, ficha técnica y piezas de taller se completan aparte."
        ),
    }
