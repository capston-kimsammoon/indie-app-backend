# app/routers/mood.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import traceback

from app.database import get_db
from app.models.mood import Mood
from app.crud import mood as mood_crud

router = APIRouter(prefix="/mood", tags=["mood"])

@router.get("")  # ← response_model 제거 (원시 JSON 반환)
def list_moods(db: Session = Depends(get_db)):
    """
    무드 전체 목록 (원시 JSON)
    """
    moods = mood_crud.get_moods(db)
    # 원시 JSON 배열로 변환
    return [{"id": m.id, "name": m.name} for m in moods]

@router.get("/{mood_id}/performances")  # ← response_model 제거 (원시 JSON 반환)
def list_performances_by_mood(
    mood_id: int,
    limit: int = Query(12, ge=1, le=50, description="가져올 개수(기본 12, 최대 50)"),
    db: Session = Depends(get_db),
):
    """
    특정 무드의 추천 공연 목록 (원시 JSON)
    응답 형태:
    {
      "moodId": <int>,
      "performances": [
        {"id": ..., "title": "...", "image_url": "...", "date": "YYYY-MM-DD", "venue": {"id": ..., "name": "..."}},
        ...
      ]
    }
    """
    # SQLAlchemy 2.x: Session.get 사용
    mood_obj: Optional[Mood] = db.get(Mood, mood_id)
    if not mood_obj:
        raise HTTPException(status_code=404, detail="Mood not found")

    try:
        rows = mood_crud.get_performance_cards_by_mood(db, mood_id=mood_id, limit=limit)
        # rows: (perf_id, title, image_url, date_str, venue_id, venue_name)
        items: List[dict] = []
        for perf_id, title, image_url, date_str, venue_id, venue_name in rows:
            venue = {"id": venue_id, "name": venue_name or ""} if venue_id is not None else None
            items.append({
                "id": perf_id,
                "title": title or "",
                "image_url": image_url,
                "date": date_str,   # 문자열 'YYYY-MM-DD'
                "venue": venue,
            })
        return {"moodId": mood_id, "performances": items}
    except Exception:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
