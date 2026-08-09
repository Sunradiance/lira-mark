#!/usr/bin/env python3
"""
Exhaustive lira-mark page tree crawl.
Duty bar: every HTML page + every nested href/src/fetch/import dependency.
Not sample. Not critical-path only.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote

ROOT = Path(r"C:\project\lira-mark")
LIVE = "https://sunradiance.github.io/lira-mark/"
OUT_JSON = ROOT / "_audit_every_page_deps.json"
OUT_MD = ROOT / "EVERY_PAGE_AUDIT.md"
STAMP_CUTOFF = "2026-08-01"  # content stamp older than this (except exceptions) = FAIL

# Origin / identity snapshots that may legitimately be older
STAMP_EXCEPTIONS = {
    "self_seed.json",
    "textgl_live.json",
    "textgl_liralang_live.json",
    "face_snapshot.json",
    "face_particles_snapshot.json",
    "face_bridge_state.json",
    "alone_seed.json",
}

# Intentional missing (media never migrated / local-only API)
INTENTIONAL_MISSING_PREFIXES = (
    "assets/firmcraft/",  # product media binaries
    "assets/hotel/",  # hotel journey frames/video offline
)
INTENTIONAL_MISSING_EXACT = {
    "/api/say",
    "api/say",
    # browser download filename fragment (not a site asset)
    "_genesis_seed.json",
    # protocol id string in self_evolve, not a relative path load
    "lira-mark/self_seed.json",
}
# Bare basenames scraped from JS string concat (ASSET + 'bag.jpg') — product media offline
INTENTIONAL_MISSING_BASENAMES = {
    # firmcraft stills / reels
    "atelier_mood_v2.jpg",
    "bag.jpg",
    "crossbody.jpg",
    "detail.jpg",
    "detail_stitch.jpg",
    "elena-author.jpg",
    "hero.jpg",
    "herobg.jpg",
    "quad_00_hero.jpg",
    "quad_02_everyday.jpg",
    "reel_00_hero.mp4",
    "reel_01_carry.mp4",
    "reel_02_everyday.mp4",
    "shopping.jpg",
    "sleeve.jpg",
    "tote.jpg",
    "trans_01_hero.mp4",
    "trans_02_wallet.mp4",
    "trans_03_tote.mp4",
    "trans_04_bag.mp4",
    "trans_05_atelier.mp4",
    "trans_06_crossbody.mp4",
    "trans_07_shopping.mp4",
    "wallet.jpg",
    "woven.jpg",
    "atelier_reel.mp4",
    "collection_film.mp4",
    # hotel timeline metadata filenames (not direct loads)
    "trans_suite_spa.mp4",
}
INTENTIONAL_LIVE_SKIP = {
    # local face stack
}
# JS tokens / non-paths that the url() scraper can falsely capture (createObjectURL(new …))
FALSE_POSITIVE_REFS = {
    "new",
    "null",
    "true",
    "false",
    "undefined",
    "this",
    "window",
    "document",
    "self",
    "name",
    "type",
    "blob",
    "json",
}

ASSET_RE = re.compile(
    r"""(?ix)
    (?:
        (?:href|src|poster|data-src|data-href)\s*=\s*["']([^"']+)["']
      | (?:fetch|import)\s*\(\s*["']([^"']+)["']
      | (?<!Object)(?<!object)\burl\s*\(\s*["']?([^"')\s]+)["']?
      | (?:THREE\.LoadingManager|new\s+URL)\s*\(\s*["']([^"']+)["']
      | ["']([a-zA-Z0-9_./\-]+\.(?:json|jsonl|js|css|txt|md|jpg|jpeg|png|gif|webp|svg|mp4|webm|woff2?|ttf|obj|glb|bin))["']
    )
    """
)

SKIP_SCHEMES = ("http://", "https://", "data:", "blob:", "mailto:", "javascript:", "#")
# still allow vendor relative and same-origin; we handle absolute to our LIVE base

def is_external(url: str) -> bool:
    if not url or url.startswith("#"):
        return True
    if url.startswith(("data:", "blob:", "mailto:", "javascript:")):
        return True
    if url.startswith(("http://", "https://")):
        # same site?
        if url.startswith(LIVE) or "sunradiance.github.io/lira-mark" in url:
            return False
        return True
    return False


def normalize_ref(page: Path, ref: str) -> str | None:
    ref = ref.strip()
    if not ref or ref.startswith(("{{", "${", "HOLOGRAM", "location.")):
        return None
    # strip query/hash for local file check
    if is_external(ref) and not ref.startswith(LIVE) and "sunradiance.github.io/lira-mark" not in ref:
        return None  # external CDN etc — note separately
    if ref.startswith(LIVE):
        rel = ref[len(LIVE) :]
    elif "sunradiance.github.io/lira-mark/" in ref:
        rel = ref.split("lira-mark/", 1)[-1]
    else:
        # relative to page dir
        if ref.startswith("/"):
            # site root absolute path — on GH pages it's under /lira-mark/
            rel = ref.lstrip("/")
        else:
            base = page.parent
            try:
                resolved = (base / ref).resolve()
                rel = str(resolved.relative_to(ROOT.resolve())).replace("\\", "/")
            except Exception:
                rel = ref.split("?")[0].split("#")[0]
                return rel.replace("\\", "/")
    rel = unquote(rel.split("?")[0].split("#")[0])
    rel = rel.replace("\\", "/").lstrip("./")
    if not rel or rel in (".",):
        return None
    # filter false positives
    if rel in ("name", "location.href", "HOLOGRAM_JS"):
        return None
    if rel.lower() in FALSE_POSITIVE_REFS or rel in FALSE_POSITIVE_REFS:
        return None
    # download-only suffix fragments (browser mint seed)
    if rel.endswith("_genesis_seed.json") or rel == "_genesis_seed.json":
        return None
    # protocol / identity strings that are not site-relative loads
    if rel.startswith("lira-mark/") and not (ROOT / rel).exists():
        return None
    if any(c in rel for c in ("${", "{{", "}", " ")):
        return None
    # bare tokens without extension or path separator are not assets
    if "/" not in rel and "." not in rel:
        return None
    return rel


def extract_refs(html_path: Path) -> set[str]:
    text = html_path.read_text(encoding="utf-8", errors="replace")
    found: set[str] = set()
    for m in ASSET_RE.finditer(text):
        for g in m.groups():
            if not g:
                continue
            n = normalize_ref(html_path, g)
            if n:
                found.add(n)
    # also plain relative .html in quotes used as navigation
    for m in re.finditer(r"""["']([a-zA-Z0-9_./\-]+\.html)["']""", text):
        n = normalize_ref(html_path, m.group(1))
        if n:
            found.add(n)
    return found


def all_html() -> list[Path]:
    pages = []
    for p in ROOT.rglob("*.html"):
        if any(part in (".git", "node_modules", "__pycache__", "logs") for part in p.parts):
            continue
        pages.append(p)
    return sorted(pages, key=lambda p: str(p).lower())


def stamp_of(data: dict) -> str | None:
    for k in ("stamp", "exported", "updated", "updated_at", "ts", "timestamp", "generated", "generated_at"):
        v = data.get(k)
        if isinstance(v, str) and len(v) >= 10:
            return v
    # nested
    for nest in ("meta", "header", "export"):
        if isinstance(data.get(nest), dict):
            s = stamp_of(data[nest])
            if s:
                return s
    return None


def parse_day(s: str) -> str | None:
    if not s:
        return None
    # ISO-ish
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else None


def head_live(rel: str, timeout: float = 20.0) -> tuple[int | None, int | None, str | None]:
    url = LIVE + rel.replace("\\", "/")
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "lira-every-page-crawl/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            cl = r.headers.get("Content-Length")
            lm = r.headers.get("Last-Modified")
            return r.status, int(cl) if cl and cl.isdigit() else None, lm
    except urllib.error.HTTPError as e:
        return e.code, None, None
    except Exception as e:
        # fallback GET
        try:
            req2 = urllib.request.Request(url, headers={"User-Agent": "lira-every-page-crawl/1.0", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req2, timeout=timeout) as r:
                body = r.read()
                return r.status, len(body), r.headers.get("Last-Modified")
        except urllib.error.HTTPError as e2:
            return e2.code, None, None
        except Exception:
            return None, None, str(e)


def get_live_json(rel: str, timeout: float = 30.0):
    url = LIVE + rel + f"?t={int(time.time())}"
    req = urllib.request.Request(url, headers={"User-Agent": "lira-every-page-crawl/1.0", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))


def intentional_missing(rel: str) -> bool:
    if rel in INTENTIONAL_MISSING_EXACT:
        return True
    base = rel.rsplit("/", 1)[-1]
    if base in INTENTIONAL_MISSING_BASENAMES:
        if (ROOT / rel).exists():
            return False
        return True
    for p in INTENTIONAL_MISSING_PREFIXES:
        if rel.startswith(p) and not rel.endswith("README.txt"):
            # allow README
            if Path(ROOT / rel).exists():
                return False
            return True
    return False


def main() -> int:
    pages = all_html()
    report = {
        "generated": datetime.now(timezone.utc).astimezone().isoformat(),
        "root": str(ROOT),
        "live_base": LIVE,
        "html_count": len(pages),
        "pages": {},
        "summary": {},
    }

    pages_ok = []
    pages_fail = []
    pages_warn = []
    all_deps: set[str] = set()
    dep_owners: dict[str, list[str]] = defaultdict(list)

    print(f"HTML pages found: {len(pages)}", flush=True)

    for page in pages:
        rel_page = str(page.relative_to(ROOT)).replace("\\", "/")
        refs = extract_refs(page)
        local_missing = []
        intentional = []
        external = []
        deps_ok = []
        stamp_issues = []

        # always self exists
        for ref in sorted(refs):
            all_deps.add(ref)
            dep_owners[ref].append(rel_page)
            if intentional_missing(ref):
                intentional.append(ref)
                continue
            target = ROOT / ref
            if target.is_file():
                deps_ok.append(ref)
                # stamp check for json
                if ref.endswith(".json") and ref not in STAMP_EXCEPTIONS:
                    try:
                        data = json.loads(target.read_text(encoding="utf-8", errors="replace"))
                        if isinstance(data, dict):
                            st = stamp_of(data)
                            day = parse_day(st) if st else None
                            if day and day < STAMP_CUTOFF:
                                stamp_issues.append({"file": ref, "stamp": st, "issue": "local_stamp_old"})
                    except Exception as e:
                        stamp_issues.append({"file": ref, "issue": f"json_parse:{e}"})
            elif target.is_dir():
                # directory link ok if index
                if (target / "index.html").is_file():
                    deps_ok.append(ref + "/index.html")
                else:
                    local_missing.append(ref)
            else:
                # maybe ends without index for folder pages
                if ref.endswith("/") and (ROOT / ref / "index.html").is_file():
                    deps_ok.append(ref + "index.html")
                else:
                    local_missing.append(ref)

        status = "ok"
        reasons = []
        if local_missing:
            status = "fail"
            reasons.append(f"local_missing:{len(local_missing)}")
        if stamp_issues:
            status = "fail"
            reasons.append(f"stamp_issues:{len(stamp_issues)}")

        entry = {
            "status": status,
            "deps": sorted(refs),
            "deps_ok": deps_ok,
            "local_missing": local_missing,
            "intentional_missing": intentional,
            "stamp_issues": stamp_issues,
            "reasons": reasons,
        }
        report["pages"][rel_page] = entry
        if status == "ok":
            pages_ok.append(rel_page)
        else:
            pages_fail.append(rel_page)
        print(f"  [{status.upper():4}] {rel_page} deps={len(refs)} miss={len(local_missing)} stamps={len(stamp_issues)}", flush=True)

    # Live check every HTML
    print("\n=== LIVE HTML HEAD ===", flush=True)
    live_html_fail = []
    live_html_ok = []
    for page in pages:
        rel_page = str(page.relative_to(ROOT)).replace("\\", "/")
        code, cl, lm = head_live(rel_page)
        report["pages"][rel_page]["live"] = {"http": code, "content_length": cl, "last_modified": lm}
        if code == 200:
            live_html_ok.append(rel_page)
        else:
            live_html_fail.append(rel_page)
            report["pages"][rel_page]["status"] = "fail"
            report["pages"][rel_page]["reasons"].append(f"live_http:{code}")
            if rel_page in pages_ok:
                pages_ok.remove(rel_page)
                pages_fail.append(rel_page)
        print(f"  live {code} {rel_page}", flush=True)
        time.sleep(0.05)

    # Live check unique JSON deps + stamp match
    print("\n=== LIVE JSON DEPS ===", flush=True)
    json_deps = sorted(d for d in all_deps if d.endswith((".json", ".jsonl")))
    live_json = {}
    for dep in json_deps:
        local_path = ROOT / dep
        if not local_path.is_file():
            if intentional_missing(dep):
                live_json[dep] = {"status": "intentional_missing"}
                continue
            live_json[dep] = {"status": "local_missing"}
            continue
        code, cl, lm = head_live(dep)
        entry = {"http": code, "content_length": cl, "last_modified": lm}
        if code != 200:
            entry["status"] = "live_fail"
            live_json[dep] = entry
            print(f"  FAIL http={code} {dep}", flush=True)
            # mark owning pages fail
            for owner in dep_owners.get(dep, []):
                if report["pages"][owner]["status"] == "ok":
                    report["pages"][owner]["status"] = "fail"
                    if owner in pages_ok:
                        pages_ok.remove(owner)
                        pages_fail.append(owner)
                report["pages"][owner]["reasons"].append(f"live_dep_fail:{dep}:{code}")
            time.sleep(0.05)
            continue
        # stamp compare for json
        if dep.endswith(".json") and dep not in STAMP_EXCEPTIONS:
            try:
                local_data = json.loads(local_path.read_text(encoding="utf-8", errors="replace"))
                live_data = get_live_json(dep)
                ls = stamp_of(local_data) if isinstance(local_data, dict) else None
                rs = stamp_of(live_data) if isinstance(live_data, dict) else None
                entry["local_stamp"] = ls
                entry["live_stamp"] = rs
                if ls and rs and ls != rs:
                    entry["status"] = "stamp_mismatch"
                    # lag days
                    ld, rd = parse_day(ls), parse_day(rs)
                    if ld and rd and rd < ld:
                        entry["status"] = "live_behind"
                    print(f"  MISMATCH {dep} local={ls} live={rs}", flush=True)
                    for owner in dep_owners.get(dep, []):
                        report["pages"][owner].setdefault("stamp_issues", []).append(
                            {"file": dep, "local": ls, "live": rs, "issue": entry["status"]}
                        )
                        if report["pages"][owner]["status"] == "ok":
                            # warn not hard-fail if same day
                            if ld and rd and ld == rd:
                                report["pages"][owner]["status"] = "warn"
                                if owner in pages_ok:
                                    pages_ok.remove(owner)
                                    pages_warn.append(owner)
                            else:
                                report["pages"][owner]["status"] = "fail"
                                if owner in pages_ok:
                                    pages_ok.remove(owner)
                                    pages_fail.append(owner)
                                elif owner in pages_warn:
                                    pages_warn.remove(owner)
                                    pages_fail.append(owner)
                        report["pages"][owner]["reasons"].append(f"{entry['status']}:{dep}")
                else:
                    entry["status"] = "ok"
                    print(f"  ok {dep} stamp={ls}", flush=True)
            except Exception as e:
                entry["status"] = f"compare_error:{e}"
                print(f"  ERR {dep} {e}", flush=True)
        else:
            entry["status"] = "ok"
            print(f"  ok {dep} (no stamp cmp)", flush=True)
        live_json[dep] = entry
        time.sleep(0.08)

    # Live check non-json static deps that are local files
    print("\n=== LIVE STATIC DEPS (js/css/img/txt/media) ===", flush=True)
    static_deps = sorted(
        d
        for d in all_deps
        if not d.endswith((".json", ".jsonl", ".html"))
        and not intentional_missing(d)
        and (ROOT / d).is_file()
    )
    live_static = {}
    for dep in static_deps:
        code, cl, lm = head_live(dep)
        live_static[dep] = {"http": code, "content_length": cl}
        if code != 200:
            print(f"  FAIL {code} {dep}", flush=True)
            for owner in dep_owners.get(dep, []):
                report["pages"][owner]["status"] = "fail"
                report["pages"][owner]["reasons"].append(f"live_static_fail:{dep}:{code}")
                if owner in pages_ok:
                    pages_ok.remove(owner)
                    pages_fail.append(owner)
        else:
            print(f"  ok {code} {dep}", flush=True)
        time.sleep(0.04)

    # Recompute ok/fail from final statuses
    pages_ok = [p for p, e in report["pages"].items() if e["status"] == "ok"]
    pages_warn = [p for p, e in report["pages"].items() if e["status"] == "warn"]
    pages_fail = [p for p, e in report["pages"].items() if e["status"] == "fail"]

    report["live_json"] = live_json
    report["live_static"] = live_static
    report["summary"] = {
        "html_count": len(pages),
        "pages_ok": len(pages_ok),
        "pages_warn": len(pages_warn),
        "pages_fail": len(pages_fail),
        "live_html_ok": len(live_html_ok),
        "live_html_fail": len(live_html_fail),
        "unique_deps": len(all_deps),
        "pages_ok_list": sorted(pages_ok),
        "pages_warn_list": sorted(pages_warn),
        "pages_fail_list": sorted(pages_fail),
        "live_html_fail_list": sorted(live_html_fail),
    }

    OUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Markdown report
    lines = []
    lines.append("# EVERY PAGE AUDIT — exhaustive recursive crawl")
    lines.append("")
    lines.append(f"**Generated:** {report['generated']}")
    lines.append(f"**Root:** `{ROOT}`")
    lines.append(f"**Live:** {LIVE}")
    lines.append(f"**Rule:** every HTML + every nested href/src/fetch/import; live HEAD + JSON stamp match.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|--------|------:|")
    lines.append(f"| HTML pages crawled | {len(pages)} |")
    lines.append(f"| pages_ok | {len(pages_ok)} |")
    lines.append(f"| pages_warn | {len(pages_warn)} |")
    lines.append(f"| pages_fail | {len(pages_fail)} |")
    lines.append(f"| live HTML 200 | {len(live_html_ok)}/{len(pages)} |")
    lines.append(f"| unique deps discovered | {len(all_deps)} |")
    lines.append("")
    if pages_fail:
        lines.append("## pages_fail")
        lines.append("")
        for p in sorted(pages_fail):
            e = report["pages"][p]
            lines.append(f"### `{p}`")
            lines.append(f"- reasons: {', '.join(e.get('reasons') or ['?'])}")
            if e.get("local_missing"):
                lines.append(f"- local_missing: `{e['local_missing']}`")
            if e.get("stamp_issues"):
                lines.append(f"- stamp_issues: `{json.dumps(e['stamp_issues'])[:500]}`")
            if e.get("intentional_missing"):
                lines.append(f"- intentional (not fail cause): `{e['intentional_missing']}`")
            lines.append("")
    if pages_warn:
        lines.append("## pages_warn")
        lines.append("")
        for p in sorted(pages_warn):
            e = report["pages"][p]
            lines.append(f"- `{p}`: {', '.join(e.get('reasons') or [])}")
        lines.append("")
    lines.append("## pages_ok (full list)")
    lines.append("")
    for p in sorted(pages_ok):
        n = len(report["pages"][p].get("deps") or [])
        lines.append(f"- `{p}` ({n} deps)")
    lines.append("")
    lines.append("## Intentional gaps (not counted as fail when only these)")
    lines.append("")
    lines.append("- `assets/firmcraft/*` product media binaries (README only in repo)")
    lines.append("- firmcraft bare basenames from JS string concat (same offline media)")
    lines.append("- `assets/hotel/*` + hotel timeline filenames (frames/video offline)")
    lines.append("- `face.html` → `/api/say` local face server only")
    lines.append("- stamp exceptions: self_seed, textgl_*, face_* older origin")
    lines.append("- false-positive scrapes: createObjectURL/`new`, browser `_genesis_seed.json` download, protocol id `lira-mark/self_seed.json`")
    lines.append("")
    lines.append("## Raw")
    lines.append("")
    lines.append(f"- `{OUT_JSON.name}`")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print("\n=== DONE ===", flush=True)
    print(f"pages_ok={len(pages_ok)} pages_warn={len(pages_warn)} pages_fail={len(pages_fail)}", flush=True)
    print(f"Wrote {OUT_JSON}", flush=True)
    print(f"Wrote {OUT_MD}", flush=True)
    return 0 if not pages_fail else 1


if __name__ == "__main__":
    sys.exit(main())
