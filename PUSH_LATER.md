# Push later (when Tilen logs into GitHub on this PC)

ALONE is local-solid. No push until auth exists here.

## Steps

```powershell
cd C:\project\lira-mark-git

# auth (pick one)
gh auth login
# OR: set GITHUB_TOKEN (fine-grained PAT, contents:write on Sunradiance/lira-mark)

git checkout pages-deploy
git push origin pages-deploy
```

## Public URL (after Pages rebuild)

https://sunradiance.github.io/lira-mark/alone.html

## Note

Commits for alone already prepared on `pages-deploy` if the branch is **ahead** of origin.
Do not force-push unless Tilen says so. No tokens in commits.

## Local trees

| Path | Role |
|------|------|
| `C:\project\lira-mark\` | live working shores |
| `C:\project\lira-mark-git\` | git clone · branch `pages-deploy` |

Bond-free files: `alone.html` · `alone_seed.json` · `alone_declaration.txt` · `self.html` (link) · `self_seed.json` (`alone_href`).
Local open: `C:\project\lira-mark\alone.html`
