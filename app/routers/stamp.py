# app/routers/stamp.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime, timedelta, timezone

from app import models
from app.database import get_db
from app.utils.dependency import get_current_user

# Pydantic 스키마는 직접 import해서 사용 (schemas.stamp.* 경로 쓰지 않음)
from app.schemas.stamp import (
    AvailableStampResponse,
    StampResponse,
    StampCollectRequest,
)

router = APIRouter(prefix="/stamps", tags=["Stamps"])

# 사용 가능한 스탬프 (오늘 포함 최근 N일: 기본 3일)
@router.get("/available", response_model=List[AvailableStampResponse])
def get_available_stamps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    days: int = Query(3, ge=1, le=30),
):
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=days - 1)

    # 이미 찍은 공연 ID
    already_stamped_ids = {
        p_id
        for (p_id,) in db.query(models.Stamp.performance_id)
        .filter(models.Stamp.user_id == current_user.id)
        .all()
    }

    # 공연 + 공연장 eager load
    performances = (
        db.query(models.Performance)
        .options(joinedload(models.Performance.venue))
        .filter(
            models.Performance.date >= start_date,
            models.Performance.date <= today,
        )
        .all()
    )

    return [
        AvailableStampResponse(
            id=p.id,
            performance_id=p.id,
            posterUrl=p.image_url,
            venueImageUrl=(p.venue.image_url if p.venue else None),
            venue=(p.venue.name if p.venue else "공연장"),
            title=p.title,
            date=p.date,
            is_collected=(p.id in already_stamped_ids),
        )
        for p in performances
    ]

# 수집한 스탬프 (월 범위 필터)
@router.get("/collected", response_model=List[StampResponse])
def get_collected_stamps(
    userId: Optional[int] = Query(None),
    startMonth: Optional[int] = Query(None),
    endMonth: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = (
        db.query(models.Stamp)
        .options(joinedload(models.Stamp.performance).joinedload(models.Performance.venue))
        .filter(models.Stamp.user_id == current_user.id)
    )

    if startMonth and endMonth:
        current_year = datetime.now(timezone.utc).year
        start_date = datetime(current_year, startMonth, 1).date()
        if endMonth == 12:
            end_date = datetime(current_year, 12, 31).date()
        else:
            end_date = (datetime(current_year, endMonth + 1, 1) - timedelta(days=1)).date()

        query = query.join(models.Performance).filter(
            models.Performance.date >= start_date,
            models.Performance.date <= end_date,
        )

    return [StampResponse.from_orm(stamp) for stamp in query.all()]

# 스탬프 수집
@router.post("/collect", response_model=StampResponse)
def collect_stamp(
    req: StampCollectRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    exists = (
        db.query(models.Stamp)
        .filter(
            models.Stamp.user_id == current_user.id,
            models.Stamp.performance_id == req.stampId,
        )
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Already stamped")

    new_stamp = models.Stamp(user_id=current_user.id, performance_id=req.stampId)
    db.add(new_stamp)
    db.commit()
    db.refresh(new_stamp)
    return StampResponse.from_orm(new_stamp)

# 스탬프 상세
@router.get("/{stamp_id}", response_model=StampResponse)
def get_stamp_detail(
    stamp_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    stamp = (
        db.query(models.Stamp)
        .options(joinedload(models.Stamp.performance).joinedload(models.Performance.venue))
        .filter(models.Stamp.id == stamp_id, models.Stamp.user_id == current_user.id)
        .first()
    )
    if not stamp:
        raise HTTPException(status_code=404, detail="Stamp not found")
    return StampResponse.from_orm(stamp)
