from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import requests

# 의존성
from app.database import get_db
from app.utils.dependency import get_current_user

# 설정
from app.config import settings as app_settings

# crud
from app.crud import user as user_crud

# utils
from app.utils.auth import kakao as kakao_utils
from app.utils.auth import auth as auth_utils

# models
from app.models.user import User

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

# 프론트에 카카오 로그인 URL 제공
@router.get("/kakao/login")
def get_kakao_login_url():
    kakao_client_id = app_settings.KAKAO_REST_API_KEY
    redirect_uri = app_settings.KAKAO_REDIRECT_URI

    login_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?client_id={kakao_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    return {"loginUrl": login_url}


# 카카오 로그인 콜백 처리 → JWT 발급
@router.get("/kakao/callback")
def kakao_callback(code: str, db: Session = Depends(get_db)):
    kakao_token = kakao_utils.get_kakao_access_token(code)
    kakao_user_info = kakao_utils.get_kakao_user_info(kakao_token)

    user = user_crud.get_or_create_user(db, kakao_user_info)

    access_token = auth_utils.create_access_token(user.id)
    refresh_token = auth_utils.create_refresh_token(user.id)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token
    }

# 로그아웃
@router.post("/logout")
def logout_user(current_user: User = Depends(get_current_user)):
    # TODO: refreshToken 무효화 처리 (예: DB 저장 시 삭제)
    return {"message": "로그아웃되었습니다."}
