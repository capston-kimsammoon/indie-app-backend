# app/services/instagram/utils.py
def find_first_match(text, patterns):
    import re
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group().strip()
    return ""