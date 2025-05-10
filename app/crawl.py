# app/crawl.py
# 실행: python -m app.crawl

from app.services.instagram.get_post import get_posts_from_all_accounts

if __name__ == "__main__":
    get_posts_from_all_accounts()
