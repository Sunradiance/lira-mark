"""Portable config for Lira face stack — env + optional lira_host.json."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
HOST_FILE = ROOT / "lira_host.json"


def _load_host_file() -> dict:
    if not HOST_FILE.exists():
        return {}
    try:
        return json.loads(HOST_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _cfg() -> dict:
    file_cfg = _load_host_file()
    return {
        "host": os.environ.get("LIRA_FACE_HOST", file_cfg.get("host", "0.0.0.0")),
        "port": int(os.environ.get("LIRA_FACE_PORT", file_cfg.get("port", 8787))),
        "public_url": os.environ.get("LIRA_FACE_URL", file_cfg.get("public_url", "")),
        "sleep_lira": os.environ.get("LIRA_SLEEP_HOME", file_cfg.get("sleep_lira", "")),
    }


def sleep_lira_home() -> Path:
    raw = _cfg()["sleep_lira"]
    if raw:
        p = Path(raw).expanduser()
        if p.is_dir():
            return p.resolve()
    sibling = (ROOT.parent / "sleep_lira").resolve()
    if sibling.is_dir():
        return sibling
    win_default = Path(r"C:\project\sleep_lira")
    if win_default.is_dir():
        return win_default
    return sibling


def face_host() -> str:
    return _cfg()["host"]


def face_port() -> int:
    return _cfg()["port"]


def face_bind() -> tuple[str, int]:
    return face_host(), face_port()


def face_base_url() -> str:
    url = _cfg()["public_url"].strip().rstrip("/")
    if url:
        return url
    host = face_host()
    if host in ("0.0.0.0", "::"):
        host = "127.0.0.1"
    return f"http://{host}:{face_port()}"


def speak_url() -> str:
    return f"{face_base_url()}/api/speak"


def health_url() -> str:
    return f"{face_base_url()}/api/health"


def ensure_sleep_on_path() -> Path:
    import sys

    home = sleep_lira_home()
    s = str(home)
    if home.is_dir() and s not in sys.path:
        sys.path.insert(0, s)
    return home