from fastapi import APIRouter, Depends, Query, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from typing import Any, Optional

from app.database import get_db
from app.models.venue import Venue
from app.models.review import Review
from app.models.user import User
from app.models.review_like import ReviewLike
from app.schemas.review import ReviewListResponse, ReviewItem, ReviewCreate
from app.utils.dependency import get_current_user, get_current_user_optional

router = APIRouter(prefix="/venue", tags=["Review"])

def to_abs(base: str, u: Optional[str]) -> Optional[str]:
    if not u:
        return None
    s = str(u).strip().strip('"').strip()
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
    # 로그인은 선택: 있으면 내 좋아요 여부 계산, 없으면 False
    current_user = Depends(get_current_user_optional),
):
    # 공연장 존재 확인
    if not db.query(Venue.id).filter(Venue.id == venue_id).first():
        raise HTTPException(status_code=404, detail="Venue not found")

    base = str(request.base_url)
    uid = getattr(current_user, "id", None) if current_user is not None else None

    # 좋아요 수 집계 서브쿼리
    sq_count = (
        db.query(
            ReviewLike.review_id.label("rid"),
            func.count(ReviewLike.id).label("like_count"),
        )
        .group_by(ReviewLike.review_id)
        .subquery()
    )

    # 내가 좋아요한 리뷰 서브쿼리 (로그인 시에만)
    sq_mine = (
        db.query(ReviewLike.review_id.label("rid"))
        .filter(ReviewLike.user_id == uid)
        .subquery()
        if uid
        else None
    )

    # 본문 + 작성자 + like_count + is_liked
    q = (
        db.query(
            Review,
            User.nickname.label("u_nickname"),
            User.profile_url.label("u_profile"),
            func.coalesce(sq_count.c.like_count, 0).label("like_count"),
            (
                case((sq_mine.c.rid.isnot(None), True), else_=False)
                if sq_mine is not None
                else func.false()
            ).label("is_liked"),
        )
        .select_from(Review)
        .outerjoin(User, User.id == Review.user_id)
        .outerjoin(sq_count, sq_count.c.rid == Review.id)
        .filter(Review.venue_id == venue_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
    )
    if sq_mine is not None:
        q = q.outerjoin(sq_mine, sq_mine.c.rid == Review.id)

    total = q.count()
    rows = q.offset((page - 1) * size).limit(size).all()

    items: list[ReviewItem] = []
    for rev, u_nickname, u_profile, like_count, is_liked in rows:
        items.append(
            ReviewItem(
                id=rev.id,
                author=u_nickname or "익명",
                content=rev.content,
                created_at=rev.created_at.isoformat() if rev.created_at else "",
                profile_url=to_abs(base, u_profile),
                like_count=int(like_count or 0),
                is_liked=bool(is_liked),
            )
        )

    return ReviewListResponse(total=total, items=items)

@router.post("/{venue_id}/review", response_model=ReviewItem, status_code=status.HTTP_201_CREATED)
def create_venue_review(
    venue_id: int,
    payload: ReviewCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user),  # 로그인 필수
):
    if not db.query(Venue.id).filter(Venue.id == venue_id).first():
        raise HTTPException(status_code=404, detail="Venue not found")

    # 작성자/아바타
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

    # 새 리뷰는 좋아요 0, is_liked=False로 반환
    return ReviewItem(
        id=rev.id,
        author=author,
        content=rev.content,
        created_at=rev.created_at.isoformat() if rev.created_at else "",
        profile_url=profile_url,
        like_count=0,
        is_liked=False,
    )
