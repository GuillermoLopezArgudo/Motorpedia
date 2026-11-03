from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.catalog import load_brand_catalog
from app.database import get_db
from app.models import Brand, CarModel, Engine, ModelYear, TechSheet
from app.schemas import (
    BrandCreate,
    BrandImportIn,
    BrandImportOut,
    BrandOut,
    CarModelCreate,
    CarModelOut,
    CatalogBrandOut,
    EngineCreate,
    EngineOut,
    EngineUpdate,
    ModelYearCreate,
    ModelYearOut,
    TechSheetOut,
    TechSheetUpdate,
    VehiclePathOut,
    VehicleTreeImportIn,
    VehicleTreeImportOut,
)
from app.vehicle_import import import_vehicle_tree, load_vehicles_catalog

router = APIRouter(prefix="/api", tags=["vehicles"])


@router.get("/health")
def health():
    return {"status": "ok", "app": "Motorpedia"}


@router.get("/brands/catalog", response_model=list[CatalogBrandOut])
def brand_catalog(db: Session = Depends(get_db)):
    existing = {name.casefold() for (name,) in db.query(Brand.name).all()}
    return [
        CatalogBrandOut(name=name, imported=name.casefold() in existing)
        for name in load_brand_catalog()
    ]


@router.get("/vehicles/catalog")
def vehicles_catalog_preview():
    data = load_vehicles_catalog()
    return {
        "brands": len(data),
        "models": sum(len(b.get("models") or []) for b in data),
        "entries": [
            {
                "brand": b["brand"],
                "models": len(b.get("models") or []),
            }
            for b in data
        ],
    }


@router.post("/vehicles/import", response_model=VehicleTreeImportOut)
def vehicles_import(payload: VehicleTreeImportIn, db: Session = Depends(get_db)):
    """Importa marca → modelo → años/motores y rellena plantillas de taller orientativas."""
    if payload.year_from and payload.year_to and payload.year_from > payload.year_to:
        raise HTTPException(400, "year_from no puede ser mayor que year_to")
    result = import_vehicle_tree(
        db,
        brand_names=payload.brands,
        year_from=payload.year_from,
        year_to=payload.year_to,
    )
    from app.content_seed import seed_baseline_content

    content = seed_baseline_content(db)
    result["note"] = (
        f"{result.get('note', '')} "
        f"Contenido taller: +{content['sheets_created']} fichas, +{content['items_created']} ítems."
    ).strip()
    return VehicleTreeImportOut(**result)


@router.post("/vehicles/seed-content")
def seed_content(db: Session = Depends(get_db)):
    """Rellena fichas y categorías vacías con plantillas orientativas."""
    from app.content_seed import seed_baseline_content

    return seed_baseline_content(db)


@router.post("/brands/import", response_model=BrandImportOut)
def import_brands(payload: BrandImportIn, db: Session = Depends(get_db)):
    catalog = {name.casefold(): name for name in load_brand_catalog()}
    existing = {b.name.casefold(): b.name for b in db.query(Brand).all()}
    created: list[str] = []
    skipped: list[str] = []

    for raw in payload.names:
        name = raw.strip()
        if not name:
            continue
        key = name.casefold()
        canonical = catalog.get(key, name)
        if key in existing:
            skipped.append(existing[key])
            continue
        brand = Brand(name=canonical)
        db.add(brand)
        existing[key] = canonical
        created.append(canonical)

    db.commit()
    return BrandImportOut(created=sorted(created, key=str.casefold), skipped=sorted(set(skipped), key=str.casefold))


@router.get("/brands", response_model=list[BrandOut])
def list_brands(db: Session = Depends(get_db)):
    return db.query(Brand).order_by(Brand.name).all()


@router.post("/brands", response_model=BrandOut, status_code=201)
def create_brand(payload: BrandCreate, db: Session = Depends(get_db)):
    brand = Brand(name=payload.name.strip())
    db.add(brand)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "La marca ya existe") from None
    db.refresh(brand)
    return brand


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


@router.post("/brands/{brand_id}/models", response_model=CarModelOut, status_code=201)
def create_model(brand_id: int, payload: CarModelCreate, db: Session = Depends(get_db)):
    brand = db.get(Brand, brand_id)
    if not brand:
        raise HTTPException(404, "Marca no encontrada")
    model = CarModel(brand_id=brand_id, name=payload.name.strip())
    db.add(model)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Ese modelo ya existe en la marca") from None
    db.refresh(model)
    return model


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


@router.post("/models/{model_id}/years", response_model=ModelYearOut, status_code=201)
def create_year(model_id: int, payload: ModelYearCreate, db: Session = Depends(get_db)):
    model = db.get(CarModel, model_id)
    if not model:
        raise HTTPException(404, "Modelo no encontrado")
    year = ModelYear(model_id=model_id, year=payload.year)
    db.add(year)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Ese año ya existe en el modelo") from None
    db.refresh(year)
    return year


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


@router.post("/years/{year_id}/engines", response_model=EngineOut, status_code=201)
def create_engine(year_id: int, payload: EngineCreate, db: Session = Depends(get_db)):
    year = db.get(ModelYear, year_id)
    if not year:
        raise HTTPException(404, "Año no encontrado")
    engine = Engine(model_year_id=year_id, **payload.model_dump())
    engine.name = engine.name.strip()
    db.add(engine)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Ese motor ya existe en el año") from None
    db.refresh(engine)
    return engine


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


@router.patch("/engines/{engine_id}", response_model=EngineOut)
def update_engine(engine_id: int, payload: EngineUpdate, db: Session = Depends(get_db)):
    engine = db.get(Engine, engine_id)
    if not engine:
        raise HTTPException(404, "Motor no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "name" in data and data["name"] is not None:
        data["name"] = data["name"].strip()
    for field, value in data.items():
        setattr(engine, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Ese nombre de motor ya existe en el año") from None
    db.refresh(engine)
    return engine


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
