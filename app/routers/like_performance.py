from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.performance import Performance
from app.models.user import User
from app.utils.dependency import get_current_user  

router = APIRouter(tags=["Performance Likes"])

# 공연 3-1. 찜 ON
@router.post("/likes", status_code=status.HTTP_201_CREATED)
def like_performance(
    payload: dict,  # 간단하게 dict로 받음, 타입 정의해도 좋음
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.get("type") != "performance":
        raise HTTPException(status_code=400, detail="Unsupported type")
    performance_id = payload.get("refId")
    if not performance_id:
        raise HTTPException(status_code=400, detail="refId is required")

    # 공연 존재 여부 체크
    performance = db.query(Performance).filter(Performance.id == performance_id).first()
    if not performance:
        raise HTTPException(status_code=404, detail="Performance not found")

    # 이미 찜했는지 확인
    existing = db.query(UserFavoritePerformance).filter_by(user_id=user.id, performance_id=performance_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already liked")

    # 찜 추가
    like = UserFavoritePerformance(user_id=user.id, performance_id=performance_id)
    db.add(like)
    db.commit()

    return {"message": "Performance liked"}

# 공연 3-2. 찜 OFF
@router.delete("/likes/{performance_id}", status_code=status.HTTP_204_NO_CONTENT)
def unlike_performance(
    performance_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    like = db.query(UserFavoritePerformance).filter_by(user_id=user.id, performance_id=performance_id).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")

    db.delete(like)
    db.commit()
    return
