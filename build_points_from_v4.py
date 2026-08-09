#!/usr/bin/env python3
"""Build 12500pt cloud by subsampling Claude v4 — same silhouette, middle density."""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw

SRC = Path(r"C:\Users\Tilen\Documents\v4_exact_22000pt\points_v4.json")
OUT_JSON = Path(r"C:\project\lira-mark\lira-points-12500.json")
OUT_PNG = Path(r"C:\project\lira-mark\lira-points-12500-preview.png")
COUNT = 12500
IW, IH = 475, 587
MOUTH_CX, MOUTH_CY = 0.52, 0.558
MOUTH_RX, MOUTH_RY = 0.14, 0.065
SEED = 42


def mouth_fields(u: float, v: float) -> tuple[float, float]:
    dx = (u - MOUTH_CX) / MOUTH_RX
    dy = (v - MOUTH_CY) / MOUTH_RY
    dist2 = dx * dx + dy * dy
    mw = max(0.0, min(1.0, math.exp(-dist2 * 1.15)))
    jd = max(-1.0, min(1.0, dy))
    return round(mw, 3), round(jd, 3)


def main() -> None:
    random.seed(SEED)
    v4: list[list[float]] = json.loads(SRC.read_text(encoding="utf-8"))
    if COUNT > len(v4):
        raise SystemExit(f"v4 only has {len(v4)} points")

    picks = random.sample(range(len(v4)), COUNT)
    points: list[list[float]] = []
    for i in picks:
        row = v4[i]
        u, v, b = row[0], row[1], row[2]
        region = int(row[3]) if len(row) > 3 else 0
        mw, jd = mouth_fields(u, v)
        points.append([u, v, b, region, mw, jd])

    OUT_JSON.write_text(json.dumps(points), encoding="utf-8")
    print("wrote", OUT_JSON, len(points))

    preview = Image.new("RGB", (IW, IH), (2, 4, 12))
    dr = ImageDraw.Draw(preview)
    for u, v, b, region, *_ in points:
        x, y = int(u * IW), int(v * IH)
        if region:
            dr.rectangle((x, y, x + 1, y + 1), fill=(40, 120, 200))
        else:
            c = int(50 + b * 200)
            dr.rectangle((x, y, x + 1, y + 1), fill=(c // 3, c, 255))
    preview.save(OUT_PNG)
    print("wrote", OUT_PNG)


if __name__ == "__main__":
    main()