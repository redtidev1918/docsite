# Upgrade and rollback

**Language / 语言:** [中文](/UPGRADE.md) · English

## Refresh a VitePress project

Requires Python 3, Node.js 22+ and npm. Run inside each target repository:

```bash
git -C /tmp/docsite pull
python3 /tmp/docsite/docsite.py update
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

Update replaces package.json/lock, config.mts, generated sidebar, docs.yml, public/.nojekyll and download-page scripts, and adds missing ignore entries. It leaves page Markdown and `_sidebar.md` unchanged. Edit `.docsite.json` for site settings and `_sidebar.md` for navigation.

For existing Node projects, docsite replaces the root package.json and lock. It backs up non-managed files first, adding a number if a backup already exists.

Merge any application scripts, dependencies and lockfile changes you need to keep, then install and build. Custom fields will produce DRIFT in check and will be replaced by the next update. The current version cannot preserve an existing Node project's package configuration automatically; check this before adopting it.

For dependency upgrades, change the template's pinned package version, run `npm install` in template/ to update its lock, then run update and npm ci in each target. After manually merging dependencies, run npm install to regenerate the target lock. V2 update automatically synchronizes engineVersion/version in .docsite.json.

## Migrate from Docsify

Commit or save current changes first. Existing sites can keep using v1 update/check/navcheck. Only migrate switches the engine to VitePress.

```bash
python3 /tmp/docsite/docsite.py migrate --dry-run
python3 /tmp/docsite/docsite.py migrate
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

- Requires a managed docs/index.html or .github/pages/index.html. Dry-run writes nothing and reports file changes, backups, workflow disabling and publication changes.
- Legacy shells and vendor assets are copied to backups and retained. Markdown and configuration are backed up before link rewrites. Update leaves Markdown intact; migrate explicitly rewrites Docsify hash links and legacy `/docs/` prefixes.
- A shell sidebar is copied into docs/ only if missing there; the original is preserved.
- Old Pages workflows such as static.yml are backed up and disabled to avoid duplicate deployments. Separate additional duties such as `cp -R themes _site` manually. Root Markdown is no longer automatically published.
- Existing configuration fields are retained; engine, engineVersion and version:2 are set. Legacy download-page linkBase `/docs` is cleared.
- Generate both download locales. A missing page referenced by a language link fails the build; fix content instead of enabling ignoreDeadLinks.

After build, preview and deployment succeed, remove legacy shells, vendor files and backups as a separate manual step. Migration does not automatically delete legacy site files.

## Rollback and rollout

For an unmerged PR, discard only tracked changes belonging to the migration and restore any previously uncommitted files from backups. Inspect and remove newly generated untracked files individually; git checkout alone does not remove them. For a merged migration, create a revert commit and restore the old workflow. Keep only one Pages deployment active.

When migrating several repositories, start with one. Check the live pages and the release → commit → dispatch → Pages flow before moving on. Submit a separate PR for each repository.

## Template sources and checks

V2 uses template/.github/workflows/docs.yml: Node 22 → npm ci → VitePress → dist artifact. V1 retains template/docs.yml and legacy shells for compatibility. Change templates, then distribute with update.

```bash
python3 /tmp/docsite/docsite.py check .
python3 /tmp/docsite/docsite.py navcheck .
```

Check validates managed files, dependency locks, rendered configuration and generated sidebar consistency. The download generator's `--check` separately validates release-page freshness.
