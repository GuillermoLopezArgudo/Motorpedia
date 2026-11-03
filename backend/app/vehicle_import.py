"""Importa estructura marca/modelo/años/motores desde catálogo local."""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Brand, CarModel, Engine, ModelYear

VEHICLES_PATH = Path(__file__).resolve().parent.parent / "data" / "vehicles_eu.json"
ENGINES_PATH = Path(__file__).resolve().parent.parent / "data" / "engines_eu.json"


def load_vehicles_catalog() -> list[dict]:
    return json.loads(VEHICLES_PATH.read_text(encoding="utf-8"))


def load_engines_catalog() -> list[dict]:
    if not ENGINES_PATH.exists():
        return []
    return json.loads(ENGINES_PATH.read_text(encoding="utf-8"))


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
    engines_created = 0
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
                y.year: y
                for y in db.query(ModelYear).filter(ModelYear.model_id == model.id).all()
            }
            for year in range(y0, y1 + 1):
                if year in existing_years:
                    continue
                row = ModelYear(model_id=model.id, year=year)
                db.add(row)
                db.flush()
                years_created += 1
                existing_years[year] = row

    engines_created = _import_engines(db, wanted=wanted, year_from=year_from, year_to=year_to)
    engines_created += _ensure_placeholder_engines(db, wanted=wanted)

    db.commit()
    return {
        "brands_touched": sorted(set(brands_touched), key=str.casefold),
        "brands_created": brands_created,
        "models_created": models_created,
        "years_created": years_created,
        "engines_created": engines_created,
        "note": (
            "Estructura importada (marca/modelo/año/motor típico). "
            "Ficha técnica y piezas de taller se completan aparte."
        ),
    }


def _ensure_placeholder_engines(db: Session, *, wanted: set[str] | None) -> int:
    """Garantiza al menos un motor por año para que la cascada nunca se quede vacía."""
    from sqlalchemy import exists

    created = 0
    years_q = (
        db.query(ModelYear)
        .join(CarModel)
        .join(Brand)
        .filter(~exists().where(Engine.model_year_id == ModelYear.id))
    )
    years = years_q.all()
    if wanted is not None:
        years = [y for y in years if y.model.brand.name.casefold() in wanted]

    for model_year in years:
        db.add(
            Engine(
                model_year_id=model_year.id,
                name="Motor (catálogo pendiente)",
                fuel="Gasolina",
                power_hp=None,
                displacement_cc=None,
                engine_code=None,
            )
        )
        created += 1
        if created % 500 == 0:
            db.flush()

    if created:
        db.flush()
    return created


def _engine_label(eng: dict) -> str:
    name = str(eng["name"]).strip()
    hp = eng.get("power_hp")
    if hp is None:
        return name
    # Evita choques UniqueConstraint (mismo nombre, distinta potencia en el mismo año)
    suffix = f"{hp} CV"
    if suffix.lower() in name.lower():
        return name
    return f"{name} {suffix}"


def _import_engines(
    db: Session,
    *,
    wanted: set[str] | None,
    year_from: int | None,
    year_to: int | None,
) -> int:
    created = 0
    pending: set[tuple[int, str]] = set()

    for entry in load_engines_catalog():
        brand_name = str(entry["brand"]).strip()
        model_name = str(entry["model"]).strip()
        if wanted is not None and brand_name.casefold() not in wanted:
            continue

        brand = db.query(Brand).filter(Brand.name == brand_name).first()
        if not brand:
            continue
        model = (
            db.query(CarModel)
            .filter(CarModel.brand_id == brand.id, CarModel.name == model_name)
            .first()
        )
        if not model:
            continue

        years = {
            y.year: y
            for y in db.query(ModelYear).filter(ModelYear.model_id == model.id).all()
        }

        for eng in entry.get("engines") or []:
            e0 = int(eng["year_from"])
            e1 = int(eng["year_to"])
            if year_from is not None:
                e0 = max(e0, year_from)
            if year_to is not None:
                e1 = min(e1, year_to)
            if e1 < e0:
                continue

            name = _engine_label(eng)
            for year in range(e0, e1 + 1):
                model_year = years.get(year)
                if not model_year:
                    continue
                key = (model_year.id, name)
                if key in pending:
                    continue
                exists = (
                    db.query(Engine)
                    .filter(Engine.model_year_id == model_year.id, Engine.name == name)
                    .first()
                )
                if exists:
                    pending.add(key)
                    continue
                db.add(
                    Engine(
                        model_year_id=model_year.id,
                        name=name,
                        fuel=eng.get("fuel"),
                        power_hp=eng.get("power_hp"),
                        displacement_cc=eng.get("displacement_cc"),
                        engine_code=eng.get("engine_code"),
                    )
                )
                pending.add(key)
                created += 1

        # Flush por modelo para no acumular miles de inserts y detectar conflictos pronto
        db.flush()

    return created
