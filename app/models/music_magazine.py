# app/models/music_magazine.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class MusicMagazine(Base):
    __tablename__ = "music_magazine"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 블록은 display_order 오름차순으로 정렬
    blocks = relationship(
        "MusicMagazineBlock",
        back_populates="magazine",
        order_by="MusicMagazineBlock.display_order",
        cascade="all, delete-orphan"
    )
