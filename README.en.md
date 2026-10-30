# docsite

**Language / 语言:** [中文](README.md) · English

Build a documentation site for a GitHub repository. VitePress renders the Markdown and GitHub Pages hosts it. A Python script sets up the project, updates configuration and generates release download pages.

Requires Python 3, Node.js 22+ and npm. The script uses Python's standard library. Install the site dependencies with `npm ci`.

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
# Run inside the target repository:
python3 /tmp/docsite/docsite.py init --repo owner/name --name Project
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

Select GitHub Actions in Settings → Pages, then push to the configured branch. Pages runs Node 22, `npm ci`, and `npm run docs:build`.

Edit Markdown under `docs/` and English translations under `docs/en/`. After changing `_sidebar.md`, run `update` to regenerate navigation. It leaves your Markdown alone. On release, the download workflow updates both language pages and triggers a new site build.

Update replaces package.json/lock, VitePress configuration, generated sidebar and workflows. Existing Node projects need to merge their application scripts and dependencies; originals are backed up before replacement. See the [upgrade guide](docs/en/UPGRADE.md) for the current limitations.

Existing Docsify sites can keep using `update`, `check` and `navcheck`. To migrate:

```bash
python3 /tmp/docsite/docsite.py migrate --dry-run
python3 /tmp/docsite/docsite.py migrate
npm ci
python3 /tmp/docsite/docsite.py build
```

Review the diff, backups and disabled legacy workflow. Remove legacy files after the build and preview pass. Upgrade each repository in its own PR.

[Quick Start](docs/en/QUICKSTART.md) · [Conventions](docs/en/CONVENTIONS.md) · [Navigation](docs/en/NAVIGATION.md) · [Upgrade and rollback](docs/en/UPGRADE.md) · [Website](https://redtidev1918.github.io/docsite/)

MIT.
