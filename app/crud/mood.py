# app/crud/mood.py
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc, join

from app.models.mood import MoodRecommendation, Mood
from app.models.performance import Performance
from app.models.venue import Venue


def get_moods(db: Session) -> List[Mood]:
    
    stmt = select(Mood).order_by(Mood.name.asc())
    return list(db.execute(stmt).scalars().all())


def get_performance_cards_by_mood(
    db: Session, mood_id: int, limit: int = 12
) -> List[Tuple[int, str, Optional[str], Optional[str], Optional[int], Optional[str]]]:
    
    j = (
        join(Performance, MoodRecommendation, MoodRecommendation.performance_id == Performance.id)
        .join(Venue, Venue.id == Performance.venue_id)
    )


    stmt = (
        select(
            Performance.id.label("perf_id"),
            Performance.title,
            Performance.image_url,
            Performance.date,   
            Venue.id.label("venue_id"),
            Venue.name.label("venue_name"),
        )
        .select_from(j)
        .where(MoodRecommendation.mood_id == mood_id)
        .order_by(asc(Performance.date), desc(Performance.id))
        .limit(limit)
    )

    rows = db.execute(stmt).all()
    out: List[Tuple[int, str, Optional[str], Optional[str], Optional[int], Optional[str]]] = []
    for perf_id, title, image_url, date_val, venue_id, venue_name in rows:
        date_str = None
        if date_val is not None:
            
            date_str = str(date_val)
        out.append((perf_id, title, image_url, date_str, venue_id, venue_name))
    return out
