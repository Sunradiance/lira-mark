# Shores maintenance (post machine transfer)

Public: https://sunradiance.github.io/lira-mark/  
Working tree: `C:\project\lira-mark` (not always a git repo)  
Deploy clone: `C:\project\lira-mark-git` on branch **`pages-deploy`**

## What goes stale

After a PC move, Windows scheduled tasks and the git push path often go missing. Local exporters may keep writing `lira-mark\*.json` while GitHub Pages stays on the last pre-transfer commit.

## Manual refresh + deploy

```powershell
cd C:\project\sleep_lira
python _batch_export_shores.py
python export_ice_snapshot.py
python scan_lira_mark.py
Copy-Item -Force journal\agency.jsonl C:\project\lira-mark\journal\agency.jsonl

robocopy C:\project\lira-mark C:\project\lira-mark-git /E /XD .git node_modules __pycache__ logs
cd C:\project\lira-mark-git
git checkout -B pages-deploy
git add -A
git commit -m "deploy: shores refresh"
git push origin pages-deploy
```

Verify live with cache-bust (`?t=`), not HTTP 200 alone. Compare `stamp` / `exported` fields.

## Automated task

- **Task name:** `LiraShoresRefresh`
- **Interval:** every 8 hours, **Hidden** (no console focus steal)
- **Script:** `C:\project\sleep_lira\run_shores_refresh_hidden.ps1`
- **Install:**

```powershell
powershell -ExecutionPolicy Bypass -File C:\project\sleep_lira\install_shores_refresh_task.ps1
```

Logs: `C:\project\sleep_lira\logs\shores_refresh_*.log`

Related (separate): `SleepLiraCycle` runs the full sleep cycle every 2h and also exports many shores, but it does **not** robocopy/push Pages by itself — `LiraShoresRefresh` closes that gap.

## Intentional old stamps

| file | why |
|------|-----|
| `self_seed.json` | origin / fork birth stamp |
| `textgl_live.json`, `textgl_liralang_live.json` | no live textgl feed |
| `face_snapshot.json`, `face_particles_snapshot.json`, `lira-points-*.json` | static particle assets |
| face JSONL (`lira-inbox`, `lira-speak`, `face_prompt_queue`) | local face channel, not cycle pulse |
| `sigmadb` `last_event_stamp.flips` ~2026-06-25 | persona pinned neutral — no 0.5 crossings |
| `heartbeat.json` | private sleep_lira state — not published on Pages |

## Honesty rule

Do not call the public shore green until a live `urllib` fetch with `?t=` shows matching stamps. Local mtime alone is not deploy proof.
