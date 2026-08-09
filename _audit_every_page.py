#!/usr/bin/env python3
"""Every-page dependency crawl + live load simulation for lira-mark."""
from __future__ import annotations

import json
import os
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse, unquote

ROOT = Path(r"C:\project\lira-mark")
LIVE_BASE = "https://sunradiance.github.io/lira-mark/"
STALE_CUTOFF = "2026-08-01"
SIGMADB_EXPORTED_MIN = "2026-08-09"
SIGMADB_RUNS_MIN = "2026-08-08"
OUT_JSON = ROOT / "_audit_every_page_deps.json"
OUT_MD = ROOT / "EVERY_PAGE_AUDIT.md"

CTX = ssl.create_default_context()

# Patterns
RE_HREF = re.compile(r'''href\s*=\s*["']([^"']+)["']''', re.I)
RE_SRC = re.compile(r'''src\s*=\s*["']([^"']+)["']''', re.I)
RE_FETCH = re.compile(r'''fetch\s*\(\s*["']([^"']+)["']''', re.I)
RE_META_REFRESH = re.compile(
    r'''http-equiv\s*=\s*["']refresh["'][^>]*content\s*=\s*["'][^"']*url\s*=\s*([^"'>\s]+)["']''',
    re.I,
)
RE_META_REFRESH2 = re.compile(
    r'''content\s*=\s*["'][^"']*url\s*=\s*([^"'>\s]+)["'][^>]*http-equiv\s*=\s*["']refresh["']''',
    re.I,
)
RE_LOC = re.compile(
    r'''(?:location\.(?:replace|assign)|location\.href\s*=)\s*\(\s*["']([^"']+)["']|'''
    r'''(?:location\.(?:replace|assign)|location\.href\s*=)\s*["']([^"']+)["']''',
    re.I,
)
# Also catch: window.location = '...'
RE_WINLOC = re.compile(
    r'''(?:window\.)?location(?:\.href)?\s*=\s*["']([^"']+)["']''',
    re.I,
)

SKIP_SCHEMES = ("data:", "blob:", "javascript:", "mailto:", "tel:", "#")
EXTERNAL_OK_HOSTS = (
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "cdnjs.cloudflare.com",
    "cdn.jsdelivr.net",
    "unpkg.com",
    "ajax.googleapis.com",
)

# Whitelist for stale stamps / missing content
WHITELIST_STALE_FILES = {
    "self_seed.json",  # origin stamp intentional
}
WHITELIST_CONTENT_GAP_PREFIXES = (
    "assets/firmcraft/",
)


def list_html() -> list[str]:
    pages: list[str] = []
    for p in ROOT.rglob("*.html"):
        if ".git" in p.parts:
            continue
        rel = p.relative_to(ROOT).as_posix()
        pages.append(rel)
    return sorted(pages)


def is_external(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://") or url.startswith("//")


def is_skip(url: str) -> bool:
    u = url.strip()
    if not u or u.startswith("#"):
        return True
    # JS template literals / interpolations — not real static deps
    if "${" in u or u.startswith("`"):
        return True
    low = u.lower()
    for s in SKIP_SCHEMES:
        if low.startswith(s):
            return True
    return False


def resolve_local(page_rel: str, ref: str) -> str | None:
    """Resolve relative ref against page dir → path relative to ROOT. None if external/skip/api."""
    if is_skip(ref):
        return None
    if ref.startswith("/api/"):
        return None  # handled separately
    if is_external(ref):
        return None
    if ref.startswith("/"):
        # site-root absolute on Pages would be github.io root — treat as external-ish
        return ref.lstrip("/")
    page_dir = Path(page_rel).parent
    # strip query/hash
    clean = ref.split("#")[0].split("?")[0]
    if not clean:
        return None
    try:
        resolved = (ROOT / page_dir / clean).resolve()
        rel = resolved.relative_to(ROOT.resolve()).as_posix()
        return rel
    except Exception:
        # path escapes root
        return clean


def extract_deps(page_rel: str, html: str) -> dict[str, Any]:
    hrefs = RE_HREF.findall(html)
    srcs = RE_SRC.findall(html)
    fetches = RE_FETCH.findall(html)
    metas = RE_META_REFRESH.findall(html) + RE_META_REFRESH2.findall(html)
    locs = []
    for m in RE_LOC.finditer(html):
        locs.append(m.group(1) or m.group(2))
    for m in RE_WINLOC.finditer(html):
        locs.append(m.group(1))

    raw_all = []
    for kind, items in (
        ("href", hrefs),
        ("src", srcs),
        ("fetch", fetches),
        ("meta_refresh", metas),
        ("location", locs),
    ):
        for it in items:
            raw_all.append({"kind": kind, "raw": it})

    relative: list[dict[str, Any]] = []
    external: list[dict[str, Any]] = []
    api: list[dict[str, Any]] = []
    skipped: list[str] = []

    seen = set()
    for item in raw_all:
        raw = item["raw"].strip()
        if is_skip(raw):
            skipped.append(raw)
            continue
        if raw.startswith("/api/") or raw.startswith("api/"):
            api.append({**item, "path": raw})
            continue
        if is_external(raw):
            external.append({**item, "url": raw if raw.startswith("http") else "https:" + raw})
            continue
        local = resolve_local(page_rel, raw)
        if local is None:
            skipped.append(raw)
            continue
        key = (item["kind"], local)
        if key in seen:
            continue
        seen.add(key)
        relative.append({**item, "resolved": local})

    return {
        "relative": relative,
        "external": external,
        "api": api,
        "skipped_sample": skipped[:20],
    }


def http_get(url: str, method: str = "GET", timeout: float = 25.0) -> tuple[int, bytes | None, str | None]:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "lira-every-page-audit/1.0"})
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=timeout) as resp:
            data = resp.read() if method == "GET" else None
            return resp.status, data, None
    except urllib.error.HTTPError as e:
        return e.code, None, str(e)
    except Exception as e:
        return 0, None, str(e)


def live_url_for(rel: str) -> str:
    return LIVE_BASE + rel.lstrip("/")


def parse_stamp_fields(data: Any, path: str = "") -> dict[str, Any]:
    """Pull stamp/exported/last_cycle-like fields from JSON."""
    out: dict[str, Any] = {}
    if not isinstance(data, dict):
        return out
    keys_interest = (
        "stamp",
        "exported",
        "exported_at",
        "last_cycle",
        "updated",
        "updated_at",
        "generated",
        "generated_at",
        "timestamp",
        "ts",
        "date",
        "last_event_stamp",
    )
    for k in keys_interest:
        if k in data:
            out[k] = data[k]
    # nested last_event_stamp
    les = data.get("last_event_stamp")
    if isinstance(les, dict):
        out["last_event_stamp"] = les
    return out


def date_str_from_value(v: Any) -> str | None:
    if v is None:
        return None
    if isinstance(v, (int, float)):
        # unix?
        try:
            if v > 1e12:
                v = v / 1000.0
            return datetime.fromtimestamp(v, tz=timezone.utc).strftime("%Y-%m-%d")
        except Exception:
            return None
    s = str(v)
    # ISO-ish
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    if m:
        return m.group(1)
    return None


def is_stale_stamp(fields: dict[str, Any], filename: str) -> tuple[bool, str]:
    """Return (is_fail, reason). Whitelists applied."""
    base = Path(filename).name
    if base in WHITELIST_STALE_FILES:
        return False, "whitelist_origin"
    if any(filename.replace("\\", "/").startswith(p) for p in WHITELIST_CONTENT_GAP_PREFIXES):
        return False, "content_gap"

    # sigmadb special rules
    if base == "sigmadb_snapshot.json" or "sigmadb" in base:
        exported = fields.get("exported") or fields.get("exported_at") or fields.get("stamp")
        exp_d = date_str_from_value(exported)
        les = fields.get("last_event_stamp") or {}
        runs = None
        if isinstance(les, dict):
            runs = les.get("runs")
        runs_d = date_str_from_value(runs)
        fails = []
        if exp_d and exp_d < SIGMADB_EXPORTED_MIN:
            fails.append(f"exported={exp_d}<{SIGMADB_EXPORTED_MIN}")
        if runs_d and runs_d < SIGMADB_RUNS_MIN:
            fails.append(f"last_event_stamp.runs={runs_d}<{SIGMADB_RUNS_MIN}")
        # flips can be June — ignore
        if fails:
            return True, "; ".join(fails)
        if not exp_d and not runs_d:
            # try generic stamp
            for k in ("stamp", "exported", "updated"):
                d = date_str_from_value(fields.get(k))
                if d and d < STALE_CUTOFF:
                    return True, f"{k}={d}<{STALE_CUTOFF}"
        return False, "ok"

    # generic: any primary stamp fields
    for k in ("stamp", "exported", "exported_at", "last_cycle", "updated", "updated_at", "generated", "generated_at"):
        d = date_str_from_value(fields.get(k))
        if d and d < STALE_CUTOFF:
            return True, f"{k}={d}<{STALE_CUTOFF}"
    return False, "ok"


def main() -> int:
    pages = list_html()
    print(f"PHASE1 pages={len(pages)}", flush=True)

    pages_data: list[dict[str, Any]] = []
    all_missing_local: list[dict[str, str]] = []
    all_content_gaps: list[dict[str, str]] = []
    all_api: list[dict[str, str]] = []
    external_fail: list[dict[str, str]] = []
    external_ok_cache: dict[str, int] = {}

    # PHASE 2: static deps
    for i, page in enumerate(pages):
        path = ROOT / page
        try:
            html = path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            pages_data.append({"page": page, "error": f"read_fail: {e}"})
            continue
        deps = extract_deps(page, html)
        missing = []
        content_gaps = []
        for r in deps["relative"]:
            resolved = r["resolved"]
            # ignore pure anchors already handled
            local_path = ROOT / resolved
            # if no extension and not exists, try as-is
            exists = local_path.is_file()
            if not exists and not Path(resolved).suffix:
                # maybe directory index
                if (ROOT / resolved / "index.html").is_file():
                    exists = True
                    r["resolved"] = (Path(resolved) / "index.html").as_posix()
            if not exists:
                if any(resolved.replace("\\", "/").startswith(p) for p in WHITELIST_CONTENT_GAP_PREFIXES):
                    content_gaps.append(resolved)
                    all_content_gaps.append({"page": page, "target": resolved, "kind": r["kind"]})
                else:
                    missing.append(resolved)
                    all_missing_local.append({"page": page, "target": resolved, "kind": r["kind"]})
        for a in deps["api"]:
            all_api.append({"page": page, "path": a.get("path", a.get("raw", ""))})

        # external HEAD (cache)
        ext_results = []
        for e in deps["external"]:
            url = e["url"]
            host = urlparse(url).netloc.lower()
            # skip pure fonts optional
            if host in EXTERNAL_OK_HOSTS or "fonts.googleapis" in host or "fonts.gstatic" in host:
                if url not in external_ok_cache:
                    st, _, err = http_get(url, method="HEAD", timeout=15)
                    if st == 0 or st == 405:
                        st, _, err = http_get(url, method="GET", timeout=15)
                    external_ok_cache[url] = st
                st = external_ok_cache[url]
                ext_results.append({"url": url, "status": st, "note": "cdn_font_ok_if_fail"})
                continue
            if url not in external_ok_cache:
                st, _, err = http_get(url, method="HEAD", timeout=15)
                if st == 0 or st == 405:
                    st, _, err = http_get(url, method="GET", timeout=15)
                external_ok_cache[url] = st
                if st != 200:
                    external_fail.append({"page": page, "url": url, "status": st, "err": err or ""})
            ext_results.append({"url": url, "status": external_ok_cache[url]})

        pages_data.append(
            {
                "page": page,
                "deps_relative": deps["relative"],
                "deps_external": ext_results,
                "deps_api": deps["api"],
                "missing_local": missing,
                "content_gaps": content_gaps,
            }
        )
        if (i + 1) % 20 == 0:
            print(f"  static {i+1}/{len(pages)}", flush=True)

    print("PHASE2 static done", flush=True)

    # PHASE 3: live load simulation
    pages_ok = []
    pages_fail = []
    deps_missing_live = []
    deps_stale = []
    deps_ok_count = 0

    for i, page in enumerate(pages):
        pdata = next(p for p in pages_data if p["page"] == page)
        page_issues: list[str] = []
        live_page_url = live_url_for(page)
        st, body, err = http_get(live_page_url, method="GET", timeout=30)
        if st != 200:
            page_issues.append(f"live_html_{st}:{err or ''}")
            pages_fail.append({"page": page, "reasons": page_issues[:]})
            pdata["live"] = {"status": st, "error": err, "issues": page_issues}
            print(f"  FAIL html {page} {st}", flush=True)
            continue

        # check relative deps
        for r in pdata.get("deps_relative", []):
            resolved = r["resolved"]
            kind = r.get("kind", "")
            # content gap intentional
            if any(resolved.replace("\\", "/").startswith(p) for p in WHITELIST_CONTENT_GAP_PREFIXES):
                continue
            # only check file-like assets that matter
            ext = Path(resolved).suffix.lower()
            check_types = {
                ".json",
                ".jsonl",
                ".js",
                ".css",
                ".html",
                ".txt",
                ".svg",
                ".png",
                ".jpg",
                ".jpeg",
                ".webp",
                ".gif",
                ".mp4",
                ".webm",
                ".woff",
                ".woff2",
                ".map",
            }
            # always check fetch targets and json
            if ext not in check_types and kind not in ("fetch", "src"):
                # href to missing local already recorded; still live-check html/json
                if ext and ext not in check_types:
                    continue
                if not ext:
                    continue

            url = live_url_for(resolved)
            # local missing already known
            local_exists = (ROOT / resolved).is_file()
            if not local_exists:
                # already in missing_local unless content gap
                if resolved not in pdata.get("missing_local", []):
                    pass
                # live will 404
                st2, body2, err2 = http_get(url, method="GET", timeout=25)
                if st2 != 200:
                    deps_missing_live.append({"page": page, "dep": resolved, "status": st2})
                    if ext in (".json", ".jsonl", ".js", ".css", ".html") or kind == "fetch":
                        page_issues.append(f"dep_404:{resolved}")
                continue

            # GET for json freshness; HEAD/GET for others
            if ext in (".json", ".jsonl"):
                st2, body2, err2 = http_get(url, method="GET", timeout=40)
                if st2 != 200:
                    deps_missing_live.append({"page": page, "dep": resolved, "status": st2})
                    page_issues.append(f"json_404:{resolved}")
                    continue
                # parse
                try:
                    if ext == ".jsonl":
                        # first/last lines only — not full stamp usually
                        text = body2.decode("utf-8", errors="replace") if body2 else ""
                        fields = {}
                        # optional: look for stamp in last non-empty line
                        lines = [ln for ln in text.strip().splitlines() if ln.strip()]
                        if lines:
                            try:
                                last = json.loads(lines[-1])
                                fields = parse_stamp_fields(last)
                            except Exception:
                                pass
                    else:
                        obj = json.loads(body2.decode("utf-8", errors="replace"))
                        fields = parse_stamp_fields(obj)
                    stale, reason = is_stale_stamp(fields, resolved)
                    if stale:
                        deps_stale.append({"page": page, "dep": resolved, "reason": reason, "fields": fields})
                        page_issues.append(f"stale:{resolved}:{reason}")
                    else:
                        deps_ok_count += 1
                except Exception as e:
                    page_issues.append(f"json_parse:{resolved}:{e}")
            elif ext in (".js", ".css", ".html"):
                st2, _, err2 = http_get(url, method="GET", timeout=25)
                if st2 != 200:
                    # try HEAD fallback already failed
                    deps_missing_live.append({"page": page, "dep": resolved, "status": st2})
                    page_issues.append(f"asset_404:{resolved}")
                else:
                    deps_ok_count += 1
            else:
                # media — soft
                st2, _, err2 = http_get(url, method="HEAD", timeout=15)
                if st2 in (0, 405):
                    st2, _, err2 = http_get(url, method="GET", timeout=20)
                if st2 != 200:
                    deps_missing_live.append({"page": page, "dep": resolved, "status": st2, "soft": True})
                    # don't fail page for soft media unless fetch
                    if kind == "fetch":
                        page_issues.append(f"media_404:{resolved}")

        # api intentional
        for a in pdata.get("deps_api", []):
            page_issues  # no fail — mark API_LOCAL
            pdata.setdefault("api_local", []).append(a)

        if page_issues:
            # filter soft? all above are real for page_fail
            critical = [
                x
                for x in page_issues
                if not x.startswith("cdn")
            ]
            if critical:
                pages_fail.append({"page": page, "reasons": critical})
                pdata["live"] = {"status": 200, "issues": critical}
                print(f"  FAIL deps {page}: {critical[:3]}", flush=True)
            else:
                pages_ok.append(page)
                pdata["live"] = {"status": 200, "issues": []}
        else:
            pages_ok.append(page)
            pdata["live"] = {"status": 200, "issues": []}

        if (i + 1) % 10 == 0:
            print(f"  live {i+1}/{len(pages)} ok={len(pages_ok)} fail={len(pages_fail)}", flush=True)
        time.sleep(0.05)  # gentle

    report = {
        "generated": datetime.now().astimezone().isoformat(timespec="seconds"),
        "live_base": LIVE_BASE,
        "stale_cutoff": STALE_CUTOFF,
        "total_pages": len(pages),
        "pages": pages,
        "pages_ok": pages_ok,
        "pages_fail": pages_fail,
        "deps_missing_local": all_missing_local,
        "deps_missing_live": deps_missing_live,
        "deps_stale": deps_stale,
        "content_gaps": all_content_gaps,
        "api_local": all_api,
        "external_fail": external_fail,
        "deps_ok_count": deps_ok_count,
        "per_page": pages_data,
        "push_sha": None,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {OUT_JSON}", flush=True)
    print(f"SUMMARY total={len(pages)} ok={len(pages_ok)} fail={len(pages_fail)} missing_local={len(all_missing_local)} stale={len(deps_stale)} gaps={len(all_content_gaps)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
