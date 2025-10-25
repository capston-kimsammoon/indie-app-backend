# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
import random
import string
import requests
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
from app.utils.auth.kakao import get_kakao_access_token, get_kakao_user_info, kakao_unlink

# models
from app.models.user import User
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm
from app.models.review import Review
from app.models.review_like import ReviewLike
from app.models.stamp import Stamp
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_performance_ticketalarm import UserPerformanceTicketAlarm

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
    로그인 성공 후 프론트로 이동할 URL. 운영에서는 환경변수로 고정해야 함.
    예) https://modiemodie.com/login/success
    """
    return (
        getattr(app_settings, "FRONT_REDIRECT_URL", None)
        or os.getenv("FRONT_REDIRECT_URL")
        or "https://modiemodie.com/login/success"
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
def get_kakao_login_url(client: str = Query("web"), force: bool = Query(False)):
    kakao_client_id = app_settings.KAKAO_REST_API_KEY
    redirect_uri = app_settings.KAKAO_REDIRECT_URI 

    # state에 모드 표시 (예: native:랜덤값)
    mode_prefix = "native:" if client == "native" else "web:"
    state = mode_prefix + token_urlsafe(16)

    login_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={kakao_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&state={state}"
    )
    if force:
        login_url += "&prompt=login"  # 계정 선택 강제

    return {"loginUrl": login_url, "state": state, "client": client}


# ─────────────────────────────────────────────────────────────
# 2) 콜백: code -> kakao token -> kakao me -> DB upsert
#    토큰 쿠키로 심고 리다이렉트/팝업/JSON
# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
# 2) 콜백: code -> kakao token -> kakao me -> DB upsert
#    토큰 쿠키로 심고 리다이렉트/팝업/JSON
# ─────────────────────────────────────────────────────────────
@router.get("/callback")
def kakao_callback(
    code: str,
    db: Session = Depends(get_db),
    state: str = Query(...),
):
    try:
        # state에서 모드 추출
        if state.startswith("native:"):
            mode = "native"
            real_state = state[len("native:"):]
        else:
            mode = "redirect"
            real_state = state[len("web:"):] if state.startswith("web:") else state

        # 1) 카카오 토큰/정보
        kakao_access_token = get_kakao_access_token(code)
        kakao_user_info = get_kakao_user_info(kakao_access_token)
        kakao_id = str(kakao_user_info["id"])
        acc = kakao_user_info.get("kakao_account") or {}
        prof = acc.get("profile") or {}
        base_nickname = (prof.get("nickname") or "").strip() or "user"
        profile_url: Optional[str] = prof.get("profile_image_url")

        # 2) DB upsert
        user: Optional[User] = db.query(User).filter(User.kakao_id == kakao_id).first()
        if not user:
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
                raise HTTPException(status_code=400, detail="닉네임 생성 실패.")
        else:
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

        # 3) 토큰 발급
        access_token = auth_utils.create_access_token(user.id)
        refresh_token = auth_utils.create_refresh_token(user.id)
        user.refresh_token = refresh_token
        db.commit()

        cookie_kw = _cookie_kwargs()
        front_redirect = _front_redirect_url()

        # ───── 웹/팝업 ─────
        if mode == "redirect":
            resp = RedirectResponse(url=front_redirect)
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
            resp = HTMLResponse(html)
            resp.set_cookie("access_token", access_token, **cookie_kw)
            resp.set_cookie("refresh_token", refresh_token, **cookie_kw)
            return resp

        # ───── 네이티브 앱 ─────
        if mode == "native":
            native_scheme = "indieapp://auth/callback"
            redirect_url = f"{native_scheme}?access={access_token}&refresh={refresh_token}"
            return RedirectResponse(redirect_url)

        # ───── fallback JSON ─────
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

def kakao_unlink_admin():
    """
    카카오 Admin Key를 사용한 사용자 unlink
    """
    url = "https://kapi.kakao.com/v1/user/unlink"
    headers = {"Authorization": f"KakaoAK {app_settings.KAKAO_ADMIN_KEY}"}
    res = requests.post(url, headers=headers)
    res.raise_for_status()
    return res.json()
    
# ─────────────────────────────────────────────────────────────
# 4) 회원 탈퇴
# ─────────────────────────────────────────────────────────────
@router.delete("/withdraw")
async def withdraw_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1) 카카오 연결 해제 (있을 때만)
    if getattr(current_user, "kakao_id", None):
        try:
            kakao_unlink(current_user.kakao_id)
        except Exception as e:
            print("[kakao_unlink:error]", e)

    # 2) 사용자 관련 하위 테이블 정리 (FK 먼저 삭제)
    def _del(model):
        try:
            db.query(model).filter_by(user_id=current_user.id).delete(synchronize_session=False)
        except Exception as e:
            print(f"[withdraw][cleanup:{model.__name__}]", e)

    _del(UserArtistTicketAlarm)
    _del(UserPerformanceTicketAlarm)
    _del(UserFavoriteArtist)
    _del(UserFavoritePerformance)
    _del(ReviewLike)
    _del(Stamp)
    _del(Review)

    # 3) 유저 삭제
    db.flush()
    db.delete(current_user)
    db.commit()

    # 4) 쿠키 제거
    resp = JSONResponse({"message": "탈퇴되었습니다."})
    delete_kw = _delete_cookie_kwargs()
    for name in ("access_token", "refresh_token"):
        resp.delete_cookie(name, **delete_kw)
    return resp
