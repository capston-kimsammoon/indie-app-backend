from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    KAKAO_REST_API_KEY: str
    KAKAO_REDIRECT_URI: str
    JWT_SECRET_KEY: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    class Config:
        # .env 파일 경로 명시적 설정
        env_file = ".env"
        env_file_encoding = "utf-8"

# 설정 인스턴스를 생성
settings = Settings()

# JWT_SECRET_KEY는 이제 settings.JWT_SECRET_KEY로 접근 가능
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
