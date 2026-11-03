"""Datos de ejemplo para desarrollo local (pocas fichas reales de demo)."""

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
