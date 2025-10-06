from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
import datetime
import os
from pathlib import Path

from app.database import get_db
from app.utils.dependency import get_current_user
from app.utils.gcs import upload_to_gcs, delete_from_gcs

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

GCS_BUCKET_URL = f"https://storage.googleapis.com/{os.getenv('GCS_BUCKET_NAME')}/"

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
@router.patch("/me/profile-image", response_model=dict)
async def update_profile_image(
    profileImage: UploadFile = File(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if not profileImage:
        # 이전 이미지 삭제
        if user.profile_url and GCS_BUCKET_URL in user.profile_url:
            delete_from_gcs(user.profile_url)
        
        # DB 기본 이미지 URL로 세팅 (또는 None)
        user.profile_url = None
        db.commit()
        db.refresh(user)
        
        return {
            "message": "기본 이미지로 변경되었습니다.",
            "profileImageUrl": None
        }
    
    # 기존 이미지 삭제
    if user.profile_url:
        delete_from_gcs(user.profile_url)

    # 새 이미지 업로드 (user-profile/{user_id})
    image_url = upload_to_gcs(profileImage, folder=f"user-profile/{user.id}")

    # DB 업데이트
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
