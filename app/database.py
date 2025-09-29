# app/database.py
from __future__ import annotations
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app.config import settings

DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
INSTANCE = settings.INSTANCE_CONNECTION_NAME  # 배포 환경에서만 설정
DB_HOST = settings.DB_HOST
DB_PORT = int(getattr(settings, "DB_PORT", 3306))

if INSTANCE:
    # Cloud Run: Cloud SQL 유닉스 소켓
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}"
        f"?unix_socket=/cloudsql/{INSTANCE}&charset=utf8mb4"
    )
else:
    # 로컬: Cloud SQL Proxy(TCP)
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )

# 커넥션 풀 설정(안정성)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
