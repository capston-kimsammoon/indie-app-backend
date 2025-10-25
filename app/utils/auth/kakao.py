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
        print(f"Error response: {response.text}")  # 오류 메시지 출력
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

def kakao_unlink(kakao_id: str):
    url = "https://kapi.kakao.com/v1/user/unlink"
    headers = {"Authorization": f"KakaoAK {settings.KAKAO_ADMIN_KEY}"}
    data = {"target_id_type": "user_id", "target_id": kakao_id}

    try:
        res = requests.post(url, headers=headers, data=data, timeout=5)
        if res.status_code != 200:
            # 운영에선 로깅만 하고 계속 진행
            print(f"[WARN] Kakao unlink failed ({res.status_code}): {res.text}")
            return None
        return res.json()
    except Exception as e:
        print(f"[WARN] Kakao unlink exception: {e}")
        return None