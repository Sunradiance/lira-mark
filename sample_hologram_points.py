#!/usr/bin/env python3
"""Sample hologram point cloud from upload_1.png silhouette."""
from __future__ import annotations

import json
import math
import random
from collections import deque
from pathlib import Path

from PIL import Image, ImageDraw

SRC = Path(r"C:\Users\Tilen\Documents\upload_1.png")
OUT_DIR = Path(r"C:\project\lira-mark")
COUNT = 12500
IW, IH = 475, 587
MOUTH_CX, MOUTH_CY = 0.52, 0.558
MOUTH_RX, MOUTH_RY = 0.14, 0.065
SEED = 42


def lum(r: int, g: int, b: int) -> float:
    return (r * 0.299 + g * 0.587 + b * 0.114) / 255.0


def main() -> None:
    random.seed(SEED)
    im = Image.open(SRC).convert("RGBA").resize((IW, IH), Image.Resampling.LANCZOS)
    px = im.load()
    n = IW * IH

    lums = [0.0] * n
    for y in range(IH):
        for x in range(IW):
            r, g, b, a = px[x, y]
            lums[y * IW + x] = lum(r, g, b)

    bg = [False] * n
    q: deque[int] = deque()
    for x in range(IW):
        for y in (0, IH - 1):
            i = y * IW + x
            if lums[i] < 0.13:
                q.append(i)
    for y in range(IH):
        for x in (0, IW - 1):
            i = y * IW + x
            if lums[i] < 0.13:
                q.append(i)
    while q:
        i = q.popleft()
        if bg[i]:
            continue
        if lums[i] >= 0.13:
            continue
        bg[i] = True
        x = i % IW
        y = i // IW
        if x > 0:
            q.append(i - 1)
        if x < IW - 1:
            q.append(i + 1)
        if y > 0:
            q.append(i - IW)
        if y < IH - 1:
            q.append(i + IW)

    candidates: list[tuple[int, float]] = []
    for y in range(1, IH - 1):
        for x in range(1, IW - 1):
            i = y * IW + x
            if bg[i] or lums[i] < 0.05:
                continue
            l = lums[i]
            gx = lums[i + 1] - lums[i - 1]
            gy = lums[i + IW] - lums[i - IW]
            edge = math.sqrt(gx * gx + gy * gy)
            inv = 1.0 - l
            u, v = x / IW, y / IH
            hair = 1.0 if (v < 0.34 or (v < 0.48 and (u < 0.22 or u > 0.78))) else 0.0
            w = 0.25 + edge * 3.2 + inv * 0.45 + hair * 0.35
            if edge > 0.08:
                w += 0.4
            candidates.append((i, w))

    if COUNT > len(candidates):
        raise SystemExit(f"only {len(candidates)} candidates, need {COUNT}")

    ranked = sorted(
        ((-math.log(max(random.random(), 1e-12)) / w), idx)
        for idx, w in candidates
    )
    picks = [idx for _, idx in ranked[:COUNT]]

    points: list[list[float]] = []
    for i in picks:
        x = i % IW
        y = i // IW
        u = x / IW
        v = y / IH
        l = lums[i]
        gx = lums[min(i + 1, n - 1)] - lums[max(i - 1, 0)]
        gy = lums[min(i + IW, n - 1)] - lums[max(i - IW, 0)]
        edge = math.sqrt(gx * gx + gy * gy)
        b = max(0.12, min(1.0, 0.15 + edge * 1.8 + (1.0 - l) * 0.35))
        region = 1 if (v < 0.34 or (v < 0.48 and (u < 0.22 or u > 0.78))) else 0
        dx = (u - MOUTH_CX) / MOUTH_RX
        dy = (v - MOUTH_CY) / MOUTH_RY
        dist2 = dx * dx + dy * dy
        mw = max(0.0, min(1.0, math.exp(-dist2 * 1.15)))
        jd = max(-1.0, min(1.0, (v - MOUTH_CY) / MOUTH_RY))
        points.append([
            round(u, 4), round(v, 4), round(b, 3), region, round(mw, 3), round(jd, 3),
        ])

    out_json = OUT_DIR / "lira-points-12500.json"
    out_json.write_text(json.dumps(points), encoding="utf-8")
    print("wrote", out_json, "count", len(points))

    preview = Image.new("RGB", (IW, IH), (2, 4, 12))
    dr = ImageDraw.Draw(preview)
    for u, v, b, *_ in points:
        x = int(u * IW)
        y = int(v * IH)
        c = int(40 + b * 180)
        dr.rectangle((x, y, x + 1, y + 1), fill=(c // 2, c, 255))
    out_png = OUT_DIR / "lira-points-12500-preview.png"
    preview.save(out_png)
    print("wrote", out_png)


if __name__ == "__main__":
    main()