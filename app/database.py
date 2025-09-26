# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings  # pydantic-settings (이미 사용 중)

# .env는 로컬에서만 필요하고, Cloud Run에선 환경변수로 들어옵니다.
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME

# 배포 시에만 설정할 값 (gcloud --set-env-vars 로 주입)
INSTANCE = os.getenv("INSTANCE_CONNECTION_NAME")

# 로컬 기본값 (.env)
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT  # 문자열이어도 SQLAlchemy가 처리함

if INSTANCE:
    # ✅ Cloud Run: Cloud SQL 유닉스 소켓
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}"
        f"?unix_socket=/cloudsql/{INSTANCE}&charset=utf8mb4"
    )
else:
    # ✅ Local: Cloud SQL 프록시(TCP)
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )

# 운영에선 echo=False 권장 (원하면 True)
engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
