# -*- coding: utf-8 -*-
"""Telegram bot sendMessage (stdlib only). Env: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional


def credentials_from_env() -> tuple[Optional[str], Optional[str]]:
    token = (os.environ.get("TELEGRAM_BOT_TOKEN") or "").strip()
    chat_id = (os.environ.get("TELEGRAM_CHAT_ID") or "").strip()
    if not token or not chat_id:
        return None, None
    return token, chat_id


def send_telegram(
    text: str,
    *,
    token: Optional[str] = None,
    chat_id: Optional[str] = None,
    timeout_sec: float = 20.0,
) -> bool:
    if token is None or chat_id is None:
        token, chat_id = credentials_from_env()
    if not token or not chat_id:
        return False
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    body = urllib.parse.urlencode({"chat_id": chat_id, "text": text[:4096]}).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            raw = resp.read().decode("utf-8")
        j = json.loads(raw)
        if not j.get("ok"):
            print(f"[telegram] sendMessage not ok: {j}")
            return False
        return True
    except urllib.error.URLError as e:
        print(f"[telegram] URLError: {e}")
        return False
