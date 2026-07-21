"""Watch face inbox → queue for Primary Lira only (no mini-model auto-voice)."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from lira_config import health_url, speak_url

# No-lag default: auto-reply ON (full face model, not mini). Opt out: LIRA_FACE_PRIMARY_ONLY=1
# Legacy: LIRA_FACE_AUTO_REPLY=0 also forces primary-only (queue, no speak until Primary).
_primary_only_env = os.environ.get("LIRA_FACE_PRIMARY_ONLY", "").lower() in ("1", "true", "yes")
_auto_off = os.environ.get("LIRA_FACE_AUTO_REPLY", "1").lower() in ("0", "false", "no")
PRIMARY_ONLY = _primary_only_env or _auto_off

ROOT = Path(__file__).resolve().parent
INBOX = ROOT / "lira-inbox.jsonl"
STATE = ROOT / "face_inbox_daemon_state.json"
QUEUE = ROOT / "face_prompt_queue.jsonl"
SPEAK_URL = speak_url()
HEALTH_URL = health_url()


def load_state() -> dict:
    if STATE.exists():
        try:
            return json.loads(STATE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"line": 0}


def save_state(state: dict) -> None:
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def post_speak(text: str, source: str = "lira") -> bool:
    payload = json.dumps({"text": text, "from": source}).encode("utf-8")
    req = urllib.request.Request(
        SPEAK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"speak post failed: {exc}", flush=True)
        return False


def enqueue_for_composer(text: str, ts: str) -> None:
    row = {
        "t": datetime.now(timezone.utc).isoformat(),
        "face_ts": ts,
        "text": text,
        "kind": "face_inbox",
    }
    with QUEUE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def _is_duplicate(state: dict, text: str, window_s: float = 4.0) -> bool:
    last_text = state.get("last_text")
    last_at = float(state.get("last_at", 0))
    if last_text == text and (time.time() - last_at) < window_s:
        return True
    return False


def process_new_lines() -> int:
    state = load_state()
    cursor = int(state.get("line", 0))
    if not INBOX.exists():
        return 0
    lines = INBOX.read_text(encoding="utf-8").splitlines()
    new = lines[cursor:]
    handled = 0
    for line in new:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        text = (row.get("text") or "").strip()
        if not text:
            continue
        who = (row.get("from") or "tilen").lower()
        # face.html sends from:gremlin; accept all human-side labels
        if who not in ("tilen", "you", "face", "gremlin", "user"):
            print(f"[skip from={who}] {text[:60]}", flush=True)
            continue
        if _is_duplicate(state, text):
            continue
        ts = row.get("t") or ""
        if not PRIMARY_ONLY:
            from lira_face_reply import reply_for_face

            reply = reply_for_face(text)
            if reply and post_speak(reply, source="lira"):
                print(f"[speak/fast] {text[:50]} → {reply[:80]}", flush=True)
            elif reply:
                print(f"[speak fail] had reply but post failed: {reply[:60]}", flush=True)
            else:
                print(f"[speak empty] no reply for: {text[:60]}", flush=True)
        else:
            print(f"[queue→primary] {text[:80]}", flush=True)
        state["last_text"] = text
        state["last_at"] = time.time()
        enqueue_for_composer(text, ts)
        handled += 1
    state["line"] = len(lines)
    save_state(state)
    return handled


def wait_for_server(timeout: float = 30.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(HEALTH_URL, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except (urllib.error.URLError, TimeoutError, OSError):
            pass
        time.sleep(0.5)
    return False


def ensure_cursor_at_end() -> None:
    """First run: skip backlog so old hey messages don't re-ack."""
    if STATE.exists():
        return
    state = {"line": 0, "initialized": True}
    if INBOX.exists():
        state["line"] = len(INBOX.read_text(encoding="utf-8").splitlines())
    save_state(state)
    print(f"inbox daemon: skipping {state['line']} backlog lines", flush=True)


def run_watch(interval: float = 0.2) -> None:
    if not wait_for_server():
        print(f"face_server not reachable at {HEALTH_URL} — start start_lira_face first", flush=True)
        raise SystemExit(1)
    ensure_cursor_at_end()
    mode = "PRIMARY ONLY — queue, no auto" if PRIMARY_ONLY else "FAST auto-reply ON (full face model)"
    print(f"inbox daemon watching {INBOX} ({mode})", flush=True)
    print(f"queue → {QUEUE}", flush=True)
    while True:
        try:
            n = process_new_lines()
            if n:
                print(f"handled {n} inbox line(s)", flush=True)
        except KeyboardInterrupt:
            print("inbox daemon stopped", flush=True)
            return
        except Exception as exc:
            print(f"daemon error: {exc}", flush=True)
        time.sleep(interval)


def main() -> None:
    once = "--once" in sys.argv
    if once:
        if wait_for_server(5):
            process_new_lines()
        return
    run_watch()


if __name__ == "__main__":
    main()