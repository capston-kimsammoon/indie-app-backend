from sqlalchemy.orm import Session
from datetime import date
from app.models.performance import Performance
from app.models.venue import Venue

# 월별 공연 날짜 리스트 조회
def get_calendar_summary_by_month(db: Session, year: int, month: int, region: str | None):
    start_date = date(year, month, 1)
    end_date = (
        date(year, month + 1, 1) if month < 12
        else date(year + 1, 1, 1)
    )

    query = db.query(Performance.date).filter(
        Performance.date >= start_date,
        Performance.date < end_date
    )

    if region and region != "전체":
        query = query.join(Performance.venue).filter(Venue.region == region)

    result = query.all()
    days = sorted({d.date.day for d in result})

    return days


# 날짜별 공연 리스트 조회
def get_performances_by_date(db: Session, target_date: date, region: str | None):
    query = db.query(Performance).filter(Performance.date == target_date)

    if region and region != "전체":
        query = query.join(Performance.venue).filter(Venue.region == region)

    performances = query.all()
    return performances
