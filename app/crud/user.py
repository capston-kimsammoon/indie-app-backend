# app/crud/user.py

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from typing import Dict

# Kakao 사용자 ID로 기존 회원 조회
def get_user_by_kakao_id(db: Session, kakao_id: int) -> User | None:
    return db.query(User).filter(User.kakao_id == kakao_id).first()

# 새 사용자 정보를 기반으로 회원 생성 및 DB 저장
def create_user(db: Session, user_data: Dict) -> User:
    nickname = user_data["kakao_account"]["profile"]["nickname"]
    profile_url = user_data["kakao_account"]["profile"].get("profile_image_url")
    kakao_id = user_data["id"]

    user = User(
        nickname=nickname,
        profile_url=profile_url,
        kakao_id=kakao_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# 사용자 ID로 기존 회원 찾고, 없으면 새로 생성하여 반환
def get_or_create_user(db: Session, kakao_user_info: Dict) -> User:
    kakao_id = kakao_user_info["id"]
    user = get_user_by_kakao_id(db, kakao_id)

    if user:
        return user
    return create_user(db, kakao_user_info)

# 사용자 닉네임 업데이트
def update_user_nickname(db: Session, user: User, new_nickname: str):
    user.nickname = new_nickname
    db.commit()
    db.refresh(user)
    return user