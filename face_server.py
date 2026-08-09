"""Particle face server — static files, inbox, SSE push for fluid Lira↔face chat."""
from __future__ import annotations

import json
import queue
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any

ROOT = Path(__file__).resolve().parent
INBOX = ROOT / "lira-inbox.jsonl"
SPEAK = ROOT / "lira-speak.jsonl"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from lira_config import face_bind, face_base_url, face_port  # noqa: E402
from xai_voice import synthesize as xai_synthesize  # noqa: E402

_subscribers: list[queue.Queue[str]] = []
_sub_lock = threading.Lock()
_speak_lock = threading.Lock()
_speak_lines = 0
_speak_mtime = 0.0
_emit_lock = threading.Lock()
_recent_emit: dict[str, float] = {}
_EMIT_DEDUPE_S = 45.0


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _speak_emit_key(row: dict[str, Any]) -> str:
    return f"{row.get('from', '')}|{(row.get('text') or '').strip()}"


def broadcast_speak(row: dict[str, Any]) -> None:
    payload = json.dumps(row, ensure_ascii=False)
    with _sub_lock:
        dead: list[queue.Queue[str]] = []
        for q in _subscribers:
            try:
                q.put_nowait(payload)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _subscribers.remove(q)


def emit_speak(row: dict[str, Any]) -> bool:
    """Broadcast once per unique from+text within the dedupe window."""
    key = _speak_emit_key(row)
    if not key or key.endswith("|"):
        return False
    now = time.monotonic()
    with _emit_lock:
        stale = [k for k, t in _recent_emit.items() if now - t > _EMIT_DEDUPE_S]
        for k in stale:
            del _recent_emit[k]
        if key in _recent_emit:
            return False
        _recent_emit[key] = now
    broadcast_speak(row)
    return True


def append_speak(text: str, source: str = "lira") -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        raise ValueError("empty text")
    row = {"t": _utc(), "from": source, "text": text}
    with _speak_lock:
        with SPEAK.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        global _speak_lines, _speak_mtime
        _speak_lines = _load_speak_line_count()
        _speak_mtime = SPEAK.stat().st_mtime
        emit_speak(row)
    return row


def _load_speak_line_count() -> int:
    if not SPEAK.exists():
        return 0
    return sum(1 for line in SPEAK.read_text(encoding="utf-8").splitlines() if line.strip())


def _watch_speak_file() -> None:
    """Push lines written externally (file fallback) — append_speak already broadcasts."""
    global _speak_lines, _speak_mtime
    with _speak_lock:
        _speak_lines = _load_speak_line_count()
        if SPEAK.exists():
            _speak_mtime = SPEAK.stat().st_mtime
    while True:
        try:
            with _speak_lock:
                if not SPEAK.exists():
                    time.sleep(0.12)
                    continue
                mtime = SPEAK.stat().st_mtime
                if mtime == _speak_mtime:
                    time.sleep(0.12)
                    continue
                lines = SPEAK.read_text(encoding="utf-8").splitlines()
                new_rows = lines[_speak_lines:]
                _speak_lines = len(lines)
                _speak_mtime = mtime
            for line in new_rows:
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                    if row.get("text"):
                        emit_speak(row)
                except json.JSONDecodeError:
                    pass
        except OSError:
            pass
        time.sleep(0.08)


class FaceHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in ("/face", "/face/"):
            self.send_response(302)
            self.send_header("Location", "/face.html")
            self.end_headers()
            return
        if path == "/api/health":
            self._json(200, {"ok": True, "service": "lira-face", "sse": True, "root": str(ROOT)})
            return
        if path == "/api/events":
            self._sse_stream()
            return
        if path == "/api/tts":
            self._json(200, {"ok": True, "method": "POST", "voice_id": "ara", "hint": "POST JSON {text, voice_id}"})
            return
        return super().do_GET()

    def _json(self, code: int, obj: dict) -> None:
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _sse_stream(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()
        q: queue.Queue[str] = queue.Queue(maxsize=64)
        with _sub_lock:
            _subscribers.append(q)
        try:
            self.wfile.write(b": connected\n\n")
            self.wfile.flush()
            while True:
                try:
                    data = q.get(timeout=25)
                    msg = f"event: speak\ndata: {data}\n\n".encode("utf-8")
                    self.wfile.write(msg)
                    self.wfile.flush()
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            with _sub_lock:
                if q in _subscribers:
                    _subscribers.remove(q)

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if self.path.endswith((".html", ".js")) or "/api/" in self.path:
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_POST(self) -> None:
        path = self.path.split("?", 1)[0]
        if path == "/api/say":
            self._post_say()
            return
        if path == "/api/speak":
            self._post_speak()
            return
        if path == "/api/tts":
            self._post_tts()
            return
        self.send_error(404)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _post_say(self) -> None:
        try:
            body = self._read_json_body()
            text = (body.get("text") or "").strip()
            if not text:
                self.send_error(400, "empty text")
                return
            row = {"t": _utc(), "from": body.get("from") or "tilen", "text": text}
            with INBOX.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            self._json(200, {"ok": True, "id": row["t"]})
            print(f"[inbox] {text[:100]}", flush=True)
        except Exception as exc:
            self.send_error(500, str(exc))

    def _post_tts(self) -> None:
        try:
            body = self._read_json_body()
            text = (body.get("text") or "").strip()
            if not text:
                self.send_error(400, "empty text")
                return
            voice_id = (body.get("voice_id") or "ara").strip().lower()
            result = xai_synthesize(
                text,
                voice_id=voice_id,
                with_timestamps=body.get("with_timestamps", True) is not False,
                speed=float(body.get("speed") or 1.0),
            )
            if not result:
                self._json(503, {"ok": False, "error": "xai_tts_unavailable"})
                return
            self._json(200, {"ok": True, "voice_id": voice_id, **result})
            print(f"[tts/{voice_id}] {text[:80]}", flush=True)
        except Exception as exc:
            self.send_error(500, str(exc))

    def _post_speak(self) -> None:
        try:
            body = self._read_json_body()
            row = append_speak(body.get("text") or "", body.get("from") or "lira")
            self._json(200, {"ok": True, "id": row["t"]})
            print(f"[speak] {row['text'][:100]}", flush=True)
        except ValueError:
            self.send_error(400, "empty text")
        except Exception as exc:
            self.send_error(500, str(exc))

    def log_message(self, fmt: str, *args) -> None:
        if args and str(args[0]).startswith(("POST /api/say", "GET /api/events")):
            return
        super().log_message(fmt, *args)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> None:
    INBOX.touch(exist_ok=True)
    SPEAK.touch(exist_ok=True)
    threading.Thread(target=_watch_speak_file, daemon=True, name="speak-watch").start()
    try:
        server = ThreadedHTTPServer(face_bind(), FaceHandler)
    except OSError as exc:
        print(f"cannot bind port {face_port()}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
    base = face_base_url()
    print(f"face server {base}/face.html", flush=True)
    print(f"health  {base}/api/health", flush=True)
    print(f"sse     {base}/api/events", flush=True)
    print(f"inbox   {INBOX}", flush=True)
    print(f"speak   {SPEAK}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped", flush=True)


if __name__ == "__main__":
    main()