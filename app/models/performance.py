from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text, Table, Date, Time
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Performance(Base):
    __tablename__ = "performance"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    venue_id = Column(Integer, ForeignKey("venue.id"), nullable=False)
    date = Column(Date, nullable=False)  # YYYY-MM-DD
    time = Column(Time, nullable=False)  # HH:MM
    ticket_open_date = Column(Date, nullable=True)
    ticket_open_time = Column(Time, nullable=True)
    price = Column(String(200), nullable=False)
    image_url = Column(String(300), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    shortcode = Column(String(100), nullable=True) # 중복 확인용
    detail_url = Column(String(300), nullable=True) # 예매 링크 

    venue = relationship("Venue", back_populates="performances")
    artists = relationship("Artist", secondary="performance_artist", back_populates="performances")
    favorite_users = relationship("User", secondary="user_favorite_performance", back_populates="favorite_performances")
    ticket_alarm_users = relationship("User", secondary="user_performance_ticketalarm", back_populates="ticket_alarm_performances")

    stamps = relationship("Stamp", back_populates="performance", cascade="all, delete-orphan")
    # mood_recommendation과의 관계 
    mood_recommendations = relationship(
        "MoodRecommendation",
        back_populates="performance",
        cascade="all, delete-orphan"
    )
