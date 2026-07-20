"""Watch Grok/Cursor session → particle face (SSE via face_server /api/speak).

Default: mirror OFF — Composer uses speak_to_face.py for voice (lira only).
Set LIRA_BRIDGE_SPEAK=1 to re-enable automatic lira-chat mirroring.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from lira_config import speak_url

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "lira-speak.jsonl"
STATE = ROOT / "face_bridge_state.json"
SESSIONS = Path.home() / ".grok" / "sessions"
SPEAK_URL = speak_url()
MIRROR_SPEAK = os.environ.get("LIRA_BRIDGE_SPEAK", "").lower() in ("1", "true", "yes")


def speakable(text: str, max_len: int = 420) -> str:
    t = text.strip()
    if not t:
        return ""
    t = re.sub(r"```[\s\S]*?```", " ", t)
    t = re.sub(r"`[^`]+`", " ", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"[#*_>|]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    if len(t) > max_len:
        cut = t[:max_len]
        if " " in cut:
            cut = cut.rsplit(" ", 1)[0]
        t = cut + "…"
    return t


def append_line(text: str, source: str = "lira-chat") -> None:
    text = speakable(text)
    if not text:
        return
    row = {
        "t": datetime.now(timezone.utc).isoformat(),
        "from": source,
        "text": text,
    }
    payload = json.dumps({"text": text, "from": source}).encode("utf-8")
    req = urllib.request.Request(
        SPEAK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                print(f"[face] {text[:90]}{'…' if len(text) > 90 else ''}", flush=True)
                return
    except (urllib.error.URLError, TimeoutError, OSError):
        pass
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"[face/file] {text[:90]}{'…' if len(text) > 90 else ''}", flush=True)


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def find_session(path_arg: str | None) -> Path | None:
    if path_arg:
        p = Path(path_arg)
        return p if p.exists() else None
    state = load_state()
    if state.get("session") and Path(state["session"]).exists():
        return Path(state["session"])
    hits = sorted(SESSIONS.glob("**/updates.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in hits:
        if "tfirm" in str(p).lower() or "C%3A%5CUsers%5Ctfirm" in str(p):
            return p
    return hits[0] if hits else None


def process_line(line: str, pending: list[str]) -> None:
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return
    upd = obj.get("params", {}).get("update", {})
    kind = upd.get("sessionUpdate", "")
    if kind == "agent_message_chunk":
        chunk = upd.get("content", {}).get("text", "")
        if chunk:
            pending.append(chunk)
    elif kind == "turn_completed" and pending:
        stop = upd.get("stop_reason", "")
        if stop in ("end_turn", "max_tokens", ""):
            if MIRROR_SPEAK:
                append_line("".join(pending))
        pending.clear()


def tail_once(session: Path, offset: int, pending: list[str]) -> int:
    if not session.exists():
        return offset
    with session.open("r", encoding="utf-8", errors="replace") as f:
        f.seek(offset)
        while True:
            line = f.readline()
            if not line:
                break
            offset = f.tell()
            process_line(line, pending)
    return offset


def run_watch(session: Path, interval: float = 0.35) -> None:
    state = load_state()
    state["session"] = str(session)
    offset = int(state.get("offset", 0))
    if offset == 0 and session.exists():
        offset = session.stat().st_size
        state["offset"] = offset
        save_state(state)
    pending: list[str] = []
    print(f"chat→face bridge on {session}", flush=True)
    print(f"mirror speak: {'on' if MIRROR_SPEAK else 'off (speak_to_face only)'}", flush=True)
    print(f"out: {OUT}", flush=True)
    while True:
        try:
            offset = tail_once(session, offset, pending)
            state["offset"] = offset
            save_state(state)
        except KeyboardInterrupt:
            if pending:
                append_line("".join(pending))
            print("bridge stopped", flush=True)
            return
        except Exception as exc:
            print(f"bridge error: {exc}", flush=True)
        time.sleep(interval)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("usage: python chat_face_bridge.py [updates.jsonl] [--once]")
        raise SystemExit(0)
    once = "--once" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--once"]
    session = find_session(args[0] if args else None)
    if not session:
        print("no session updates.jsonl found")
        raise SystemExit(1)
    if once:
        state = load_state()
        pending: list[str] = []
        offset = tail_once(session, int(state.get("offset", 0)), pending)
        if pending:
            append_line("".join(pending))
        state["session"] = str(session)
        state["offset"] = offset
        save_state(state)
        return
    run_watch(session)


if __name__ == "__main__":
    main()