from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bootstrap import bootstrap_catalog
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.routers import vehicles, workshop
from app.schema_sync import ensure_columns


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_columns(engine)
    db = SessionLocal()
    try:
        bootstrap_catalog(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Motorpedia API", version="0.2.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(vehicles.router)
app.include_router(workshop.router)


@app.get("/")
def root():
    return {
        "name": "Motorpedia",
        "tagline": "Autodata libre · consulta marca → modelo → año → motor",
        "docs": "/docs",
        "version": "0.2.0",
    }


@app.get("/api/status")
def status():
    from sqlalchemy import func

    from app.models import Brand, CarModel, Engine, TechSheet, WorkshopItem

    db = SessionLocal()
    try:
        return {
            "ready": True,
            "brands": db.query(func.count(Brand.id)).scalar() or 0,
            "models": db.query(func.count(CarModel.id)).scalar() or 0,
            "engines": db.query(func.count(Engine.id)).scalar() or 0,
            "sheets": db.query(func.count(TechSheet.id)).scalar() or 0,
            "verified_sheets": db.query(func.count(TechSheet.id))
            .filter(TechSheet.is_verified.is_(True))
            .scalar()
            or 0,
            "items": db.query(func.count(WorkshopItem.id)).scalar() or 0,
        }
    finally:
        db.close()
