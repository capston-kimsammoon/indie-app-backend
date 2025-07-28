# app/utile/dependency.py
# ❌ 배포 전 삭제 !! ❌

from fastapi import Depends
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_db

def get_current_user(db: Session = Depends(get_db)) -> User:
    # 임시 user ID 1번으로 고정
    user = db.query(User).filter(User.id == 1).first()
    print("dependency user: ", user)
    return user
