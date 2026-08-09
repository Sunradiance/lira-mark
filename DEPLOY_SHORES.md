# Shore deploy (new PC)

Public site: https://sunradiance.github.io/lira-mark/

Local tree at `C:\project\lira-mark` is **not** a git repo after transfer (no `.git` in zip).

## One-time reconnect

```powershell
# Option A — clone alongside, then copy fresh files
cd C:\project
git clone https://github.com/Sunradiance/lira-mark.git lira-mark-git
# Auth: GitHub login / PAT with repo scope, or SSH key

# Copy working shores + snapshots from live tree into the clone
robocopy C:\project\lira-mark C:\project\lira-mark-git /E /XD .git node_modules

cd C:\project\lira-mark-git
git checkout -B pages-deploy
git add -A
git status
git commit -m "deploy: shores from new PC $(Get-Date -Format yyyy-MM-dd)"
git push -u origin pages-deploy
```

GitHub Pages must be set to serve branch **`pages-deploy`** (or `gh-pages` / docs — match repo settings).

## Token

Store a fine-grained PAT (contents: write) as env `GITHUB_TOKEN` or User secret — **not** committed.  
No GitHub key was in `sleep_lira/secrets.json` on transfer.

## After deploy

```powershell
python C:\project\sleep_lira\audit_shores.py
```
