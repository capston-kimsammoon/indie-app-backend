# app/utile/dependency.py
# ❌ 배포 전 삭제 !! ❌

from fastapi import Depends
from typing import Optional
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_db

def get_current_user(db: Session = Depends(get_db)) -> User:
    # 임시 user ID 500번으로 고정
    user = db.query(User).filter(User.id == 500).first()
    print("dependency user: ", user)
    return user

def get_current_user_optional(db: Session = Depends(get_db)) -> Optional[User]:
    user = db.query(User).filter(User.id == 500).first()
    return user