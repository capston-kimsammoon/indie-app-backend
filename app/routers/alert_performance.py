# app/routers/alerts.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, Any
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm
from app.utils.dependency import get_current_user 

router = APIRouter(tags=["Alerts"])

class AlertRequest(BaseModel):
    type: str 
    refId: int

# 공연 4-1. 예매 알림 ON
@router.post("/alerts")
def alert_on(
    alert: AlertRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if alert.type != "performance":
        raise HTTPException(status_code=400, detail="Invalid type")

    # 이미 ON 되어 있는지 확인
    existing = db.query(UserPerformanceTicketAlarm).filter_by(user_id=user.id, performance_id=alert.refId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alert already set")

    new_alert = UserPerformanceTicketAlarm(user_id=user.id, performance_id=alert.refId)
    db.add(new_alert)
    db.commit()

    return {"message": "Alert set successfully"}

# 공연 4-2. 예매 알림 OFF
@router.delete("/alerts/{performance_id}")
def alert_off(
    performance_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    alarm = db.query(UserPerformanceTicketAlarm).filter_by(user_id=user.id, performance_id=performance_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alarm)
    db.commit()

    return {"message": "Alert removed successfully"}
