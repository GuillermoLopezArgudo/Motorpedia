from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category, Engine, WorkshopItem
from app.schemas import (
    CategoryOut,
    CategorySummaryOut,
    WorkshopItemCreate,
    WorkshopItemOut,
    WorkshopItemUpdate,
)

router = APIRouter(prefix="/api", tags=["workshop"])


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.sort_order, Category.name).all()


@router.get("/engines/{engine_id}/workshop", response_model=list[CategorySummaryOut])
def workshop_overview(engine_id: int, db: Session = Depends(get_db)):
    engine = db.get(Engine, engine_id)
    if not engine:
        raise HTTPException(404, "Motor no encontrado")

    rows = (
        db.query(
            Category.id,
            Category.slug,
            Category.name,
            Category.description,
            Category.sort_order,
            func.count(WorkshopItem.id),
        )
        .outerjoin(
            WorkshopItem,
            (WorkshopItem.category_id == Category.id) & (WorkshopItem.engine_id == engine_id),
        )
        .group_by(
            Category.id,
            Category.slug,
            Category.name,
            Category.description,
            Category.sort_order,
        )
        .order_by(Category.sort_order, Category.name)
        .all()
    )
    return [
        CategorySummaryOut(
            id=r[0],
            slug=r[1],
            name=r[2],
            description=r[3],
            sort_order=r[4],
            item_count=int(r[5] or 0),
        )
        for r in rows
    ]


@router.get(
    "/engines/{engine_id}/categories/{slug}/items",
    response_model=list[WorkshopItemOut],
)
def list_category_items(engine_id: int, slug: str, db: Session = Depends(get_db)):
    engine = db.get(Engine, engine_id)
    if not engine:
        raise HTTPException(404, "Motor no encontrado")
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(404, "Categoría no encontrada")

    return (
        db.query(WorkshopItem)
        .filter(
            WorkshopItem.engine_id == engine_id,
            WorkshopItem.category_id == category.id,
        )
        .order_by(WorkshopItem.is_recommended.desc(), WorkshopItem.title)
        .all()
    )


@router.post(
    "/engines/{engine_id}/categories/{slug}/items",
    response_model=WorkshopItemOut,
    status_code=201,
)
def create_item(engine_id: int, slug: str, payload: WorkshopItemCreate, db: Session = Depends(get_db)):
    engine = db.get(Engine, engine_id)
    if not engine:
        raise HTTPException(404, "Motor no encontrado")
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(404, "Categoría no encontrada")

    item = WorkshopItem(
        engine_id=engine_id,
        category_id=category.id,
        **payload.model_dump(),
    )
    item.title = item.title.strip()
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.patch("/workshop-items/{item_id}", response_model=WorkshopItemOut)
def update_item(item_id: int, payload: WorkshopItemUpdate, db: Session = Depends(get_db)):
    item = db.get(WorkshopItem, item_id)
    if not item:
        raise HTTPException(404, "Ítem no encontrado")
    data = payload.model_dump(exclude_unset=True)
    if "title" in data and data["title"] is not None:
        data["title"] = data["title"].strip()
    for field, value in data.items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/workshop-items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.get(WorkshopItem, item_id)
    if not item:
        raise HTTPException(404, "Ítem no encontrado")
    db.delete(item)
    db.commit()
    return None
