# app/utils/auth/kakao.py

import requests
from fastapi import HTTPException
from app.config import settings


def get_kakao_access_token(code: str) -> str:
    response = requests.post(
        "https://kauth.kakao.com/oauth/token",
        data={
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_REST_API_KEY,
            "redirect_uri": settings.KAKAO_REDIRECT_URI,
            "code": code,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="카카오 access_token 발급 실패")
    return response.json()["access_token"]


def get_kakao_user_info(access_token: str) -> dict:
    response = requests.get(
        "https://kapi.kakao.com/v2/user/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="카카오 사용자 정보 요청 실패")
    return response.json()
