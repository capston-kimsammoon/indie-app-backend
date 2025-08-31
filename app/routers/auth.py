from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import os
import random
import string
from secrets import token_urlsafe

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
# 프론트에 카카오 로그인 URL 제공 (force=true면 계정선택 강제)
# ─────────────────────────────────────────────────────────────
@router.get("/kakao/login")
def get_kakao_login_url(force: bool = Query(False)):
    kakao_client_id = app_settings.KAKAO_REST_API_KEY
    redirect_uri = app_settings.KAKAO_REDIRECT_URI

    state = token_urlsafe(16)  # (선택) CSRF 방지용 – 콜백에서 검증하려면 세션/스토리지에 저장 필요

    login_url = (
        "https://kauth.kakao.com/oauth/authorize"
        f"?client_id={kakao_client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&state={state}"
    )

    # ✅ 다른 계정으로 로그인 강제
    if force:
        login_url += "&prompt=login"

    return {"loginUrl": login_url}


# ─────────────────────────────────────────────────────────────
# 콜백: code -> kakao token -> kakao me -> DB upsert
# 그리고 앱 토큰을 쿠키로 심고 프론트로 리다이렉트
# mode=popup 이면 postMessage 로 전달 후 창 닫기
# ─────────────────────────────────────────────────────────────
@router.get("/callback")
def kakao_callback(
    code: str,
    db: Session = Depends(get_db),
    mode: str = Query(default="redirect"),  # redirect | popup | json
):
    try:
        # 1) code -> kakao access_token
        kakao_access_token = get_kakao_access_token(code)

        # 2) kakao me
        kakao_user_info = get_kakao_user_info(kakao_access_token)
        kakao_id = str(kakao_user_info["id"])  # ⚠️ 문자열로 통일
        acc = kakao_user_info.get("kakao_account", {}) or {}
        prof = acc.get("profile", {}) or {}

        base_nickname = (prof.get("nickname") or "").strip() or "user"
        profile_url = prof.get("profile_image_url") or None

        # 3) DB upsert (kakao_id 기준)
        user: User | None = db.query(User).filter(User.kakao_id == kakao_id).first()
        if not user:
            nickname = base_nickname
            # 닉네임 UNIQUE 충돌 시 5회까지 꼬리표 붙여 재시도
            for _ in range(5):
                try:
                    user = User(
                        kakao_id=kakao_id,
                        nickname=nickname,
                        profile_url=profile_url if profile_url is not None else "",
                        alarm_enabled=False,
                        location_enabled=False,
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
                raise HTTPException(status_code=400, detail="닉네임 생성에 실패했습니다. 다시 시도해 주세요.")
        else:
            changed = False
            # 닉네임은 값이 있고 다를 때만 갱신 (유니크 충돌 시 되돌림)
            if base_nickname and user.nickname != base_nickname:
                old = user.nickname
                try:
                    user.nickname = base_nickname
                    db.commit()
                    db.refresh(user)
                    changed = True
                except IntegrityError:
                    db.rollback()
                    user.nickname = old
            if user.alarm_enabled is None:
                user.alarm_enabled = False; changed = True
            if user.location_enabled is None:
                user.location_enabled = False; changed = True
            if profile_url and user.profile_url != profile_url:
                user.profile_url = profile_url; changed = True
            if changed:
                db.commit()
                db.refresh(user)

        # 4) 우리 앱 토큰 생성 및 refresh 저장 (DB user.id 사용!)
        access_token = auth_utils.create_access_token(user.id)
        refresh_token = auth_utils.create_refresh_token(user.id)
        user.refresh_token = refresh_token
        db.commit()

        # 5) 동작 분기: redirect / popup / json
        front_redirect = (
            getattr(app_settings, "FRONT_REDIRECT_URL", None)
            or os.getenv("FRONT_REDIRECT_URL")
            or "http://localhost:3000/login/success"
        )

        cookie_kwargs = dict(
            httponly=True,
            secure=str(os.getenv("COOKIE_SECURE", "false")).lower() in {"1", "true", "yes"},
            samesite=os.getenv("COOKIE_SAMESITE", "Lax"),
            max_age=60 * 60 * 24 * 7,
            path="/",  # ✅ 덮어쓰기 확실히
        )

        if mode == "redirect":
            resp = RedirectResponse(url=front_redirect, status_code=302)
            resp.set_cookie("access_token", access_token, **cookie_kwargs)
            resp.set_cookie("refresh_token", refresh_token, **cookie_kwargs)
            return resp

        if mode == "popup":
            # 부모 창 도메인 추출(대충 프런트 루트)
            base = front_redirect.split("/login")[0]
            html = f"""
            <script>
              (function(){{
                const payload = {{ token: "{access_token}", refresh: "{refresh_token}" }};
                if (window.opener) {{
                  window.opener.postMessage(payload, "{base}");
                }}
                window.close();
              }})();
            </script>
            """
            return HTMLResponse(content=html)

        # fallback: JSON 직접 반환
        return {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "user": {"id": user.id, "nickname": user.nickname},
        }

    except HTTPException:
        raise
    except Exception as e:
        # 예상치 못한 예외는 500 처리
        raise HTTPException(status_code=500, detail=f"카카오 로그인 처리 중 오류 발생: {str(e)}")


# ─────────────────────────────────────────────────────────────
# 로그아웃: refreshToken 무효화
# ─────────────────────────────────────────────────────────────
@router.post("/logout")
def logout_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    current_user.refresh_token = None
    db.commit()
    return {"message": "로그아웃되었습니다."}
