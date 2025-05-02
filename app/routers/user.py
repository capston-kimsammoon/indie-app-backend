# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from db.database import get_db
# from models.user import User as UserModel
# from schemas.user import UserCreate, UserRead

# router = APIRouter(prefix="/users", tags=["users"])

# # 사용자 생성
# @router.post("/", response_model=UserRead)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = db.query(UserModel).filter(UserModel.kakao_id == user.kakao_id).first()
#     if db_user:
#         raise HTTPException(status_code=400, detail="User already registered")
    
#     new_user = UserModel(**user.dict())
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

# # 사용자 조회
# @router.get("/{user_id}", response_model=UserRead)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(UserModel).filter(UserModel.id == user_id).first()
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user
