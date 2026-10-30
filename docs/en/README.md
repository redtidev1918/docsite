# docsite

**Language / 语言:** [中文](/) · English

A lightweight documentation website generator: VitePress rendering, a Python project management layer, and GitHub Pages hosting. Requires Python 3, Node.js 22+ and npm; run `npm ci` before building.

[Quick Start](/en/QUICKSTART.md) · [Conventions](/en/CONVENTIONS.md) · [Navigation](/en/NAVIGATION.md) · [Upgrade](/en/UPGRADE.md)

## What it solves

A dozen repositories each hand-rolling their own docs site means a dozen incompatible
configurations, a dozen different deploy workflows, and download pages that quietly
rot at old versions. docsite manages the project; the repository keeps the Markdown.

## Design trade-offs

| Choice | Why |
| :-- | :-- |
| Python standard library | Project management needs no Python packages; site builds require Node 22+ and locked npm dependencies |
| Default VitePress engine | Package manifests, config, generated sidebar and workflows are managed; update never overwrites user Markdown |
| No content pushed down | Download pages are the exception: they are generated from release data, because a hand-written one always goes stale |
| No bulk upgrade | Every repo runs `update` itself, so each diff stays visible and reviewable |

## Not goals

- Locales and independent sidebars organize Chinese and English pages; README.md remains the homepage source
- No server-side search, no custom theme system
- No "upgrade every repository at once" switch
