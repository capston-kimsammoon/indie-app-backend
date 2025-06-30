# 한 번만 실행되는 일회성 스크립트
# 수동으로 spotify 플레이리스트에서 아티스트를 긁어와 DB나 엑셀에 저장

# market=kR로 검색을 한국 시장으로 한정
# 아티스트 이름 완전 일치 우선 (EX. '아이유' != 'IU')
# 없을 경우 대체로 첫 번째 검색 결과 사용 

import pandas as pd
from app.services.spotify.client import get_spotify_client
from app.services.spotify.api import get_artist_profile
from spotipy.exceptions import SpotifyException

sp = get_spotify_client()

playlist_url = "https://open.spotify.com/playlist/6JHrQ81tKu9IhAzt4Nn44A?si=dGJh0BOeQueAZu3lfOs7rQ"
playlist_id = playlist_url.split("/")[-1].split("?")[0]

def get_artists_from_playlist(sp, playlist_id):
    results = sp.playlist_items(playlist_id)
    artists = set()

    while results:
        for item in results["items"]:
            track = item.get("track")
            if track:
                artists.add(track["artists"][0]["name"])
        results = sp.next(results) if results.get("next") else None

    return sorted(artists)


def get_artist_profile(sp, artist_name):
    try:
        results = sp.search(q=artist_name, type='artist', limit=10, market="KR")
        items = results['artists']['items']

        if not items:
            print(f"❌ '{artist_name}' 검색 결과 없음.")
            return None

        # 이름이 대소문자까지 완전히 일치해야만 통과
        for artist in items:
            if artist['name'].strip() == artist_name.strip():
                print(f"✅ 정확히 일치: '{artist_name}' → '{artist['name']}'")
                image_url = artist['images'][0]['url'] if artist['images'] else None
                spotify_url = artist['external_urls']['spotify']

                return {
                    'name': artist['name'],
                    'image_url': image_url,
                    'spotify_url': spotify_url
                }

        # 아무 일치 없음
        print(f"⚠️ 정확히 일치하는 아티스트 없음: '{artist_name}'")
        print("   🔍 후보:", [a['name'] for a in items])
        return None

    except SpotifyException as e:
        print(f"❌ Spotify API 오류: {e}")
        return None
    except Exception as e:
        print(f"❌ '{artist_name}' 처리 중 오류 발생: {e}")
        return None



def format_artist_info(artist):
    return {
        "name": artist["name"],
        "image_url": artist["images"][0]["url"] if artist["images"] else None,
        "spotify_url": artist["external_urls"]["spotify"]
    }


    
if __name__ == "__main__":
    artist_names = get_artists_from_playlist(sp, playlist_id)

    artist_data = []
    for name in artist_names:
        info = get_artist_profile(sp, name)
        if info:
            artist_data.append(info)

    df = pd.DataFrame(artist_data)
    df.to_excel("artist_list_2.xlsx", index=False)
    print("✅ artist_list_2.xlsx 저장 완료!")
