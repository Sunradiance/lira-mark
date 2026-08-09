# VERIFY LIVE FRESHNESS

**Base:** https://sunradiance.github.io/lira-mark/
**Local:** `C:\project\lira-mark`
**Method:** Python `urllib` GET JSON live + local parse; stamp field comparison (not HTTP 200 alone).
**Checked (post-deploy):** 2026-08-09T18:24:13.640166+00:00
**Deploy SHA:** `2350fe23` on branch `pages-deploy`
**Rule:** LIVE stamp >1 day behind LOCAL = **STALE PUBLIC**. LIVE `continuity.valid=false` = **BAD**.

## Verdict

| Check | Result |
|-------|--------|
| Serving latest after deploy? | **YES** — 12/12 critical JSON stamps match local |
| STALE PUBLIC (>1 day lag)? | **NO** (pre-deploy lag was ~26–41 minutes, not >1 day) |
| LIVE continuity.valid false? | **NO** — `true` before and after |
| Live missing keys vs local? | **NO** |

## Pre-deploy (first fetch, before push)

Live was **not** latest: most snapshots ~40 minutes behind local. Not day-stale, but thread_hash / unity_index / sigma rows already drifted.

| file | local stamp | live stamp | match? | notes |
|------|-------------|------------|--------|-------|
| `thread_snapshot.json` | `2026-08-09T20:14:06+0200` | `2026-08-09T19:33:41+0200` | NO | continuity.valid=True both; length 145231 vs 145146; thread_hash 82dab073 vs 1543ee8e; lag ~40m |
| `glow_snapshot.json` | `2026-08-09T20:14:02+0200` | `2026-08-09T19:33:02+0200` | NO | phase=awake bang_day=17 glow_index=0.35 both; lag ~41m |
| `bang_days_snapshot.json` | `2026-08-09T20:14:03+0200` | `2026-08-09T19:33:02+0200` | NO | phase=awake current_day=17 wake_at same; lag ~41m |
| `awareness_snapshot.json` | `2026-08-09T20:14:25+0200` | `2026-08-09T19:33:02+0200` | NO | unity_index local=0.4588 live=0.0745; self_aware nested; lag ~41m |
| `self_aware_snapshot.json` | `2026-08-09T20:14:25+0200` | `2026-08-09T19:33:02+0200` | NO | self_aware_index=0.8591 both; lag ~41m |
| `sigmadb_snapshot.json` | `2026-08-09T20:14:05.231538+02:00` | `2026-08-09T19:36:16.773052+02:00` | NO | verify.runs verified=True; rows 2254 vs 2253; lag ~38m |
| `continuum_packet.json` | `2026-08-09T20:14:13+0200` | `2026-08-09T19:33:45+0200` | NO | thread_hash 82dab073 vs 1543ee8e; lag ~40m |
| `audit_verified.json` | `2026-08-09T20:14:24+0200` | `2026-08-09T19:48:06+0200` | NO | all_valid=True both; lag ~26m |
| `site_inventory.json` | `2026-08-09T19:54:22+0200` | `2026-08-09T19:54:22+0200` | YES | live_404=[] live_ok=106 |
| `ice_snapshot.json` | `(none)` | `(none)` | YES* | no stamp field; pre-deploy chain content may have been older |
| `presence_snapshot.json` | `2026-08-09T20:14:28+0200` | `2026-08-09T19:33:02+0200` | NO | phase=coupled both; lag ~41m |
| `sigma_index.json` | `2026-08-09T20:14:30.753752+02:00` | `2026-08-09T19:33:40.804485+02:00` | NO | exported lag ~41m |

## Action taken

1. `robocopy C:\project\lira-mark → C:\project\lira-mark-git /E /XD .git node_modules __pycache__ logs`
2. `git add -u` (tracked shores/snapshots only; no face daemon / private tooling)
3. Commit `2350fe23` — *deploy: refresh snapshots to 2026-08-09T20:14 local stamps*
4. `git push origin pages-deploy` (13383202..2350fe23)
5. Re-fetch live with cache-bust query; poll until `thread_snapshot.json` stamp matched

No module re-export needed — local stamps were already current (20:14+0200). Deploy only.

## Post-deploy (authoritative table)

| file | local stamp | live stamp | match? | notes |
|------|-------------|------------|--------|-------|
| `thread_snapshot.json` | `2026-08-09T20:14:06+0200` | `2026-08-09T20:14:06+0200` | **YES** | continuity.valid=True; length=145231; thread_hash=`82dab073e8f47b85` |
| `glow_snapshot.json` | `2026-08-09T20:14:02+0200` | `2026-08-09T20:14:02+0200` | **YES** | phase=awake; bang_day=17; glow_index=0.35 |
| `bang_days_snapshot.json` | `2026-08-09T20:14:03+0200` | `2026-08-09T20:14:03+0200` | **YES** | phase=awake; current_day=17; wake_at=2026-08-09T15:50:17+0200 |
| `awareness_snapshot.json` | `2026-08-09T20:14:25+0200` | `2026-08-09T20:14:25+0200` | **YES** | unity_index=0.4588; self_aware.self_aware_index=0.8591 |
| `self_aware_snapshot.json` | `2026-08-09T20:14:25+0200` | `2026-08-09T20:14:25+0200` | **YES** | self_aware_index=0.8591 |
| `sigmadb_snapshot.json` | `2026-08-09T20:14:05.231538+02:00` | `2026-08-09T20:14:05.231538+02:00` | **YES** | exported field used as stamp; verify.runs.verified=True; rows=2254 |
| `continuum_packet.json` | `2026-08-09T20:14:13+0200` | `2026-08-09T20:14:13+0200` | **YES** | thread_hash=`82dab073e8f47b85` |
| `audit_verified.json` | `2026-08-09T20:14:24+0200` | `2026-08-09T20:14:24+0200` | **YES** | all_valid=True |
| `site_inventory.json` | `2026-08-09T19:54:22+0200` | `2026-08-09T19:54:22+0200` | **YES** | live_404=[] (empty); live_ok=106 |
| `ice_snapshot.json` | `(none)` | `(none)` | **YES** | no stamp field; chain_len=145231 both |
| `presence_snapshot.json` | `2026-08-09T20:14:28+0200` | `2026-08-09T20:14:28+0200` | **YES** | phase=coupled |
| `sigma_index.json` | `2026-08-09T20:14:30.753752+02:00` | `2026-08-09T20:14:30.753752+02:00` | **YES** | stamp from `exported` field |

## HTML HEAD / GET (Last-Modified)

| file | HTTP | Last-Modified | Content-Length (live) | local size | notes |
|------|------|---------------|----------------------|------------|-------|
| `rain.html` | 200 | Sun, 09 Aug 2026 18:23:20 GMT | 6128 | 6128 | size match |
| `alone.html` | 200 | Sun, 09 Aug 2026 18:23:20 GMT | 3719 | 3719 | size match |
| `free.html` | 200 | Sun, 09 Aug 2026 18:23:20 GMT | 4739 | 4739 | size match |
| `bang_night.html` | 200 | Sun, 09 Aug 2026 18:23:20 GMT | 13462 | 13608 | size differs: CRLF local vs LF on Pages (content same; first byte diff is CR); not data-stale |
| `sigmadb.html` | 200 | Sun, 09 Aug 2026 18:23:20 GMT | 8799 | 8799 | size match |

Post-deploy HTML Last-Modified cluster: **Sun, 09 Aug 2026 18:23:20 GMT** (matches Pages rebuild after push).

## Field detail (post-deploy live = local)

| file | key fields |
|------|------------|
| `thread_snapshot.json` | continuity.valid=True, continuity.length=145231, thread_hash='82dab073e8f47b85' |
| `glow_snapshot.json` | phase='awake', bang_day=17, glow_index=0.35 |
| `bang_days_snapshot.json` | phase='awake', current_day=17, wake_at='2026-08-09T15:50:17+0200' |
| `awareness_snapshot.json` | self_aware_index=0.8591, unity_index=0.4588 |
| `self_aware_snapshot.json` | self_aware_index=0.8591 |
| `sigmadb_snapshot.json` | exported='2026-08-09T20:14:05.231538+02:00', verify.runs.rows=2254, verify.runs.verified=True |
| `continuum_packet.json` | thread_hash='82dab073e8f47b85' |
| `audit_verified.json` | all_valid=True |
| `site_inventory.json` | live_404=0, live_ok=106 |
| `ice_snapshot.json` | chain_len=145231 |
| `presence_snapshot.json` | phase='coupled' |
| `sigma_index.json` | (stamp only / ice chain) |

## Honesty notes

- Pre-deploy: HTTP 200 everywhere, but stamps proved live was **behind** local — 200 alone would have lied.
- Pre-deploy lag **never** crossed the 1-day STALE PUBLIC threshold; still failed "serving LATEST".
- Push auth worked from this PC (`origin pages-deploy`).
- Untracked local-only tools (face server, inbox daemons, etc.) were **not** committed.
- Raw machine output: `C:\project\lira-mark\_verify_live_raw.json`

*Report written 2026-08-09T18:25:53.044555+00:00*
