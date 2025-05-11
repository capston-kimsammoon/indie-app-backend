from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import datetime

class UserPerformanceTicketAlarm(Base):
    __tablename__ = "user_performances_ticketalarm"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    performance_id = Column(Integer, ForeignKey("performances.id"), primary_key=True)