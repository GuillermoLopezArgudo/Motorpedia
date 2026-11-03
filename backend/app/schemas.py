from pydantic import BaseModel, ConfigDict, Field


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class CarModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    name: str


class ModelYearOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    year: int


class EngineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_year_id: int
    name: str
    fuel: str | None = None
    power_hp: int | None = None
    displacement_cc: int | None = None


class TechSheetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    engine_id: int
    summary: str | None = None
    body_type: str | None = None
    doors: int | None = None
    seats: int | None = None
    transmission: str | None = None
    drive: str | None = None
    notes: str | None = None


class VehiclePathOut(BaseModel):
    brand: BrandOut
    model: CarModelOut
    year: ModelYearOut
    engine: EngineOut
    sheet: TechSheetOut | None = None


class TechSheetUpdate(BaseModel):
    summary: str | None = None
    body_type: str | None = Field(default=None, max_length=80)
    doors: int | None = None
    seats: int | None = None
    transmission: str | None = Field(default=None, max_length=80)
    drive: str | None = Field(default=None, max_length=80)
    notes: str | None = None
