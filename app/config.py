# app/config.py

from pydantic_settings  import BaseSettings

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
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
