# import importlib
# import pkgutil
# from app.database import Base

# for loader, name, is_pkg in pkgutil.iter_modules(__path__):
#     importlib.import_module(f"{__name__}.{name}")

from app.database import Base

from .user import User
from .artist import Artist
from .performance import Performance
from .venue import Venue
from .post import Post
from .comment import Comment
from .performance_artist import PerformanceArtist
from .user_favorite_artist import UserFavoriteArtist
from .user_favorite_performance import UserFavoritePerformance
from .user_performance_ticketalarm import UserPerformanceTicketAlarm
from .user_artist_ticketalarm import UserArtistTicketAlarm
