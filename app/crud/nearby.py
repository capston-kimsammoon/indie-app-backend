# app/crud/nearby.py

from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_, or_
from app.models.venue import Venue
from app.schemas.nearby import PerformanceBoundsRequest
from app.models.performance import Performance
from math import radians
import datetime, pytz

kst = pytz.timezone("Asia/Seoul")

# -------------------------------
# 반경 내 공연장 목록 조회 (오늘 공연 + 현재 시각 이후)
# -------------------------------

def get_nearby_venues(db: Session, lat: float, lng: float, radius_km: float):
    
    now = datetime.datetime.now(kst)
    today = now.date()
    current_time = now.time()

    # 근처 후보
    venues = db.query(Venue).filter(
        (Venue.latitude >= lat - 0.05) & (Venue.latitude <= lat + 0.05),
        (Venue.longitude >= lng - 0.05) & (Venue.longitude <= lng + 0.05)
    ).all()

    result = []
    for v in venues:
        performance_exists = db.query(Performance).filter(
            Performance.venue_id == v.id,
            Performance.date == today,
            Performance.time >= current_time
        ).first()

        if performance_exists:
            result.append({
                "venue_id": v.id,
                "name": v.name,
                "address": getattr(v, "address", None),
                "latitude": v.latitude,
                "longitude": v.longitude,
                "image_url": getattr(v, "image_url", None)
            })

    return result


# -------------------------------
# 지도 범위 내 공연장들의 오늘 공연 목록 조회
# -------------------------------
def get_performances_in_bounds(db: Session, req: PerformanceBoundsRequest):
    now = datetime.datetime.now(kst)
    today = now.date()
    current_time = now.time()

    performances = db.query(Performance, Venue).join(Venue).filter(
        Venue.latitude >= req.sw_lat,
        Venue.latitude <= req.ne_lat,
        Venue.longitude >= req.sw_lng,
        Venue.longitude <= req.ne_lng,
        Performance.date == today,
        Performance.time >= current_time
    ).all()

    venue_dict = {}
    for p, v in performances:
        if v.id not in venue_dict:
            venue_dict[v.id] = {
                "venue_id": v.id,
                "name": v.name,
                "address": getattr(v, "address", None),
                "image_url": getattr(v, "image_url", None),
                "latitude": getattr(v, "latitude", None),
                "longitude": getattr(v, "longitude", None),
                "performance": []
            }
        venue_dict[v.id]["performance"].append({
            "id": p.id,
            "title": p.title,
            "time": p.time.strftime("%H:%M:%S") if p.time else None,
            "image_url": p.image_url,
            "address": getattr(v, "address", None)
        })

    return list(venue_dict.values())


# -------------------------------
# 특정 공연장의 오늘 공연 (현재 시간 이후)
# -------------------------------
def get_performances_by_venue(db: Session, venue_id: int, after: datetime.datetime):
    today = after.date()
    current_time = after.time()

    performances = db.query(Performance).filter(
        Performance.venue_id == venue_id,
        Performance.date == today,
        Performance.time >= current_time
    ).all()

    return [{
        "performance_id": p.id,
        "title": p.title,
        "time": p.time.strftime("%H:%M:%S") if p.time else None,
        "address": p.venue.address,
        "image_url": p.image_url
    } for p in performances]
