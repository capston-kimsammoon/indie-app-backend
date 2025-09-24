# app/crud/mood.py
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc, join

from app.models.mood import MoodRecommendation, Mood
from app.models.performance import Performance
from app.models.venue import Venue


def get_moods(db: Session) -> List[Mood]:
    """
    모든 무드 목록 (이름 오름차순)
    """
    stmt = select(Mood).order_by(Mood.name.asc())
    return list(db.execute(stmt).scalars().all())


def get_performance_cards_by_mood(
    db: Session, mood_id: int, limit: int = 12
) -> List[Tuple[int, str, Optional[str], Optional[str], Optional[int], Optional[str]]]:
    """
    특정 무드의 공연 카드용 필드만 안전하게 선택해서 반환.
    반환 튜플 스키마:
      (perf_id, title, image_url, date_str, venue_id, venue_name)

    - 관계 로딩 없이 JOIN + 필요한 칼럼만 SELECT
    - date는 문자열로 변환 (JSON 직렬화 논란 제거)
    """
    j = (
        join(Performance, MoodRecommendation, MoodRecommendation.performance_id == Performance.id)
        .join(Venue, Venue.id == Performance.venue_id)
    )

    # MySQL/Maria에서 DATE를 문자열로 캐스팅하지 않아도 Pydantic가 처리하긴 하지만,
    # API 응답을 100% 안전하게 만들기 위해 문자열로 변환해 보냄.
    stmt = (
        select(
            Performance.id.label("perf_id"),
            Performance.title,
            Performance.image_url,
            Performance.date,   # 후단에서 str() 처리
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
            # date_val: datetime.date 또는 str
            date_str = str(date_val)
        out.append((perf_id, title, image_url, date_str, venue_id, venue_name))
    return out
