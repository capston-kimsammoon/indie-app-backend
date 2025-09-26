# app/config.py
from __future__ import annotations
import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# 레포 루트의 .env 로드 (로컬 개발용)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

class Settings(BaseSettings):
    # ===== 외부 연동 / 보안 =====
    KAKAO_REST_API_KEY: str
    KAKAO_REDIRECT_URI: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # ===== DB =====
    # 로컬 기본값 제공 → Cloud Run에서는 무시됨(유닉스 소켓 사용)
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Cloud Run 전용(유닉스 소켓). 선택값이어야 함.
    INSTANCE_CONNECTION_NAME: str | None = None

    # pydantic-settings v2 스타일 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # 정의 안 된 env가 있어도 무시
    )

settings = Settings()
