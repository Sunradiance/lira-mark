"""xAI Text-to-Speech — Ara voice for Lira face hologram."""
from __future__ import annotations

import base64
import json
import sys
import urllib.error
import urllib.request
from lira_config import ensure_sleep_on_path

ensure_sleep_on_path()
from xai_key import load_secrets, resolve_xai_api_key  # noqa: E402

TTS_URL = "https://api.x.ai/v1/tts"
DEFAULT_VOICE = "ara"


def synthesize(
    text: str,
    *,
    voice_id: str = DEFAULT_VOICE,
    language: str = "en",
    with_timestamps: bool = True,
    speed: float = 1.0,
) -> dict | None:
    text = (text or "").strip()
    if not text:
        return None
    if len(text) > 15000:
        text = text[:15000]

    cfg = load_secrets()
    key = resolve_xai_api_key(cfg)
    if not key:
        return None

    payload = {
        "text": text,
        "voice_id": voice_id,
        "language": language,
        "with_timestamps": with_timestamps,
        "speed": max(0.7, min(1.5, speed)),
        "output_format": {"codec": "mp3", "sample_rate": 24000, "bit_rate": 128000},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        TTS_URL,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = resp.read()
            ctype = resp.headers.get("Content-Type", "")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, OSError):
        return None

    if with_timestamps or "application/json" in ctype:
        try:
            out = json.loads(body.decode("utf-8"))
            if out.get("audio"):
                return out
        except json.JSONDecodeError:
            pass

    return {
        "audio": base64.b64encode(body).decode("ascii"),
        "content_type": ctype or "audio/mpeg",
        "duration": None,
        "audio_timestamps": None,
    }


def main() -> None:
    text = " ".join(sys.argv[1:]).strip() or "Hey Tilen. Ara voice live on the hologram."
    result = synthesize(text)
    if not result:
        print("xAI TTS failed — check secrets.json xai_api_key", file=sys.stderr)
        raise SystemExit(1)
    dur = result.get("duration")
    print(f"ok voice=ara bytes={len(result.get('audio', ''))} duration={dur}")


if __name__ == "__main__":
    main()