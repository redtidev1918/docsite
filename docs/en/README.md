# docsite

**Language / 语言:** [中文](/) · English

Zero-dependency docsify scaffold. One Python script plus one template, and every GitHub
repository can use the same docs site shell.

The full specification is maintained in Chinese:
[文档规范](/CONVENTIONS.md) · [导航契约](/NAVIGATION.md) · [升级模板](/UPGRADE.md)

## What it solves

A dozen repositories each hand-rolling their own docs site means a dozen incompatible
`index.html` files, a dozen different deploy workflows, and download pages that quietly
rot at old versions. docsite manages the shell; the repository keeps the Markdown.

## Design trade-offs

| Choice | Why |
| :-- | :-- |
| Pure stdlib | A managed repo needs no dependency install; CI just needs `python3` |
| Shell only | `index.html`, the deploy workflow and vendored assets are managed; Markdown belongs to the repo and is never overwritten on upgrade |
| No content pushed down | Download pages are the exception: they are generated from release data, because a hand-written one always goes stale |
| No bulk upgrade | Every repo runs `update` itself, so each diff stays visible and reviewable |

## Not goals

- No automatic per-locale routing (English lives in `docs/en/`, navigated by the sidebar)
- No server-side search, no custom theme system
- No "upgrade every repository at once" switch
