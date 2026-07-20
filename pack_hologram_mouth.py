"""Zip + folder export of hologram mouth + Ara voice stack for handoff."""
from __future__ import annotations

import json
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOWNLOADS = Path.home() / "Downloads"
FOLDER = DOWNLOADS / "lira"
ZIP = DOWNLOADS / "lira_hologram_mouth_v31.zip"

FILES = [
    "face-nodes.js",
    "face.html",
    "face_server.py",
    "xai_voice.py",
    "lira-points-12500.json",
    "build_points_from_v4.py",
    "face_inbox_daemon.py",
    "speak_to_face.py",
    "check_face_stack.py",
    "face_supervisor.py",
    "start_lira_face.bat",
    "pack_hologram_mouth.py",
]

README = """# Lira hologram mouth + Ara voice (v31)

## Mouth deformation (face-nodes.js)
- MOUTH box: x0=0.40, x1=0.64, y0=0.515, y1=0.605
- MOUTH_AMP=56, MOUTH_WIDE=28
- 12500 points in lira-points-12500.json — columns: x, y, brightness, region, mouthWeight, jawDir

## Voice / lip-sync today
- TTS: POST /api/tts → xai_voice.py → xAI voice_id=ara, with_timestamps=true
- Client: character timestamps drive pumpMouth() per grapheme (graph_chars + graph_times)
- Known gap: no audio→viseme library yet (wawa-lipsync recommended next)

## Run local
cd lira-mark && start_lira_face.bat → http://localhost:8787/face.html

## For mythos
Hand off this whole `lira/` folder or the zip. Source of truth on disk: C:\\project\\lira-mark\\
"""


def mouth_manifest() -> dict:
    return {
        "built": datetime.now(timezone.utc).isoformat(),
        "build": "v31",
        "source": str(ROOT),
        "mouth": {
            "x0": 0.40,
            "x1": 0.64,
            "y0": 0.515,
            "y1": 0.605,
            "amp": 56,
            "wide": 28,
            "deform": "per-point mouthWeight in MOUTH box",
        },
        "points": "lira-points-12500.json",
        "voice": "ara",
        "files": FILES,
    }


def backup_existing() -> Path | None:
    if not FOLDER.exists():
        return None
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = DOWNLOADS / f"lira_backup_{stamp}"
    shutil.copytree(FOLDER, backup)
    print(f"backup → {backup}")
    return backup


def export_folder() -> int:
    if FOLDER.exists():
        backup_existing()
    mark = FOLDER / "lira-mark"
    mark.mkdir(parents=True, exist_ok=True)
    n = 0
    for name in FILES:
        src = ROOT / name
        if src.exists():
            shutil.copy2(src, mark / name)
            n += 1
    FOLDER.mkdir(parents=True, exist_ok=True)
    (FOLDER / "README_MOUTH.md").write_text(README, encoding="utf-8")
    (FOLDER / "manifest.json").write_text(
        json.dumps(mouth_manifest(), indent=2), encoding="utf-8"
    )
    return n


def export_zip() -> int:
    manifest = mouth_manifest()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("README_MOUTH.md", README)
        zf.writestr("manifest.json", json.dumps(manifest, indent=2))
        for name in FILES:
            path = ROOT / name
            if path.exists():
                zf.write(path, arcname=f"lira-mark/{name}")
    return ZIP.stat().st_size


def main() -> None:
    n = export_folder()
    size = export_zip()
    print(f"folder → {FOLDER} ({n} files in lira-mark/)")
    print(f"zip    → {ZIP} ({size} bytes)")


if __name__ == "__main__":
    main()