from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    models: Mapped[list["CarModel"]] = relationship(back_populates="brand", cascade="all, delete-orphan")


class CarModel(Base):
    __tablename__ = "car_models"
    __table_args__ = (UniqueConstraint("brand_id", "name", name="uq_brand_model"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    brand: Mapped[Brand] = relationship(back_populates="models")
    years: Mapped[list["ModelYear"]] = relationship(back_populates="model", cascade="all, delete-orphan")


class ModelYear(Base):
    __tablename__ = "model_years"
    __table_args__ = (UniqueConstraint("model_id", "year", name="uq_model_year"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_id: Mapped[int] = mapped_column(ForeignKey("car_models.id", ondelete="CASCADE"), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    model: Mapped[CarModel] = relationship(back_populates="years")
    engines: Mapped[list["Engine"]] = relationship(back_populates="model_year", cascade="all, delete-orphan")


class Engine(Base):
    __tablename__ = "engines"
    __table_args__ = (UniqueConstraint("model_year_id", "name", name="uq_year_engine"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_year_id: Mapped[int] = mapped_column(
        ForeignKey("model_years.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    fuel: Mapped[str | None] = mapped_column(String(60), nullable=True)
    power_hp: Mapped[int | None] = mapped_column(Integer, nullable=True)
    displacement_cc: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    model_year: Mapped[ModelYear] = relationship(back_populates="engines")
    sheet: Mapped["TechSheet | None"] = relationship(
        back_populates="engine", uselist=False, cascade="all, delete-orphan"
    )


class TechSheet(Base):
    """Ficha técnica e información del vehículo (marca/modelo/año/motor)."""

    __tablename__ = "tech_sheets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    engine_id: Mapped[int] = mapped_column(
        ForeignKey("engines.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    body_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    doors: Mapped[int | None] = mapped_column(Integer, nullable=True)
    seats: Mapped[int | None] = mapped_column(Integer, nullable=True)
    transmission: Mapped[str | None] = mapped_column(String(80), nullable=True)
    drive: Mapped[str | None] = mapped_column(String(80), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    engine: Mapped[Engine] = relationship(back_populates="sheet")
