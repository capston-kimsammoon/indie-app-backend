# app/models/__init__.py
from app.database import Base
from .mood import Mood
from .mood import MoodRecommendation

from .artist import Artist
from .comment import Comment
from .notification import Notification
from .performance_artist import PerformanceArtist
from .performance import Performance
from .post_image import PostImage
from .post_like import PostLike
from .post import Post
from .user_artist_ticketalarm import UserArtistTicketAlarm
from .user_favorite_artist import UserFavoriteArtist
from .user_favorite_performance import UserFavoritePerformance
from .user_performance_open_alarm import UserPerformanceOpenAlarm
from .user_performance_ticketalarm import UserPerformanceTicketAlarm
from .user import User
from .venue import Venue

# ✅ 공연장 리뷰만 유지 (공연 리뷰 관련 서브테이블 제거)
from .review import Review

# 그대로 유지
from .stamp import Stamp
from .magazine import Magazine
from .magazine_block import MagazineBlock   