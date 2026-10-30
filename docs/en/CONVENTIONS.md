# File conventions

**Language / 语言:** [中文](/CONVENTIONS.md) · English

## Ownership and build

VitePress requires Node.js 22+ and npm ci. Python's standard library manages project files, checks and migration.

| Owner | Files | Update behavior |
| --- | --- | --- |
| Managed dependencies | package.json / package-lock.json | Replaced from templates; manually merge existing application fields |
| Managed rendering | docs/.vitepress/config.mts, .github/workflows/docs.yml | Rendered from .docsite.json |
| Managed generation | docs/.vitepress/sidebar.generated.mjs | Generated from both locale sidebars |
| Managed copies | docs/public/.nojekyll, download generator/workflow | Synchronized by update |
| User content | docs/*.md, docs/en/*.md, including _sidebar.md | Never overwritten by update; init only creates missing starter pages |
| Repository configuration | .docsite.json, .github/scripts/download-page.json | Maintained by the repository; migrate explicitly upgrades and backs up fields |

README.md and en/README.md are rewritten to `/` and `/en/`. Sidebar Markdown is excluded from page output. V2 needs no custom index.html, vendored frontend or custom theme. Legacy templates remain only for unmigrated v1 projects.

The .docsite.json top-level whitelist is repo/name/emoji/description/branch/themeKey/version/engine/engineVersion/navigation. Unknown fields and invalid types are rejected; legacy fields retain defaults. See [Navigation](/en/NAVIGATION.md) for the two boolean exceptions.

## Languages and names

Chinese is the default: root README.md, docs/README.md and docs/PAGE.md. The root English mirror is README.en.md; site mirrors use docs/en/README.md and docs/en/PAGE.md. Keep matching page names and a language link at the top. Do not create README_EN.md, README_CN.md or separate docs/zh-CN trees.

Machine-generated, legal and industry-standard files retain canonical names and original languages: CHANGELOG.md, LICENSE, THIRD_PARTY_NOTICES.md and SECURITY.md. Translation copies may use .zh-CN.md / .en.md. Never rename files required by release-please, package managers or compliance tools for cosmetic consistency. Registry READMEs remain Chinese with an English link; do not invent separate npm/PyPI language rules.

## Download pages

The managed `.github/scripts/update_download_page.py` and `.github/workflows/update-download-page.yml` generate both language pages from release metadata. Do not maintain per-repository generator forks. Repository settings belong in `.github/scripts/download-page.json`:

```json
{
  "displayName": "Project",
  "previewFile": "docs/download-preview.md",
  "linkBase": ""
}
```

DisplayName changes the product title; previewFile adds a handwritten preview. V2 uses empty linkBase: VitePress handles the repository base. `/docs` applies only to legacy assembled v1 sites and is cleared during migration. Languages/outputs default to zh and en; custom output paths must satisfy language links and navigation. Missing referenced locale pages fail the build.

TrackPrerelease defaults to false. DocsWorkflow defaults to docs.yml. Pass `--tag v1.2.3` for an exact release, `--input-json release.json` for local testing, and `--check` to validate freshness. Page markers record repository, tag and publication date. Stale-write protection blocks late older tags; `--force` explicitly overrides it.

Binary assets are grouped by platform with stable latest-download links and checksums. Package-only projects document registry installation instead of inventing binaries. GITHUB_TOKEN-created releases must use workflow_call or workflow_dispatch; release:published is the fallback. After changed pages are committed, the workflow explicitly dispatches docs.yml because its GITHUB_TOKEN push does not trigger push-based deployment.

## Deployment

One active Pages workflow per repository. V2 docs.yml runs Node 22 → npm ci → npm run docs:build → uploads docs/.vitepress/dist → deploys Pages. Public/.nojekyll is copied into dist; root Markdown is not automatically published. The deployment branch matches .docsite.json.

Init/update skip docs.yml when another Pages deployment exists. Migrate backs up and disables the old workflow, reporting extra copied directories so other publishing duties can be separated manually.

V2 workflow source: template/.github/workflows/docs.yml. V1 compatibility source: template/docs.yml. Edit templates and run update instead of changing generated files.
