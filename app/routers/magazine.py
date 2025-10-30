# app/routers/magazine.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.crud.magazine import (
    get_magazines,
    get_magazine_by_id,
    get_magazine_blocks,
    hydrate_list_item_fields,
)
from app.schemas.magazine import (
    MagazineListItem,
    MagazineDetailResponse,
)

router = APIRouter()

@router.get("/magazine", response_model=List[MagazineListItem])
def list_magazines(
    limit: Optional[int] = Query(None, ge=1, le=50),
    page: Optional[int] = Query(None, ge=1),
    size: Optional[int] = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
):
    try:
        magazines = get_magazines(db, limit=limit, page=page, size=size)
        items = hydrate_list_item_fields(db, magazines)
        return items
    except Exception as e:
        import traceback
        traceback.print_exc() 
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/magazine/{magazine_id}", response_model=MagazineDetailResponse)
def get_magazine_detail(
    magazine_id: int,
    db: Session = Depends(get_db),
):
    m = get_magazine_by_id(db, magazine_id)
    if not m:
        raise HTTPException(status_code=404, detail="Magazine not found")

    blocks = get_magazine_blocks(db, m.id)

    first_image_url = None
    for b in blocks:
        if b.type == "image" and b.image_url:
            first_image_url = b.image_url
            break

    return {
        "id": m.id,
        "slug": None,
        "title": m.title,
        "author": None,
        "cover_image_url": first_image_url,
        "created_at": m.created_at,
        "blocks": blocks,
        "content": m.content if m.content not in [None, '', 0] else None,  # ✅ 빈 값 체크
    }

