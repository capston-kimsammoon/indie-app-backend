# app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")          # 로컬 프록시에서만 사용
DB_PORT = os.getenv("DB_PORT")          # 로컬 프록시에서만 사용
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

def _build_db_url():
    # Cloud Run: INSTANCE_CONNECTION_NAME이 있으면 무조건 유닉스 소켓 사용
    if INSTANCE_CONNECTION_NAME:
        socket_dir = "/cloudsql"
        return (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@/{DB_NAME}"
            f"?unix_socket={socket_dir}/{INSTANCE_CONNECTION_NAME}&charset=utf8mb4"
        )
    # 로컬/프록시: host:port 사용 (예: 127.0.0.1:3307)
    if DB_HOST and DB_PORT:
        return (
            f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
            f"?charset=utf8mb4"
        )
    # 마지막 안전장치: 프록시 기본값(3307)
    return (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@127.0.0.1:3307/{DB_NAME}"
        f"?charset=utf8mb4"
    )

SQLALCHEMY_DATABASE_URL = _build_db_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=3600)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
