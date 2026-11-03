"""Añade columnas nuevas en tablas existentes (MVP sin Alembic)."""

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine


def ensure_columns(engine: Engine) -> None:
    inspector = inspect(engine)
    table_columns = {
        "engines": {
            "torque_nm": "INTEGER",
            "cylinders": "INTEGER",
            "engine_code": "VARCHAR(60)",
        },
        "tech_sheets": {
            "length_mm": "INTEGER",
            "width_mm": "INTEGER",
            "height_mm": "INTEGER",
            "wheelbase_mm": "INTEGER",
            "weight_kg": "INTEGER",
            "fuel_tank_l": "DOUBLE PRECISION",
            "consumption_l_100km": "DOUBLE PRECISION",
            "co2_g_km": "INTEGER",
            "acceleration_0_100": "DOUBLE PRECISION",
            "top_speed_kmh": "INTEGER",
        },
    }

    with engine.begin() as conn:
        for table, columns in table_columns.items():
            if table not in inspector.get_table_names():
                continue
            existing = {col["name"] for col in inspector.get_columns(table)}
            for name, sql_type in columns.items():
                if name in existing:
                    continue
                conn.execute(text(f'ALTER TABLE "{table}" ADD COLUMN "{name}" {sql_type}'))
