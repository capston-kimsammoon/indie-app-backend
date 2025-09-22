import re

def clean_title(title: str) -> str:
    """공연 제목의 중복 문자열을 제거"""
    if not title:
        return title
    normalized = title.strip()
    half = len(normalized) // 2
    first, second = normalized[:half].strip(), normalized[half:].strip()
    if first == second:
        return first
    if re.fullmatch(r'(.)\1+', normalized):
        return normalized[:2]
    return normalized
