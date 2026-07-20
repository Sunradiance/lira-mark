"""Push a line to particle Lira (SSE via face_server). Usage: python speak_to_face.py "text" """
from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from lira_config import speak_url

OUT = Path(__file__).resolve().parent / "lira-speak.jsonl"
SPEAK_URL = speak_url()


def main() -> None:
    text = " ".join(sys.argv[1:]).strip()
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if not text:
        print("usage: python speak_to_face.py <text>")
        raise SystemExit(1)
    payload = json.dumps({"text": text, "from": "lira"}).encode("utf-8")
    req = urllib.request.Request(
        SPEAK_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=4) as resp:
            if resp.status == 200:
                print(f"spoke: {text[:80]}{'…' if len(text) > 80 else ''}")
                return
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        print(f"sse unavailable ({exc}), writing file", flush=True)
    row = {
        "t": datetime.now(timezone.utc).isoformat(),
        "from": "lira",
        "text": text,
    }
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"spoke/file: {text[:80]}{'…' if len(text) > 80 else ''}")


if __name__ == "__main__":
    main()