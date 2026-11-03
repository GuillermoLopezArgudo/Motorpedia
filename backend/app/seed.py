"""Datos de ejemplo para desarrollo local (pocas fichas reales de demo)."""

from sqlalchemy.orm import Session

from app.models import Brand, CarModel, Category, Engine, ModelYear, TechSheet, WorkshopItem

DEFAULT_CATEGORIES = [
    ("ficha", "Ficha técnica", "Datos generales del vehículo", 0),
    ("correas", "Correas", "Correas de distribución, auxiliar y tensores", 10),
    ("filtros", "Filtros", "Aceite, aire, combustible y habitáculo", 20),
    ("aceites", "Aceites y fluidos", "Motor, caja, frenos, refrigerante", 30),
    ("frenos", "Frenos", "Pastillas, discos y líquido", 40),
    ("bujias", "Bujías / calentadores", "Encendido o precalentamiento", 50),
    ("fallos", "Fallos frecuentes", "Problemas típicos de este motor", 60),
]


def seed_categories(db: Session) -> dict[str, Category]:
    by_slug: dict[str, Category] = {}
    for slug, name, description, sort_order in DEFAULT_CATEGORIES:
        cat = db.query(Category).filter(Category.slug == slug).first()
        if not cat:
            cat = Category(slug=slug, name=name, description=description, sort_order=sort_order)
            db.add(cat)
            db.flush()
        by_slug[slug] = cat
    db.commit()
    return by_slug


def seed_demo(db: Session) -> None:
    categories = seed_categories(db)

    if not db.query(Brand).first():
        seat = Brand(name="Seat")
        vw = Brand(name="Volkswagen")
        db.add_all([seat, vw])
        db.flush()

        ibiza = CarModel(brand_id=seat.id, name="Ibiza")
        leon = CarModel(brand_id=seat.id, name="León")
        golf = CarModel(brand_id=vw.id, name="Golf")
        db.add_all([ibiza, leon, golf])
        db.flush()

        ibiza_2000 = ModelYear(model_id=ibiza.id, year=2000)
        ibiza_1993 = ModelYear(model_id=ibiza.id, year=1993)
        leon_2018 = ModelYear(model_id=leon.id, year=2018)
        golf_2015 = ModelYear(model_id=golf.id, year=2015)
        db.add_all([ibiza_2000, ibiza_1993, leon_2018, golf_2015])
        db.flush()

        eng_tdi = Engine(
            model_year_id=ibiza_2000.id,
            name="1.9 TDI",
            fuel="Diésel",
            power_hp=90,
            displacement_cc=1896,
            torque_nm=210,
            cylinders=4,
            engine_code="AGR",
        )
        eng_14 = Engine(
            model_year_id=ibiza_2000.id,
            name="1.4",
            fuel="Gasolina",
            power_hp=60,
            displacement_cc=1390,
            torque_nm=116,
            cylinders=4,
        )
        eng_93 = Engine(
            model_year_id=ibiza_1993.id,
            name="1.5",
            fuel="Gasolina",
            power_hp=75,
            displacement_cc=1498,
            cylinders=4,
        )
        eng_leon = Engine(
            model_year_id=leon_2018.id,
            name="1.5 TSI",
            fuel="Gasolina",
            power_hp=150,
            displacement_cc=1498,
            torque_nm=250,
            cylinders=4,
            engine_code="DADA",
        )
        eng_golf = Engine(
            model_year_id=golf_2015.id,
            name="2.0 TDI",
            fuel="Diésel",
            power_hp=150,
            displacement_cc=1968,
            torque_nm=320,
            cylinders=4,
        )
        db.add_all([eng_tdi, eng_14, eng_93, eng_leon, eng_golf])
        db.flush()

        db.add(
            TechSheet(
                engine_id=eng_tdi.id,
                summary="Seat Ibiza (2000) 1.9 TDI — ficha de ejemplo para Motorpedia.",
                body_type="Hatchback",
                doors=5,
                seats=5,
                transmission="Manual 5 velocidades",
                drive="Delantera",
                length_mm=3877,
                width_mm=1640,
                height_mm=1415,
                wheelbase_mm=2443,
                weight_kg=1125,
                fuel_tank_l=45,
                consumption_l_100km=5.0,
                co2_g_km=135,
                acceleration_0_100=12.5,
                top_speed_kmh=180,
                notes="Datos orientativos de demo. Sustituir por ficha verificada.",
            )
        )
        db.commit()

    # Workshop demo for Seat Ibiza 2000 1.9 TDI (idempotente)
    eng_tdi = (
        db.query(Engine)
        .join(ModelYear)
        .join(CarModel)
        .join(Brand)
        .filter(
            Brand.name == "Seat",
            CarModel.name == "Ibiza",
            ModelYear.year == 2000,
            Engine.name == "1.9 TDI",
        )
        .first()
    )
    if not eng_tdi:
        return
    if db.query(WorkshopItem).filter(WorkshopItem.engine_id == eng_tdi.id).first():
        return

    items = [
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["correas"].id,
            title="Correa de distribución",
            oem_ref="06A109119C",
            alt_ref="Gates 5419XS (equiv. orientativa)",
            position="Distribución",
            quantity="1",
            interval_km=90000,
            interval_months=60,
            notes="Cambiar kit completo (correa + tensores + bomba de agua recomendada).",
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["correas"].id,
            title="Correa auxiliar / accesorios",
            oem_ref="06A903137E",
            position="Alternador / dirección / A/C según equipamiento",
            quantity="1",
            interval_km=60000,
            interval_months=48,
            notes="Revisar estado en cada mantenimiento.",
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["filtros"].id,
            title="Filtro de aceite",
            oem_ref="06A115561B",
            quantity="1",
            notes="Con cada cambio de aceite.",
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["filtros"].id,
            title="Filtro de aire",
            oem_ref="6K0129620",
            quantity="1",
            interval_km=30000,
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["filtros"].id,
            title="Filtro de combustible",
            oem_ref="1J0127401A",
            quantity="1",
            interval_km=60000,
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["aceites"].id,
            title="Aceite de motor",
            oem_ref="VW 505.01 / 505.00",
            quantity="≈ 4,3 L",
            notes="Viscosidad habitual 5W-40 diésel según especificación VW. Verificar tapón.",
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["aceites"].id,
            title="Líquido de frenos",
            oem_ref="DOT 4",
            quantity="Según sangrado",
            interval_months=24,
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["frenos"].id,
            title="Pastillas delanteras",
            position="Eje delantero",
            quantity="1 juego",
            notes="Referencia según disco/llanta; verificar al desmontar.",
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["fallos"].id,
            title="Caudalímetro (MAF) sucio o fallando",
            notes="Tirones, humo, falta de potencia. Limpieza o sustitución frecuente en TDI de la época.",
            is_recommended=True,
        ),
        WorkshopItem(
            engine_id=eng_tdi.id,
            category_id=categories["fallos"].id,
            title="Inyectores / junta de inyector",
            notes="Holgura, ruidos metálicos o pérdida de compresión en cámara. Revisar pares de apriete.",
            is_recommended=True,
        ),
    ]
    db.add_all(items)
    db.commit()
