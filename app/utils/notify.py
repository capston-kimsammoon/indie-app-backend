# app/utils/notify.py
import httpx
from typing import Optional

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"

async def send_expo_push(token: str, title: str, body: str, payload: Optional[dict] = None):
    """Expo 푸시 토큰으로 알림 발송"""
    if not token:
        return {"error": "no push token"}

    message = {
        "to": token,
        "title": title,
        "body": body,
        "data": payload or {},
        "sound": "default",
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(EXPO_PUSH_URL, json=message)
    return resp.json()
