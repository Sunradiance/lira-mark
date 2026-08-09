#!/usr/bin/env python3
"""Quick face stack probe — run when Tilen sees 404s."""
from __future__ import annotations

import json
import urllib.error
import urllib.request

from lira_config import face_base_url

BASE = face_base_url()
CHECKS = [
    ("GET", "/api/health", None),
    ("GET", "/face.html", None),
    ("GET", "/face-nodes.js", None),
    ("GET", "/lira-points-12500.json", None),
    ("GET", "/api/tts", None),
    ("POST", "/api/speak", {"text": "stack check", "from": "lira"}),
]


def probe(method: str, path: str, body: dict | None) -> tuple[int, str]:
    url = BASE + path
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if data else {},
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            snippet = resp.read(120).decode("utf-8", errors="replace").replace("\n", " ")
            return resp.status, snippet[:80]
    except urllib.error.HTTPError as exc:
        return exc.code, exc.reason
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return 0, str(exc)


def main() -> None:
    print(f"probing {BASE}")
    ok = 0
    for method, path, body in CHECKS:
        code, msg = probe(method, path, body)
        mark = "OK" if code == 200 else "FAIL"
        if code == 200:
            ok += 1
        print(f"  [{mark}] {code} {method} {path} — {msg}")
    print(f"{ok}/{len(CHECKS)} passed")
    if ok < len(CHECKS):
        raise SystemExit(1)


if __name__ == "__main__":
    main()