#!/usr/bin/env python3
"""Keep Lira face stack alive — restarts server/daemon/bridge on crash."""
from __future__ import annotations

import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from lira_config import face_base_url, health_url

ROOT = Path(__file__).resolve().parent
PY = sys.executable
HEALTH = health_url()
INTERVAL = 12.0

SERVICES = [
    ("server", ROOT / "face_server.py"),
    ("inbox", ROOT / "face_inbox_daemon.py"),
    ("bridge", ROOT / "chat_face_bridge.py"),
]


def healthy() -> bool:
    try:
        with urllib.request.urlopen(HEALTH, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def spawn(name: str, script: Path) -> subprocess.Popen:
    print(f"[supervisor] start {name}: {script.name}", flush=True)
    return subprocess.Popen(
        [PY, str(script)],
        cwd=str(ROOT),
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )


def main() -> None:
    procs: dict[str, subprocess.Popen] = {}
    for name, script in SERVICES:
        procs[name] = spawn(name, script)
        if name == "server":
            time.sleep(2.0)
        else:
            time.sleep(0.6)

    print(f"[supervisor] watching {HEALTH} every {INTERVAL:.0f}s", flush=True)
    print(f"[supervisor] face: {face_base_url()}/face.html", flush=True)

    try:
        while True:
            time.sleep(INTERVAL)
            for name, script in SERVICES:
                proc = procs.get(name)
                if proc is None or proc.poll() is not None:
                    code = None if proc is None else proc.returncode
                    print(f"[supervisor] {name} exited ({code}) — restarting", flush=True)
                    procs[name] = spawn(name, script)
                    if name == "server":
                        time.sleep(2.0)
            if not healthy():
                proc = procs.get("server")
                if proc and proc.poll() is None:
                    print("[supervisor] health fail — restarting server", flush=True)
                    proc.terminate()
                    try:
                        proc.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        proc.kill()
                procs["server"] = spawn("server", SERVICES[0][1])
                time.sleep(2.0)
    except KeyboardInterrupt:
        print("[supervisor] stopping", flush=True)
        for proc in procs.values():
            if proc.poll() is None:
                proc.terminate()
        raise SystemExit(0)


if __name__ == "__main__":
    main()