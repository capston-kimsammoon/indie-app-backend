# 알림, 찜 공용 스키마
from pydantic import BaseModel
from enum import Enum

class TargetType(str, Enum):
    performance = "performance"
    artist = "artist"

class TargetRequest(BaseModel):
    type: TargetType
    refId: int
