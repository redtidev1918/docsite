# Quick Start

**Language / 语言:** [中文](/QUICKSTART.md) · English

## Attach a new repository

Inside the **target repository root**:

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite

python3 /tmp/docsite/docsite.py init \
  --repo owner/name \
  --name DisplayName \
  --emoji 🐱 \
  --branch main
```

| Flag | Meaning | Default |
| :-- | :-- | :-- |
| `--repo` | `owner/name`, required | — |
| `--name` | Site display name | repository name |
| `--emoji` | Favicon and title emoji | 📘 |
| `--description` | Page meta description | `<name> documentation…` |
| `--branch` | Branch that triggers deployment | `main` |
| `--theme-key` | localStorage key for the theme preference | `<lowercased name>-theme` |

Two kinds of files come out:

```
Managed (do not edit)   docs/index.html · docs/assets/vendor/
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

When a `docs/` directory or another docs site already exists, `init` is defensive:

- An existing `docs/index.html` or `.github/workflows/docs.yml` that is *not* the
  docsite-managed version is backed up to `*.docsite.bak` rather than silently replaced
- A Pages workflow under a different filename (for example `static.yml`) is reported,
  not deleted
- Existing Markdown is never touched

Afterwards:

1. Review `git status` and check whether `docs/index.html.docsite.bak` holds custom
   configuration worth merging into the template
2. Once `docs.yml` deploys successfully, delete the old deploy workflow so the site is
   not deployed twice
3. Align the sidebar with the navigation contract

## Day-to-day edits

No script needed. Edit Markdown directly:

1. Add or change a `.md` under `docs/`
2. Add its link to `docs/_sidebar.md` using a **root-absolute path** (`- [Title](/PAGE.md)`)
3. `git commit && git push`. The workflow watches `docs/**` and the site updates in a
   minute or two

A relative sidebar link (`[Title](PAGE.md)`) breaks with a 404 on `docs/en/` pages.

## Check consistency

```bash
python3 docsite.py check --all /path/to/repos   # every git repo in that directory
python3 docsite.py check .                      # just this repository
```

Each file reports `ok` / `MISSING` / `DRIFT`. Run `python3 docsite.py update` in the
offending repository, review the diff, commit.
