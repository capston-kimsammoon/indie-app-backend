#app/schemas/naerby.py

from pydantic import BaseModel
from typing import Optional, List

# 근처 공연장 정보 응답 모델
class NearbyVenueResponse(BaseModel):
    venue_id: int
    name: str
    latitude: float
    longitude: float

# 지도 내 공연장/공연 조회 시 사용되는 요청 모델 (지도 좌표 범위)
class PerformanceBoundsRequest(BaseModel):
    sw_lat: float
    sw_lng: float
    ne_lat: float
    ne_lng: float

# 공연 요약 정보 (장소별 공연 리스트에 포함되는 간략 정보)
class PerformanceSummary(BaseModel):
    id: int
    title: Optional[str] = None
    time: str
    image_url: Optional[str] = None
    address: Optional[str] = None

# 공연장별 예정 공연 응답 모델 (지도 위 공연장 클릭 시 사용)
class NearbyPerformanceResponse(BaseModel):
    venue_id: int
    name: str
    performance: List[PerformanceSummary]

    address: Optional[str] = None
    image_url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

# 사용자 현재 위치 좌표 요청 모델
class LocationRequest(BaseModel):
    lat: float
    lng: float

# 특정 공연장 내 공연 정보를 담는 아이템 (수평 공연 카드용)
class VenuePerformanceItem(BaseModel):
    performance_id: int
    title: str
    time: str
    address: str
    image_url: Optional[str]

# 현재 위치 기준으로 지도 리센터 시 사용되는 요청 모델
class RecenterRequest(BaseModel):
    lat: float
    lng: float
