"""Bundle Lira face stack for migration to another host."""
from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from lira_config import ROOT, face_base_url, sleep_lira_home

OUT_DIR = Path.home() / "Downloads" / "lira_migrate"
ZIP = Path.home() / "Downloads" / "lira_migrate_bundle.zip"

INCLUDE = [
    "face-nodes.js",
    "face.html",
    "face_server.py",
    "face_supervisor.py",
    "face_inbox_daemon.py",
    "chat_face_bridge.py",
    "xai_voice.py",
    "lira_face_reply.py",
    "lira_config.py",
    "speak_to_face.py",
    "peek_face_inbox.py",
    "check_face_stack.py",
    "pack_hologram_mouth.py",
    "pack_migrate.py",
    "lira-points-12500.json",
    "build_points_from_v4.py",
    "start_lira_face.bat",
    "start_lira_face.sh",
    "lira_host.json.example",
]

MIGRATE_TXT = """LIRA FACE — HOST MIGRATION
==========================

1. Unzip to e.g. /opt/lira-mark or C:\\project\\lira-mark

2. Copy lira_host.json.example → lira_host.json and set:
   - public_url: http://YOUR_SERVER:8787
   - sleep_lira: path to sleep_lira (for xAI key + inbox replies)
   OR set env: LIRA_FACE_URL, LIRA_SLEEP_HOME, XAI_API_KEY

3. xAI key (pick one):
   - sleep_lira/secrets.json with "xai_api_key"
   - export XAI_API_KEY=...

4. Start:
   Windows: start_lira_face.bat
   Linux:   chmod +x start_lira_face.sh && ./start_lira_face.sh

5. Open: {url}/face.html  (hard refresh)

6. Verify: python check_face_stack.py

7. Firewall: allow TCP {port}

Files created on first run:
   lira-inbox.jsonl, lira-speak.jsonl, face_inbox_daemon_state.json

Voice needs the Python server (not GitHub Pages alone).
"""


def main() -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    bundle = OUT_DIR / f"lira-mark-{stamp}"
    if bundle.exists():
        shutil.rmtree(bundle)
    mark = bundle / "lira-mark"
    mark.mkdir(parents=True)

    copied = []
    for name in INCLUDE:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, mark / name)
            copied.append(name)

    manifest = {
        "built": datetime.now(timezone.utc).isoformat(),
        "build": "migrate",
        "source": str(ROOT),
        "sleep_lira": str(sleep_lira_home()),
        "public_url": face_base_url(),
        "files": copied,
    }
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    port = manifest.get("port", 8787)
    (bundle / "MIGRATE.txt").write_text(
        MIGRATE_TXT.format(url=face_base_url(), port=8787),
        encoding="utf-8",
    )

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in bundle.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(bundle.parent))

    print(f"bundle → {bundle}")
    print(f"zip    → {ZIP}")
    print(f"files  → {len(copied)}")


if __name__ == "__main__":
    main()