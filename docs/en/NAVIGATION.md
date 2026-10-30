# Navigation rules

**Language / 语言:** [中文](/NAVIGATION.md) · English

Group sidebar links by what readers need to find. Chinese and English each have a sidebar; readers switch languages from the top menu. Use the homepage to introduce the project, the sidebar to link pages and the outline to list headings on the current page. A new README heading does not need a sidebar entry.

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

Edit docs/_sidebar.md and docs/en/_sidebar.md, then run update to generate sidebar.generated.mjs. The converter keeps categories, order and two levels of nesting, removes .md suffixes for routes and retains external links. Write the homepages in README.md and en/README.md. Sidebar Markdown is not published as a page.

Locales provide language menus; corresponding translations retain the page path. Verify fallback behavior for missing translations, and fix explicit language links to avoid dead links. V2 English pages live under `/en/`. Unmigrated v1 shells retain their old publication layout, including `/docs/en/` where applicable.

V2 retires Docsify alias/subMaxLevel checks; GLOBAL_SIDEBAR_ALIAS and HEADING_INJECTION remain in the v1 rule table. VitePress's default theme provides the page outline and local search.

## Suggested structure

For a small site, two to four categories are usually enough: Getting Started, Usage & Configuration, Development and Project. Use the groups you have content for. Give pages specific names, such as Development → Architecture. Put download in the sidebar once; the homepage may link it too. Add changelogs, licenses or security files when readers need them, keeping their original paths.

## Exceptions

```json
{
  "navigation": {
    "allowSidebarAnchors": true,
    "allowCombinedLocales": true
  }
}
```

Navigation accepts these two boolean fields. Unknown keys, wrong types and invalid JSON produce NAVIGATION_SCHEMA errors.

The navigation workflow runs weekly and on relevant changes. If it fails, check the rule name and file path in the logs. `navcheck --all` checks navigation rules; build also checks links in the rendered pages.
