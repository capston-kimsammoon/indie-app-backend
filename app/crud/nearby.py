from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.venue import Venue
from app.schemas.nearby import PerformanceBoundsRequest
from app.models.performance import Performance
from math import radians
import datetime

# 반경 내 공연장 목록 조회
def get_nearby_venues(db: Session, lat: float, lng: float, radius_km: float):
    # Haversine 공식 (거리 계산 공식)
    earth_radius_km = 6371.0

    lat_rad = radians(lat)
    lng_rad = radians(lng)

    return db.query(Venue).filter(
        earth_radius_km * func.acos(
            func.sin(func.radians(lat)) * func.sin(func.radians(Venue.latitude)) +
            func.cos(func.radians(lat)) * func.cos(func.radians(Venue.latitude)) *
            func.cos(func.radians(Venue.longitude) - func.radians(lng))
        ) <= radius_km
    ).all()


# 지도 범위 내 공연장들의 예정 공연 목록 조회
def get_performances_in_bounds(db: Session, req):
    now = datetime.datetime.utcnow()

    # 공연장 + 공연 조인하여 필터링
    performances = db.query(Performance, Venue).join(Venue).filter(
        Performance.date > now,
        Venue.latitude >= req.sw_lat,
        Venue.latitude <= req.ne_lat,
        Venue.longitude >= req.sw_lng,
        Venue.longitude <= req.ne_lng
    ).all()

    # 공연장별로 묶어서 정리
    venue_dict = {}
    for p, v in performances:
        if v.id not in venue_dict:
            venue_dict[v.id] = {
                "venue_id": v.id,
                "name": v.name,
                "performance": []
            }
        venue_dict[v.id]["performance"].append({
            "id": p.id,
            "time": p.time.strftime("%H:%M:%S") if p.time else None,
            "image_url": p.image_url
        })

    return list(venue_dict.values())


# 특정 공연장의 YYYY-MM-DDTHH:MM:SS 시각 이후 예정 공연 목록 조회
def get_performances_by_venue(db: Session, venue_id: int, after: datetime):
    performances = db.query(Performance).join(Venue).filter(
        Performance.venue_id == venue_id,
        Performance.date > after
    ).all()

    return [{
        "performance_id": p.id,
        "title": p.title,
        "time": p.time.strftime("%H:%M:%S") if p.time else None,
        "address": p.venue.address,
        "image_url": p.image_url
    } for p in performances]