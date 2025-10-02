from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, func, Index, UniqueConstraint, text
)
from app.database import Base

class Notification(Base):
    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer,
                     ForeignKey("user.id", ondelete="CASCADE"),
                     nullable=False)

    
    type = Column(String(32), nullable=False)

    title = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)

    link_url = Column(String(300), nullable=True)

    
    payload_json = Column(String(64), nullable=True)

    is_read = Column(Boolean, nullable=False, server_default=text("0"))
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    __table_args__ = (
        Index("ix_notification_user_created", "user_id", "created_at"),
        UniqueConstraint("user_id", "type", "payload_json",
                         name="uq_notification_user_type_payload"),
    )
