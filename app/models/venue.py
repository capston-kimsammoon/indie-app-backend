from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base

class Venue(Base):
    __tablename__ = "venue"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    region = Column(String(100), nullable=False)
    instagram_account = Column(String(100), nullable=False)
    image_url = Column(String(200))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    performances = relationship("Performance", back_populates="venue")

