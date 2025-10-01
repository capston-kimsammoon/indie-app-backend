# ✅ app/crud/calendar.py
from sqlalchemy.orm import Session
from datetime import date
from app.models.performance import Performance
from app.models.venue import Venue


def get_calendar_summary_by_month(db: Session, year: int, month: int, region: list[str] | None):
    start_date = date(year, month, 1)
    end_date = date(year, month + 1, 1) if month < 12 else date(year + 1, 1, 1)

    query = db.query(Performance.date).filter(
        Performance.date >= start_date,
        Performance.date < end_date
    )

    if region:
        query = query.join(Performance.venue).filter(Venue.region.in_(region))

    result = query.all()
    days = sorted({d.date.day for d in result})
    return days

def get_performances_by_date(db: Session, target_date: date, region: list[str] | None):
    query = db.query(Performance).filter(Performance.date == target_date)

    if region:
        query = query.join(Performance.venue, isouter=True).filter(Venue.region.in_(region))

    return query.all()
