from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# 회원 생성 시 사용하는 모델(내부적으로만 사용)
class UserCreate(BaseModel):
    kakao_id: str
    nickname: str

# 유저 정보 조회 응답 모델(게시물 등에서 사용)
class UserRead(BaseModel):
    id: int
    kakao_id: str
    nickname: str
    profile_url: Optional[str]

    class Config:
        from_attributes = True

# 마이페이지 정보 조회 응답 모델
class UserMyPageResponse(BaseModel):
    id: int
    nickname: str
    profile_url: Optional[str] = None
    alarm_enabled: bool
    location_enabled: bool

# 닉네임 수정 요청 모델
class UserUpdateNickname(BaseModel):
    nickname: str

# 프로필 이미지 변경 응답 모델
class UserProfileImageResponse(BaseModel):
    message: str
    profileImageUrl: Optional[str] = None 

# 공연 알림/위치 설정 변경 요청 모델
class UserSettingUpdateRequest(BaseModel):
    alarm_enabled: bool
    location_enabled: bool

# 공연 알림/위치 설정 변경 응답 모델    
class UserSettingUpdateResponse(BaseModel):
    message: str
    alarm_enabled: bool
    location_enabled: bool