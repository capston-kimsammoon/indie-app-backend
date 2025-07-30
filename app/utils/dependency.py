# app/utile/dependency.py
# ❌ 배포 전 삭제 !! ❌

from fastapi import Depends
from typing import Optional
from app.models.user import User
from sqlalchemy.orm import Session
from app.database import get_db

# 강제 로그인된 유저 반환 (user_id=1)
def get_current_user(db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == 1).first()
    return user

# 로그인 없을 수도 있는 API에서 사용 (user_id=1 or None)
def get_current_user_optional(db: Session = Depends(get_db)) -> Optional[User]:
    user = db.query(User).filter(User.id == 1).first()
    return user