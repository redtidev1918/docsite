# 获取 docsite

**语言 / Language:** 中文 · [English](/en/download.md)

<!-- docsite-release-repo: redtidev1918/docsite -->
<!-- docsite-release-tag: -->
<!-- docsite: hand-written until the first release; the managed generator
     (update_download_page.py) rewrites this page once a release exists. -->

docsite 通过 Git 仓库分发，克隆后即可运行 Python 脚本。构建网站还需要 Node.js 22+ 和 npm。

## 获取方式

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
```

查看命令帮助：

```bash
python3 /tmp/docsite/docsite.py --help
```

脚本和模板放在同一个仓库中。需要固定版本时，checkout 对应的 commit 或 tag：

```bash
git -C /tmp/docsite checkout <commit>
```

按[快速开始](/QUICKSTART.md)初始化目标仓库，再运行 `npm ci`、`npm run docs:build` 和 `npm run docs:preview` 验证网站。
