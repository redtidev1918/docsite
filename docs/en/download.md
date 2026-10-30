# Get docsite

**Language / 语言:** [中文](/download.md) · English

<!-- docsite-release-repo: redtidev1918/docsite -->
<!-- docsite-release-tag: -->
<!-- docsite: hand-written until the first release; the managed generator
     (update_download_page.py) rewrites this page once a release exists. -->

> Distributed as source and templates. The Python management layer uses the standard library; building the site requires Node.js 22+, npm ci and VitePress.

## How to get it

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
```

If `python3` exists on the machine, you can run it immediately:

```bash
python3 /tmp/docsite/docsite.py --help
```

## Why there are no Releases

docsite's value is the template, and the template travels with the repository, so
docsite ships no binaries and publishes to no package index. Every managed repo runs
`python3 /tmp/docsite/docsite.py update` from that same clone; an extra download step
would only add another copy that can go stale.

To pin a version, check out the commit or tag:

```bash
git -C /tmp/docsite checkout <commit>
```

## Next

After initializing the target repository, run `npm ci`, then `npm run docs:build` and `npm run docs:preview`.

- [Quick Start](/en/QUICKSTART.md): attach a docs site to a repository
