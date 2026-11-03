"""Datos de ejemplo para desarrollo local."""

from sqlalchemy.orm import Session

from app.models import Brand, CarModel, Engine, ModelYear, TechSheet


def seed_demo(db: Session) -> None:
    if db.query(Brand).first():
        return

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
    )
    eng_14 = Engine(
        model_year_id=ibiza_2000.id,
        name="1.4",
        fuel="Gasolina",
        power_hp=60,
        displacement_cc=1390,
    )
    eng_93 = Engine(
        model_year_id=ibiza_1993.id,
        name="1.5",
        fuel="Gasolina",
        power_hp=75,
        displacement_cc=1498,
    )
    eng_leon = Engine(
        model_year_id=leon_2018.id,
        name="1.5 TSI",
        fuel="Gasolina",
        power_hp=150,
        displacement_cc=1498,
    )
    eng_golf = Engine(
        model_year_id=golf_2015.id,
        name="2.0 TDI",
        fuel="Diésel",
        power_hp=150,
        displacement_cc=1968,
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
            notes="Datos orientativos de demo. Sustituir por ficha real.",
        )
    )
    db.commit()
