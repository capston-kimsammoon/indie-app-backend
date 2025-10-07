# app/routers/review.py
from fastapi import Body
from typing import List, Optional
from uuid import uuid4
import os
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form, status, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.database import get_db
from app.models.review import Review
from app.models.review_like import ReviewLike
from app.models.review_image import ReviewImage
from app.models.venue import Venue
from app.models.user import User
from app.utils.dependency import get_current_user, get_current_user_optional  # 로그인 사용자 (없으면 401)
from app.utils.gcs import upload_to_gcs, delete_from_gcs
from app.schemas.review import ReviewOut, ReviewListOut,  UserBrief, ReviewImageOut, ReviewCreateIn
from datetime import datetime, timedelta, timezone

router = APIRouter(prefix="/venue", tags=["Review"])
GCS_BUCKET_URL = f"https://storage.googleapis.com/{os.getenv('GCS_BUCKET_NAME')}/"

KST = timezone(timedelta(hours=9))

def to_kst_iso(dt: Optional[datetime]) -> Optional[str]:
    """naive는 UTC로 간주해서 tzinfo 채운 뒤 KST로 변환해 isoformat 반환"""
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST).isoformat()

# ------------ 유틸 ------------
def _abs_url(base: str, path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    s = str(path).strip().strip('"')
    if not s:
        return None
    if s.startswith(("http://", "https://", "data:")):
        return s
    if s.startswith("/"):
        return f"{base.rstrip('/')}{s}"
    return f"{base.rstrip('/')}/{s}"

def _serialize_review(
    request: Request,
    r: Review,
    like_count_map: dict[int, int],
    liked_ids: set[int],
    include_venue: bool = False,
    current_user: Optional[User] = None,
) -> dict:
    base = str(request.base_url)

    def _venue_logo_path(v):
        for key in ("logo_url", "logo", "image_url", "logoPath", "logo_path"):
            val = getattr(v, key, None)
            if val:
                return val
        return None

    data = {
        "id": r.id,
        "content": r.content,
        "created_at": r.created_at.isoformat() if r.created_at else None,
        "user": {
            "id": r.user.id if r.user else None,
            "nickname": (r.user.nickname if r.user else None) or "익명",
            "profile_url": _abs_url(base, getattr(r.user, "profile_url", None)),
        },
        "images": [{"image_url": _abs_url(base, img.image_url)} for img in (r.images or [])],
        "like_count": like_count_map.get(r.id, 0),
        "liked_by_me": r.id in liked_ids,
        "is_mine": r.user_id == getattr(current_user, "id", None)
    }

    if include_venue and r.venue:
        data["venue"] = {
            "id": r.venue.id,
            "name": getattr(r.venue, "name", None),
            "logo_url": _abs_url(base, _venue_logo_path(r.venue)),
        }

    return data


def _review_like_counts(db: Session, review_ids: List[int]) -> dict[int, int]:
    if not review_ids:
        return {}
    rows = (
        db.query(ReviewLike.review_id, func.count(ReviewLike.id))
        .filter(ReviewLike.review_id.in_(review_ids))
        .group_by(ReviewLike.review_id)
        .all()
    )
    return {rid: cnt for rid, cnt in rows}

def _my_liked_set(db: Session, review_ids: List[int], user_id: Optional[int]) -> set[int]:
    if not review_ids or not user_id:
        return set()
    rows = (
        db.query(ReviewLike.review_id)
        .filter(ReviewLike.user_id == user_id, ReviewLike.review_id.in_(review_ids))
        .all()
    )
    return {rid for (rid,) in rows}

# ------------ 전체 리뷰 목록 ------------
@router.get("/reviews/all", response_model=ReviewListOut)
def list_all_reviews(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    전체 리뷰 목록 (로그인 불필요)
    - like_count: 총 좋아요 수
    - liked_by_me: 로그인 시 내가 누른 여부
    """
    q = db.query(Review).options(
        joinedload(Review.user),
        joinedload(Review.images),
        joinedload(Review.venue),
    )

    # 정렬
    if order == "asc":
        q = q.order_by(Review.created_at.asc(), Review.id.asc())
    else:
        q = q.order_by(Review.created_at.desc(), Review.id.desc())

    # 전체 개수
    total = db.query(func.count(Review.id)).scalar() or 0

    # 페이지 아이템
    rows: List[Review] = q.offset((page - 1) * size).limit(size).all()
    ids = [r.id for r in rows]

    like_count_map = _review_like_counts(db, ids)
    liked_ids = _my_liked_set(db, ids, getattr(current_user, "id", None))

    items = [_serialize_review(request, r, like_count_map, liked_ids, include_venue=True, current_user=current_user) for r in rows]
    return {"items": items, "total": total, "page": page, "size": size}

# ------------ 내가 쓴 리뷰 ------------
@router.get("/my/review", response_model=ReviewListOut)
def list_my_reviews(
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    order: str = Query("desc"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    로그인한 사용자가 작성한 리뷰 목록 조회
    venue 정보도 포함
    """
    q = (
        db.query(Review)
        .options(joinedload(Review.images), joinedload(Review.user), joinedload(Review.venue))  # venue join
        .filter(Review.user_id == current_user.id)
    )

    # 정렬
    q = q.order_by(Review.created_at.desc() if order == "desc" else Review.created_at.asc())

    total = q.count()
    rows = q.offset((page - 1) * size).limit(size).all()

    ids = [r.id for r in rows]
    like_count_map = _review_like_counts(db, ids)
    liked_ids = _my_liked_set(db, ids, current_user.id)

    # ✅ venue 포함하도록 include_venue=True
    items = [_serialize_review(request, r, like_count_map, liked_ids, include_venue=True) for r in rows]

    return ReviewListOut(items=items, total=total, page=page, size=size)

# ------------ 공연장 리뷰 ------------
@router.get("/{venue_id}/review", response_model=ReviewListOut)
def list_venue_reviews(
    venue_id: int,
    request: Request,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),  # ✅ 변경
    # Depends(lambda: None),  # 로그인 없어도 OK
):
    # ✅ 존재 확인(안전판)
    venue = db.query(Venue.id).filter(Venue.id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    q = (
        db.query(Review)
        .options(joinedload(Review.user), joinedload(Review.images))
        .filter(Review.venue_id == venue_id)
        .order_by(Review.created_at.desc(), Review.id.desc())  # ✅ 최신순
    )

    # ✅ total 안전 계산 (버전 호환)
    total = db.query(func.count(Review.id)).filter(Review.venue_id == venue_id).scalar() or 0

    items: List[Review] = q.offset((page - 1) * size).limit(size).all()
    ids = [r.id for r in items]
    like_count_map = _review_like_counts(db, ids)
    liked_ids = _my_liked_set(db, ids, getattr(current_user, "id", None))

    data = [_serialize_review(request, r, like_count_map, liked_ids) for r in items]
    return {"items": data, "total": total, "page": page, "size": size}

# ------------ 미리보기(상세 하단: 최대 n개) ------------
@router.get("/{venue_id}/review/preview", response_model=ReviewListOut, status_code=status.HTTP_201_CREATED)
def review_preview(
    venue_id: int,
    request: Request,
    limit: int = Query(2, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    q = (
        db.query(Review)
        .options(joinedload(Review.user), joinedload(Review.images))
        .filter(Review.venue_id == venue_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
        .limit(limit)
    )
    items = q.all()
    ids = [r.id for r in items]
    like_count_map = _review_like_counts(db, ids)
    liked_ids = _my_liked_set(db, ids, getattr(current_user, "id", None))
    data = [_serialize_review(request, r, like_count_map, liked_ids) for r in items]
    return {"items": data, "total": len(data), "page": 1, "size": len(data)}

# ------------ 작성 (로그인 필요) ------------
@router.post("/{venue_id}/review/write", response_model=ReviewOut, status_code=201)
async def create_review(
    venue_id: int,
    request: Request,
    content: str = Form(..., min_length=1, max_length=300),
    images: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 공연장 존재 확인
    venue_exists = db.query(Venue.id).filter(Venue.id == venue_id).first()
    if not venue_exists:
        raise HTTPException(status_code=404, detail="Venue not found")

    # 리뷰 저장
    review = Review(user_id=current_user.id, venue_id=venue_id, content=content.strip())
    db.add(review)
    db.flush()

    # 이미지 저장
    ALLOWED = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
    MAX_FILES = 6

    saved_rows: list[ReviewImage] = []
    for up in (images or [])[:MAX_FILES]:
        ext = os.path.splitext(up.filename)[-1].lower()
        if ext not in ALLOWED:
            continue  # 허용되지 않는 확장자 제외

        uid = getattr(current_user, "kakao_id", None) or getattr(current_user, "social_id", None) or current_user.id
        folder = f"review/{uid}/{venue_id}"   # 예: review/123456/42/xxxx.jpg
        url = upload_to_gcs(up, folder=folder)
        saved_rows.append(ReviewImage(review_id=review.id, image_url=url))

    if saved_rows:
        db.add_all(saved_rows)

    db.commit()
    db.refresh(review)

    images_out = [ReviewImageOut(image_url=_abs_url(str(request.base_url), im.image_url)) for im in (review.images or [])]

    return ReviewOut(
        id=review.id,
        content=review.content,
        created_at=review.created_at,
        user=UserBrief(
            id=current_user.id,
            nickname=current_user.nickname or "익명",
            profile_url=_abs_url(str(request.base_url), current_user.profile_url),
        ),
        images=images_out,
        like_count=0,
        liked_by_me=False,
    )


# ------------ 삭제 (작성자만) ------------
@router.delete("/review/{review_id}", tags=["Review"])
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = (
        db.query(Review)
        .options(joinedload(Review.user), joinedload(Review.images))
        .filter(Review.id == review_id)
        .first()
    )
    if not r:
        raise HTTPException(status_code=404, detail="Review not found")
    if r.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the author")

    # 이미지 삭제
    if r.images:
        for img in r.images:
            delete_from_gcs(img.image_url)

    db.delete(r)
    db.commit()
    return {"ok": True}


# ------------ 좋아요 토글 (로그인 필요) ------------
@router.post("/review/{review_id}/like", tags=["Review"])
def like_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 중복 방지: UniqueConstraint(review_id, user_id)
    exists_like = (
        db.query(ReviewLike)
        .filter(ReviewLike.review_id == review_id, ReviewLike.user_id == current_user.id)
        .first()
    )
    if not exists_like:
        db.add(ReviewLike(review_id=review_id, user_id=current_user.id))
        db.commit()

    # 최신 like_count/liked_by_me 반환
    cnt = db.query(func.count(ReviewLike.id)).filter(ReviewLike.review_id == review_id).scalar()
    return {"like_count": cnt, "liked_by_me": True}

@router.delete("/review/{review_id}/like", tags=["Review"])
def unlike_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rl = (
        db.query(ReviewLike)
        .filter(ReviewLike.review_id == review_id, ReviewLike.user_id == current_user.id)
        .first()
    )
    if rl:
        db.delete(rl)
        db.commit()
    cnt = db.query(func.count(ReviewLike.id)).filter(ReviewLike.review_id == review_id).scalar()
    return {"like_count": cnt, "liked_by_me": False}
