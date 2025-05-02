from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ArtistCreate(BaseModel):
    name: str
    genre: Optional[str] = None
    band_id: Optional[int] = None
    spotify_url: Optional[str] = None
    image_url: Optional[str] = None
    instagram_account: Optional[str] = None

class ArtistRead(ArtistCreate):
    id: int

    class Config:
        orm_mode = True
