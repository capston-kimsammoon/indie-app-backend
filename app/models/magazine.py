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

    images = relationship("MagazineImage", back_populates="magazine", cascade="all, delete-orphan")
