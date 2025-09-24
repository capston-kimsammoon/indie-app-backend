#스키마/캘린더.py
from pydantic import BaseModel
from typing import List, Optional

# 월별 공연 날짜 응답 스키마
class CalendarSummaryResponse(BaseModel):
    year: int
    month: int
    hasPerformanceDates: List[int]

# 특정 날짜의 공연 항목 스키마
class CalendarPerformanceItem(BaseModel):
    id: int
    title: str
    venue: str
    thumbnail: Optional[str]

# 날짜별 공연 리스트 응답 스키마
class CalendarPerformanceListResponse(BaseModel):
    date: str
    region: List[str]  # ✅ 여기를 수정 (str → List[str])
    performances: List[CalendarPerformanceItem]
