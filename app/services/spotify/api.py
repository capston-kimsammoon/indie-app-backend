# 서비스 운영용 FastAPI 백엔드
# 사용자가 특정 아티스트 요청했을 때 DB에 없으면 spotify에서 검색해서 저장 후 반환

def get_artist_profile(sp, artist_name):
    try:
        results = sp.search(q=f'artist:{artist_name}', type='artist', limit=1)
        items = results['artists']['items']
        if not items:
            return None
        artist = items[0]
        return {
            "name": artist["name"],
            "image_url": artist["images"][0]["url"] if artist["images"] else None,
            "spotify_url": artist["external_urls"]["spotify"]
        }
    except Exception as e:
        print(f"❌ {artist_name} 검색 실패: {e}")
        return None
