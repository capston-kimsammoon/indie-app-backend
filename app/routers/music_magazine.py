from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.database import get_db
from app.crud.music_magazine import (
    get_magazines,
    get_magazine_by_id,
    get_magazine_blocks,
    hydrate_list_item_fields,
)
from app.schemas.music_magazine import (
    MusicMagazineListItem,
    MusicMagazineDetailResponse,
    MusicMagazineBlockOut,
)

router = APIRouter()

@router.get("/", response_model=List[MusicMagazineListItem])
def list_music_magazines(
    limit: Optional[int] = Query(None, ge=1, le=50),
    page: Optional[int] = Query(None, ge=1),
    size: Optional[int] = Query(None, ge=1, le=100),
    db: Session = Depends(get_db),
):
    magazines = get_magazines(db, limit=limit, page=page, size=size)
    items = hydrate_list_item_fields(db, magazines)
    return items

@router.get("/{magazine_id}", response_model=MusicMagazineDetailResponse)
def get_music_magazine_detail(
    magazine_id: int,
    db: Session = Depends(get_db),
):
    m = get_magazine_by_id(db, magazine_id)
    if not m:
        raise HTTPException(status_code=404, detail="MusicMagazine not found")

    blocks = get_magazine_blocks(db, m.id)

    # cover image
    first_image_url = None
    for b in blocks:
        if b.type == "image" and b.image_url:
            first_image_url = b.image_url
            break

    # 스키마 호환: display_order -> order 로 매핑
    blocks_out: List[MusicMagazineBlockOut] = [
        MusicMagazineBlockOut(
            id=b.id,
            order=b.display_order,
            type=b.type,
            semititle=b.semititle,
            text=b.text,
            image_url=b.image_url,
            artist_id=b.artist_id,
        )
        for b in blocks
    ]

    return {
        "id": m.id,
        "slug": None,
        "title": m.title,
        "author": None,
        "cover_image_url": first_image_url,
        "created_at": m.created_at,
        "blocks": blocks_out,
        "content": None,  # MusicMagazine에는 별도 content 컬럼 없음
    }
