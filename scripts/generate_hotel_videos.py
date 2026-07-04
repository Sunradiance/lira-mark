#!/usr/bin/env python3
"""Generate AETHER hotel scroll videos via xAI Grok Imagine video API."""
from __future__ import annotations

import base64
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "hotel"
STATE_FILE = ASSETS / "video_gen_state.json"
SECRETS = Path(__file__).resolve().parents[2] / "sleep_lira" / "secrets.json"

API = "https://api.x.ai/v1"
MODEL = "grok-imagine-video"
POLL_SEC = 8
MAX_POLL = 180
FADE_DUR = 2.0

CLIP_PLAN = [
    ("scene_exterior.mp4", "exterior", "scene"),
    ("trans_ext_lobby.mp4", None, "transition"),
    ("scene_lobby.mp4", "lobby", "scene"),
    ("trans_lobby_corridor.mp4", None, "transition"),
    ("scene_corridor.mp4", "corridor", "scene"),
    ("trans_corridor_suite.mp4", None, "transition"),
    ("scene_suite.mp4", "suite", "scene"),
    ("trans_suite_spa.mp4", None, "transition"),
    ("scene_spa.mp4", "spa", "scene"),
    ("trans_spa_unicorn.mp4", None, "transition"),
    ("scene_unicorn_meadow.mp4", "unicorn_meadow", "scene"),
    ("scene_unicorn_glade.mp4", "unicorn_glade", "scene"),
]


def load_key() -> str:
    sys.path.insert(0, str(SECRETS.parent))
    try:
        from xai_key import resolve_xai_api_key, load_secrets
        key = resolve_xai_api_key(load_secrets())
    except Exception:
        key = None
    if not key and SECRETS.exists():
        key = json.loads(SECRETS.read_text(encoding="utf-8")).get("xai_api_key")
    if not key:
        raise SystemExit("No xAI API key in sleep_lira/secrets.json or XAI_API_KEY env")
    return key


def b64_uri(path: Path) -> str:
    mime = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def headers(key: str) -> dict:
    return {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}


def poll(key: str, request_id: str) -> dict:
    for i in range(MAX_POLL):
        r = requests.get(f"{API}/videos/{request_id}", headers=headers(key), timeout=60)
        r.raise_for_status()
        data = r.json()
        status = data.get("status")
        print(f"  poll {i+1}: {status}")
        if status == "done":
            return data
        if status in ("failed", "expired"):
            raise RuntimeError(f"Video job {status}: {json.dumps(data, indent=2)}")
        time.sleep(POLL_SEC)
    raise TimeoutError(f"Timed out waiting for {request_id}")


def post_and_poll(key: str, url: str, payload: dict) -> dict:
    r = requests.post(url, headers=headers(key), json=payload, timeout=120)
    if not r.ok:
        raise RuntimeError(f"POST {url} failed {r.status_code}: {r.text}")
    request_id = r.json()["request_id"]
    print(f"  request_id: {request_id}")
    return poll(key, request_id)


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, stream=True, timeout=300)
    r.raise_for_status()
    with open(dest, "wb") as f:
        for chunk in r.iter_content(65536):
            f.write(chunk)
    print(f"  saved {dest} ({dest.stat().st_size // 1024} KB)")


STEPS = {
    "intro": {
        "type": "image",
        "image": "exterior.jpg",
        "out": "intro_loop.mp4",
        "duration": 8,
        "prompt": (
            "Animate this exact hotel exterior image. Slow breathing camera at blue hour, "
            "golden window lights pulse gently, subtle mist, hypnotic seamless loop, Cartier film quality"
        ),
    },
    "scene_exterior": {
        "type": "image",
        "image": "exterior.jpg",
        "out": "scene_exterior.mp4",
        "duration": 7,
        "prompt": (
            "Animate this EXACT exterior image. Night façade of Aether hotel, rain-slick stone, "
            "cool blue dusk sky, distant city glow, slow forward camera float toward entrance doors. "
            "Preserve architecture from image. Exterior only — not interior."
        ),
    },
    "scene_lobby": {
        "type": "image",
        "image": "lobby.jpg",
        "out": "scene_lobby.mp4",
        "duration": 7,
        "prompt": (
            "Animate this EXACT lobby image. Vast marble atrium, towering columns, crystal chandeliers, "
            "warm champagne gold light, reflective floor. Slow inward glide. Interior lobby only — "
            "completely different from exterior street view."
        ),
    },
    "scene_corridor": {
        "type": "image",
        "image": "corridor.jpg",
        "out": "scene_corridor.mp4",
        "duration": 7,
        "prompt": (
            "Animate this EXACT corridor image. Narrow velvet-walled passage, repeating brass sconces, "
            "deep one-point perspective, intimate low ceiling vs grand lobby. Slow forward drift. "
            "Moody amber firelight — not a lobby, not a suite."
        ),
    },
    "scene_suite": {
        "type": "image",
        "image": "suite.jpg",
        "out": "scene_suite.mp4",
        "duration": 7,
        "prompt": (
            "Animate this EXACT suite image. Penthouse living room, floor-to-ceiling windows, "
            "night skyline visible outside, silk furnishings, cool glass reflections mixed with warm lamps. "
            "Slow parallax pan. Private residence — not corridor, not spa."
        ),
    },
    "scene_spa": {
        "type": "image",
        "image": "spa.jpg",
        "out": "scene_spa.mp4",
        "duration": 7,
        "prompt": (
            "Animate this EXACT spa image. Underground stone pool, black water, rising steam, "
            "scattered candles, cavernous dim atmosphere. Slow meditative camera. Wet organic textures — "
            "completely unlike lobby marble or suite glass."
        ),
    },
    "trans_ext_lobby": {
        "type": "reference",
        "images": ["exterior.jpg", "lobby.jpg"],
        "out": "trans_ext_lobby.mp4",
        "duration": 5,
        "prompt": (
            "Cinematic dance between two worlds. <IMAGE_1> cool blue hotel exterior at night dissolves "
            "through golden luminous veil and floating dust into <IMAGE_2> warm marble lobby interior. "
            "Camera passes through glass doors. Slow morph crossfade, no hard cut, ethereal transition"
        ),
    },
    "trans_lobby_corridor": {
        "type": "reference",
        "images": ["lobby.jpg", "corridor.jpg"],
        "out": "trans_lobby_corridor.mp4",
        "duration": 5,
        "prompt": (
            "Scene dance transition. <IMAGE_1> grand open lobby with chandeliers compresses and darkens, "
            "morphing through champagne light particles into <IMAGE_2> intimate velvet corridor with sconces. "
            "Scale shrinks, ceiling lowers, seamless crossfade"
        ),
    },
    "trans_corridor_suite": {
        "type": "reference",
        "images": ["corridor.jpg", "suite.jpg"],
        "out": "trans_corridor_suite.mp4",
        "duration": 5,
        "prompt": (
            "Scene dance transition. <IMAGE_1> narrow corridor doors open, golden light floods forward, "
            "walls dissolve into <IMAGE_2> vast penthouse suite with city skyline through glass. "
            "Space expands dramatically, smooth cinematic morph"
        ),
    },
    "trans_suite_spa": {
        "type": "reference",
        "images": ["suite.jpg", "spa.jpg"],
        "out": "trans_suite_spa.mp4",
        "duration": 5,
        "prompt": (
            "Scene dance transition. <IMAGE_1> bright glass suite descends through warm veil into "
            "<IMAGE_2> dark underground spa with steam and black water. Light fades to candle glow, "
            "materials shift from silk and glass to stone and mist, seamless crossfade"
        ),
    },
    "trans_spa_unicorn": {
        "type": "reference",
        "images": ["spa.jpg", "unicorn_meadow.jpg"],
        "out": "trans_spa_unicorn.mp4",
        "duration": 10,
        "prompt": (
            "Scene dance transition. <IMAGE_1> luxury spa steam and candlelight on black water glows "
            "with inner starlight and dissolves into <IMAGE_2> a vast unicorn meadow at dawn with "
            "aurora, iridescent grass, and distant unicorns. Dreamlike morph, seamless crossfade"
        ),
    },
    "scene_unicorn_meadow": {
        "type": "image",
        "image": "unicorn_meadow.jpg",
        "out": "scene_unicorn_meadow.mp4",
        "duration": 10,
        "prompt": (
            "Animate this EXACT unicorn meadow. Slow forward float, distant unicorns lift their heads, "
            "aurora shimmers, bioluminescent flowers pulse. Premium fantasy cinematography, 16:9"
        ),
    },
    "scene_unicorn_glade": {
        "type": "image",
        "image": "unicorn_glade.jpg",
        "out": "scene_unicorn_glade.mp4",
        "duration": 10,
        "prompt": (
            "Animate this EXACT enchanted glade. Slow glide toward the white unicorn, floating petals, "
            "stardust particles, mirror pool ripples. Sacred luxury fantasy, no cartoon style"
        ),
    },
}


def run_step(key: str, name: str, cfg: dict, force: bool = False) -> None:
    out = ASSETS / cfg["out"]
    if out.exists() and out.stat().st_size > 10000 and not force:
        print(f"[skip] {name} -> {out.name} exists")
        return

    print(f"[gen] {name} -> {out.name}")
    if cfg["type"] == "image":
        payload = {
            "model": MODEL,
            "prompt": cfg["prompt"],
            "image": {"url": b64_uri(ASSETS / cfg["image"])},
            "duration": cfg["duration"],
            "aspect_ratio": "16:9",
            "resolution": "720p",
        }
        result = post_and_poll(key, f"{API}/videos/generations", payload)
    elif cfg["type"] == "reference":
        payload = {
            "model": MODEL,
            "prompt": cfg["prompt"],
            "reference_images": [{"url": b64_uri(ASSETS / img)} for img in cfg["images"]],
            "duration": cfg["duration"],
            "aspect_ratio": "16:9",
            "resolution": "720p",
        }
        result = post_and_poll(key, f"{API}/videos/generations", payload)
    else:
        raise ValueError(f"Unknown step type: {cfg['type']}")

    download(result["video"]["url"], out)


def ffmpeg_bin() -> str:
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def probe_duration(path: Path) -> float:
    import re
    import subprocess
    try:
        proc = subprocess.run(
            [ffmpeg_bin(), "-i", str(path)],
            capture_output=True, text=True, timeout=30,
        )
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.?\d*)", proc.stderr)
        if m:
            h, mnt, sec = m.groups()
            return round(int(h) * 3600 + int(mnt) * 60 + float(sec), 3)
    except Exception:
        pass
    return 8.0


def concat_experience() -> list[dict]:
    import subprocess

    out = ASSETS / "experience.mp4"
    tmp = ASSETS / "experience_build.mp4"
    parts = [ASSETS / fname for fname, _, _ in CLIP_PLAN]
    missing = [p.name for p in parts if not p.exists()]
    if missing:
        print(f"[concat] waiting for: {', '.join(missing)}")
        return []

    durations = [probe_duration(p) for p in parts]
    n = len(parts)
    fade = FADE_DUR
    transitions = ["fade", "fadeblack", "dissolve", "smoothleft", "smoothright", "circlecrop", "distance", "radial"]

    filters = []
    prev = "0:v"
    offset = durations[0] - fade
    for i in range(1, n):
        label = f"v{i}" if i < n - 1 else "vout"
        trans = transitions[(i - 1) % len(transitions)]
        filters.append(
            f"[{prev}][{i}:v]xfade=transition={trans}:duration={fade}:offset={max(offset, 0):.3f}[{label}]"
        )
        prev = label
        offset += durations[i] - fade

    ff = ffmpeg_bin()
    cmd = [ff, "-y"]
    for p in parts:
        cmd.extend(["-i", str(p)])
    cmd.extend([
        "-filter_complex", ";".join(filters),
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(tmp),
    ])
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    if proc.returncode != 0:
        raise RuntimeError(f"xfade concat failed: {proc.stderr[-800:]}")
    try:
        if out.exists():
            out.unlink()
        tmp.rename(out)
    except OSError:
        fallback = ASSETS / "experience_v2.mp4"
        tmp.rename(fallback)
        print(f"[concat] locked — wrote {fallback.name}; refresh browser cache")
        out = fallback
    print(f"[concat] {out.name} with {fade}s crossfades ({out.stat().st_size // 1024} KB)")

    timeline = []
    cursor = 0.0
    for i, ((fname, scene, kind), dur) in enumerate(zip(CLIP_PLAN, durations)):
        start = cursor
        end = cursor + dur - (fade if i < n - 1 else 0)
        timeline.append({
            "file": fname,
            "scene": scene,
            "kind": kind,
            "start": round(start, 3),
            "end": round(end, 3),
            "duration": round(dur, 3),
        })
        cursor = end
    return timeline


def build_segments_hint(timeline: list[dict], total: float) -> list[dict]:
    scenes = [c for c in timeline if c["kind"] == "scene"]
    transitions = [c for c in timeline if c["kind"] == "transition"]

    frame_map = {
        "exterior": "entry",
        "lobby": "lobby",
        "corridor": "corridor",
        "suite": "suite",
        "spa": "spa",
        "unicorn_meadow": "unicorn",
        "unicorn_glade": "realm",
    }

    segments = []
    for i, clip in enumerate(scenes):
        scene = clip["scene"]
        frame_id = frame_map.get(scene, scene)
        trans_before = transitions[i - 1] if i > 0 else None
        trans_after = transitions[i] if i < len(transitions) else None

        enter = trans_before["start"] if trans_before else clip["start"]
        if i == 0:
            enter = 0
        peak = clip["start"] + (clip["end"] - clip["start"]) * 0.45
        exit_t = trans_after["end"] if trans_after else clip["end"]
        if i == len(scenes) - 1:
            exit_t = total

        loop_start = clip["start"] + (clip["end"] - clip["start"]) * 0.55
        loop_end = min(clip["end"], total - 0.01)

        segments.append({
            "id": frame_id if frame_id != "entry" else "entry",
            "frameId": frame_id,
            "scene": scene,
            "transitionStart": round(enter, 3),
            "transitionEnd": round(clip["start"] + (clip["end"] - clip["start"]) * 0.35, 3),
            "loopStart": round(loop_start, 3),
            "loopEnd": round(loop_end, 3),
            "scrollResume": round(exit_t if i < len(scenes) - 1 else total, 3),
        })

    segments.append({
        "id": "outro",
        "frameId": "complete",
        "scene": "spa",
        "transitionStart": round(scenes[-1]["end"] * 0.85, 3),
        "transitionEnd": round(total, 3),
        "loopStart": round(total * 0.9, 3),
        "loopEnd": round(total, 3),
        "scrollResume": round(total, 3),
    })
    return segments


def experience_path() -> Path:
    for name in ("experience_fast.mp4", "experience_v2.mp4", "experience.mp4"):
        p = ASSETS / name
        if p.exists():
            return p
    return ASSETS / "experience.mp4"


def write_meta(timeline: list[dict] | None = None) -> None:
    intro = ASSETS / "intro_loop.mp4"
    exp = experience_path()
    meta = {
        "intro": probe_duration(intro) if intro.exists() else 8.0,
        "experience": probe_duration(exp) if exp.exists() else None,
        "experience_file": exp.name,
        "fade_duration": FADE_DUR,
        "timeline": timeline or [],
        "segments_hint": None,
    }
    if meta["experience"] and timeline:
        meta["segments_hint"] = build_segments_hint(timeline, meta["experience"])
    (ASSETS / "video_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[meta] {ASSETS / 'video_meta.json'}")


def main() -> None:
    args = sys.argv[1:]
    force = "--force" in args
    only = [a for a in args if a != "--force"] or None

    key = load_key()
    ASSETS.mkdir(parents=True, exist_ok=True)

    order = [
        "intro",
        "scene_exterior", "scene_lobby", "scene_corridor", "scene_suite", "scene_spa",
        "trans_ext_lobby", "trans_lobby_corridor", "trans_corridor_suite", "trans_suite_spa",
        "trans_spa_unicorn", "scene_unicorn_meadow", "scene_unicorn_glade",
    ]
    for name in order:
        if only and name not in only:
            continue
        run_step(key, name, STEPS[name], force=force)

    timeline = []
    if not only or "concat" in only:
        timeline = concat_experience()
    write_meta(timeline)
    print("Done.")


if __name__ == "__main__":
    main()