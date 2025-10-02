# app/crud/nearby.py

from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_, or_
from app.models.venue import Venue
from app.schemas.nearby import PerformanceBoundsRequest
from app.models.performance import Performance
from math import radians
import datetime, pytz

# 반경 내 공연장 목록 조회
def get_nearby_venues(db: Session, lat: float, lng: float, radius_km: float):
    
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
    now = datetime.datetime.now(pytz.timezone("Asia/Seoul"))
    today = now.date()
    current_time = now.time()

    performances = db.query(Performance, Venue).join(Venue).filter(
        and_(
            Venue.latitude >= req.sw_lat,
            Venue.latitude <= req.ne_lat,
            Venue.longitude >= req.sw_lng,
            Venue.longitude <= req.ne_lng,
            or_(
                Performance.date > today,
                and_(
                    Performance.date == today,
                    Performance.time >= current_time
                )
            )
        )
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

# 특정 공연장의 현재 시각 이후 예정 공연 목록 조회
def get_performances_by_venue(db: Session, venue_id: int, after: datetime):
    after_date = after.date()
    after_time = after.time()

    performances = db.query(Performance).filter(
        Performance.venue_id == venue_id,
        or_(
            Performance.date > after_date,
            and_(
                Performance.date == after_date,
                Performance.time >= after_time
            )
        )
    ).all()

    return [{
        "performance_id": p.id,
        "title": p.title,
        "time": p.time.strftime("%H:%M:%S") if p.time else None,
        "address": p.venue.address,
        "image_url": p.image_url
    } for p in performances]
