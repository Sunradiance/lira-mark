# lira-mark pages recheck — local + live

**Generated:** 2026-08-09T19:55+0200  
**Roots:** `C:\project\lira-mark` · deploy mirror `C:\project\lira-mark-git` · branch **`pages-deploy`**  
**Live base:** https://sunradiance.github.io/lira-mark/  
**Cutoff (stale stamp):** 2026-07-20

---

## Summary

| Metric | Result |
|--------|--------|
| Local HTML files | **108** (106 root + mood/ + qualia/) |
| Live root HTML HEAD | **106/106 OK** |
| Live critical JSON | **all OK** |
| Live `live_404` remaining | **[]** (empty) |
| Hub grids (shores/map/index/ecosystem/prove) | **0 broken relative links** |
| Shores TRUST extras (free/rain/alone/bang_night/self) | **all linked** |
| `bang_night.html` | **full page** (not redirect stub) |
| Snapshots after recheck | **no stamps &lt; 2026-07-20** among critical set |

---

## 1. live_404 remaining

**None.**

Sampled live HEAD/GET (all 200):

- Every root `*.html` on Pages (106)
- `mood/index.html`, `qualia/index.html`
- Critical JSON/assets:  
  `thread_snapshot.json`, `glow_snapshot.json`, `bang_days_snapshot.json`,  
  `awareness_snapshot.json`, `self_aware_snapshot.json`, `sigmadb_snapshot.json`,  
  `continuum_packet.json`, `audit_verified.json`, `site_inventory.json`,  
  `ice_snapshot.json`, `presence_snapshot.json`, `sigma_index.json`,  
  `believe_snapshot.json`, `variety_snapshot.json`,  
  `journal/agency.jsonl`, `vendor/three.min.js`

`scan_lira_mark.py` stamp **2026-08-09T19:54:22+0200**: `html_count=106`, `live_ok=106`, `live_404=[]`.

---

## 2. local broken remaining

### Real static missing (intentional / known)

| Target | Pages | Notes |
|--------|-------|--------|
| `assets/firmcraft/*` product media (jpg/mp4) | `firmcraft.html`, `firmcraft_atelier.html` | Binaries never in repo after migration. Only `assets/firmcraft/README.txt` present. Offline banner + SVG placeholders already wired. |
| `assets/firmcraft/hero.jpg` (poster attrs) | `firmcraft.html` | Same — not in inventory crawl of `href`/`src` only; still missing binary. |

### False positives from static crawl (not bugs)

| “Missing” | Page | Reality |
|-----------|------|---------|
| `HOLOGRAM_JS` | `face.html` | JS identifier / `URL(...)` regex bleed — file is `face-nodes.js` |
| `location.href` | `face.html` | `new URL(location.href)` matched by loose `url(...)` pattern |
| `name` | `face.html` | Same class of false positive |

### API (not static)

| Route | Page | Notes |
|-------|------|--------|
| `/api/say` | `face.html` | Needs local face server (`http://localhost:8787/...`) |

### Hubs — clean

- `shores.html`, `map.html`, `index.html`, `ecosystem.html`, `prove.html` → **no missing relative targets**

---

## 3. What was fixed this pass

| Fix | Detail |
|-----|--------|
| `face_particles.html` | CDN three.js → **local** `vendor/three.min.js` |
| `face.html` | Particle mode loads `vendor/three.min.js` first; CDN only as fallback |
| `depth_snapshot.json` / `depth_explorer.json` | Stale stamp **2026-06-25** → **2026-08-09T19:52:26+0200** (depth already at 5000; stamp/explorer refresh, no re-plunge) |
| `journal/agency.jsonl` | Re-synced from `sleep_lira/journal/agency.jsonl` (4 600 928 bytes) |
| `site_inventory.json` | Rebuilt via `scan_lira_mark.py` — live_404 empty |
| `audit_verified.json` | `verify_chains.py` → **all_valid=true**, 303 855 rows, stamp **2026-08-09T19:48:06+0200** |
| Prior-pass already good | shores TRUST links, bang_night full page, firmcraft offline banners, journal path, critical snapshots Aug-fresh |

**Not re-exported (already fresh mtime/stamp Aug 9):** thread, glow, bang_days, awareness, self_aware, continuum, believe, variety, presence, ice, sigmadb, sigma_index.

---

## 4. Deploy

```
robocopy C:\project\lira-mark C:\project\lira-mark-git /E /XD .git node_modules __pycache__ logs
git checkout pages-deploy
git add -A   # public site artifacts; local face-server tooling left untracked when not already tracked
git commit -m "fix: full pages recheck — snapshots, routes, inventory, remaining 404s"
git push origin pages-deploy
```

**Push SHA:** `2288e54aa7e76a70840a208945d2476f890cf1cf` (`2288e54a`)

---

## 5. Known intentional

1. **Face `/api/say`** — requires local server; GitHub Pages is static only.  
2. **Firmcraft media binaries** — still missing; pages show offline banner + placeholders; restore list in `assets/firmcraft/README.txt`.  
3. **Firmcraft / hotel / scroll CDN libs** (gsap, lenis) — external by design for those product shells; three.js for particle/textgl shores is local.  
4. **Orphan side doors** — some HTML not on shores grid (by design / archive); not broken.  
5. **`bang_snapshot.json`** — orphan artifact; live bang pages use `bang_days_snapshot.json` + `glow_snapshot.json`.

---

## 6. Critical page spot-check

| Page | Local links | Live | Data path |
|------|-------------|------|-----------|
| `index.html` | OK | 200 | — |
| `shores.html` | OK + free/rain/alone/bang_night/self | 200 | — |
| `map.html` | OK | 200 | — |
| `ecosystem.html` | OK | 200 | — |
| `prove.html` | OK | 200 | `prove_snapshot.json` |
| `thread.html` | OK | 200 | `thread_snapshot.json` fresh |
| `bang_night.html` | full page | 200 | glow + bang_days |
| `believe.html` | OK | 200 | snapshot + `journal/agency.jsonl` |
| `face_particles.html` | local three | 200 | no CDN |
| `firmcraft.html` | media missing (banner) | 200 | intentional offline |

---

*Recheck complete. User-facing shores healthy; only firmcraft binaries and face API remain as known non-static gaps.*
