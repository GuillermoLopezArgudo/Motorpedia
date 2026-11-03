from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Brand, CarModel, Engine, ModelYear, TechSheet
from app.schemas import (
    BrandOut,
    CarModelOut,
    EngineOut,
    ModelYearOut,
    TechSheetOut,
    TechSheetUpdate,
    VehiclePathOut,
)

router = APIRouter(prefix="/api", tags=["vehicles"])


@router.get("/health")
def health():
    return {"status": "ok", "app": "Motorpedia"}


@router.get("/brands", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.query(Brand).order_by(Brand.name).all()


@router.get("/brands/{brand_id}/models", response_model=list[CarModelOut])
def list_models(brand_id: int, db: Session = Depends(get_db)):
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(404, "Marca no encontrada")
    return (
        db.query(CarModel)
        .filter(CarModel.brand_id == brand_id)
        .order_by(CarModel.name)
        .all()
    )


@router.get("/models/{model_id}/years", response_model=list[ModelYearOut])
def list_years(model_id: int, db: Session = Depends(get_db)):
    model = db.get(CarModel, model_id)
    if not model:
        raise HTTPException(404, "Modelo no encontrado")
    return (
        db.query(ModelYear)
        .filter(ModelYear.model_id == model_id)
        .order_by(ModelYear.year.desc())
        .all()
    )


@router.get("/years/{year_id}/engines", response_model=list[EngineOut])
def list_engines(year_id: int, db: Session = Depends(get_db)):
    year = db.get(ModelYear, year_id)
    if not year:
        raise HTTPException(404, "Año no encontrado")
    return (
        db.query(Engine)
        .filter(Engine.model_year_id == year_id)
        .order_by(Engine.name)
        .all()
    )


@router.get("/engines/{engine_id}", response_model=VehiclePathOut)
def get_vehicle(engine_id: int, db: Session = Depends(get_db)):
    engine = (
        db.query(Engine)
        .options(
            joinedload(Engine.sheet),
            joinedload(Engine.model_year).joinedload(ModelYear.model).joinedload(CarModel.brand),
        )
        .filter(Engine.id == engine_id)
        .first()
    )
    if not engine:
        raise HTTPException(404, "Motor no encontrado")
    year = engine.model_year
    model = year.model
    brand = model.brand
    return VehiclePathOut(
        brand=brand,
        model=model,
        year=year,
        engine=engine,
        sheet=engine.sheet,
    )


@router.put("/engines/{engine_id}/sheet", response_model=TechSheetOut)
def upsert_sheet(engine_id: int, payload: TechSheetUpdate, db: Session = Depends(get_db)):
    engine = db.get(Engine, engine_id)
    if not engine:
        raise HTTPException(404, "Motor no encontrado")

    sheet = db.query(TechSheet).filter(TechSheet.engine_id == engine_id).first()
    if not sheet:
        sheet = TechSheet(engine_id=engine_id)
        db.add(sheet)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(sheet, field, value)

    db.commit()
    db.refresh(sheet)
    return sheet
