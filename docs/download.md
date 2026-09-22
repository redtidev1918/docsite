# 获取 docsite

**语言 / Language:** 中文 · [English](/en/download.md)

<!-- docsite-release-repo: redtidev1918/docsite -->
<!-- docsite-release-tag: -->
<!-- docsite: hand-written until the first release; the managed generator
     (update_download_page.py) rewrites this page once a release exists. -->

> 本仓库没有安装包，也没有发布产物。docsite 就是一个 Python 脚本加一份模板，
> 不需要 pip、npm、构建步骤，也不需要联网安装依赖。

## 获取方式

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
```

只要系统里有 `python3`，就能直接跑：

```bash
python3 /tmp/docsite/docsite.py --help
```

## 为什么没有 Releases

docsite 的价值在模板，模板跟着仓库走，所以不分发二进制，也不上包索引。
各个接入仓库在根目录跑 `python3 /tmp/docsite/docsite.py update` 时，用的就是克隆下来的
这份仓库；中间多一个下载步骤只会多一个过期的副本。

如果你需要固定版本，直接 checkout 对应的 commit 或 tag：

```bash
git -C /tmp/docsite checkout <commit>
```

## 接下来

- [快速开始](/QUICKSTART.md)：把站点接到一个仓库上
- [文件与命名规范](/CONVENTIONS.md)：下载页为什么由脚本生成而不是手写
