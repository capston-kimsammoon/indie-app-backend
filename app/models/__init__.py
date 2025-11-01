# app/models/__init__.py
from app.database import Base
from .mood import Mood
from .mood import MoodRecommendation

from .artist import Artist
from .notification import Notification
from .performance_artist import PerformanceArtist
from .performance import Performance
from .user_artist_ticketalarm import UserArtistTicketAlarm
from .user_favorite_artist import UserFavoriteArtist
from .user_favorite_performance import UserFavoritePerformance
from .user_performance_ticketalarm import UserPerformanceTicketAlarm
from .user import User
from .venue import Venue


from .review_like import ReviewLike
from .review_image import ReviewImage
from .review import Review

from .stamp import Stamp
from .magazine import Magazine
from .magazine_block import MagazineBlock   

from .review_report import ReviewReport



#  새로 추가 (뮤직 매거진)
from .music_magazine import MusicMagazine
from .music_magazine_block import MusicMagazineBlock