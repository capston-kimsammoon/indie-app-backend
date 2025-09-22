# app/schemas/review_image.py
from pydantic import BaseModel
from datetime import datetime

class ReviewImageCreate(BaseModel):
    image_url: str

class ReviewImageItem(BaseModel):
    id: int
    review_id: int
    image_url: str
    created_at: datetime

    class Config:
        from_attributes = True
