from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.venue import Venue
from app.models.performance import Performance
from datetime import datetime, time as dtime

# 지역 이름으로 공연장 목록 조회
def get_venues_by_region(db: Session, region: str, skip: int, limit: int):
    query = db.query(Venue).filter(Venue.region == region)
    total = query.count()
    venues = query.offset(skip).limit(limit).all()
    return venues, total

# 공연장 ID로 공연장 상세 정보 조회
def get_venue_by_id(db: Session, venue_id: int):
    return db.query(Venue).filter(Venue.id == venue_id).first()

from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.venue import Venue
from app.models.performance import Performance
from datetime import date

# 지역 이름으로 공연장 목록 조회
def get_venues_by_region(db: Session, region: str, skip: int, limit: int):
    query = db.query(Venue).filter(Venue.region == region)
    total = query.count()
    venues = query.offset(skip).limit(limit).all()
    return venues, total

# 공연장 ID로 공연장 상세 정보 조회
def get_venue_by_id(db: Session, venue_id: int):
    return db.query(Venue).filter(Venue.id == venue_id).first()

def _now_parts():
    now = datetime.now()
    return now.date(), dtime(now.hour, now.minute, now.second)

# 예정 공연 (오늘 이후 + 오늘 중 남은 시간)
def get_upcoming_performances_by_venue(db: Session, venue_id: int, limit: int | None = None):
    today, now_t = _now_parts()
    q = (
        db.query(Performance)
        .filter(Performance.venue_id == venue_id)
        .filter(
            or_(
                Performance.date > today,
                and_(Performance.date == today, or_(Performance.time == None, Performance.time >= now_t)),
            )
        )
        .order_by(Performance.date.asc(), Performance.time.asc())
    )
    if limit:
        q = q.limit(limit)
    return q.all()

# 지난 공연 (어제까지 + 오늘 중 이미 지난 시간)
def get_past_performances_by_venue(db: Session, venue_id: int, limit: int | None = None):
    today, now_t = _now_parts()
    q = (
        db.query(Performance)
        .filter(Performance.venue_id == venue_id)
        .filter(
            or_(
                Performance.date < today,
                and_(Performance.date == today, Performance.time != None, Performance.time < now_t),
            )
        )
        .order_by(Performance.date.desc(), Performance.time.desc())
    )
    if limit:
        q = q.limit(limit)
    return q.all()

