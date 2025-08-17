from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func
from app.database import Base

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

   
    type = Column(String(32), nullable=False)

    title = Column(String(200), nullable=False)  
    body = Column(Text, nullable=False)         

    link_url = Column(String(300), nullable=True)     
    payload_json = Column(Text, nullable=True)        

    is_read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
