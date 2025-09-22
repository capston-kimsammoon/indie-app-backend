# app/routers/review.py
from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import outerjoin
from typing import Any, Optional

from app.database import get_db
from app.models.venue import Venue
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewListResponse, ReviewItem, ReviewCreate
from app.utils.dependency import get_current_user

router = APIRouter(prefix="/venue", tags=["Review"])

def to_abs(base: str, u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    s = str(u).strip().strip('"').strip()  # 여분의 따옴표/공백 제거
    if not s:
        return None
    if s.startswith(("http://","https://","data:")):
        return s
    if s.startswith("/"):
        return f"{base.rstrip('/')}{s}"
    return f"{base.rstrip('/')}/{s.lstrip('/')}"

@router.get("/{venue_id}/review", response_model=ReviewListResponse)
def list_venue_reviews(
    venue_id: int,
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    # 공연장 존재 확인
    if not db.query(Venue.id).filter(Venue.id == venue_id).first():
        raise HTTPException(status_code=404, detail="Venue not found")

    # ✅ 관계객체 대신 컬럼 조인으로 직접 뽑기 (LEFT OUTER JOIN)
    base = str(request.base_url)
    q = (
        db.query(
            Review,
            User.nickname.label("u_nickname"),
            User.profile_url.label("u_profile"),
        )
        .select_from(Review)
        .outerjoin(User, User.id == Review.user_id)
        .filter(Review.venue_id == venue_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
    )

    total = q.count()
    rows = q.offset((page - 1) * size).limit(size).all()

    items: list[ReviewItem] = []
    for rev, u_nickname, u_profile in rows:
        author = u_nickname or "익명"
        profile_url = to_abs(base, u_profile)
        print("⭐⭐ : ", profile_url)
        items.append(
            ReviewItem(
                id=rev.id,
                author=author,
                content=rev.content,
                created_at=rev.created_at.isoformat() if rev.created_at else "",
                profile_url=profile_url,  # ← 컬럼에서 바로 보정한 값
            )
        )
   

    

    return ReviewListResponse(total=total, items=items)

@router.post("/{venue_id}/review", response_model=ReviewItem, status_code=status.HTTP_201_CREATED)
def create_venue_review(
    venue_id: int,
    payload: ReviewCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),
):
    if not db.query(Venue.id).filter(Venue.id == venue_id).first():
        raise HTTPException(status_code=404, detail="Venue not found")

    # current_user에서 바로 추출
    author = (
        getattr(current_user, "nickname", None)
        or (current_user.get("nickname") if isinstance(current_user, dict) else None)
        or getattr(current_user, "name", None)
        or (current_user.get("name") if isinstance(current_user, dict) else None)
        or "익명"
    )
    raw_profile = (
        getattr(current_user, "profile_url", None)
        or (current_user.get("profile_url") if isinstance(current_user, dict) else None)
    )
    profile_url = to_abs(str(request.base_url), raw_profile)

    user_id = getattr(current_user, "id", None) or (current_user.get("id") if isinstance(current_user, dict) else None)
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")

    rev = Review(venue_id=venue_id, user_id=user_id, content=payload.content.strip())
    db.add(rev)
    db.commit()
    db.refresh(rev)

    return ReviewItem(
        id=rev.id,
        author=author,
        content=rev.content,
        created_at=rev.created_at.isoformat() if rev.created_at else "",
        profile_url=profile_url,
    )
