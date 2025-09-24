# app/crud/magazine.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc

from app.models.magazine import Magazine
from app.models.magazine_block import MagazineBlock

def _first_image_url(db: Session, magazine_id: int) -> Optional[str]:
    b = (
        db.query(MagazineBlock)
        .filter(MagazineBlock.magazine_id == magazine_id, MagazineBlock.type == "image")
        .order_by(asc(MagazineBlock.order))
        .first()
    )
    return b.image_url if b else None

def _first_text_excerpt(db: Session, magazine_id: int, max_len: int = 140) -> Optional[str]:
    b = (
        db.query(MagazineBlock)
        .filter(MagazineBlock.magazine_id == magazine_id, MagazineBlock.type == "text")
        .order_by(asc(MagazineBlock.order))
        .first()
    )
    if not b or not b.text:
        return None
    text = b.text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "…"

def get_magazines(db: Session, limit: Optional[int], page: Optional[int], size: Optional[int]) -> List[Magazine]:
    q = db.query(Magazine).order_by(desc(Magazine.created_at))
    if limit:
        return q.limit(limit).all()
    if page and size:
        return q.offset((page - 1) * size).limit(size).all()
    return q.all()

def get_magazine_by_id(db: Session, magazine_id: int) -> Optional[Magazine]:
    return db.query(Magazine).filter(Magazine.id == magazine_id).first()

def get_magazine_blocks(db: Session, magazine_id: int) -> List[MagazineBlock]:
    return (
        db.query(MagazineBlock)
        .filter(MagazineBlock.magazine_id == magazine_id)
        .order_by(asc(MagazineBlock.order))
        .all()
    )

def hydrate_list_item_fields(db: Session, magazines: List[Magazine]) -> List[dict]:
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
            }
        )
    return items
