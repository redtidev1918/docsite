# docsite

**语言 / Language:** 中文 · [English](README.en.md)

轻量级开源项目文档网站生成器：VitePress 负责渲染、默认主题、搜索与多语言，Python CLI 负责初始化、升级、检查、迁移与下载页，GitHub Pages 负责托管。

前提：Python 3、Node.js 22+ 和 npm。Python 管理层仅用标准库；网站通过 `npm ci` 安装锁定依赖并构建。

站点：[docsite](https://redtidev1918.github.io/docsite/)。下游旧站仍可使用 Docsify；迁移须逐仓库执行并审查独立 PR。

## 从哪开始

| 场景 | 看这里 |
| --- | --- |
| 给新仓库加 Pages 文档站 | [快速开始](docs/QUICKSTART.md) |
| 中英文目录、下载页、侧边栏的约定 | [文件与命名规范](docs/CONVENTIONS.md) |
| 只改文档内容 | 直接编辑 `docs/*.md`，推送到 `main` |
| 更新模板或托管 workflow | [升级模板](docs/UPGRADE.md) |

Markdown 留在业务仓库里，`update` 永不覆盖正文或 `_sidebar.md`。侧边栏由 `_sidebar.md` 生成，不手工维护第二份配置。

## 快速开始

在目标仓库根目录执行：

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
python3 /tmp/docsite/docsite.py init \
  --repo owner/name \
  --name 显示名 \
  --emoji 📘 \
  --branch main
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

推送到远程后，GitHub Actions 会发布 Pages。首次部署需要在仓库 `Settings → Pages` 里确认 Source 是 GitHub Actions。

生成的站点地址是：

```text
https://<owner>.github.io/<name>/
```

`<name>` 必须和仓库名完全一致，因为 GitHub Pages 路径区分大小写。

## 会生成什么

```text
.docsite.json
package.json / package-lock.json
docs/
├── .vitepress/config.mts
├── .vitepress/sidebar.generated.mjs
├── public/.nojekyll
├── _sidebar.md
├── README.md
├── QUICKSTART.md
├── download.md
└── en/
.github/workflows/docs.yml
.github/workflows/update-download-page.yml
.github/scripts/update_download_page.py
```

Markdown 由仓库自己维护；依赖清单、VitePress 配置、生成的 sidebar 和部署链路由模板托管。已有 Node 工程的 scripts/依赖需要在 PR 中人工合并，详见[升级指南](docs/UPGRADE.md)。

## 日常使用

1. 往 `docs/` 增加或修改 `.md` 文件。
2. 在 `docs/_sidebar.md` 中用根绝对路径加入口，例如 `- [架构](/ARCHITECTURE.md)`。
3. 修改侧边栏后运行 `python3 /tmp/docsite/docsite.py update`，再构建预览并推送。

下载页由 `.github/workflows/update-download-page.yml` 根据 Release 数据刷新，并显式 dispatch `docs.yml` 重建。旧 Docsify 站点先运行 `migrate --dry-run`，再按[升级指南](docs/UPGRADE.md)迁移。

## 质量检查

```bash
python3 docsite.py check .
python3 docsite.py navcheck .
python3 docsite.py update
```

`check` 校验托管文件、依赖锁、配置和下载页链路；`navcheck` 校验导航与生成 sidebar 一致性。下载页内容版本通过生成器的 `--check` 单独核对。

## 非目标

不维护自定义主题、服务端搜索或外部搜索服务；使用 VitePress 默认主题和本地搜索。每个仓库独立升级、独立 PR，不自动合并。

## 许可

MIT。完整规范、部署边界和升级方式见 [文档站](https://redtidev1918.github.io/docsite/)。
