from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings  # settings가 .env를 읽어옵니다.

# settings에서 환경변수 읽기
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD

print(f"DB_HOST: {DB_HOST}")  # 확인용 로그 (개발 중에만 사용)

# SQLAlchemy 접속 URL
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
)

# SQLAlchemy 엔진 생성
engine = create_engine(DATABASE_URL, echo=True)  # echo=True: SQL 실행 로그 보기

# 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모델의 Base 클래스
Base = declarative_base()

# DB 세션 의존성 주입용 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
