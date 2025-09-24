# app/models/user_artist_ticketalarm.py
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from app.database import Base

class UserArtistTicketAlarm(Base):
    __tablename__ = "user_artist_ticketalarm"

    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    artist_id = Column(Integer, ForeignKey("artist.id"), primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint("user_id", "artist_id"),
    )
