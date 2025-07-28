from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class Venue(Base):
    __tablename__ = "venue"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)  # 주소 기반으로 유지 (위도경도는 나중에 별도 필드 추가 가능)
    region = Column(String(100), nullable=False)
    instagram_account = Column(String(100), nullable=False)

    performances = relationship("Performance", back_populates="venue")

