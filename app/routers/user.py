from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
import datetime
import os
from pathlib import Path

from app.database import get_db
from app.utils.dependency import get_current_user

# crud
from app.crud import user as user_crud
from app.crud import user_favorite_performance as fav_perf_crud
from app.crud import user_favorite_artist as fav_artist_crud

# schemas
from app.schemas import user as user_schema
from app.schemas import user_favorite_performance as fav_perf_schema
from app.schemas import user_favorite_artist as fav_artist_schema

# models
from app.models.user import User
from app.models.artist import Artist
from app.models.performance import Performance
from app.models.user_favorite_artist import UserFavoriteArtist
from app.models.user_favorite_performance import UserFavoritePerformance
from app.models.user_artist_ticketalarm import UserArtistTicketAlarm

BASE_DIR = Path(__file__).resolve().parent.parent  # app/ 내부라면
STATIC_DIR = os.path.join(BASE_DIR, "static")

router = APIRouter(
    prefix="/user",
    tags=["User"]
)

# 로그인 후 유저 정보 조회
@router.get("/me", response_model=user_schema.UserMyPageResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return current_user

# 닉네임 수정
@router.patch("/me")
def update_nickname(
    request: user_schema.UserUpdateNickname,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    updated_user = user_crud.update_user_nickname(db, user, request.nickname)
    return {
        "message": "닉네임이 성공적으로 수정되었습니다.",
        "nickname": updated_user.nickname
    }

# 프로필 이미지 변경
@router.patch("/me/profile-image", response_model=user_schema.UserProfileImageResponse)
async def update_profile_image(
    profileImage: UploadFile = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not profileImage:
        raise HTTPException(status_code=400, detail="이미지가 필요합니다")

    save_dir = os.path.join(STATIC_DIR, "profiles")
    os.makedirs(save_dir, exist_ok=True)

    filename = f"{user.id}_{profileImage.filename}"
    save_path = os.path.join(save_dir, filename)

    with open(save_path, "wb") as f:
        f.write(await profileImage.read())

    image_url = f"http://localhost:8000/static/profiles/{user.id}_{profileImage.filename}"

    user.profile_url = image_url
    db.commit()
    db.refresh(user)

    return {
        "message": "프로필 이미지가 성공적으로 변경되었습니다.",
        "profileImageUrl": image_url
    }

# 설정 ON/OFF (알림, 위치)
@router.patch("/me/setting", response_model=user_schema.UserSettingUpdateResponse)
def update_user_settings(
    setting_data: user_schema.UserSettingUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    user.alarm_enabled = setting_data.alarm_enabled
    user.location_enabled = setting_data.location_enabled
    db.commit()
    db.refresh(user)

    return {
        "message": "설정이 성공적으로 변경되었습니다.",
        "alarm_enabled": user.alarm_enabled,
        "location_enabled": user.location_enabled
    }

# 찜한 공연 목록 조회
@router.get("/me/like/performance", response_model=fav_perf_schema.UserLikedPerformanceListResponse)
def get_liked_performances(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * size

    liked_performance_query = (
        db.query(Performance)
        .join(UserFavoritePerformance, UserFavoritePerformance.performance_id == Performance.id)
        .filter(UserFavoritePerformance.user_id == current_user.id)
    )
    total = liked_performance_query.count()
    performances = liked_performance_query.offset(skip).limit(size).all()

    result = [
        fav_perf_schema.UserLikedPerformanceResponse(
            id=p.id,
            title=p.title,
            venue=p.venue.name,
            date=datetime.datetime.combine(p.date, p.time),
            image_url=p.image_url,
            isLiked=True,
        ) for p in performances
    ]

    total_pages = (total + size - 1) // size
    return fav_perf_schema.UserLikedPerformanceListResponse(
        page=page,
        totalPages=total_pages,
        performances=result
    )

# 찜한 아티스트 목록
@router.get("/me/like/artist", response_model=fav_artist_schema.UserLikedArtistListResponse)
def get_liked_artists(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * size

    liked_artist_query = (
        db.query(Artist)
        .join(UserFavoriteArtist, UserFavoriteArtist.artist_id == Artist.id)
        .filter(UserFavoriteArtist.user_id == current_user.id)
    )
    total = liked_artist_query.count()
    artists = liked_artist_query.offset(skip).limit(size).all()

    result = []
    for artist in artists:
        isAlarmEnabled = db.query(UserArtistTicketAlarm).filter_by(
            user_id=current_user.id,
            artist_id=artist.id
        ).first() is not None

        result.append(
            fav_artist_schema.UserLikedArtistResponse(
                id=artist.id,
                name=artist.name,
                image_url=artist.image_url,
                isLiked=True,
                isAlarmEnabled=isAlarmEnabled
            )
        )

    total_pages = (total + size - 1) // size
    return fav_artist_schema.UserLikedArtistListResponse(
        page=page,
        totalPages=total_pages,
        artists=result
    )
