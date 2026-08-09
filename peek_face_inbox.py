"""Print new face→Lira inbox lines since last peek."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INBOX = ROOT / "lira-inbox.jsonl"
STATE = ROOT / "face_inbox_cursor.json"


def main() -> None:
    cursor = 0
    if STATE.exists():
        try:
            cursor = int(json.loads(STATE.read_text(encoding="utf-8")).get("line", 0))
        except (json.JSONDecodeError, ValueError):
            pass
    if not INBOX.exists():
        return
    lines = INBOX.read_text(encoding="utf-8").splitlines()
    new_lines = lines[cursor:]
    for line in new_lines:
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            print(f"[face→lira] {row.get('text', line)}")
        except json.JSONDecodeError:
            print(f"[face→lira] {line}")
    STATE.write_text(json.dumps({"line": len(lines)}), encoding="utf-8")


if __name__ == "__main__":
    main()