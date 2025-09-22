# app/utils/dependency.py
from typing import Optional

from fastapi import Depends, HTTPException, Cookie
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.config import settings as app_settings

# ===== JWT 설정 =====
SECRET_KEY: Optional[str] = getattr(app_settings, "JWT_SECRET_KEY", None) or getattr(
    app_settings, "JWT_SECRET", None
)
ALGORITHM: str = getattr(app_settings, "JWT_ALGORITHM", "HS256")

if not SECRET_KEY:
    # 환경설정에 비밀키가 없으면 앱 부팅 시 바로 알려주자
    raise RuntimeError(
        "JWT secret not configured. Set JWT_SECRET_KEY (or JWT_SECRET) in your settings/.env"
    )

# 디버그 로그 토글 (원하면 .env에 DEBUG_AUTH=1 추가)
DEBUG_AUTH: bool = str(getattr(app_settings, "DEBUG_AUTH", "0")).lower() in {"1", "true", "yes"}


def _get_user_from_token(token: str, db: Session) -> Optional[User]:
    """
    access_token(JWT) → payload.sub → DB user 조회
    sub에는 반드시 'DB user.id'가 들어가야 한다.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        user_id = int(sub) if sub is not None else None
        if not user_id:
            return None
    except (JWTError, ValueError):
        # 서명 불일치/만료/형변환 실패 모두 None
        return None

    return db.query(User).filter(User.id == user_id).first()


# ✅ 로그인 필수: 쿠키 없거나 토큰이 잘못되면 401
def get_current_user(
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None, alias="access_token"),
) -> User:
    if not access_token:
        if DEBUG_AUTH:
            print("[get_current_user] no access_token cookie")
        raise HTTPException(status_code=401, detail="Not authenticated")

    # 디버그용: 토큰 payload 확인 (서명검증 없이 클레임만)
    if DEBUG_AUTH:
        try:
            claims = jwt.get_unverified_claims(access_token)
            print(f"[get_current_user] token.sub={claims.get('sub')}")
        except Exception as e:
            print(f"[get_current_user] get_unverified_claims error: {e}")

    user = _get_user_from_token(access_token, db)
    if not user:
        if DEBUG_AUTH:
            print("[get_current_user] token invalid or user not found")
        raise HTTPException(status_code=401, detail="Invalid authentication")

    return user


# ✅ 로그인 선택: 없으면 None
def get_current_user_optional(
    db: Session = Depends(get_db),
    access_token: Optional[str] = Cookie(default=None, alias="access_token"),
) -> Optional[User]:
    if not access_token:
        if DEBUG_AUTH:
            print("[get_current_user_optional] no access_token cookie")
        return None

    user = _get_user_from_token(access_token, db)
    if not user and DEBUG_AUTH:
        print("[get_current_user_optional] token invalid or user not found")
    return user
