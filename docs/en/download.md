# Get docsite

**Language / 语言:** [中文](/download.md) · English

<!-- docsite-release-repo: redtidev1918/docsite -->
<!-- docsite-release-tag: -->
<!-- docsite: hand-written until the first release; the managed generator
     (update_download_page.py) rewrites this page once a release exists. -->

> This repository ships no packages and no release artifacts — docsite is a single
> Python script plus a template. No pip, no npm, no build step, no dependency install.

## How to get it

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
```

If `python3` exists on the machine, you can run it immediately:

```bash
python3 /tmp/docsite/docsite.py --help
```

## Why there are no Releases

docsite ships no binaries and publishes to no package index: its value is the
**template**, and the template travels with the repository. Every managed repo runs
`python3 /tmp/docsite/docsite.py update` from that same clone — an extra download step
would only add another copy that can go stale.

To pin a version, check out the commit or tag:

```bash
git -C /tmp/docsite checkout <commit>
```

## Next

- [Quick Start](/en/QUICKSTART.md) — attach a docs site to a repository
