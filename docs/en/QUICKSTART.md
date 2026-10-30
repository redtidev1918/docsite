# Quick Start

**Language / 语言:** [中文](/QUICKSTART.md) · English

## Attach a new repository

Requires Python 3, Node.js 22+ and npm. The Python management layer uses the standard library; VitePress requires dependency installation and a build.

Inside the **target repository root**:

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite

python3 /tmp/docsite/docsite.py init \
  --repo owner/name \
  --name DisplayName \
  --emoji 🐱 \
  --branch main
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

| Flag | Meaning | Default |
| :-- | :-- | :-- |
| `--repo` | `owner/name`, required | — |
| `--name` | Site display name | repository name |
| `--emoji` | Favicon and title emoji | 📘 |
| `--description` | Page meta description | `<name> documentation…` |
| `--branch` | Branch that triggers deployment | `main` |
| `--theme-key` | Legacy Docsify compatibility only; VitePress manages theme preferences | unset |

Two kinds of files come out:

```
Managed (do not edit)   package.json · package-lock.json
                        docs/.vitepress/config.mts · sidebar.generated.mjs
                        docs/public/.nojekyll
                        .github/workflows/docs.yml
                        .github/scripts/update_download_page.py
                        .github/workflows/update-download-page.yml
Your content            docs/README.md · docs/_sidebar.md · docs/download.md
                        same-named pages under docs/en/
```

Push and the workflow deploys automatically. Set **Settings → Pages → Source** to
GitHub Actions (the first `configure-pages` run normally does it). The site lives at
`https://<owner>.github.io/<name>/`.

## Attach an existing repository

Existing docsite configurations and managed Docsify shells require an explicit migration. See [Upgrade and rollback](/en/UPGRADE.md).

```bash
python3 /tmp/docsite/docsite.py migrate --dry-run
python3 /tmp/docsite/docsite.py migrate
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

Afterwards:

1. Review the diff, backups, rewritten links and disabled legacy workflow.
2. Existing Node projects must merge their scripts and dependencies into the managed root package.json.
3. Remove legacy shells only after build and preview pass. Use one PR per repository.

For a new site, init preserves existing Markdown and fills in missing starter pages. Non-managed configurations are backed up before takeover. An existing alternative Pages workflow blocks generation of docs.yml until deployment responsibilities are resolved.

## Day-to-day edits

Edit Markdown directly; regenerate the sidebar after changing its source:

1. Add or change a `.md` under `docs/`
2. Add its link to `docs/_sidebar.md` using a **root-absolute path** (`- [Title](/PAGE.md)`)
3. Run `python3 /tmp/docsite/docsite.py update`, then `build` and `preview`.
4. Review, commit and push. CI installs locked dependencies and builds with Node 22.

Only edit `_sidebar.md`, never `sidebar.generated.mjs`. The default theme provides light/dark modes, local search and page outlines. README.md remains the homepage source, rewritten to `/` and `/en/`.

## Check consistency

```bash
python3 docsite.py check --all /path/to/repos   # every git repo in that directory
python3 docsite.py check .                      # just this repository
```

Each file reports `ok` / `MISSING` / `DRIFT`. Run `python3 docsite.py update` in the
offending repository, review the diff, commit.
