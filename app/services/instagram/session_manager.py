# app/services/instagram/session_manager.py
# 인스타그램 세션 저장
from playwright.sync_api import sync_playwright

def save_instagram_login_session(path: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.instagram.com/accounts/login/")
        print("⏳ 30초 안에 인스타그램에 로그인 해주세요")
        page.wait_for_timeout(30000)
        context.storage_state(path=path)
        print("✅ 로그인 세션 저장 완료")
        browser.close()
