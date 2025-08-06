from sqlalchemy.orm import Session
from sqlalchemy import extract, or_
from typing import List
from app.models.performance import Performance
from app.models.venue import Venue


def parse_region_param(region) -> List[str]:
    region_list = []
    if region:
        if isinstance(region, str):
            region_list = [r.strip().lower() for r in region.split(",") if r.strip()]
        elif isinstance(region, list):
            for r in region:
                for p in r.split(","):
                    p = p.strip().lower()
                    if p:
                        region_list.append(p)
    return region_list


def get_calendar_summary_by_month(db: Session, year: int, month: int, region=None):
    region_list = parse_region_param(region)

    query = db.query(extract("day", Performance.date)).join(Venue)

    if region_list and "전체" not in region_list:
        conditions = [Venue.region.ilike(f"%{r}%") for r in region_list]
        query = query.filter(or_(*conditions))

    query = query.filter(
        extract("year", Performance.date) == year,
        extract("month", Performance.date) == month
    )

    days = query.distinct().all()
    return [day[0] for day in days]


def get_performances_by_date(db: Session, target_date, region=None):
    region_list = parse_region_param(region)

    query = db.query(Performance).join(Venue)

    if region_list and "전체" not in region_list:
        conditions = [Venue.region.ilike(f"%{r}%") for r in region_list]
        query = query.filter(or_(*conditions))

    query = query.filter(Performance.date == target_date)

    return query.all()
