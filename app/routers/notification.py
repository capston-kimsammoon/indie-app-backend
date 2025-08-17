# app/routers/notification.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from fastapi import APIRouter
from app.database import get_db
from app.utils.dependency import get_current_user
from app.models.notification import Notification

router = APIRouter(prefix="/notifications", tags=["Notification"])
alias = APIRouter(prefix="/notices", tags=["Notification"])
alias.include_router(router)

class NotificationRead(BaseModel):
    id: int
    type: str
    title: str
    body: str
    link_url: str | None = None
    is_read: bool
    created_at: datetime  # ← 문자열이 아니라 datetime으로 바꿔서 검증 오류 방지
    class Config:
        from_attributes = True


@router.get("", response_model=List[NotificationRead])
def list_notifications(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )
    return rows


@router.patch("/{nid}/read")
def mark_read(nid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.query(Notification).filter_by(id=nid, user_id=user.id).first()
    if not n:
        raise HTTPException(404, "Notification not found")
    n.is_read = True
    db.commit()
    return {"ok": True}


@router.delete("/{nid}")
def remove(nid: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    n = db.query(Notification).filter_by(id=nid, user_id=user.id).first()
    if not n:
        raise HTTPException(404, "Notification not found")
    db.delete(n)
    db.commit()
    return {"ok": True}


# ✅ 스케줄 알림 수동 디스패치 (예매오픈/공연 D-1)
@router.post("/dispatch-due")
def dispatch_due(db: Session = Depends(get_db)):
    from app.services.notify import dispatch_scheduled_notifications
    return dispatch_scheduled_notifications(db)
