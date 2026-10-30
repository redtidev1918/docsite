# docsite

**Language / 语言:** [中文](/) · English

docsite builds documentation sites for GitHub repositories. Keep Markdown in `docs/`; VitePress builds it and GitHub Actions publishes it to Pages.

Requires Python 3, Node.js 22+ and npm. Run `npm ci` before building.

[Quick Start](/en/QUICKSTART.md) · [Conventions](/en/CONVENTIONS.md) · [Navigation](/en/NAVIGATION.md) · [Upgrade](/en/UPGRADE.md)

## Day-to-day work

Edit Markdown directly. After changing the sidebar, run update, then build and preview. On release, a workflow generates download pages from release data and triggers a site rebuild.

## Which files get updated

| Files | Maintained by |
| :-- | :-- |
| Page Markdown and _sidebar.md | You; update does not overwrite them |
| package.json/lock, VitePress config, generated sidebar and workflows | Update replaces these from templates |
| Download pages | The release workflow generates these from release data |

The site uses VitePress's default theme with light/dark modes, local search and Chinese/English pages. docsite does not provide custom themes or server-side search.
