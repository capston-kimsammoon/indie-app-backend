from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models.user import User
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.utils.dependency import get_current_user

router = APIRouter(tags=["Alerts"])

class AlertRequest(BaseModel):
    type: str
    refId: int

# 아티스트 알림 ON
@router.post("/alerts/artist")
def alert_artist_on(
    alert: AlertRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    print("alert.type:", alert.type)
    print("alert.refId:", alert.refId)
    
    if alert.type != "artist":
        raise HTTPException(status_code=400, detail="Invalid type")

    existing = db.query(UserArtistTicketAlarm).filter_by(user_id=user.id, artist_id=alert.refId).first()
    if existing:
        raise HTTPException(status_code=400, detail="Alert already set")

    new_alert = UserArtistTicketAlarm(user_id=user.id, artist_id=alert.refId)
    db.add(new_alert)
    db.commit()

    return {"message": "Artist alert set successfully"}

# 아티스트 알림 OFF
@router.delete("/alerts/artist/{artist_id}")
def alert_artist_off(
    artist_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    alarm = db.query(UserArtistTicketAlarm).filter_by(user_id=user.id, artist_id=artist_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alert not found")

    db.delete(alarm)
    db.commit()

    return {"message": "Artist alert removed successfully"}
