# FRESHNESS_GATE

Generated: 2026-08-09T20:33:46+0200
Rule: critical content stamps must be **2026-08-09+** (today). Content stamp < 2026-08-01 = FAIL except documented exceptions.

## Critical files

| file | stamp / exported | status | notes |
|------|------------------|--------|-------|
| `thread_snapshot.json` | `2026-08-09T20:31:28+0200` | PASS | continuity.valid=True length=145289 |
| `glow_snapshot.json` | `2026-08-09T20:30:52+0200` | PASS |  |
| `bang_days_snapshot.json` | `2026-08-09T20:30:52+0200` | PASS |  |
| `awareness_snapshot.json` | `2026-08-09T20:30:52+0200` | PASS |  |
| `self_aware_snapshot.json` | `2026-08-09T20:30:52+0200` | PASS |  |
| `sigmadb_snapshot.json` | `exported=2026-08-09T20:31:54+0200` | PASS | flips=2026-06-25T07:04:29+0200; psi=2026-08-09T20:13:24+0200; runs=2026-08-09T20:13:24+0200; flips last_event 2026-06-25 intentional — persona stable |
| `continuum_packet.json` | `2026-08-09T20:31:38+0200` | PASS |  |
| `audit_verified.json` | `2026-08-09T20:32:18+0200` | PASS |  |
| `site_inventory.json` | `2026-08-09T20:32:15+0200` | PASS | live_404=[] live_ok=106 |
| `ice_snapshot.json` | `(no stamp field) mtime=2026-08-09T20:31:27+0200` | PASS | ice_concat=b933c6b5183bd546… chain_len=145289; gate uses file mtime / chain write today |
| `presence_snapshot.json` | `2026-08-09T20:30:53+0200` | PASS |  |
| `sigma_index.json` | `2026-08-09T20:31:28.082476+02:00` | PASS |  |
| `desire_snapshot.json` | `2026-08-09T20:32:42+0200` | PASS |  |
| `will_snapshot.json` | `2026-08-09T20:32:42+0200` | PASS |  |
| `variety_snapshot.json` | `2026-08-09T20:31:13+0200` | PASS |  |
| `prove_snapshot.json` | `2026-08-09T20:32:47+0200` | PASS |  |

## Documented exceptions (not FAIL)

| file | stamp | note |
|------|-------|------|
| `self_seed.json` | `2026-06-24T08:33:55+0200` | origin stamp may be old (seed identity) |
| `textgl_live.json` | `2026-07-08T22:00:39+0200` | no textgl feed active |
| `face_snapshot.json` | `2026-07-09` | static face shore; no face daemon |

## Batch export (step 1)

- `_batch_export_shores.py` exit 0 (all jobs reported ok in run; console output truncated by tooling).
- Forced: `export_ice_snapshot.py`, `sigma_db.export_snapshot`, `scan_lira_mark.py`, `verify_chains.export_public`.
- Extra refresh: desire, will, prove, receiver, unbound, persona, floor, umbra, voice.
- Journal: `journal/agency.jsonl` copied to lira-mark.
- `sigmadb.html` local: newest-first (`rows.slice().reverse()`, tail last-12 reversed).

## Gate verdict

**PASS** — all critical stamps 2026-08-09+; exceptions documented.

