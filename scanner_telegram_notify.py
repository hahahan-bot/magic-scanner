# -*- coding: utf-8 -*-
"""섹터 스캐너 결과(relay/sp500 JSON)를 읽어 피크 경고·Grade A 시 텔레그램 알림.

환경변수: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (telegram_secrets.cmd 와 동일)
중복 방지: state-dir 에 scanner_telegram_notify_state.json (해시 비교)
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

from telegram_notify import credentials_from_env, send_telegram

DEFAULT_PWA_URL = "https://hahahan-bot.github.io/magic-scanner/pwa/index.html"
STATE_FILENAME = "scanner_telegram_notify_state.json"

MARKET_FILES = {
    "kospi": "relay_universe.json",
    "sp500": "sp500_universe.json",
}

LABELS = {
    "kospi": "코스피",
    "sp500": "S&P 500",
}


def _score(s: dict[str, Any]) -> float:
    v = s.get("signal_score")
    if v is None:
        v = s.get("score")
    return float(v) if v is not None else 0.0


def collect_grade_a(data: dict[str, Any]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}

    def add(st: dict[str, Any], sector_label: str | None = None) -> None:
        if not st or st.get("grade") != "A":
            return
        t = str(st.get("ticker") or st.get("code") or "").strip()
        if not t or t in seen:
            return
        sec = st.get("sector") or sector_label or "—"
        seen[t] = {**st, "sector": sec}

    for c in data.get("candidates") or []:
        add(c)
    for c in data.get("watchlist") or []:
        add(c)
    all_sec = data.get("all_sectors")
    if isinstance(all_sec, dict):
        for sec_key, sv in all_sec.items():
            if not isinstance(sv, dict):
                continue
            for row in sv.get("stocks") or []:
                if isinstance(row, dict):
                    add(row, sec_key)
    return sorted(seen.values(), key=lambda x: -_score(x))


def fingerprint(peak: bool, reasoning: str, tickers_a: list[str]) -> str:
    payload = json.dumps(
        {"peak": peak, "reasoning": reasoning or "", "a": sorted(tickers_a)},
        ensure_ascii=False,
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_message(
    market: str,
    data: dict[str, Any],
    grade_a: list[dict[str, Any]],
    pwa_url: str,
) -> str:
    label = LABELS.get(market, market)
    gen = data.get("generated_at") or "—"
    ns = data.get("next_sectors") or {}
    peak = bool(ns.get("current_peak_risk"))
    lines = [f"[섹터스캐너 · {label}]", gen, ""]

    if peak and ns.get("reasoning"):
        lines.append("⚠ 피크 경고")
        lines.append(str(ns["reasoning"]))
        lines.append("")

    hc = ns.get("high_conviction") or []
    if hc:
        lines.append("고확신: " + " · ".join(str(x) for x in hc))
    nic = ns.get("next_in_cycle") or []
    if nic:
        lines.append("순환 대기: " + " · ".join(str(x) for x in nic))
    rr = ns.get("rs_rising") or []
    if rr:
        lines.append("RS 상승: " + " · ".join(str(x) for x in rr) + " ↑")
    if hc or nic or rr:
        lines.append("")

    if grade_a:
        lines.append(f"Grade A ({len(grade_a)}종)")
        for s in grade_a[:30]:
            lines.append(
                f" · {s.get('ticker','')} {_score(s):.0f}  {s.get('sector','')}"
                + (f"  {s.get('entry_signal')}" if s.get("entry_signal") else "")
            )
        if len(grade_a) > 30:
            lines.append(f" … 외 {len(grade_a) - 30}종")
    else:
        lines.append("Grade A: 없음")

    lines.append("")
    lines.append(f"앱: {pwa_url}")
    return "\n".join(lines)[:4096]


def load_state(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        return raw if isinstance(raw, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_state(path: Path, state: dict[str, str]) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except OSError as e:
        print(f"[scanner-notify] state 저장 실패: {e}", file=sys.stderr)


def main() -> int:
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    ap = argparse.ArgumentParser(description="섹터 스캐너 피크·Grade A 텔레그램 알림")
    ap.add_argument("--state-dir", required=True, help="relay/sp500 JSON 및 state 파일 디렉터리")
    ap.add_argument(
        "--market",
        choices=sorted(MARKET_FILES.keys()),
        required=True,
    )
    ap.add_argument("--dry-run", action="store_true", help="전송 없이 메시지만 출력")
    ap.add_argument("--force", action="store_true", help="중복 해시와 관계없이 전송")
    args = ap.parse_args()

    base = Path(args.state_dir).resolve()
    fname = MARKET_FILES[args.market]
    jpath = base / fname
    if not jpath.is_file():
        print(f"[scanner-notify] 파일 없음: {jpath}", file=sys.stderr)
        return 1
    try:
        with open(jpath, encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[scanner-notify] JSON 읽기 실패: {e}", file=sys.stderr)
        return 1

    if not isinstance(data, dict):
        print("[scanner-notify] 잘못된 JSON 루트", file=sys.stderr)
        return 1

    ns = data.get("next_sectors") or {}
    peak = bool(ns.get("current_peak_risk"))
    reasoning = str(ns.get("reasoning") or "")
    grade_a = collect_grade_a(data)
    tickers = [str(s.get("ticker") or "") for s in grade_a]

    if not peak and not grade_a:
        print("[scanner-notify] 피크 경고 없음 · Grade A 없음 — 알림 생략")
        return 0

    fp = fingerprint(peak, reasoning, tickers)
    state_path = base / STATE_FILENAME
    state = load_state(state_path)
    key = args.market
    prev = state.get(key) if isinstance(state.get(key), str) else None

    if not args.force and prev == fp:
        print("[scanner-notify] 내용 동일 — 텔레그램 생략")
        return 0

    pwa_url = (os.environ.get("SCANNER_PWA_URL") or "").strip() or DEFAULT_PWA_URL
    body = build_message(args.market, data, grade_a, pwa_url)

    if args.dry_run:
        print(body)
        return 0

    tok, cid = credentials_from_env()
    if not tok or not cid:
        print(
            "[scanner-notify] TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID 없음 — "
            "telegram_secrets.cmd 설정 후 재실행",
            file=sys.stderr,
        )
        return 2

    if send_telegram(body):
        print("[scanner-notify] 텔레그램 전송됨")
        state[key] = fp
        save_state(state_path, state)
        return 0
    print("[scanner-notify] 텔레그램 전송 실패", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
