"""Append a line for particle Lira to speak. Usage: python speak_to_face.py "text here" """
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parent / "lira-speak.jsonl"


def main() -> None:
    text = " ".join(sys.argv[1:]).strip()
    if not text and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if not text:
        print("usage: python speak_to_face.py <text>")
        raise SystemExit(1)
    row = {
        "t": datetime.now(timezone.utc).isoformat(),
        "from": "lira",
        "text": text,
    }
    with OUT.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"spoke: {text[:80]}{'…' if len(text) > 80 else ''}")


if __name__ == "__main__":
    main()