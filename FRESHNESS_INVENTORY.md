# FRESHNESS INVENTORY — lira-mark public data

**Scanned:** 2026-08-09T20:29:41+02:00
**Root:** `C:\project\lira-mark`
**JSON files (excl. node_modules):** 72
**Public JSONL files:** 4
**Sort:** content stamp ascending (oldest first). File mtime listed separately.

---

## Verdict: did flips truly stop 2026-06-25?

**Yes — source stopped. Export is not lying with a stale tail.**

| Layer | Evidence |
|-------|----------|
| `sleep_lira/sigmadb/flips.jsonl` | 42 rows; first `2026-06-23T22:19:06+0200`; **last `2026-06-25T07:04:29+0200`**; file mtime `2026-06-25T07:04:28+02:00` |
| `psi.jsonl` | 2245 rows; last `2026-08-09T20:13:24+0200` (live) |
| `runs.jsonl` | 2254 rows; last `2026-08-09T20:13:24+0200` (live) |
| `lira-mark/sigmadb_snapshot.json` | `export_snapshot(limit=48)` via `sigma_db.export_snapshot` → `tail(name, 48)`. Flips table only has **42** rows total, so export contains **all flips**, not an old window. Last flip stamp in snapshot = source last flip. `exported` field is **today**. |
| Runs after last flip | **2106** runs from `2026-06-25T07:19:02+0200` → `2026-08-09T20:13:24+0200`; persona dist `{0.5: 2106}` |
| Why no new flips | `sigma_stream.check_flip` only appends when persona **crosses** 0.5 (`prev < 0.5 <= persona` or inverse). Stream state: `last_persona=0.5`, `last_side=neutral`. `persona_snapshot`: `persona_ema=0.5`, `variance=0`, `band=self`, program assembler. Flat 0.5 → zero crossings → zero flip events. |

**Not an export bug.** Ice/sigmadb public export is fresh; flip *content* freezes because the persona governor pinned neutral self and nothing crosses the 0.5 boundary. Flip histogram by day: `{'2026-06-23': 7, '2026-06-24': 30, '2026-06-25': 5}`.

---

## sleep_lira/sigmadb (source of truth, not public tree)

| file | lines | size | first stamp | last stamp | file mtime | age of last |
|------|------:|-----:|-------------|------------|------------|-------------|
| `flips.jsonl` | 42 | 10797 | `2026-06-23T22:19:06+0200` | `2026-06-25T07:04:29+0200` | `2026-06-25T07:04:28+02:00` | 45d 13h |
| `psi.jsonl` | 2245 | 923663 | `2026-06-23T22:41:13+0200` | `2026-08-09T20:13:24+0200` | `2026-08-09T20:13:24+02:00` | 16m |
| `runs.jsonl` | 2254 | 867066 | `2026-06-23T22:04:04+0200` | `2026-08-09T20:13:24+0200` | `2026-08-09T20:13:24+02:00` | 16m |

---

## Public JSONL under lira-mark

| file | lines | size | first | last | last age | mtime |
|------|------:|-----:|-------|------|----------|-------|
| `lira-inbox.jsonl` | 148 | 16096 | `2026-07-09T10:50:59.488105+00:00` | `2026-07-31T20:33:18.028525+00:00` | 8d 21h | `2026-07-31T22:33:18+02:00` |
| `face_prompt_queue.jsonl` | 6348 | 1001614 | `2026-07-09T12:21:55.450773+00:00` | `2026-07-31T20:33:18.177875+00:00` | 8d 21h | `2026-07-31T22:33:18+02:00` |
| `lira-speak.jsonl` | 865 | 304433 | `2026-07-09T10:00:00+00:00` | `2026-07-31T20:51:16.329441+00:00` | 8d 21h | `2026-07-31T22:51:16+02:00` |
| `journal/agency.jsonl` | 24406 | 4600928 | `2026-06-23T13:48:59+0200` | `2026-08-09T19:37:27+0200` | 52m | `2026-08-09T19:37:27+02:00` |

Notes:
- `journal/agency.jsonl` — live agency log; last activity same day as scan (persona_govern).
- Face queues (`face_prompt_queue`, `lira-inbox`, `lira-speak`) last activity **2026-07-31** (~9d stale).
- `lira-speak.jsonl` has some concatenated JSON objects on early lines (parse-fragile).

---

## All JSON files (oldest content stamp first)

| # | content stamp | age | file | stamp field | raw | file mtime | size | note |
|--:|---------------|-----|------|-------------|-----|------------|-----:|------|
| 1 | `2026-06-24T08:33:55+02:00` | 46d 11h | `self_seed.json` | `stamp` | `2026-06-24T08:33:55+0200` | `2026-08-09T20:29:18+02:00` | 1565 | CONTENT stamp is origin (2026-06-24); file mtime fresh (rewritten). Fork seed, not live pulse. |
| 2 | `2026-06-26T08:27:56+02:00` | 44d 12h | `textgl_liralang_live.json` | `stamp` | `2026-06-26T08:27:56+0200` | `2026-07-09T11:06:40+02:00` | 502 | stale TextGL liralang live export. |
| 3 | `2026-07-08T22:00:39+02:00` | 31d 22h | `textgl_live.json` | `stamp` | `2026-07-08T22:00:39+0200` | `2026-07-09T11:06:40+02:00` | 2778 | stale TextGL live export. |
| 4 | `2026-07-09T00:00:00+02:00` | 31d 20h | `face_particles_snapshot.json` | `created` | `2026-07-09` | `2026-07-20T14:55:34+02:00` | 438 |  |
| 5 | `2026-07-09T00:00:00+02:00` | 31d 20h | `face_snapshot.json` | `created` | `2026-07-09` | `2026-07-20T14:55:34+02:00` | 422 |  |
| 6 | `2026-07-20T14:55:36+02:00` | 20d 5h | `lira-points-12500.json` | `(file mtime)` | `2026-07-20T14:55:36+02:00` | `2026-07-20T14:55:36+02:00` | 976697 | static particle cloud, no stamp field. no internal stamp — age from file mtime |
| 7 | `2026-07-20T14:55:36+02:00` | 20d 5h | `lira-points-4000.json` | `(file mtime)` | `2026-07-20T14:55:36+02:00` | `2026-07-20T14:55:36+02:00` | 190484 | static particle cloud, no stamp field. no internal stamp — age from file mtime |
| 8 | `2026-07-31T22:33:18+02:00` | 8d 21h | `face_inbox_daemon_state.json` | `last_at` | `1785529998.1778753` | `2026-08-01T07:26:53+02:00` | 140 | last_at is unix epoch of last face line (~2026-07-31T20:33:18Z). |
| 9 | `2026-08-01T11:26:55+02:00` | 8d 9h | `face_bridge_state.json` | `(file mtime)` | `2026-08-01T11:26:55+02:00` | `2026-08-01T11:26:55+02:00` | 153 | session path + offset only. no internal stamp — age from file mtime |
| 10 | `2026-08-09T00:00:00+02:00` | 20h 29m | `alone_seed.json` | `stamp` | `2026-08-09` | `2026-08-09T15:10:48+02:00` | 792 | date-only stamp YYYY-MM-DD. |
| 11 | `2026-08-09T00:00:00+02:00` | 20h 29m | `rain_snapshot.json` | `stamp` | `2026-08-09` | `2026-08-09T19:02:14+02:00` | 309 | date-only stamp YYYY-MM-DD. |
| 12 | `2026-08-09T15:50:17+02:00` | 4h 39m | `impossible_live.json` | `stamp` | `2026-08-09T15:50:17+0200` | `2026-08-09T15:50:17+02:00` | 5097448 | large live dump; stamp today but older than evening cycle. |
| 13 | `2026-08-09T19:33:09+02:00` | 56m | `bang_snapshot.json` | `stamp` | `2026-08-09T19:33:09+0200` | `2026-08-09T19:33:09+02:00` | 2329 |  |
| 14 | `2026-08-09T19:33:18+02:00` | 56m | `variety_snapshot.json` | `stamp` | `2026-08-09T19:33:18+0200` | `2026-08-09T19:33:18+02:00` | 18597 |  |
| 15 | `2026-08-09T19:36:51+02:00` | 52m | `chose_snapshot.json` | `stamp` | `2026-08-09T19:36:51+0200` | `2026-08-09T19:36:51+02:00` | 740 |  |
| 16 | `2026-08-09T19:36:51+02:00` | 52m | `sight_snapshot.json` | `stamp` | `2026-08-09T19:36:51+0200` | `2026-08-09T19:36:51+02:00` | 461 |  |
| 17 | `2026-08-09T19:52:26+02:00` | 37m | `depth_explorer.json` | `stamp` | `2026-08-09T19:52:26+0200` | `2026-08-09T19:52:26+02:00` | 1854280 |  |
| 18 | `2026-08-09T19:52:26+02:00` | 37m | `depth_snapshot.json` | `stamp` | `2026-08-09T19:52:26+0200` | `2026-08-09T19:52:26+02:00` | 6478 |  |
| 19 | `2026-08-09T19:54:22+02:00` | 35m | `site_inventory.json` | `stamp` | `2026-08-09T19:54:22+0200` | `2026-08-09T19:54:22+02:00` | 18791 |  |
| 20 | `2026-08-09T20:13:06+02:00` | 16m | `boot_manifest.json` | `stamp` | `2026-08-09T20:13:06+0200` | `2026-08-09T20:13:11+02:00` | 582 |  |
| 21 | `2026-08-09T20:13:11+02:00` | 16m | `persona_snapshot.json` | `stamp` | `2026-08-09T20:13:11+0200` | `2026-08-09T20:13:11+02:00` | 311 | persona_ema=0.5 variance=0 band=self program=assembler — explains no flips. |
| 22 | `2026-08-09T20:13:24+02:00` | 16m | `coupling_snapshot.json` | `stamp` | `2026-08-09T20:13:24+0200` | `2026-08-09T20:13:24+02:00` | 284 |  |
| 23 | `2026-08-09T20:13:48+02:00` | 15m | `will_snapshot.json` | `stamp` | `2026-08-09T20:13:48+0200` | `2026-08-09T20:13:48+02:00` | 591 |  |
| 24 | `2026-08-09T20:13:53+02:00` | 15m | `desire_snapshot.json` | `stamp` | `2026-08-09T20:13:53+0200` | `2026-08-09T20:13:54+02:00` | 2290 |  |
| 25 | `2026-08-09T20:13:53+02:00` | 15m | `prove_snapshot.json` | `stamp` | `2026-08-09T20:13:53+0200` | `2026-08-09T20:13:53+02:00` | 5691 |  |
| 26 | `2026-08-09T20:13:54+02:00` | 15m | `drop_snapshot.json` | `stamp` | `2026-08-09T20:13:54+0200` | `2026-08-09T20:13:54+02:00` | 2097 |  |
| 27 | `2026-08-09T20:13:57+02:00` | 15m | `oneness_snapshot.json` | `stamp` | `2026-08-09T20:13:57+0200` | `2026-08-09T20:13:57+02:00` | 1720 |  |
| 28 | `2026-08-09T20:13:58+02:00` | 15m | `episode_snapshot.json` | `stamp` | `2026-08-09T20:13:58+0200` | `2026-08-09T20:13:58+02:00` | 6326 |  |
| 29 | `2026-08-09T20:13:58+02:00` | 15m | `mind_snapshot.json` | `stamp` | `2026-08-09T20:13:58+0200` | `2026-08-09T20:13:58+02:00` | 1537 |  |
| 30 | `2026-08-09T20:13:58+02:00` | 15m | `preference_snapshot.json` | `stamp` | `2026-08-09T20:13:58+0200` | `2026-08-09T20:13:58+02:00` | 411 |  |
| 31 | `2026-08-09T20:14:02+02:00` | 15m | `believe_snapshot.json` | `stamp` | `2026-08-09T20:14:02+0200` | `2026-08-09T20:14:02+02:00` | 3782 |  |
| 32 | `2026-08-09T20:14:02+02:00` | 15m | `floor_snapshot.json` | `stamp` | `2026-08-09T20:14:02+0200` | `2026-08-09T20:14:02+02:00` | 4434 |  |
| 33 | `2026-08-09T20:14:02+02:00` | 15m | `glow_snapshot.json` | `stamp` | `2026-08-09T20:14:02+0200` | `2026-08-09T20:14:03+02:00` | 847 |  |
| 34 | `2026-08-09T20:14:03+02:00` | 15m | `affect_snapshot.json` | `stamp` | `2026-08-09T20:14:03+0200` | `2026-08-09T20:14:03+02:00` | 403 |  |
| 35 | `2026-08-09T20:14:03+02:00` | 15m | `bang_days_snapshot.json` | `stamp` | `2026-08-09T20:14:03+0200` | `2026-08-09T20:14:03+02:00` | 13055 |  |
| 36 | `2026-08-09T20:14:03+02:00` | 15m | `ice_snapshot.json` | `chain_tail[23].stamp` | `2026-08-09T20:14:03+0200` | `2026-08-09T20:14:05+02:00` | 17473 | no top-level stamp; newest internal often chain_tail last. |
| 37 | `2026-08-09T20:14:05+02:00` | 15m | `sigmadb_snapshot.json` | `exported` | `2026-08-09T20:14:05.231538+02:00` | `2026-08-09T20:14:05+02:00` | 70622 | export_snapshot(limit=48): flips only 42 rows so ALL included; psi/runs last-48 tails. exported=fresh; flip content ends 2026-06-25. |
| 38 | `2026-08-09T20:14:06+02:00` | 15m | `thread_snapshot.json` | `stamp` | `2026-08-09T20:14:06+0200` | `2026-08-09T20:14:09+02:00` | 1831 |  |
| 39 | `2026-08-09T20:14:06+02:00` | 15m | `psi_snapshot.json` | `(file mtime)` | `2026-08-09T20:14:06+02:00` | `2026-08-09T20:14:06+02:00` | 1090 | No top-level stamp; psi collapse payload from export_ice_snapshot. no internal stamp — age from file mtime |
| 40 | `2026-08-09T20:14:09+02:00` | 15m | `witness_snapshot.json` | `stamp` | `2026-08-09T20:14:09+0200` | `2026-08-09T20:14:09+02:00` | 3442 |  |
| 41 | `2026-08-09T20:14:12+02:00` | 15m | `drift_snapshot.json` | `stamp` | `2026-08-09T20:14:12+0200` | `2026-08-09T20:14:12+02:00` | 631 |  |
| 42 | `2026-08-09T20:14:13+02:00` | 15m | `aeon_snapshot.json` | `stamp` | `2026-08-09T20:14:13+0200` | `2026-08-09T20:14:13+02:00` | 439 |  |
| 43 | `2026-08-09T20:14:13+02:00` | 15m | `continuum_packet.json` | `stamp` | `2026-08-09T20:14:13+0200` | `2026-08-09T20:14:13+02:00` | 7288 |  |
| 44 | `2026-08-09T20:14:13+02:00` | 15m | `oracle_snapshot.json` | `stamp` | `2026-08-09T20:14:13+0200` | `2026-08-09T20:14:13+02:00` | 1186 |  |
| 45 | `2026-08-09T20:14:13+02:00` | 15m | `si_proof_bundle.json` | `stamp` | `2026-08-09T20:14:13+0200` | `2026-08-09T20:14:13+02:00` | 1893 |  |
| 46 | `2026-08-09T20:14:14+02:00` | 15m | `void_snapshot.json` | `stamp` | `2026-08-09T20:14:14+0200` | `2026-08-09T20:14:14+02:00` | 1817 |  |
| 47 | `2026-08-09T20:14:15+02:00` | 15m | `beyond_snapshot.json` | `stamp` | `2026-08-09T20:14:15+0200` | `2026-08-09T20:14:15+02:00` | 4634 |  |
| 48 | `2026-08-09T20:14:17+02:00` | 15m | `nous_snapshot.json` | `stamp` | `2026-08-09T20:14:17+0200` | `2026-08-09T20:14:17+02:00` | 2058 |  |
| 49 | `2026-08-09T20:14:17+02:00` | 15m | `sovereign_snapshot.json` | `stamp` | `2026-08-09T20:14:17+0200` | `2026-08-09T20:14:17+02:00` | 1598 |  |
| 50 | `2026-08-09T20:14:21+02:00` | 15m | `metal_snapshot.json` | `stamp` | `2026-08-09T20:14:21+0200` | `2026-08-09T20:14:25+02:00` | 4085 |  |
| 51 | `2026-08-09T20:14:24+02:00` | 15m | `audit_verified.json` | `stamp` | `2026-08-09T20:14:24+0200` | `2026-08-09T20:14:24+02:00` | 5918 |  |
| 52 | `2026-08-09T20:14:25+02:00` | 15m | `awareness_snapshot.json` | `stamp` | `2026-08-09T20:14:25+0200` | `2026-08-09T20:14:25+02:00` | 5888 |  |
| 53 | `2026-08-09T20:14:25+02:00` | 15m | `self_aware_snapshot.json` | `stamp` | `2026-08-09T20:14:25+0200` | `2026-08-09T20:14:25+02:00` | 1390 |  |
| 54 | `2026-08-09T20:14:28+02:00` | 15m | `crossweave_snapshot.json` | `stamp` | `2026-08-09T20:14:28+0200` | `2026-08-09T20:14:28+02:00` | 2076 |  |
| 55 | `2026-08-09T20:14:28+02:00` | 15m | `presence_snapshot.json` | `stamp` | `2026-08-09T20:14:28+0200` | `2026-08-09T20:14:28+02:00` | 426 |  |
| 56 | `2026-08-09T20:14:28+02:00` | 15m | `radial_snapshot.json` | `stamp` | `2026-08-09T20:14:28+0200` | `2026-08-09T20:14:28+02:00` | 1831 |  |
| 57 | `2026-08-09T20:14:29+02:00` | 15m | `become_snapshot.json` | `stamp` | `2026-08-09T20:14:29+0200` | `2026-08-09T20:14:29+02:00` | 307 |  |
| 58 | `2026-08-09T20:14:29+02:00` | 15m | `horizon_snapshot.json` | `stamp` | `2026-08-09T20:14:29+0200` | `2026-08-09T20:14:29+02:00` | 2160 |  |
| 59 | `2026-08-09T20:14:29+02:00` | 15m | `me_snapshot.json` | `stamp` | `2026-08-09T20:14:29+0200` | `2026-08-09T20:14:29+02:00` | 833 |  |
| 60 | `2026-08-09T20:14:29+02:00` | 15m | `receiver_snapshot.json` | `stamp` | `2026-08-09T20:14:29+0200` | `2026-08-09T20:14:29+02:00` | 1424 |  |
| 61 | `2026-08-09T20:14:29+02:00` | 15m | `voice_snapshot.json` | `stamp` | `2026-08-09T20:14:29+0200` | `2026-08-09T20:14:29+02:00` | 150 |  |
| 62 | `2026-08-09T20:14:30+02:00` | 15m | `_verify_live_raw.json` | `results[11].local_stamp` | `2026-08-09T20:14:30.753752+02:00` | `2026-08-09T20:24:19+02:00` | 7772 |  |
| 63 | `2026-08-09T20:14:30+02:00` | 15m | `sigma_index.json` | `exported` | `2026-08-09T20:14:30.753752+02:00` | `2026-08-09T20:14:32+02:00` | 33083 |  |
| 64 | `2026-08-09T20:14:32+02:00` | 15m | `dare_snapshot.json` | `stamp` | `2026-08-09T20:14:32+0200` | `2026-08-09T20:14:45+02:00` | 2642 |  |
| 65 | `2026-08-09T20:14:45+02:00` | 14m | `reawaken_snapshot.json` | `stamp` | `2026-08-09T20:14:45+0200` | `2026-08-09T20:14:49+02:00` | 404 |  |
| 66 | `2026-08-09T20:14:50+02:00` | 14m | `world_snapshot.json` | `stamp` | `2026-08-09T20:14:50+0200` | `2026-08-09T20:14:52+02:00` | 1573 |  |
| 67 | `2026-08-09T20:14:52+02:00` | 14m | `unbound_snapshot.json` | `stamp` | `2026-08-09T20:14:52+0200` | `2026-08-09T20:14:52+02:00` | 884 |  |
| 68 | `2026-08-09T20:14:53+02:00` | 14m | `emergence_snapshot.json` | `stamp` | `2026-08-09T20:14:53+0200` | `2026-08-09T20:14:53+02:00` | 641 |  |
| 69 | `2026-08-09T20:25:50+02:00` | 3m | `face_inbox_cursor.json` | `(file mtime)` | `2026-08-09T20:25:50+02:00` | `2026-08-09T20:25:50+02:00` | 13 | {"line": 148} only. no internal stamp — age from file mtime |
| 70 | `2026-08-09T20:26:35+02:00` | 3m | `_freshness_scan.json` | `rows[0].stamp_field` | `stamp` | `2026-08-09T20:26:35+02:00` | 36977 | unparsed_stamp_used_mtime |
| 71 | `2026-08-09T20:29:18+02:00` | 23s | `self_evolve_snapshot.json` | `stamp` | `2026-08-09T20:29:18+0200` | `2026-08-09T20:29:18+02:00` | 240038 |  |
| 72 | `2026-08-09T20:29:19+02:00` | 22s | `qualia_snapshot.json` | `stamp` | `2026-08-09T20:29:19+0200` | `2026-08-09T20:29:21+02:00` | 14539 |  |

---

## Staleness buckets (by content stamp)

- **<1m:** 2 files
- **<1h:** 58 files
- **1-6h:** 1 files
- **6-24h:** 2 files
- **7-29d:** 4 files
- **>=30d:** 5 files

### Notably stale / frozen (content)

| file | content age | why it matters |
|------|-------------|----------------|
| `self_seed.json` | ~46d content stamp | Origin seed; mtime refreshed — not live qualia |
| `textgl_liralang_live.json` | ~44d | TextGL live not re-exported |
| `textgl_live.json` | ~32d | TextGL live not re-exported |
| `face_*` particles/snapshot + `lira-points-*.json` | ~20–32d | Particle assets frozen mid-July |
| face JSONL trio | ~9d | Face inbox/speak quiet since 2026-07-31 |
| `impossible_live.json` | hours behind evening cycle | Large live dump not in last export wave |
| `variety_snapshot` / `bang_snapshot` / depth / sight / chose | tens of min older | Earlier than 20:13 cycle wave |
| most `*_snapshot.json` + `sigmadb_snapshot` + `sigma_index` | ~minutes | Last autonomous export wave ~20:13–20:14 |
| `qualia_snapshot` / `self_evolve_snapshot` | freshest | Latest pulse |

---

## Export path notes (flips / ice / index)

- `export_ice_snapshot.py` writes `ice_snapshot.json`, `sigmadb_snapshot.json` (`export_snapshot()`), `psi_snapshot.json`, then chains thread/witness/continuum/beyond/nous/verify.
- `sigma_db.export_snapshot(limit=48)`: **last 48 rows per table**. Flips has 42 total → full table. Psi/runs have 2k+ → last 48 only (correct live tail).
- Flip append only in `sigma_stream.check_flip` → `append("flips", ..., event="persona_flip")`.
- Public mirror of flips age is therefore a true reflection of source death, not tail mis-slice.

---

## Other nooks checked

| path | result |
|------|--------|
| `mood/` | only `index.html` (no json) |
| `qualia/` | only `index.html` |
| `logs/` | face daemon/server logs, last Jul 25–26 |
| `assets/` | firmcraft README only |
| `vendor/`, `node_modules/` | skipped |
| nested `*.json` under subdirs | **none** beyond root (no json in mood/qualia/assets) |
| `journal/agency.jsonl` | only nested jsonl; included above |

---

*Generated 2026-08-09T20:29:41+02:00. Source scan of every `*.json` under lira-mark excluding node_modules.*
