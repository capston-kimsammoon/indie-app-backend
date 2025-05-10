# app/services/instagram/get_post.py
import json, os
from playwright.sync_api import sync_playwright
from .account_loader import load_accounts, load_previous_posts, save_accounts
from .post_manager import is_duplicate_post
from app.database import SessionLocal

LOGIN_STATE_PATH = "app/services/instagram/data/ig_login_state.json"
ACCOUNTS_PATH = "app/services/instagram/data/account_list.json"
PREVIOUS_POSTS_PATH = "app/services/instagram/data/previous_posts.json"
NEW_POSTS_PATH = 'app/services/instagram/data/today_new_posts.json'


# === 최신 게시물의 shortcode만 추출 ===
def get_latest_shortcode(page, account, max_posts_to_check=4):
    try:
        page.goto(f"https://www.instagram.com/{account}/")
        page.wait_for_timeout(3000)

        posts = page.locator('a[href*="/p/"]')
        post_count = posts.count()
        if post_count == 0:
            return None
        
        for i in range(min(post_count, max_posts_to_check)):
            try:
                post_link = posts.nth(i).get_attribute("href")

                shortcode = None
                if post_link:
                    # shortcode 추출
                    parts = post_link.strip("/").split("/")
                    if "p" not in parts:
                        continue
                    p_index = parts.index("p")
                    if len(parts) <= p_index + 1:
                        continue

                    shortcode = parts[p_index + 1]
                    return shortcode
            except Exception as e:
                print(f"❌ Failed to get shortcode @{account}: {e}")
                continue

        return None
    except Exception as e:
        print(f"❌ Failed to access @{account}: {e}")
        return None


# === 게시물 본문과 이미지 추출 (shortcode 확인 이후) ===
def get_post_info(page):
    try:
        page.wait_for_timeout(1000)  # 게시물 열기 후 잠시 대기

        # 본문 추출
        try:
            text = page.locator('div[role="dialog"] h1._ap3a').inner_text()
            print('text: ', text)
        except:
            text = None

        # 이미지 URL 추출
        try:
            image_url = page.locator('div[role="dialog"] img').first.get_attribute("src")
            print('image: ', image_url)
        except:
            image_url = None

        return {"text": text, "image_url": image_url}
    except Exception as e:
        print(f"❌ Failed to extract post info: {e}")
        return None


# === 여러 계정 순회하며 새 게시물 여부 확인 ===
def get_posts_from_all_accounts():
    accounts = load_accounts(ACCOUNTS_PATH)
    previous_posts = load_previous_posts(PREVIOUS_POSTS_PATH)
    # print('accounts: ', accounts)
    # print('previous_posts: ', previous_posts)

    new_posts = {}
    db = SessionLocal()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=LOGIN_STATE_PATH)
        page = context.new_page()

        for account in accounts:
            print(f"🔍 Checking @{account} ...")

            shortcode = get_latest_shortcode(page, account)
            if not shortcode:
                continue

            if previous_posts.get(account) != shortcode and not is_duplicate_post(db, shortcode):
                print(f"🆕 New post found @{account}: {shortcode}")

                # 게시물 클릭 → 게시물 정보 추출
                try:
                    post_link_selector = page.locator(f'a[href*="/p/{shortcode}/"]').first
                    post_link_selector.click()
                    page.wait_for_timeout(3000)

                    post_info = get_post_info(page)
                    if post_info:
                        post_info.update({"account": account, "shortcode": shortcode})
                        # save_post_to_db(post_info)  # 필요 시 DB 저장
                        previous_posts[account] = shortcode
                        new_posts[account] = shortcode
                    else:
                        print(f"⚠️ 게시물 정보 추출 실패 @{account}")
                except Exception as e:
                    print(f"❌ 게시물 클릭 실패 @{account}: {e}")
            else:
                print(f"✅ No new post for @{account}")

        browser.close()
    db.close()

    save_accounts(PREVIOUS_POSTS_PATH, previous_posts)
    if new_posts:
        save_accounts(NEW_POSTS_PATH, new_posts)
