from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.schemas.target import TargetRequest, TargetType
from app.database import get_db
from app.models.user import User
from app.crud.like import create_like, delete_like
from app.utils.dependency import get_current_user

router = APIRouter(prefix="/like", tags=["Like"])

@router.post("")
def like_on(
    body: TargetRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = create_like(db, user.id, body.type.value, body.refId)
    if result is None:
        raise HTTPException(status_code=409, detail="Already liked")
    elif result is False:
        raise HTTPException(status_code=400, detail="Invalid like type")

    return {"message": f"{body.type.value.capitalize()} like set successfully"}

@router.delete("/{ref_id}")
def like_off(
    ref_id: int,
    type: TargetType = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = delete_like(db, user.id, type.value, ref_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Like not found")
    elif result is False:
        raise HTTPException(status_code=400, detail="Invalid like type")

    return {"message": f"{type.value.capitalize()} like removed successfully"}
