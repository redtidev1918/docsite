# Navigation contract

**Language / 语言:** [中文](/NAVIGATION.md) · English

Organize navigation around user tasks. Language is a site dimension, not a sidebar category. The homepage introduces and directs; sidebars link independent pages; the outline describes the current page. Adding a heading does not require adding a sidebar entry.

## Checked rules

| Rule | Severity |
| --- | --- |
| Root sidebar must not contain an English document tree; clearly labeled single-page English fallbacks are allowed | COMBINED_LOCALES error |
| English pages require docs/en/_sidebar.md | EN_SIDEBAR_MISSING error |
| No sidebar heading anchors | ANCHOR_LINK error |
| No duplicate targets within a sidebar | DUPLICATE_LINK error |
| Categories should usually contain at least two pages | SINGLE_PAGE_CATEGORY warning |
| Use root-absolute local paths | NOT_ROOT_ABSOLUTE warning |
| Mark Chinese fallbacks in the English sidebar individually or under a Chinese category | EN_SIDEBAR_ZH_LINK warning |
| V2 targets must correspond to real files under docs/; `/` maps to README.md | BROKEN_SIDEBAR_LINK error |
| Generated sidebar must match regeneration from Markdown sources | SIDEBAR_STALE error |

Errors affect the exit code; warnings are advisory. Subjective category naming is not checked.

## Source and locales

Edit docs/_sidebar.md and docs/en/_sidebar.md, then run update. Never edit sidebar.generated.mjs manually. The converter preserves categories, order and two levels of nesting, removes .md suffixes for routes and retains external links. README.md rewrites keep homepage source names stable. Sidebar Markdown is not published as a page.

Locales provide language menus; corresponding translations retain the page path. Verify fallback behavior for missing translations, and fix explicit language links to avoid dead links. V2 English pages live under `/en/`. Unmigrated v1 shells retain their old publication layout, including `/docs/en/` where applicable.

V2 retires Docsify alias/subMaxLevel checks; GLOBAL_SIDEBAR_ALIAS and HEADING_INJECTION remain in the v1 rule table. VitePress's default theme provides the page outline and local search.

## Suggested structure

Use two to four categories for a small site: Getting Started, Usage & Configuration, Development and Project. Avoid empty template categories, vague labels and a second sitemap. Put download under Getting Started once; homepage links may repeat it. Include canonical changelogs, licenses or security files only when useful, preserving their required paths.

## Explicit exceptions

```json
{
  "navigation": {
    "allowSidebarAnchors": true,
    "allowCombinedLocales": true
  }
}
```

Only these two boolean fields are accepted under navigation. Unknown keys, wrong types and invalid JSON produce NAVIGATION_SCHEMA errors; there is no blanket ignore option.

The navigation workflow runs against managed repositories weekly and on relevant changes. Every structural exception must be declared in the repository configuration. `navcheck --all` checks navigation contracts, while build also checks rendered-page links.
