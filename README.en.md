# docsite

**Language / 语言:** [中文](README.md) · English

A lightweight documentation website generator for open-source projects. VitePress handles rendering, the default theme, local search and locales. The Python CLI manages projects, templates, migrations and release download pages. GitHub Pages hosts the build.

Requires Python 3, Node.js 22+ and npm. The Python layer uses the standard library; the site requires locked npm dependencies and a build.

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
# Run inside the target repository:
python3 /tmp/docsite/docsite.py init --repo owner/name --name Project
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

Select GitHub Actions in Settings → Pages, then push to the configured branch. Pages runs Node 22, `npm ci`, and `npm run docs:build`.

Edit Markdown under `docs/` and English mirrors under `docs/en/`. After changing `_sidebar.md`, run `update` to regenerate the sidebar. `update` preserves user Markdown. Release workflows generate both download pages and explicitly dispatch the Pages workflow.

The managed files include package.json/lock, VitePress configuration, generated sidebar and workflows. Existing Node projects must merge their custom scripts and dependencies during PR review; originals are backed up before takeover.

Existing Docsify sites remain supported by `update`, `check` and `navcheck` until an explicit migration:

```bash
python3 /tmp/docsite/docsite.py migrate --dry-run
python3 /tmp/docsite/docsite.py migrate
npm ci
python3 /tmp/docsite/docsite.py build
```

Review the diff, backups and disabled legacy workflow. Remove legacy files only after a successful build and preview. Each repository gets its own PR; PRs are never automatically merged.

[Quick Start](docs/en/QUICKSTART.md) · [Conventions](docs/en/CONVENTIONS.md) · [Navigation](docs/en/NAVIGATION.md) · [Upgrade and rollback](docs/en/UPGRADE.md) · [Website](https://redtidev1918.github.io/docsite/)

MIT.
