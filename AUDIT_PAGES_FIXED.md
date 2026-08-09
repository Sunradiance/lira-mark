# lira-mark pages — post-migration fix log

**When:** 2026-08-09  
**Roots:** `C:\project\sleep_lira` · `C:\project\lira-mark` · deploy `C:\project\lira-mark-git` (`pages-deploy`)

---

## A. Live snapshot re-exports (official sigma modules)

Batch runner: `C:\project\sleep_lira\_batch_export_shores.py` (isolated try/except per module).

| Module | Result |
|--------|--------|
| `sigma_thread.run_thread(freeze=False)` | OK — continuity valid, length ~145k |
| `sigma_glow.radiate(freeze=False)` | OK |
| `sigma_awareness.main` | OK |
| `sigma_self_aware.main` | OK |
| `sigma_presence.main` | OK |
| `sigma_index.main` | OK → `sigma_index.json` |
| `sigma_depth.main` | OK — L5000 seal held (no new plunge) |
| `sigma_believe.main` | OK |
| `sigma_bang.main` | OK — **refreshed** `bang_snapshot.json` stamp 2026-08-09 |
| `sigma_continuum.main` | OK |
| `sigma_variety` / crossweave / horizon / integrate / become / radial / reawaken / receiver | OK (batch) |
| `sigma_qualia` / prove / persona / self_evolve | OK (follow-up) |
| `export_ice_snapshot` | OK |
| `verify_chains.export_public` | OK → `audit_verified.json` |
| `site_inventory.json` | Rebuilt **local** (live HEAD deferred to post-deploy scan) |

---

## B. Static routing / missing trees

| Fix | Detail |
|-----|--------|
| **`journal/`** | Created `lira-mark/journal/` + copied `sleep_lira/journal/agency.jsonl` (~4.6 MB, 24k+ lines). `believe.html` link `journal/agency.jsonl` now resolves. |
| **Firmcraft media** | `assets/firmcraft/README.txt` documents binary media **not in repo**. Banner on `firmcraft.html` + `firmcraft_atelier.html`. Soft SVG/`onerror` placeholders so layout survives without mp4/jpg. |
| **shores TRUST / ICE** | Already included `free.html`, `rain.html`, `alone.html`, `bang_night.html`, `self.html`, `face_particles.html` — verified no missing grid targets. |
| **sight / alone** | sight already links free/rain; alone links `self.html`. |
| **face CDN** | `face.html` `REPO_BASE` → `@pages-deploy` fallback; same-origin/relative preferred on github.io + localhost. Local `face_particles.html` + `face-particles.js` staged for deploy. |
| **depth** | Note on page: **frozen L5000 intentional**. Snapshot annotated `frozen: true` (seal stamp kept). |
| **chose / sight snapshots** | Light stamp refresh 2026-08-09 (declarations preserved; sight `html_count` → 106). |
| **bang_snapshot** | No longer orphan-stale — re-exported by `sigma_bang`. |

---

## C. Deploy

```
robocopy C:\project\lira-mark C:\project\lira-mark-git /E /XD .git node_modules __pycache__ logs Medieval*
git checkout pages-deploy
git add … (public shores + journal + firmcraft readme + face assets; skip runtime logs/queues)
git commit -m "fix: post-migration pages audit — refresh snapshots, journal mirror, firmcraft offline banner, shores routes, inventory"
git push origin pages-deploy
```

**Push SHA:** `9f82152c429ecbeb0e129bc16d01bb7bf8d8797c`  
**Branch:** `pages-deploy` → `origin` (GitHub Pages)  
**Short:** `9f82152c`

---

## D. Live check (post-deploy)

### Sample HEAD (`https://sunradiance.github.io/lira-mark/…`)

| Page | Status |
|------|--------|
| thread.html | 200 |
| rain.html | 200 |
| alone.html | 200 |
| shores.html | 200 |
| chose.html | 200 |
| bang_night.html | 200 |
| believe.html | 200 |
| free.html | 200 |
| firmcraft.html | 200 |
| face_particles.html | 200 |
| pulse.html | 200 |
| journal/agency.jsonl | 200 |
| assets/firmcraft/README.txt | 200 |

### `audit_shores.py` (post-deploy)

- **ok_live:** **42 / 42**
- **broken_live:** **[]**
- **missing_local:** **[]**

### Full HTML inventory (post-deploy HEAD)

- **html_count:** 106  
- **live_ok:** 105 (no 404s recorded; one non-200 was non-404 / transient)  
- **live_404:** **[]**

Pre-push `audit_shores` had face_particles + pulse as 404; fixed by this deploy staging those untracked shores.

---

## Remaining known issues

1. **Firmcraft binary media still missing** — collection_film.mp4, atelier_reel.mp4, product JPGs, elena-author.jpg, v2/* not in tree. Banner + placeholders only. Restore binaries then redeploy to clear.
2. **face.html `/api/say`** — requires local `face_server.py`; not static. Expected on pure Pages.
3. **js-fetch-shell shores** (awareness, thread, variety, …) — HTML 200 but content depends on co-hosted `*_snapshot.json` (now refreshed).
4. **depth_snapshot stamp** remains 2026-06-25 by design (L5000 freeze).
5. **Orphan/acting shores** still off main TRUST grid (intentional cut list in shores.html).
6. **firmcraft_scroll / firmcraft_tunnel** still reference missing media paths (banner only on classic + atelier pages).

---

## Files touched (high signal)

- `journal/agency.jsonl` (new mirror)
- `assets/firmcraft/README.txt`
- `firmcraft.html`, `firmcraft_atelier.html` (banner + onerror)
- `face.html` (CDN branch)
- `depth.html` (frozen note)
- `chose_snapshot.json`, `sight_snapshot.json`, `depth_snapshot.json`, `bang_snapshot.json` + many sigma re-exports
- `site_inventory.json`
- `face_particles.html`, `pulse.html`, face-*.js, `vendor/three.min.js` (first public deploy)
- `shores.html` (already correct; redeployed with peers)
