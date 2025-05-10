# # app/routers/posts.py
# from fastapi import APIRouter
# from app.services.instagram.get_post import get_post_info, get_posts_from_all_accounts

# router = APIRouter()

# @router.post("/crawl/{account}")
# def crawl_account(account: str):
#     raw_post = get_post_info(account)
#     if not raw_post:
#         return {"message": "게시물이 없습니다."}

#     # 파싱 함수가 없다면, 그냥 텍스트 그대로 넘기기
#     parsed = raw_post["text"]

#     return {
#         "image": raw_post["image_url"],
#         "info": parsed
#     }
