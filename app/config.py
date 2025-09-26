from dotenv import load_dotenv
from pydantic_settings import BaseSettings
import os

# .env 파일을 명시적으로 로드
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))  # .env 파일 경로가 맞는지 확인

class Settings(BaseSettings):
    KAKAO_REST_API_KEY: str
    KAKAO_REDIRECT_URI: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    INSTANCE_CONNECTION_NAME: str | None = None   # ✅ 이 줄 추가

    class Config:
        # .env 파일 경로 명시적 설정
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

