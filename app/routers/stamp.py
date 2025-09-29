from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timedelta, timezone, date
from calendar import monthrange

from app import models
from app.database import get_db
from app.utils.dependency import get_current_user

from app.schemas.stamp import (
    AvailableStampResponse,
    StampResponse,
    StampCollectRequest,
    PerformanceResponse,
    VenueResponse,
)

router = APIRouter(prefix="/stamps", tags=["Stamps"])

# ------------------------------
# 사용 가능한 스탬프
# ------------------------------
@router.get("/available", response_model=List[AvailableStampResponse])
def get_available_stamps(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    days: int = Query(3, ge=1, le=30),
):
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=days - 1)

    already_stamped_ids = {
        p_id
        for (p_id,) in db.query(models.Stamp.performance_id)
        .filter(models.Stamp.user_id == current_user.id)
        .all()
    }

    performances = (
        db.query(models.Performance)
        .options(joinedload(models.Performance.venue))
        .filter(
            models.Performance.date >= start_date,
            models.Performance.date <= today,
        )
        .order_by(models.Performance.date.desc())
        .all()
    )

    res: List[AvailableStampResponse] = []
    for p in performances:
        res.append(
            AvailableStampResponse(
                id=p.id,
                performance_id=p.id,
                posterUrl=p.image_url,
                venueImageUrl=(p.venue.image_url if p.venue else None),
                venue=(p.venue.name if p.venue else "공연장"),
                title=p.title,
                date=str(p.date),
                is_collected=(p.id in already_stamped_ids),
            )
        )
    return res

# ------------------------------
# 수집한 스탬프 (월 범위)
# ------------------------------
@router.get("/collected", response_model=List[StampResponse])
def get_collected_stamps(
    startMonth: Optional[int] = Query(None, ge=1, le=12),
    endMonth: Optional[int] = Query(None, ge=1, le=12),
    startYear: Optional[int] = Query(None, ge=1970, le=2100),
    endYear: Optional[int] = Query(None, ge=1970, le=2100),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    q = (
        db.query(models.Stamp)
        .options(joinedload(models.Stamp.performance).joinedload(models.Performance.venue))
        .filter(models.Stamp.user_id == current_user.id)
    )

    if startMonth and endMonth and startYear and endYear:
        sY, sM, eY, eM = startYear, startMonth, endYear, endMonth
        # (연,월) 역순이면 스왑
        if (sY, sM) > (eY, eM):
            sY, eY = eY, sY
            sM, eM = eM, sM
        start_date = date(sY, sM, 1)
        end_date = date(eY, eM, monthrange(eY, eM)[1])
        q = q.join(models.Performance).filter(
            models.Performance.date.between(start_date, end_date)
        )

    elif startMonth and endMonth:
        year = datetime.now(timezone.utc).year
        start_date = date(year, startMonth, 1)
        end_date = date(year, endMonth, monthrange(year, endMonth)[1])
        q = q.join(models.Performance).filter(
            models.Performance.date.between(start_date, end_date)
        )

    stamps = q.order_by(models.Stamp.created_at.desc()).all()

    out: List[StampResponse] = []
    for s in stamps:
        perf_resp = None
        if s.performance:
            v = s.performance.venue
            perf_resp = PerformanceResponse(
                id=s.performance.id,
                title=s.performance.title,
                date=str(s.performance.date),
                image_url=s.performance.image_url,
                venue=VenueResponse(
                    id=v.id, name=v.name, image_url=v.image_url
                ) if v else None,
            )
        out.append(
            StampResponse(
                id=s.id,
                user_id=s.user_id,
                performance_id=s.performance_id,
                created_at=s.created_at,
                performance=perf_resp,
            )
        )
    return out

# ------------------------------
# 스탬프 수집
# ------------------------------
@router.post("/collect", response_model=StampResponse)
def collect_stamp(
    req: StampCollectRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        new_stamp = models.Stamp(
            user_id=current_user.id,
            performance_id=req.stampId,
        )
        db.add(new_stamp)
        db.commit()
        db.refresh(new_stamp)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Already stamped")

    s = (
        db.query(models.Stamp)
        .options(joinedload(models.Stamp.performance).joinedload(models.Performance.venue))
        .filter(models.Stamp.id == new_stamp.id)
        .first()
    )

    perf_resp = None
    if s and s.performance:
        v = s.performance.venue
        perf_resp = PerformanceResponse(
            id=s.performance.id,
            title=s.performance.title,
            date=str(s.performance.date),
            image_url=s.performance.image_url,
            venue=VenueResponse(
                id=v.id, name=v.name, image_url=v.image_url
            ) if v else None,
        )

    return StampResponse(
        id=s.id,
        user_id=s.user_id,
        performance_id=s.performance_id,
        created_at=s.created_at,
        performance=perf_resp,
    )

# ------------------------------
# 스탬프 상세
# ------------------------------
@router.get("/{stamp_id}", response_model=StampResponse)
def get_stamp_detail(
    stamp_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    s = (
        db.query(models.Stamp)
        .options(joinedload(models.Stamp.performance).joinedload(models.Performance.venue))
        .filter(models.Stamp.id == stamp_id, models.Stamp.user_id == current_user.id)
        .first()
    )
    if not s:
        raise HTTPException(status_code=404, detail="Stamp not found")

    perf_resp = None
    if s.performance:
        v = s.performance.venue
        perf_resp = PerformanceResponse(
            id=s.performance.id,
            title=s.performance.title,
            date=str(s.performance.date),
            image_url=s.performance.image_url,
            venue=VenueResponse(
                id=v.id, name=v.name, image_url=v.image_url
            ) if v else None,
        )

    return StampResponse(
        id=s.id,
        user_id=s.user_id,
        performance_id=s.performance_id,
        created_at=s.created_at,
        performance=perf_resp,
    )
