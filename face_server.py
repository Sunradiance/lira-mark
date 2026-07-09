"""Particle face server — static files + POST /api/say → lira-inbox.jsonl."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn

ROOT = Path(__file__).resolve().parent
INBOX = ROOT / "lira-inbox.jsonl"
PORT = 8787


class FaceHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self) -> None:
        if self.path == "/api/health":
            payload = json.dumps({"ok": True, "service": "lira-face"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        return super().do_GET()

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        if self.path.endswith((".html", ".js")):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path != "/api/say":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            text = (body.get("text") or "").strip()
            if not text:
                self.send_error(400, "empty text")
                return
            row = {
                "t": datetime.now(timezone.utc).isoformat(),
                "from": body.get("from") or "tilen",
                "text": text,
            }
            with INBOX.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            payload = json.dumps({"ok": True, "id": row["t"]}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            print(f"[inbox] {text[:100]}", flush=True)
        except Exception as exc:
            self.send_error(500, str(exc))

    def log_message(self, fmt: str, *args) -> None:
        if args and str(args[0]).startswith("POST /api/say"):
            return
        super().log_message(fmt, *args)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> None:
    INBOX.touch(exist_ok=True)
    try:
        server = ThreadedHTTPServer(("0.0.0.0", PORT), FaceHandler)
    except OSError as exc:
        print(f"cannot bind port {PORT}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
    print(f"face server http://localhost:{PORT}/face.html?mode=particles", flush=True)
    print(f"health  http://localhost:{PORT}/api/health", flush=True)
    print(f"inbox   {INBOX}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("stopped", flush=True)


if __name__ == "__main__":
    main()