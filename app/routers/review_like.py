from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from app.database import get_db
from app.utils.dependency import get_current_user
from app.models.review import Review
from app.models.review_like import ReviewLike
from app.schemas.review_like import ReviewLikeToggleResponse  # fields: review_id, like_count, liked

router = APIRouter(prefix="/review", tags=["ReviewLike"])

def _ensure_review_exists(db: Session, review_id: int) -> None:
    exists = db.query(Review.id).filter(Review.id == review_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Review not found")

def _get_user_id(current_user) -> int:
    uid = getattr(current_user, "id", None) or (
        current_user.get("id") if isinstance(current_user, dict) else None
    )
    if not uid:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return uid

def _count_likes(db: Session, review_id: int) -> int:
    return int(
        db.query(func.count(ReviewLike.id))
        .filter(ReviewLike.review_id == review_id)
        .scalar() or 0
    )

@router.post("/{review_id}/like", response_model=ReviewLikeToggleResponse, status_code=status.HTTP_200_OK)
def like_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    좋아요 ON (멱등성 보장)
    - 이미 누른 상태여도 200 + 현재 like_count/liked 반환
    """
    _ensure_review_exists(db, review_id)
    user_id = _get_user_id(current_user)

    try:
        db.add(ReviewLike(review_id=review_id, user_id=user_id))
        db.commit()
    except IntegrityError:
        # 이미 존재해도 OK (unique (review_id, user_id) 가정)
        db.rollback()

    like_count = _count_likes(db, review_id)
    return ReviewLikeToggleResponse(review_id=review_id, like_count=like_count, liked=True)

@router.delete("/{review_id}/like", response_model=ReviewLikeToggleResponse, status_code=status.HTTP_200_OK)
def unlike_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    좋아요 OFF (멱등성 보장)
    - 이미 안 눌린 상태여도 200 + 현재 like_count/liked=False 반환
    """
    _ensure_review_exists(db, review_id)
    user_id = _get_user_id(current_user)

    row = (
        db.query(ReviewLike)
        .filter(ReviewLike.review_id == review_id, ReviewLike.user_id == user_id)
        .first()
    )
    if row:
        db.delete(row)
        db.commit()

    like_count = _count_likes(db, review_id)
    return ReviewLikeToggleResponse(review_id=review_id, like_count=like_count, liked=False)
