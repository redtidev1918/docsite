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

Update refreshes package.json/lock, config.mts, generated sidebar, docs.yml, public/.nojekyll and download-page tooling, and adds missing ignore entries. It never changes user Markdown, including `_sidebar.md`. Edit `.docsite.json` and sidebar sources, not generated files.

**Existing Node projects:** the root package.json and lock are replaced by managed templates. Non-managed files are backed up before takeover; numbered backups preserve earlier copies. Manually merge application scripts, dependencies and lockfile during PR review. Custom fields currently produce DRIFT under the byte-for-byte check and are replaced by subsequent updates. Evaluate this limitation before adopting docsite in a complex Node project.

For dependency upgrades, change the template's pinned package version, run `npm install` in template/ to update its lock, then run update and npm ci in each target. After manually merging dependencies, run npm install to regenerate the target lock. V2 update automatically synchronizes engineVersion/version in .docsite.json.

## Explicit Docsify migration

Commit or separately preserve current work first. Until migration, v1 remains supported by update/check/navcheck and is never silently switched to VitePress.

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

Validate docsite after its PR merges, then migrate one business repository as a pilot. Verify the real release → commit → dispatch → Pages flow before proceeding to PixivFlow, DAViewer and TelePost one at a time. Each repository gets an independent PR; never automatically merge or migrate in bulk.

## Template sources and checks

V2 uses template/.github/workflows/docs.yml: Node 22 → npm ci → VitePress → dist artifact. V1 retains template/docs.yml and legacy shells for compatibility. Change templates, then distribute with update.

```bash
python3 /tmp/docsite/docsite.py check .
python3 /tmp/docsite/docsite.py navcheck .
```

Check validates managed files, dependency locks, rendered configuration and generated sidebar consistency. The download generator's `--check` separately validates release-page freshness.
