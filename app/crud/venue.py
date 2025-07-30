from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.venue import Venue
from app.models.performance import Performance
from datetime import date

# 지역 이름)으로 공연장 목록 조회
def get_venues_by_region(db: Session, region: str, skip: int, limit: int):
    query = db.query(Venue).filter(Venue.region == region)
    total = query.count()
    venues = query.offset(skip).limit(limit).all()
    return venues, total

# 공연장 ID로 공연장 상세 정보 조회
def get_venue_by_id(db: Session, venue_id: int):
    return db.query(Venue).filter(Venue.id == venue_id).first()

# 특정 공연장에서 현재 시각 이후에 예정된 공연 목록 조회
def get_upcoming_performances_by_venue(db: Session, venue_id: int):
    return db.query(Performance).filter(
        Performance.venue_id == venue_id,
        Performance.date >= date.today()
    ).order_by(Performance.date).all()
