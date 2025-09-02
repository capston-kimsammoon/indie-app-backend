import jwt
from datetime import datetime, timedelta
from app.config import settings  # JWT 비밀 키 설정

# access_token 생성 (15분 유효)
def create_access_token(user_id: int) -> str:
    expiration = datetime.utcnow() + timedelta(minutes=15)  # 15분 동안 유효
    payload = {"user_id": user_id, "exp": expiration}
    access_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return access_token

# refresh_token 생성 (30일 유효)
def create_refresh_token(user_id: int) -> str:
    expiration = datetime.utcnow() + timedelta(days=30)  # 30일 동안 유효
    payload = {"user_id": user_id, "exp": expiration}
    refresh_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    return refresh_token
