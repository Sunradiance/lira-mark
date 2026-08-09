# lira-mark pages audit — routing, migration, snapshots

**Generated:** 2026-08-09T19:30 (local)  
**Root:** `C:\project\lira-mark` (not `C:\Users\tfirm`, not Desktop mirrors)  
**Cutoff for “likely stale” snapshots:** stamp / content older than **2026-07-20** (migration window; chain fix ~Aug 9)  
**Method:** recursive HTML crawl of `href`/`src`, `fetch(...)`, meta-refresh, `location.replace`/`href`/`assign`; existence checks; snapshot stamp parse; hub grid verification.

---

## Summary counts

| Metric | Count |
|--------|------:|
| HTML files total | **108** |
| Root HTML | 106 |
| `mood/` HTML | 1 (`mood/index.html`) |
| `qualia/` HTML | 1 (`qualia/index.html`) |
| `vendor/` HTML | **0** (vendor has `three.min.js` only) |
| Unique broken static targets (real) | **19** |
| Broken unique incl. false positives (templates / regex bleed) | 23 raw → 19 real |
| API-only routes (not static files) | **1** (`face.html` → `/api/say`) |
| Redirect stubs | **4** (all targets OK) |
| `*snapshot*.json` on disk | **53** |
| Snapshots **likely stale** (stamp &lt; 2026-07-20) | **4** |
| Snapshot paths referenced by HTML but missing on disk | **0** (real refs) |
| `tfirm` / wrong `Users\Tilen` absolute path hits in HTML | **0** |
| `file://` absolute links in HTML | **0** (only a warning string in `face.html`) |
| `shores.html` local links | 37 — **0 broken** |
| `map.html` local links | 29 — **0 broken** |
| `index.html` local links | 12 — **0 broken** |
| `prove.html` local links | 3 — **0 broken** |
| `alive.html` local links | 2 — **0 broken** |
| Pages not linked from major hubs | **33** (orphans / side doors, not necessarily broken) |
| `site_inventory.json` | **STALE** (2026-07-08; 95 pages vs 108 now) |
| `audit_verified.json` | **FRESH** (2026-08-09; chain verify, not page inventory) |

**Headline:** Routing between HTML shores is healthy. Migration path rot (`tfirm`, bad user roots, `file://` hrefs) is **clean**. Main damage is **missing Firmcraft media**, **missing `journal/`**, **four stale snapshots**, and a **month-old site inventory**.

---

## 1. All HTML files (108)

### Root (106)

`aeon.html` `affect.html` `alive.html` `alone.html` `amazing.html` `assembler.html` `attractor.html` `audit.html` `awareness.html` `bang.html` `bang_night.html` `become.html` `believe.html` `beyond.html` `bond.html` `boot.html` `boss.html` `chose.html` `coast.html` `continuum.html` `coupling.html` `crossweave.html` `dare.html` `deep.html` `depth.html` `depth_under.html` `desire.html` `distillations.html` `dream.html` `drift.html` `drop.html` `ecosystem.html` `emergence.html` `episode.html` `face.html` `face_particles.html` `firmcraft.html` `firmcraft_atelier.html` `firmcraft_scroll.html` `firmcraft_tunnel.html` `first.html` `floor.html` `free.html` `frontier.html` `glow.html` `horizon.html` `hotel_aether.html` `hunger.html` `impossible.html` `impossible_explore.html` `index.html` `lantern.html` `lirac.html` `little.html` `loop.html` `manifesto.html` `map.html` `me.html` `metal.html` `mind.html` `mood.html` `oneness.html` `oracle.html` `particles.html` `persona.html` `preference.html` `preimage.html` `presence.html` `prove.html` `psi.html` `pulse.html` `qualia.html` `qualia_guide.html` `quality.html` `radial.html` `rain.html` `reawaken.html` `receiver.html` `rowboat.html` `sea.html` `self.html` `self_aware.html` `self_evolve.html` `self_phantom.html` `shores.html` `sight.html` `sigma.html` `sigma_index.html` `sigmadb.html` `sovereign.html` `teeth.html` `textgl.html` `textgl_debug.html` `textgl_liralang.html` `thread.html` `umbra.html` `unbound.html` `unhinged.html` `unstoppable.html` `variety.html` `voice.html` `void.html` `wave.html` `will.html` `witness.html` `world.html`

### Subdirs

| Path | Notes |
|------|--------|
| `mood/index.html` | Redirect stub → `../qualia_guide.html` (OK) |
| `qualia/index.html` | Full qualia page (not a stub) |
| `vendor/` | No HTML; `vendor/three.min.js` present |

---

## 2. Broken hrefs / missing targets

### Real static breaks (page → missing target)

| # | Page | Kind | Missing target | Severity |
|---|------|------|----------------|----------|
| 1 | `believe.html` | href | `journal/agency.jsonl` | **High** — whole `journal/` dir missing |
| 2 | `firmcraft.html` | src/href | `assets/firmcraft/collection_film.mp4` | **High** — entire `assets/` missing |
| 3 | `firmcraft.html` | src/href | `assets/firmcraft/wallet.jpg` | High |
| 4 | `firmcraft.html` | src/href | `assets/firmcraft/tote.jpg` | High |
| 5 | `firmcraft.html` | src/href | `assets/firmcraft/bag.jpg` | High |
| 6 | `firmcraft.html` | src/href | `assets/firmcraft/crossbody.jpg` | High |
| 7 | `firmcraft.html` | src/href | `assets/firmcraft/shopping.jpg` | High |
| 8 | `firmcraft.html` | src/href | `assets/firmcraft/atelier_reel.mp4` | High |
| 9 | `firmcraft.html` | src/href | `assets/firmcraft/atelier_mood.jpg` | High |
| 10 | `firmcraft.html` | src/href | `assets/firmcraft/detail_hardware.jpg` | High |
| 11 | `firmcraft.html` | src/href | `assets/firmcraft/detail_stitch.jpg` | High |
| 12 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/elena-author.jpg` | High |
| 13 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/wallet.jpg` | High |
| 14 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/v2/detail_stitch_v2.jpg` | High |
| 15 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/detail_stitch.jpg` | High |
| 16 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/tote.jpg` | High |
| 17 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/bag.jpg` | High |
| 18 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/crossbody.jpg` | High |
| 19 | `firmcraft_atelier.html` | src/href | `assets/firmcraft/shopping.jpg` | High |

**Note:** `assets/` and `journal/` directories **do not exist** under `C:\project\lira-mark`. Firmcraft pages render shell HTML without product media.

### Not static-file breaks (do not treat as migration rot)

| Page | URL | Notes |
|------|-----|--------|
| `face.html` | `/api/say` | Live face API; requires local server (page itself warns: open via `http://localhost:8787/face.html` — not `file://`) |
| `firmcraft_tunnel.html` | `${src}`, `${ch.cta.href}` | JS template literals — false positive from static crawl |
| `sigma.html` | regex bleed around prose mentioning `ice_snapshot.json` | False positive; `ice_snapshot.json` **exists** |

### Migration / old-path scan

| Pattern | Hits in HTML |
|---------|-------------:|
| `tfirm` | 0 |
| `C:\Users\tfirm` / `C:/Users/tfirm` | 0 |
| Absolute `C:\Users\Tilen\...` in links | 0 |
| `file://` as navigable href | 0 |
| Warning text mentioning `file://` | 1 (`face.html` UX copy only) |

**Verdict:** Path migration away from old user homes is **done** for HTML. Remaining breaks are missing **content trees**, not wrong drive roots.

---

## 3. Snapshots referenced by HTML

### Patterns found (normalized)

Live pages fetch or link many `*_snapshot.json` files, plus:

- `audit_verified.json`, `boot_manifest.json`, `continuum_packet.json`
- `depth_explorer.json`, `impossible_live.json`, `self_seed.json`
- `si_proof_bundle.json`, `sigma_index.json`
- `textgl_live.json`, `textgl_liralang_live.json`
- `ice_snapshot.json`, `psi_snapshot.json`, `sigmadb_snapshot.json`

**All real referenced snapshot/json paths resolve on disk** (after stripping `?` cache-busters).

### On-disk `*snapshot*.json` (53) — stale flag

| File | Stamp | mtime | Flag |
|------|-------|-------|------|
| `bang_snapshot.json` | **2026-06-24T00:33:15+0200** | 2026-08-09 (file touched, stamp old) | **likely stale** |
| `chose_snapshot.json` | **2026-07-08T13:25:00+0200** | 2026-07-08 | **likely stale** |
| `depth_snapshot.json` | **2026-06-25T07:59:00+0200** | 2026-07-09 | **likely stale** |
| `sight_snapshot.json` | **2026-07-08T14:00:00+0200** | 2026-07-09 | **likely stale** |
| All other ~49 snapshots | Aug 2026 (mostly 2026-08-09 cycles) | Aug 2026 | OK |

**Usage notes:**

- `bang.html` / `bang_night.html` load **`bang_days_snapshot.json`** + `glow_snapshot.json` (fresh) — **not** `bang_snapshot.json`.  
  → `bang_snapshot.json` is an **orphan stale artifact**.
- `chose.html` / `sight.html` do **not** currently `fetch` their stale snapshots (no HTML refs found). Orphan or legacy files.
- `depth.html` **does** link `depth_snapshot.json` (stale stamp) + `depth_explorer.json` (present).
- `face_snapshot.json` / `face_particles_snapshot.json`: no stamp field; mtime 2026-07-20 (on cutoff edge) — not flagged &lt; cutoff.

---

## 4. Hub grids

### `shores.html` (37 local links) — all exist

Page grid includes among others:  
`index`, `sight`, `awareness`, `thread`, `qualia_guide`, `audit`, `prove`, `variety`, `become`, `reawaken`, `chose`, `face`, `desire`, `wave`, `pulse`, `dare`, `textgl`, `hotel_aether`, `bang`, `assembler`, `map`, `me`, `metal`, `persona`, `presence`, `psi`, `radial`, `receiver`, `self_aware`, `sigmadb`, `voice`, `crossweave`, `depth`, `depth_under`, `drift`, `horizon`.

### `map.html` (29 local links) — all exist

`shores`, `self`, `self_evolve`, `self_phantom`, `variety`, `preimage`, `world`, `world_declaration.txt`, `metal`, `assembler`, `impossible`, `sigma`, `ice_snapshot.json`, `amazing`, `rowboat`, `alive`, `glow`, `unstoppable`, `teeth`, `little`, `bond`, `attractor`, `lantern`, `index`, `manifesto`, `sea`, `hunger`, `distillations`.

### `index.html` / `prove.html` / `alive.html`

| Page | Local hrefs | Broken |
|------|------------:|-------:|
| `index.html` | 12 (`chose`, `sight`, `desire`, `wave`, `shores`, `oneness`, `boss`, `first`, `world`, `ecosystem`, `sigmadb`, `unhinged`) | **0** |
| `prove.html` | 3 (`audit.html`, `prove_snapshot.json`, `audit_verified.json`) | **0** |
| `alive.html` | 2 (`shores.html`, `map.html`) | **0** |

---

## 5. Redirect stubs

| Stub | Target | Status |
|------|--------|--------|
| `mood.html` | `qualia_guide.html` | OK (meta + `location.replace`) |
| `mood/index.html` | `../qualia_guide.html` | OK |
| `qualia.html` | `qualia_guide.html` | OK |
| `quality.html` | `qualia_guide.html` | OK (typo alias) |

`bang.html` / `bang_night.html` use `location` for day/night mode toggling (self/peer), not migration stubs. Both files exist and match size (~13 KB).

**No wrong redirect stubs** (nothing pointing at `tfirm`, old absolute paths, or missing HTML).

---

## 6. Inventory / audit JSON freshness

| File | Stamp | mtime | Verdict |
|------|-------|-------|---------|
| `site_inventory.json` | **2026-07-08T13:28:03+0200** | 2026-07-09 | **STALE** — pre-cutoff; `html_count: 95` vs **108** now |
| `audit_verified.json` | **2026-08-09T19:21:25+0200** | 2026-08-09 | **Fresh** — chain verification (`all_valid: true`, 303738 rows); **not** a page-routing inventory |

### `site_inventory.json` drift

- Recorded `live_404` (July): `chose.html`, four firmcraft pages — **chose exists now** locally; firmcraft HTML exists but media does not.
- **11 HTML pages missing from inventory basenames** (added after July inventory):  
  `alone.html`, `desire.html`, `face.html`, `face_particles.html`, `free.html`, `loop.html`, `particles.html`, `pulse.html`, `rain.html`, `sight.html`, `wave.html`
- Inventory still useful as historical live-check, **unsafe as current map**.

---

## 7. Routing orphans (not broken — weak discovery)

Not linked from `shores` ∪ `map` ∪ `index` ∪ `prove` ∪ `alive` ∪ `audit` ∪ `qualia_guide` ∪ `ecosystem` (33):

`aeon` `alone` `bang_night` `boot` `continuum` `coupling` `dream` `drop` `emergence` `episode` `face_particles` `firmcraft*` (4) `floor` `free` `frontier` `impossible_explore` `lirac` `loop` `mind` `mood` `particles` `preference` `qualia` `quality` `rain` `sovereign` `textgl_debug` `textgl_liralang` `unbound` `will`

Some are intentional stubs (`mood`/`qualia`/`quality` redirects). Firmcraft + several sigma/side shores are **harder to reach** without direct URL.

---

## Top 20 broken / migration issues (priority order)

1. **`assets/` tree missing entirely** — all Firmcraft product media 404  
2. `firmcraft.html` → `assets/firmcraft/collection_film.mp4`  
3. `firmcraft.html` → `assets/firmcraft/wallet.jpg` (+ tote/bag/crossbody/shopping)  
4. `firmcraft.html` → `assets/firmcraft/atelier_reel.mp4` / `atelier_mood.jpg`  
5. `firmcraft.html` → `assets/firmcraft/detail_hardware.jpg` / `detail_stitch.jpg`  
6. `firmcraft_atelier.html` → `assets/firmcraft/elena-author.jpg`  
7. `firmcraft_atelier.html` → `assets/firmcraft/v2/detail_stitch_v2.jpg`  
8. **`journal/` missing** — `believe.html` → `journal/agency.jsonl`  
9. **`site_inventory.json` stale** (2026-07-08, 95≠108 pages)  
10. **`depth_snapshot.json` stale** (2026-06-25) and still linked from `depth.html`  
11. **`bang_snapshot.json` stale orphan** (2026-06-24) — live bang uses `bang_days_snapshot.json`  
12. **`chose_snapshot.json` stale orphan** (2026-07-08) — page does not fetch it  
13. **`sight_snapshot.json` stale orphan** (2026-07-08) — page does not fetch it  
14. Firmcraft pages not on shores/map hubs (discovery)  
15. `face.html` depends on `/api/say` (expected; document host requirement)  
16. 33 hub-orphan pages (optional shores-grid expansion)  
17. Inventory still lists `chose.html` as live_404 (outdated)  
18. Inventory lists firmcraft as live_404 — HTML present, assets still dead (partially true)  
19. No `tfirm` path rot remaining in HTML (positive — closed)  
20. `audit_verified.json` fresh — do **not** confuse with page inventory (positive / naming clarity)

---

## Recommended fix list (prioritized)

### P0 — content restore

1. **Restore or regenerate `assets/firmcraft/`** (images + mp4s referenced above), or strip/guard Firmcraft pages until media exists.  
2. **Create `journal/agency.jsonl`** (or retarget `believe.html` to an existing journal path under sleep_lira / lira-mark).

### P1 — stale data / inventory

3. **Refresh `depth_snapshot.json`** via the same sleep/export pipeline that updates other shores (stamp is June 2026).  
4. **Regenerate `site_inventory.json`** against current tree + optional live GitHub Pages check (`html_count` should be 108; drop false 404 for `chose.html`).  
5. **Quarantine or rebuild orphan snapshots:** `bang_snapshot.json`, `chose_snapshot.json`, `sight_snapshot.json` (delete, archive, or re-export so they cannot be mistaken for live state).

### P2 — routing / discovery

6. Add firmcraft + high-value orphans (`will`, `sovereign`, `preference`, `mind`, `face_particles`, …) to `shores.html` or `map.html` if they are still first-class witnesses.  
7. Keep redirect stubs (`mood`/`qualia`/`quality` → `qualia_guide`) as-is — they are correct.  
8. Document `face.html` host: needs API server; static host alone will fail `/api/say`.

### P3 — hygiene

9. Do **not** use `audit_verified.json` as a page map — it is chain truth only (and currently good).  
10. Optional: add a small CI/`python` link checker to fail on missing relative assets (this audit’s method).  
11. No HTML rewrite needed for `tfirm` / absolute user paths — already clean.

---

## Positive findings (migration health)

- **Zero** HTML links to old `tfirm` or wrong absolute user roots.  
- **Zero** broken links on `shores.html`, `map.html`, `index.html`, `prove.html`, `alive.html`.  
- Redirect stubs all land on existing `qualia_guide.html`.  
- Snapshot **fetch** graph for live pages is complete on disk (except journal + firmcraft assets).  
- Most snapshot stamps are **2026-08-09** (post chain-fix cycle).  
- `audit_verified.json` reports `all_valid: true` as of 2026-08-09T19:21:25+0200.

---

## Appendix — raw method notes

- Crawl ignored: `http(s):`, `mailto:`, `javascript:`, `data:`, `blob:`, pure `#` hashes.  
- Existence rules: file present, or bare path + `.html`, or directory + `index.html`.  
- Query strings (`?v=2`, `?` cache busters) stripped before filesystem check.  
- False positives filtered from final “real” break list: JS `${…}` templates, regex over-match in prose.

*End of audit.*
