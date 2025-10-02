# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
import random
import string
from secrets import token_urlsafe
from typing import Optional
from urllib.parse import urlparse

# 의존성
from app.database import get_db
from app.utils.dependency import get_current_user

# 설정
from app.config import settings as app_settings

# utils
from app.utils.auth import auth as auth_utils
from app.utils.auth.kakao import get_kakao_access_token, get_kakao_user_info

# models
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


# ─────────────────────────────────────────────────────────────
# 내부 유틸
# ─────────────────────────────────────────────────────────────
def _env_bool(key: str, default: bool = False) -> bool:
    v = os.getenv(key)
    if v is None:
        return default
    return str(v).lower() in {"1", "true", "yes", "y"}

def _front_redirect_url() -> str:
    """
    로그인 성공 후 프론트로 이동할 URL. 운영에서는 환경변수로 고정하세요.
    예) https://modiemodie.com/login/success
    """
    return (
        getattr(app_settings, "FRONT_REDIRECT_URL", None)
        or os.getenv("FRONT_REDIRECT_URL")
        or "http://localhost:3000/login/success"
    )

def _front_origin() -> str:
    """
    postMessage target origin 용. (scheme + host)
    예) https://modiemodie.com
    """
    u = urlparse(_front_redirect_url())
    return f"{u.scheme}://{u.netloc}"

def _cookie_kwargs() -> dict:
    """
    로컬(기본):
      - secure=False, samesite="Lax", domain=None
    운영(HTTPS, 크로스사이트):
      - COOKIE_SECURE=true, COOKIE_SAMESITE=None, COOKIE_DOMAIN=modiemodie.com
    """
    return dict(
        httponly=True,
        secure=_env_bool("COOKIE_SECURE", False),
        samesite=os.getenv("COOKIE_SAMESITE", "Lax"),
        max_age=60 * 60 * 24 * 7,  # 7 days
        path="/",
        domain=os.getenv("COOKIE_DOMAIN") or None,
    )

def _delete_cookie_kwargs() -> dict:
    """set_cookie에 준 domain/path와 동일하게 맞춰서 삭제되도록"""
    return dict(
        path="/",
        domain=os.getenv("COOKIE_DOMAIN") or None,
    )


# ─────────────────────────────────────────────────────────────
# 1) 프론트에 카카오 로그인 URL 제공 (force=true면 계정선택 강제)
# ─────────────────────────────────────────────────────────────
@router.get("/kakao/login")
def get_kakao_login_url(force: bool = Query(False)):
    kakao_client_id = app_settings.KAKAO_REST_API_KEY
    redirect_uri = app_settings.KAKAO_REDIRECT_URI
    state = token_urlsafe(16)  # (선택) CSRF 방지 – 세션/스토리지로 검증하려면 추가 구현

    login_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={kakao_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&state={state}"
    )
    if force:
        login_url += "&prompt=login"  # 계정 선택 강제

    return {"loginUrl": login_url, "state": state}


# ─────────────────────────────────────────────────────────────
# 2) 콜백: code -> kakao token -> kakao me -> DB upsert
#    토큰 쿠키로 심고 리다이렉트/팝업/JSON
# ─────────────────────────────────────────────────────────────
@router.get("/callback")
def kakao_callback(
    code: str,
    db: Session = Depends(get_db),
    mode: str = Query(default="redirect", pattern="^(redirect|popup|json)$"),
):
    try:
        # (1) code -> kakao access_token
        kakao_access_token = get_kakao_access_token(code)

        # (2) kakao me
        kakao_user_info = get_kakao_user_info(kakao_access_token)
        kakao_id = str(kakao_user_info["id"])  # 문자열로 통일
        acc = (kakao_user_info.get("kakao_account") or {})
        prof = (acc.get("profile") or {})
        base_nickname = (prof.get("nickname") or "").strip() or "user"
        profile_url: Optional[str] = prof.get("profile_image_url")

        # (3) DB upsert
        user: Optional[User] = db.query(User).filter(User.kakao_id == kakao_id).first()
        if not user:
            # 신규 가입
            nickname = base_nickname
            for _ in range(6):
                try:
                    user = User(
                        kakao_id=kakao_id,
                        nickname=nickname,
                        profile_url=profile_url or "",
                        alarm_enabled=False if hasattr(User, "alarm_enabled") else None,
                        location_enabled=False if hasattr(User, "location_enabled") else None,
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    break
                except IntegrityError:
                    db.rollback()
                    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
                    nickname = f"{base_nickname}_{suffix}"
            else:
                raise HTTPException(status_code=400, detail="닉네임 생성 실패. 다시 시도해 주세요.")
        else:
            # 기존 유저: 비어있는 필드만 보정(사용자 입력은 보존)
            changed = False
            if (not user.nickname or user.nickname.strip() == "") and base_nickname:
                user.nickname = base_nickname; changed = True
            if (not user.profile_url or user.profile_url.strip() == "") and profile_url:
                user.profile_url = profile_url; changed = True
            if hasattr(user, "alarm_enabled") and user.alarm_enabled is None:
                user.alarm_enabled = False; changed = True
            if hasattr(user, "location_enabled") and user.location_enabled is None:
                user.location_enabled = False; changed = True
            if changed:
                try:
                    db.commit()
                    db.refresh(user)
                except IntegrityError:
                    db.rollback()

        # (4) 토큰 발급/저장
        access_token = auth_utils.create_access_token(user.id)
        refresh_token = auth_utils.create_refresh_token(user.id)
        user.refresh_token = refresh_token
        db.commit()

        # (5) 쿠키 세팅 + 응답 형태 분기
        cookie_kw = _cookie_kwargs()
        front_redirect = _front_redirect_url()

        if mode == "redirect":
            resp = RedirectResponse(url=front_redirect, status_code=302)
            resp.set_cookie("access_token", access_token, **cookie_kw)
            resp.set_cookie("refresh_token", refresh_token, **cookie_kw)
            return resp

        if mode == "popup":
            origin = _front_origin()
            html = f"""
            <!doctype html>
            <meta charset="utf-8">
            <script>
              (function(){{
                try {{
                  const payload = {{ token: "{access_token}", refresh: "{refresh_token}" }};
                  if (window.opener) {{
                    window.opener.postMessage(payload, "{origin}");
                  }}
                }} catch(e) {{
                  console.error(e);
                }} finally {{
                  window.close();
                }}
              }})();
            </script>
            """
            resp = HTMLResponse(content=html)
            # 팝업 흐름에서도 백엔드 도메인에 쿠키 심어둠
            resp.set_cookie("access_token", access_token, **cookie_kw)
            resp.set_cookie("refresh_token", refresh_token, **cookie_kw)
            return resp

        # fallback: JSON
        resp = JSONResponse({
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {"id": user.id, "nickname": user.nickname},
        })
        resp.set_cookie("access_token", access_token, **cookie_kw)
        resp.set_cookie("refresh_token", refresh_token, **cookie_kw)
        return resp

    except HTTPException:
        raise
    except Exception as e:
        # 개발 편의상 detail에 원인 출력 (운영에서는 일반화된 메시지 권장)
        raise HTTPException(status_code=500, detail=f"카카오 로그인 처리 중 오류: {e}")


# ─────────────────────────────────────────────────────────────
# 3) 로그아웃: refreshToken 무효화 + 쿠키 즉시 삭제
# ─────────────────────────────────────────────────────────────
@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.refresh_token = None
    db.commit()

    resp = JSONResponse({"message": "로그아웃되었습니다."})
    delete_kw = _delete_cookie_kwargs()
    for name in ("access_token", "refresh_token"):
        resp.delete_cookie(name, **delete_kw)
    return resp
