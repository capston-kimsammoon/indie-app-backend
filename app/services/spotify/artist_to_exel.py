import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

# Spotify 인증 정보
CLIENT_ID = "1162b7de8ed24b37abf5ebc5cea2c10a"
CLIENT_SECRET = "55c82038c9ff4ab790b81f118aa6f74f"
REDIRECT_URI = 'http://127.0.0.1:8888/callback'

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope='playlist-read-private'
))

# 플레이리스트 URL → ID 추출
playlist_url = 'https://open.spotify.com/playlist/6JHrQ81tKu9IhAzt4Nn44A?si=dGJh0BOeQueAZu3lfOs7rQ'
playlist_id = playlist_url.split("/")[-1].split("?")[0]

# 아티스트 프로필 추출
def get_artist_profile(artist_name):
    try:
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
        items = results['artists']['items']
        if not items:
            return None

        artist = items[0]
        image_url = artist['images'][0]['url'] if artist['images'] else None
        spotify_url = artist['external_urls']['spotify'] if 'external_urls' in artist else None

        return {
            'name': artist_name,
            'image_url': image_url,
            'spotify_url': spotify_url
        }

    except Exception as e:
        print(f"❌ {artist_name} 처리 중 오류 발생: {e}")
        return None

# 플레이리스트에서 고유 아티스트 목록 추출
def get_artists_from_playlist(playlist_id):
    results = sp.playlist_items(playlist_id)
    artists = set()

    while results:
        for item in results['items']:
            track = item.get('track')
            if track:
                main_artist = track['artists'][0]['name']
                artists.add(main_artist)

        if results.get('next'):
            results = sp.next(results)
        else:
            results = None

    return sorted(list(artists))

# 전체 실행
if __name__ == "__main__":
    artist_list = get_artists_from_playlist(playlist_id)

    artist_data = []
    for artist_name in artist_list:
        info = get_artist_profile(artist_name)
        if info:
            artist_data.append(info)

    if artist_data:
        df = pd.DataFrame(artist_data)
        df.to_excel("artist_list.xlsx", index=False)
        print("✅ artist_list.xlsx 파일이 생성되었습니다.")
    else:
        print("⚠️ 저장할 아티스트 정보가 없습니다.")
