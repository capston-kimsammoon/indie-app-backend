from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Venue(Base):
    __tablename__ = "venues"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    address = Column(String(200))  # 주소 기반으로 유지 (위도경도는 나중에 별도 필드 추가 가능)
    instagram_account = Column(String(100))

    performances = relationship("Performance", back_populates="venue")

