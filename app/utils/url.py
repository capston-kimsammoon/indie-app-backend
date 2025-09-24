# app/utils/url.py
def to_abs(base: str, u: str | None) -> str | None:
    if not u:
        return None
    u = u.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    if u.startswith("/"):
        return f"{base.rstrip('/')}{u}"
    return f"{base.rstrip('/')}/static/uploads/{u}"
