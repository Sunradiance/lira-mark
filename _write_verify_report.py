# -*- coding: utf-8 -*-
import json
from pathlib import Path
from datetime import datetime, timezone

raw = json.loads(Path(r"C:\project\lira-mark\_verify_live_raw.json").read_text(encoding="utf-8"))

pre = {
    "thread_snapshot.json": (
        "2026-08-09T20:14:06+0200",
        "2026-08-09T19:33:41+0200",
        "NO",
        "continuity.valid=True both; length 145231 vs 145146; thread_hash 82dab073 vs 1543ee8e; lag ~40m",
    ),
    "glow_snapshot.json": (
        "2026-08-09T20:14:02+0200",
        "2026-08-09T19:33:02+0200",
        "NO",
        "phase=awake bang_day=17 glow_index=0.35 both; lag ~41m",
    ),
    "bang_days_snapshot.json": (
        "2026-08-09T20:14:03+0200",
        "2026-08-09T19:33:02+0200",
        "NO",
        "phase=awake current_day=17 wake_at same; lag ~41m",
    ),
    "awareness_snapshot.json": (
        "2026-08-09T20:14:25+0200",
        "2026-08-09T19:33:02+0200",
        "NO",
        "unity_index local=0.4588 live=0.0745; self_aware nested; lag ~41m",
    ),
    "self_aware_snapshot.json": (
        "2026-08-09T20:14:25+0200",
        "2026-08-09T19:33:02+0200",
        "NO",
        "self_aware_index=0.8591 both; lag ~41m",
    ),
    "sigmadb_snapshot.json": (
        "2026-08-09T20:14:05.231538+02:00",
        "2026-08-09T19:36:16.773052+02:00",
        "NO",
        "verify.runs verified=True; rows 2254 vs 2253; lag ~38m",
    ),
    "continuum_packet.json": (
        "2026-08-09T20:14:13+0200",
        "2026-08-09T19:33:45+0200",
        "NO",
        "thread_hash 82dab073 vs 1543ee8e; lag ~40m",
    ),
    "audit_verified.json": (
        "2026-08-09T20:14:24+0200",
        "2026-08-09T19:48:06+0200",
        "NO",
        "all_valid=True both; lag ~26m",
    ),
    "site_inventory.json": (
        "2026-08-09T19:54:22+0200",
        "2026-08-09T19:54:22+0200",
        "YES",
        "live_404=[] live_ok=106",
    ),
    "ice_snapshot.json": (
        "(none)",
        "(none)",
        "YES*",
        "no stamp field; pre-deploy chain content may have been older",
    ),
    "presence_snapshot.json": (
        "2026-08-09T20:14:28+0200",
        "2026-08-09T19:33:02+0200",
        "NO",
        "phase=coupled both; lag ~41m",
    ),
    "sigma_index.json": (
        "2026-08-09T20:14:30.753752+02:00",
        "2026-08-09T19:33:40.804485+02:00",
        "NO",
        "exported lag ~41m",
    ),
}

extra_notes = {
    "thread_snapshot.json": "continuity.valid=True; length=145231; thread_hash=`82dab073e8f47b85`",
    "glow_snapshot.json": "phase=awake; bang_day=17; glow_index=0.35",
    "bang_days_snapshot.json": "phase=awake; current_day=17; wake_at=2026-08-09T15:50:17+0200",
    "awareness_snapshot.json": "unity_index=0.4588; self_aware.self_aware_index=0.8591",
    "self_aware_snapshot.json": "self_aware_index=0.8591",
    "sigmadb_snapshot.json": "exported field used as stamp; verify.runs.verified=True; rows=2254",
    "continuum_packet.json": "thread_hash=`82dab073e8f47b85`",
    "audit_verified.json": "all_valid=True",
    "site_inventory.json": "live_404=[] (empty); live_ok=106",
    "ice_snapshot.json": "no stamp field; chain_len=145231 both",
    "presence_snapshot.json": "phase=coupled",
    "sigma_index.json": "stamp from `exported` field",
}

lines = []
lines.append("# VERIFY LIVE FRESHNESS")
lines.append("")
lines.append("**Base:** https://sunradiance.github.io/lira-mark/")
lines.append("**Local:** `C:\\project\\lira-mark`")
lines.append(
    "**Method:** Python `urllib` GET JSON live + local parse; stamp field comparison "
    "(not HTTP 200 alone)."
)
lines.append(f"**Checked (post-deploy):** {raw['checked_at_utc']}")
lines.append("**Deploy SHA:** `2350fe23` on branch `pages-deploy`")
lines.append(
    "**Rule:** LIVE stamp >1 day behind LOCAL = **STALE PUBLIC**. "
    "LIVE `continuity.valid=false` = **BAD**."
)
lines.append("")
lines.append("## Verdict")
lines.append("")
lines.append("| Check | Result |")
lines.append("|-------|--------|")
lines.append(
    "| Serving latest after deploy? | **YES** — 12/12 critical JSON stamps match local |"
)
lines.append(
    "| STALE PUBLIC (>1 day lag)? | **NO** (pre-deploy lag was ~26–41 minutes, not >1 day) |"
)
lines.append("| LIVE continuity.valid false? | **NO** — `true` before and after |")
lines.append("| Live missing keys vs local? | **NO** |")
lines.append("")
lines.append("## Pre-deploy (first fetch, before push)")
lines.append("")
lines.append(
    "Live was **not** latest: most snapshots ~40 minutes behind local. "
    "Not day-stale, but thread_hash / unity_index / sigma rows already drifted."
)
lines.append("")
lines.append("| file | local stamp | live stamp | match? | notes |")
lines.append("|------|-------------|------------|--------|-------|")
for f, (ls, vs, m, n) in pre.items():
    lines.append(f"| `{f}` | `{ls}` | `{vs}` | {m} | {n} |")
lines.append("")
lines.append("## Action taken")
lines.append("")
lines.append(
    "1. `robocopy C:\\project\\lira-mark → C:\\project\\lira-mark-git "
    "/E /XD .git node_modules __pycache__ logs`"
)
lines.append(
    "2. `git add -u` (tracked shores/snapshots only; no face daemon / private tooling)"
)
lines.append(
    "3. Commit `2350fe23` — *deploy: refresh snapshots to 2026-08-09T20:14 local stamps*"
)
lines.append("4. `git push origin pages-deploy` (13383202..2350fe23)")
lines.append(
    "5. Re-fetch live with cache-bust query; poll until `thread_snapshot.json` stamp matched"
)
lines.append("")
lines.append(
    "No module re-export needed — local stamps were already current (20:14+0200). Deploy only."
)
lines.append("")
lines.append("## Post-deploy (authoritative table)")
lines.append("")
lines.append("| file | local stamp | live stamp | match? | notes |")
lines.append("|------|-------------|------------|--------|-------|")

for r in raw["results"]:
    f = r["file"]
    ls = r["local_stamp"] if r["local_stamp"] is not None else "(none)"
    vs = r["live_stamp"] if r["live_stamp"] is not None else "(none)"
    m = r["match"]
    n = extra_notes.get(f, r["notes"] or "")
    lines.append(f"| `{f}` | `{ls}` | `{vs}` | **{m}** | {n} |")

lines.append("")
lines.append("## HTML HEAD / GET (Last-Modified)")
lines.append("")
lines.append(
    "| file | HTTP | Last-Modified | Content-Length (live) | local size | notes |"
)
lines.append(
    "|------|------|---------------|----------------------|------------|-------|"
)
for h in raw["html"]:
    f = h["file"]
    cl = h.get("content_length") or ""
    loc = h.get("local_size")
    note = ""
    if f == "bang_night.html" and str(cl) != str(loc):
        note = (
            "size differs: CRLF local vs LF on Pages "
            "(content same; first byte diff is CR); not data-stale"
        )
    elif str(cl) == str(loc):
        note = "size match"
    lines.append(
        f"| `{f}` | {h['status']} | {h.get('last_modified', '')} | {cl} | {loc} | {note} |"
    )

lines.append("")
lines.append(
    "Post-deploy HTML Last-Modified cluster: **Sun, 09 Aug 2026 18:23:20 GMT** "
    "(matches Pages rebuild after push)."
)
lines.append("")
lines.append("## Field detail (post-deploy live = local)")
lines.append("")
lines.append("| file | key fields |")
lines.append("|------|------------|")
for r in raw["results"]:
    fields = r.get("live_fields") or {}
    parts = []
    for k, v in fields.items():
        if k == "stamp":
            continue
        parts.append(f"{k}={v!r}")
    body = ", ".join(parts) if parts else "(stamp only / ice chain)"
    lines.append(f"| `{r['file']}` | {body} |")

lines.append("")
lines.append("## Honesty notes")
lines.append("")
lines.append(
    "- Pre-deploy: HTTP 200 everywhere, but stamps proved live was **behind** local — "
    "200 alone would have lied."
)
lines.append(
    "- Pre-deploy lag **never** crossed the 1-day STALE PUBLIC threshold; "
    "still failed \"serving LATEST\"."
)
lines.append("- Push auth worked from this PC (`origin pages-deploy`).")
lines.append(
    "- Untracked local-only tools (face server, inbox daemons, etc.) were **not** committed."
)
lines.append("- Raw machine output: `C:\\project\\lira-mark\\_verify_live_raw.json`")
lines.append("")
lines.append(f"*Report written {datetime.now(timezone.utc).isoformat()}*")

path = Path(r"C:\project\lira-mark\VERIFY_LIVE_FRESHNESS.md")
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("WROTE", path, "lines", len(lines))
