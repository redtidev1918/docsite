# File conventions

**Language / 语言:** [中文](/CONVENTIONS.md) · English

## Who maintains each file

The Python script updates configuration and checks files. VitePress builds the site with Node.js 22+ after `npm ci`.

| Owner | Files | Update behavior |
| --- | --- | --- |
| Managed dependencies | package.json / package-lock.json | Replaced from templates; manually merge existing application fields |
| Managed rendering | docs/.vitepress/config.mts, .github/workflows/docs.yml | Rendered from .docsite.json |
| Managed generation | docs/.vitepress/sidebar.generated.mjs | Generated from both locale sidebars |
| Managed copies | docs/public/.nojekyll, download generator/workflow | Synchronized by update |
| User content | docs/*.md, docs/en/*.md, including _sidebar.md | Never overwritten by update; init only creates missing starter pages |
| Repository configuration | .docsite.json, .github/scripts/download-page.json | You; migrate backs up these files before updating fields |

README.md and en/README.md appear at `/` and `/en/`. Sidebar Markdown supplies navigation and is not published as a page. Unmigrated v1 repositories keep using the Docsify templates.

The .docsite.json fields are repo/name/emoji/description/branch/themeKey/version/engine/engineVersion/navigation/packageMode. PackageMode is managed by default, or merge to preserve an existing Node project and add only documentation scripts and VitePress. Unknown fields and invalid types are rejected; legacy fields retain defaults. See [Navigation](/en/NAVIGATION.md) for the two boolean exceptions.

## Languages and names

Chinese is the default: root README.md, docs/README.md and docs/PAGE.md. The root English mirror is README.en.md; site mirrors use docs/en/README.md and docs/en/PAGE.md. Keep matching page names and a language link at the top. Do not create README_EN.md, README_CN.md or separate docs/zh-CN trees.

Keep the original names and languages of files such as CHANGELOG.md, LICENSE, THIRD_PARTY_NOTICES.md and SECURITY.md. Translation copies may use .zh-CN.md / .en.md. For example, Graf uses release-please to maintain the English CHANGELOG.md and keeps its Chinese translation in CHANGELOG.zh-CN.md. Keep fixed paths required by package managers and compliance tools too.

The npm and PyPI READMEs use the Chinese README with an English link at the top. Keep pyproject.toml's readme pointing to README.md; handle a separate English package description in the release process if needed.

## Download pages

Update synchronizes `.github/scripts/update_download_page.py` and `.github/workflows/update-download-page.yml`. These generate both language pages from release data. Put project-specific settings in `.github/scripts/download-page.json` so update does not overwrite them:

```json
{
  "displayName": "Project",
  "previewFile": "docs/download-preview.md",
  "linkBase": ""
}
```

`displayName` changes the product title; `previewFile` adds a handwritten preview. V2 uses an empty `linkBase` because VitePress handles the repository base. `/docs` applies to legacy assembled v1 sites and is cleared during migration. `languages` / `outputs` default to zh and en. Custom output paths need working language links and navigation; a missing linked page fails the build.

`trackPrerelease` defaults to false; `docsWorkflow` defaults to docs.yml. Use `--tag v1.2.3` for a specific release, `--input-json release.json` for local testing and `--check` to check for updates. Page markers record the repository, tag and publication date. A late task for an older tag will not overwrite a newer page unless you use `--force`.

List binary assets by platform with latest-download links and checksums. For package-only projects, give installation commands and registry links. Releases created with GITHUB_TOKEN need workflow_call or workflow_dispatch to start the download-page workflow; other releases can use release:published. After committing changed pages, the workflow triggers docs.yml because a GITHUB_TOKEN push does not trigger push-based deployment.

`previewFiles` selects a preview for each language, for example `{"en":"docs/en/download-preview.md"}`. It takes precedence over previewFile for that language.

## Deployment

One active Pages workflow per repository. V2 docs.yml runs Node 22 → npm ci → npm run docs:build → uploads docs/.vitepress/dist → deploys Pages. Public/.nojekyll is copied into dist; root Markdown is not automatically published. The deployment branch matches .docsite.json.

Init/update skip docs.yml when another Pages deployment exists. Migrate backs up and disables the old workflow, reporting extra copied directories so other publishing duties can be separated manually.

V2 workflow source: template/.github/workflows/docs.yml. V1 compatibility source: template/docs.yml. Edit templates and run update instead of changing generated files.
