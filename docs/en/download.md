# Get docsite

**Language / 语言:** [中文](/download.md) · English

<!-- docsite-release-repo: redtidev1918/docsite -->
<!-- docsite-release-tag: -->
<!-- docsite: hand-written until the first release; the managed generator
     (update_download_page.py) rewrites this page once a release exists. -->

Clone the Git repository to get docsite's script and templates. The script runs with Python 3; building the site also requires Node.js 22+ and npm.

## How to get it

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
```

View command help:

```bash
python3 /tmp/docsite/docsite.py --help
```

The script and templates live in the same repository. To pin a version, check out the commit or tag:

```bash
git -C /tmp/docsite checkout <commit>
```

Follow [Quick Start](/en/QUICKSTART.md) to initialize the target repository, then run `npm ci`, `npm run docs:build` and `npm run docs:preview`.
