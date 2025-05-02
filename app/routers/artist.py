# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from db.database import get_db
# from models.artist import Artist as ArtistModel
# from schemas.artist import ArtistCreate, ArtistRead

# router = APIRouter(prefix="/artists", tags=["artists"])

# # 아티스트 등록
# @router.post("/", response_model=ArtistRead)
# def create_artist(artist: ArtistCreate, db: Session = Depends(get_db)):
#     db_artist = db.query(ArtistModel).filter(ArtistModel.name == artist.name).first()
#     if db_artist:
#         raise HTTPException(status_code=400, detail="Artist already exists")

#     new_artist = ArtistModel(**artist.dict())
#     db.add(new_artist)
#     db.commit()
#     db.refresh(new_artist)
#     return new_artist

# # 아티스트 조회
# @router.get("/{artist_id}", response_model=ArtistRead)
# def read_artist(artist_id: int, db: Session = Depends(get_db)):
#     artist = db.query(ArtistModel).filter(ArtistModel.id == artist_id).first()
#     if artist is None:
#         raise HTTPException(status_code=404, detail="Artist not found")
#     return artist
