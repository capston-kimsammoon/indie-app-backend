# app/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

def build_database_url() -> str:
    user = settings.DB_USER
    password = settings.DB_PASSWORD
    name = settings.DB_NAME

    # Cloud Run: INSTANCE_CONNECTION_NAME이 있고 DB_HOST가 비어있으면 유닉스 소켓 사용
    if settings.INSTANCE_CONNECTION_NAME and not settings.DB_HOST:
        socket_dir = "/cloudsql"
        unix_socket = f"{socket_dir}/{settings.INSTANCE_CONNECTION_NAME}"
        return f"mysql+pymysql://{user}:{password}@/{name}?unix_socket={unix_socket}&charset=utf8mb4"

    # 로컬(프록시) 또는 명시적 호스트
    host = settings.DB_HOST or "127.0.0.1"
    port = settings.DB_PORT or "3306"
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}?charset=utf8mb4"

DATABASE_URL = build_database_url()

# 연결 튼튼하게
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# FastAPI DB dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
