from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.target import TargetRequest, TargetType
from app.database import get_db
from app.models.user import User
from app.crud.alert import create_alert, delete_alert
from app.utils.dependency import get_current_user

router = APIRouter(prefix="/alert", tags=["Alert"])

@router.post("")
def alert_on(
    body: TargetRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = create_alert(db, user.id, body.type.value, body.refId)
    if result is None:
        raise HTTPException(status_code=400, detail="Alert already set")
    elif result is False:
        raise HTTPException(status_code=400, detail="Invalid alert type")

    return {"message": f"{body.type.value.capitalize()} alert set successfully"}

@router.delete("/{ref_id}")
def alert_off(
    ref_id: int,
    type: TargetType = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = delete_alert(db, user.id, type.value, ref_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    elif result is False:
        raise HTTPException(status_code=400, detail="Invalid alert type")

    return {"message": f"{type.value.capitalize()} alert removed successfully"}
