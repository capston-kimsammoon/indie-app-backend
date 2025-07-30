from fastapi import FastAPI
from app import models  # ✅ 반드시 먼저 import
from app.database import Base, engine
from app.routers import post, auth, user, search, nearby, venue

app = FastAPI()

# Alembic 사용 시 x
# Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(post.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(search.router)
app.include_router(nearby.router)
app.include_router(venue.router)

@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
