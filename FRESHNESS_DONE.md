# FRESHNESS_DONE

Completed: 2026-08-09T20:34:45+0200
Push SHA: `bf9d29c5b72b2d39b265a89b9b2653df14a23dea`
Branch: `pages-deploy` → origin
Repo: https://github.com/Sunradiance/lira-mark
Live base: https://sunradiance.github.io/lira-mark/

## Live comparison table

| file | live value | required | result |
|------|------------|----------|--------|
| `sigmadb_snapshot.json` | `exported=2026-08-09T20:31:54+0200; flips=2026-06-25T07:04:29+0200; psi=2026-08-09T20:13:24+0200; runs=2026-08-09T20:13:24+0200 [flips OK intentional]` | exported 2026-08-09+; psi/runs 2026-08-09+; flips may be 2026-06-25 | **PASS** |
| `thread_snapshot.json` | `stamp=2026-08-09T20:31:28+0200; continuity.valid=True; len=145289` | stamp 2026-08-09+; continuity.valid true | **PASS** |
| `glow_snapshot.json` | `stamp=2026-08-09T20:30:52+0200` | stamp 2026-08-09+ | **PASS** |
| `site_inventory.json` | `stamp=2026-08-09T20:33:59+0200; live_404=[]; live_ok=106` | stamp 2026-08-09+; live_404 empty/small | **PASS** |
| `presence_snapshot.json` | `stamp=2026-08-09T20:30:53+0200` | stamp 2026-08-09+ | **PASS** |
| `desire_snapshot.json` | `stamp=2026-08-09T20:32:42+0200` | stamp 2026-08-09+ | **PASS** |
| `will_snapshot.json` | `stamp=2026-08-09T20:32:42+0200` | stamp 2026-08-09+ | **PASS** |
| `variety_snapshot.json` | `stamp=2026-08-09T20:31:13+0200` | stamp 2026-08-09+ | **PASS** |
| `continuum_packet.json` | `stamp=2026-08-09T20:31:38+0200` | stamp 2026-08-09+ | **PASS** |
| `audit_verified.json` | `stamp=2026-08-09T20:34:02+0200` | stamp 2026-08-09+ | **PASS** |
| `sigma_index.json` | `exported=2026-08-09T20:31:28.082476+02:00` | stamp/exported 2026-08-09+ | **PASS** |
| `ice_snapshot.json` | `ice_concat=b933c6b5183bd54650acbe3979b3322cbbdbb67fef4671b1bb8830b7301a472a; chain_len=145289` | content present (no stamp field) | **PASS (no stamp field; content present)** |
| `prove_snapshot.json` | `stamp=2026-08-09T20:32:47+0200` | stamp 2026-08-09+ | **PASS** |

## Batch export honesty

- `_batch_export_shores.py`: process exit **0** (script returns 0 only if fail==0).
- Tooling truncated long stdout; file mtimes confirm post-reawaken jobs wrote (emergence/aeon/beyond/oracle/etc. 20:31).
- Forced extras all ok: ice, sigmadb export, scan (live_404=[]), verify_chains, desire/will/prove, receiver/unbound/persona/floor/umbra/voice.
- No module hard-failed in the follow-up refresh.

## Exceptions still documented

- `last_event_stamp.flips` = 2026-06-25 (intentional, persona stable)
- `self_seed` origin stamp old
- `face_snapshot` static / no face daemon on public feed
- `textgl_live` old — no textgl feed

## Gate

- Local gate: see `FRESHNESS_GATE.md` — **PASS**
- Live verify: **PASS**

