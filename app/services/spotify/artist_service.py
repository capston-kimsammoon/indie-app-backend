from app.models import Artist
from app.services.spotify.api import get_artist_profile
from app.services.spotify.client import get_spotify_client

sp = get_spotify_client()

def get_or_create_artist(db, artist_name):
    existing = db.query(Artist).filter_by(name=artist_name).first()
    if existing:
        return existing

    profile = get_artist_profile(sp, artist_name)
    if not profile:
        return None

    new_artist = Artist(**profile)
    db.add(new_artist)
    db.commit()
    db.refresh(new_artist)
    return new_artist
