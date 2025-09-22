# models/magazine.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Magazine(Base):
    __tablename__ = "magazine"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

     # ✅ 본문은 blocks로
    blocks = relationship(
        "MagazineBlock",
        back_populates="magazine",
        order_by="MagazineBlock.order",
        cascade="all, delete-orphan"
    )
