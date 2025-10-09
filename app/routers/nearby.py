# app/routers/nearby.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
import datetime, pytz
from dateutil import parser

# 의존성
from app.database import get_db

# crud
from app.crud import nearby as nearby_crud

# schemas
from app.schemas import nearby as nearby_schema

router = APIRouter(prefix="/nearby", tags=["Nearby"])


# -------------------------------
# 반경 내 공연장 조회
# -------------------------------
@router.get("/venue", response_model=List[nearby_schema.NearbyVenueResponse])
def get_nearby_venues(
    lat: float = Query(..., description="사용자 위도"),
    lng: float = Query(..., description="사용자 경도"),
    radius: float = Query(3.0, description="검색 반경 (km)"),
    db: Session = Depends(get_db)
):
    venues = nearby_crud.get_nearby_venues(db, lat, lng, radius)
    return venues

# -------------------------------
# 지도 영역 내 공연장들의 예정 공연 조회
# -------------------------------
@router.post("/performance", response_model=List[nearby_schema.NearbyPerformanceResponse])
def get_performances_in_bounds(
    request: nearby_schema.PerformanceBoundsRequest,
    db: Session = Depends(get_db)
):
    return nearby_crud.get_performances_in_bounds(db, request)


# -------------------------------
# 특정 공연장의 예정 공연 조회
# -------------------------------
@router.get("/venue/{venue_id}/performance", response_model=List[nearby_schema.VenuePerformanceItem])
def get_venue_performances(
    venue_id: int,
    after: str = Query(None),
    db: Session = Depends(get_db)
):
    kst = pytz.timezone('Asia/Seoul')
    if after:
        try:
            after_dt_utc = parser.isoparse(after)       # ISO 문자열 파싱
            after_time = after_dt_utc.astimezone(kst)   # KST 변환
        except Exception:
            after_time = datetime.datetime.now(kst)
    else:
        after_time = datetime.datetime.now(kst)

    return nearby_crud.get_performances_by_venue(db, venue_id, after_time)


# 현재 위치 기준 지도 리센터
@router.post("/recenter")
def recenter_map(request: nearby_schema.RecenterRequest):
    # 실제 서버 상태 업데이트는 없음 (프론트에서 지도 중심 이동)
    return {"message": "지도 중심 이동 성공"}
