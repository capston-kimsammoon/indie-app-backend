from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.models.music_magazine import MusicMagazine
from app.models.music_magazine_block import MusicMagazineBlock

def _first_image_url(db: Session, magazine_id: int) -> Optional[str]:
    b = (
        db.query(MusicMagazineBlock)
        .filter(
            MusicMagazineBlock.magazine_id == magazine_id,
            MusicMagazineBlock.type == "image",
        )
        .order_by(asc(MusicMagazineBlock.display_order))
        .first()
    )
    return b.image_url if b else None

def _first_text_excerpt(db: Session, magazine_id: int, max_len: int = 140) -> Optional[str]:
    """
    ✅ type='text'이면서 text 필드가 NULL이 아닌 블록 중
    display_order가 가장 작은 것의 text를 반환
    """
    b = (
        db.query(MusicMagazineBlock)
        .filter(
            MusicMagazineBlock.magazine_id == magazine_id,
            MusicMagazineBlock.type == "text",
            MusicMagazineBlock.text.isnot(None),  # ✅ text가 NULL이 아닌 것만
            MusicMagazineBlock.text != "",         # ✅ 빈 문자열도 제외
        )
        .order_by(asc(MusicMagazineBlock.display_order))
        .first()
    )
    if not b or not b.text:
        return None
    text = b.text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"

def get_magazines(db: Session, limit: Optional[int], page: Optional[int], size: Optional[int]) -> List[MusicMagazine]:
    q = db.query(MusicMagazine).order_by(desc(MusicMagazine.created_at))
    if limit:
        return q.limit(limit).all()
    if page and size:
        return q.offset((page - 1) * size).limit(size).all()
    return q.all()

def get_magazine_by_id(db: Session, magazine_id: int) -> Optional[MusicMagazine]:
    return db.query(MusicMagazine).filter(MusicMagazine.id == magazine_id).first()

def get_magazine_blocks(db: Session, magazine_id: int) -> List[MusicMagazineBlock]:
    return (
        db.query(MusicMagazineBlock)
        .filter(MusicMagazineBlock.magazine_id == magazine_id)
        .order_by(asc(MusicMagazineBlock.display_order))
        .all()
    )

def hydrate_list_item_fields(db: Session, magazines: List[MusicMagazine]) -> List[dict]:
    items: List[dict] = []
    for m in magazines:
        items.append(
            {
                "id": m.id,
                "slug": None,
                "title": m.title,
                "excerpt": _first_text_excerpt(db, m.id),
                "cover_image_url": _first_image_url(db, m.id),
                "author": None,
                "created_at": m.created_at,
                "content": None,
            }
        )
    return items
