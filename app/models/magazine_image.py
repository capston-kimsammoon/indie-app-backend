from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class MagazineImage(Base):
    __tablename__ = "magazine_image"

    id = Column(Integer, primary_key=True, index=True)
    magazine_id = Column(Integer, ForeignKey("magazine.id"), nullable=False)
    image_url = Column(String(300), nullable=False)

    magazine = relationship("Magazine", back_populates="images")
