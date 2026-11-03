from pydantic import BaseModel, ConfigDict, Field


class BrandOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class BrandCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class BrandImportIn(BaseModel):
    names: list[str] = Field(min_length=1)


class BrandImportOut(BaseModel):
    created: list[str]
    skipped: list[str]


class CatalogBrandOut(BaseModel):
    name: str
    imported: bool


class CarModelOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    brand_id: int
    name: str


class CarModelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class ModelYearOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_id: int
    year: int


class ModelYearCreate(BaseModel):
    year: int = Field(ge=1886, le=2100)


class EngineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    model_year_id: int
    name: str
    fuel: str | None = None
    power_hp: int | None = None
    displacement_cc: int | None = None
    torque_nm: int | None = None
    cylinders: int | None = None
    engine_code: str | None = None


class EngineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    fuel: str | None = Field(default=None, max_length=60)
    power_hp: int | None = None
    displacement_cc: int | None = None
    torque_nm: int | None = None
    cylinders: int | None = None
    engine_code: str | None = Field(default=None, max_length=60)


class EngineUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    fuel: str | None = Field(default=None, max_length=60)
    power_hp: int | None = None
    displacement_cc: int | None = None
    torque_nm: int | None = None
    cylinders: int | None = None
    engine_code: str | None = Field(default=None, max_length=60)


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
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    wheelbase_mm: int | None = None
    weight_kg: int | None = None
    fuel_tank_l: float | None = None
    consumption_l_100km: float | None = None
    co2_g_km: int | None = None
    acceleration_0_100: float | None = None
    top_speed_kmh: int | None = None
    notes: str | None = None
    is_verified: bool = False


class TechSheetUpdate(BaseModel):
    summary: str | None = None
    body_type: str | None = Field(default=None, max_length=80)
    doors: int | None = None
    seats: int | None = None
    transmission: str | None = Field(default=None, max_length=80)
    drive: str | None = Field(default=None, max_length=80)
    length_mm: int | None = None
    width_mm: int | None = None
    height_mm: int | None = None
    wheelbase_mm: int | None = None
    weight_kg: int | None = None
    fuel_tank_l: float | None = None
    consumption_l_100km: float | None = None
    co2_g_km: int | None = None
    acceleration_0_100: float | None = None
    top_speed_kmh: int | None = None
    notes: str | None = None
    is_verified: bool | None = None


class VehiclePathOut(BaseModel):
    brand: BrandOut
    model: CarModelOut
    year: ModelYearOut
    engine: EngineOut
    sheet: TechSheetOut | None = None
    data_quality: str = "orientativo"
    verified_items: int = 0
    total_items: int = 0


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str | None = None
    sort_order: int


class CategorySummaryOut(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None = None
    sort_order: int
    item_count: int


class WorkshopItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    engine_id: int
    category_id: int
    title: str
    oem_ref: str | None = None
    alt_ref: str | None = None
    position: str | None = None
    quantity: str | None = None
    interval_km: int | None = None
    interval_months: int | None = None
    notes: str | None = None
    is_recommended: bool = True
    is_verified: bool = False


class WorkshopItemCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    oem_ref: str | None = Field(default=None, max_length=120)
    alt_ref: str | None = Field(default=None, max_length=120)
    position: str | None = Field(default=None, max_length=120)
    quantity: str | None = Field(default=None, max_length=60)
    interval_km: int | None = None
    interval_months: int | None = None
    notes: str | None = None
    is_recommended: bool = True
    is_verified: bool = False


class WorkshopItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    oem_ref: str | None = Field(default=None, max_length=120)
    alt_ref: str | None = Field(default=None, max_length=120)
    position: str | None = Field(default=None, max_length=120)
    quantity: str | None = Field(default=None, max_length=60)
    interval_km: int | None = None
    interval_months: int | None = None
    notes: str | None = None
    is_recommended: bool | None = None
    is_verified: bool | None = None


class VehicleTreeImportIn(BaseModel):
    brands: list[str] | None = None
    year_from: int | None = Field(default=None, ge=1950, le=2100)
    year_to: int | None = Field(default=None, ge=1950, le=2100)


class VehicleTreeImportOut(BaseModel):
    brands_touched: list[str]
    brands_created: int
    models_created: int
    years_created: int
    engines_created: int = 0
    note: str
