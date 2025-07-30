from fastapi import FastAPI
from app import models 
from app.database import Base, engine
from app.routers import post
from app.routers import performance_home
from app.routers import calender
from app.routers import performance
from app.routers import like_performance
from app.routers import alert_performance
from app.routers import artist
from app.routers.like_artist import router as like_artist_router
from app.routers import post_free
from app.routers import comment
from app.routers import alert_artist
from app.routers import post, auth, user, search, nearby, venue

app = FastAPI()

# Alembic 사용 시 x
Base.metadata.create_all(bind=engine)

# 라우터 등록
app.include_router(post.router)

app.include_router(performance_home.router, prefix="/performance/home")
app.include_router(calender.router)
app.include_router(performance.router)
app.include_router(like_performance.router)
app.include_router(alert_performance.router)
app.include_router(artist.router)
app.include_router(like_artist_router)
app.include_router(post_free.router)
app.include_router(comment.router)
app.include_router(alert_artist.router)
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(search.router)
app.include_router(nearby.router)
app.include_router(venue.router)

@app.get("/")
def root():
    return {"message": "MySQL 테이블 생성 완료 !!"}
