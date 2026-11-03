"""Rellena ficha + categorías de taller con plantillas orientativas por motor.

No sustituye un catálogo OEM (Autodata/TecDoc). Sirve para que la UI no esté vacía
y el mecánico tenga una base editable.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models import Engine, TechSheet, WorkshopItem
from app.seed import seed_categories


def _fuel_key(fuel: str | None) -> str:
    f = (fuel or "").casefold()
    if "díesel" in f or "diesel" in f:
        return "diesel"
    if "híbrid" in f or "hybrid" in f:
        return "hybrid"
    if "eléct" in f or "electr" in f:
        return "ev"
    if "glp" in f or "gnc" in f:
        return "gas"
    return "petrol"


def _sheet_for_engine(engine: Engine) -> TechSheet:
    fuel = engine.fuel or "—"
    bits = [engine.name]
    if engine.power_hp:
        bits.append(f"{engine.power_hp} CV")
    if engine.displacement_cc:
        bits.append(f"{engine.displacement_cc} cc")
    if engine.engine_code:
        bits.append(f"cód. {engine.engine_code}")
    summary = f"Ficha base de {', '.join(bits)}. Combustible: {fuel}."
    return TechSheet(
        engine_id=engine.id,
        summary=summary,
        notes=(
            "Datos orientativos generados automáticamente. "
            "No sustituyen ficha verificada ni manual OEM. Confirmar siempre con VIN."
        ),
        is_verified=False,
    )


def _items_for_engine(engine: Engine, categories: dict) -> list[WorkshopItem]:
    key = _fuel_key(engine.fuel)
    eid = engine.id
    items: list[WorkshopItem] = []

    def add(slug: str, **kwargs):
        items.append(
            WorkshopItem(
                engine_id=eid,
                category_id=categories[slug].id,
                is_recommended=True,
                is_verified=False,
                **kwargs,
            )
        )

    # Aceites / fluidos
    if key == "diesel":
        add(
            "aceites",
            title="Aceite de motor (diésel)",
            quantity="Consultar capacidad",
            notes="Especificación habitual del grupo: ACEA C3 / normas VW-Audi-Mercedes según marca. Verificar tapón y homologación.",
            interval_km=15000,
            interval_months=12,
        )
    elif key == "ev":
        add(
            "aceites",
            title="Líquido refrigerante sistema HV / electrónica",
            notes="No usar refrigerante genérico sin especificación del fabricante.",
            interval_months=24,
        )
    else:
        add(
            "aceites",
            title="Aceite de motor",
            quantity="Consultar capacidad",
            notes="Viscosidad y norma según fabricante (p. ej. VW 508/504, BMW LL, PSA). Verificar en tapón/manual.",
            interval_km=15000,
            interval_months=12,
        )

    add(
        "aceites",
        title="Líquido de frenos",
        oem_ref="DOT 4",
        quantity="Según sangrado",
        interval_months=24,
        notes="Sustituir periódicamente; no mezclar tipos distintos.",
    )

    # Filtros
    add(
        "filtros",
        title="Filtro de aceite",
        quantity="1",
        notes="Cambiar en cada servicio de aceite. Referencia OEM según VIN.",
    )
    add(
        "filtros",
        title="Filtro de aire",
        quantity="1",
        interval_km=30000,
        notes="Acortar intervalo en ambientes polvorientos.",
    )
    add(
        "filtros",
        title="Filtro de habitáculo",
        quantity="1",
        interval_km=30000,
        interval_months=24,
    )
    if key in {"diesel"}:
        add(
            "filtros",
            title="Filtro de combustible",
            quantity="1",
            interval_km=60000,
            notes="Crítico en common-rail. Usar calidad OEM o equivalente aprobado.",
        )

    # Correas
    if key == "ev":
        add(
            "correas",
            title="Correas auxiliares",
            notes="Muchos EV no usan correa de distribución clásica. Revisar accesorios según modelo.",
        )
    else:
        add(
            "correas",
            title="Distribución (correa o cadena)",
            interval_km=90000,
            interval_months=60,
            notes=(
                "Confirmar si este motor lleva CORREA o CADENA. "
                "Si es correa: kit completo + bomba de agua recomendada. Intervalo exacto según fabricante."
            ),
        )
        add(
            "correas",
            title="Correa auxiliar / accesorios",
            interval_km=60000,
            interval_months=48,
            notes="Revisar grietas y tensores en cada mantenimiento.",
        )

    # Ruedas
    add(
        "ruedas",
        title="Medida de neumático (orientativa)",
        notes=(
            "Confirmar en lateral del neumático o placa de fabricante. "
            "Ejemplos habituales según segmento: 185/65 R15, 205/55 R16, 225/45 R17. "
            "Presión según carga/velocidad en tapa de combustible o marco de puerta."
        ),
    )
    add(
        "ruedas",
        title="Par de apriete de rueda",
        notes="Típico 110–140 Nm en turismos; verificar valor exacto del modelo.",
    )

    # Frenos
    add(
        "frenos",
        title="Pastillas / discos",
        notes="Medir desgaste; referencia según eje y tamaño de pinza/llanta. No inventar OEM sin VIN.",
    )

    # Bujías / calentadores
    if key == "diesel":
        add(
            "bujias",
            title="Calentadores",
            notes="Fallos de arranque en frío / humo blanco: comprobar resistencia y control.",
        )
    elif key != "ev":
        add(
            "bujias",
            title="Bujías de encendido",
            interval_km=60000,
            notes="Tipo (níquel/iridio) e intervalo según fabricante. Par de apriete crítico.",
        )

    # Fallos
    add(
        "fallos",
        title="Puntos a vigilar en este motor",
        notes=(
            f"Plantilla para {engine.name} ({engine.fuel or 'combustible n/d'}). "
            "Añadir fallos reales conocidos del código motor cuando se verifiquen."
        ),
    )

    return items


def seed_baseline_content(db: Session) -> dict:
    categories = seed_categories(db)
    sheets_created = 0
    items_created = 0

    engines = db.query(Engine).all()
    for engine in engines:
        if not db.query(TechSheet).filter(TechSheet.engine_id == engine.id).first():
            db.add(_sheet_for_engine(engine))
            sheets_created += 1

        existing_cat_ids = {
            row[0]
            for row in db.query(WorkshopItem.category_id)
            .filter(WorkshopItem.engine_id == engine.id)
            .distinct()
            .all()
        }

        batch = _items_for_engine(engine, categories)
        if not existing_cat_ids:
            db.add_all(batch)
            items_created += len(batch)
            continue

        # Completar categorías nuevas (p. ej. ruedas) sin pisar lo ya curado
        missing_cat_ids = {
            item.category_id for item in batch if item.category_id not in existing_cat_ids
        }
        for item in batch:
            if item.category_id not in missing_cat_ids:
                continue
            db.add(item)
            items_created += 1

    db.commit()
    return {"sheets_created": sheets_created, "items_created": items_created}
