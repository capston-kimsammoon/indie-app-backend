from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    kakao_id: str
    nickname: str

class UserRead(BaseModel):
    id: int
    kakao_id: str
    nickname: str
    created_at: datetime

    class Config:
        orm_mode = True
