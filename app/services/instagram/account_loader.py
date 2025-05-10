# app/services/instagram/account_loader.py
# 공연장 계정 목록 관리
import json
from pathlib import Path

# 계정 목록 불러오기
def load_json(path):
    path = Path(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"파일이 존재하지 않습니다: {path}. 새 파일을 생성합니다.")
        return {}  # 파일이 없을 경우 빈 객체 반환
    except json.JSONDecodeError as e:
        print(f"JSON 파일을 로드할 수 없습니다: {e}. 빈 파일을 반환합니다.")
        return {}  # JSON 오류가 발생한 경우 빈 객체 반환
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}. 빈 파일을 반환합니다.")
        return {}  # 기타 오류 발생 시 빈 객체 반환

# 계정 목록 로드
def load_accounts(path):
    data = load_json(path)
    return data.get("accounts", [])

# previous_posts.json 로드
def load_previous_posts(path):
    return load_json(path)

# 계정 목록 저장하기(json 파일에)
def save_accounts(path, account_list):
    # 부모 디렉토리 없으면 생성
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(account_list, f, ensure_ascii=False, indent=2)

# 계정 목록에 새 계정 추가하기(중복x)
def add_account(new_account):
    accounts = load_accounts()
    if new_account not in accounts:
        accounts.append(new_account)
        save_accounts(accounts)

# 계정 목록에서 계정 제거
def remove_account(account):
    accounts = load_accounts()
    if account in accounts:
        accounts.remove(account)
        save_accounts(accounts)

