from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Boolean, Text, Table, Date, Time
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class Performance(Base):
    __tablename__ = "performances"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    venue_id = Column(Integer, ForeignKey("venues.id"))
    date = Column(Date)  # YYYY-MM-DD
    time = Column(Time)  # HH:MM
    ticket_open_date = Column(Date)
    ticket_open_time = Column(Time)
    price = Column(Integer)
    ticket_url = Column(String(300), nullable=True)
    image_url = Column(String(300))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_canceled = Column(Boolean, default=False)

    venue = relationship("Venue", back_populates="performances")
    artists = relationship("Artist", secondary="performance_artists", back_populates="performances")
    favorite_users = relationship("User", secondary="user_performances_favorite", back_populates="favorite_performances")
    ticket_alarm_users = relationship("User", secondary="user_performances_ticketalarm", back_populates="ticket_alarm_performances")