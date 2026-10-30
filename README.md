# docsite

**语言 / Language:** 中文 · [English](README.en.md)

给 GitHub 仓库生成文档站。用 VitePress 渲染 Markdown，部署到 GitHub Pages；用 Python 脚本初始化、更新配置和生成下载页。

需要 Python 3、Node.js 22+ 和 npm。Python 脚本只用标准库，网站依赖用 `npm ci` 安装。

[查看文档站](https://redtidev1918.github.io/docsite/)。旧 Docsify 站点的迁移步骤见[升级指南](docs/UPGRADE.md)。

## 从哪开始

| 场景 | 看这里 |
| --- | --- |
| 给新仓库加 Pages 文档站 | [快速开始](docs/QUICKSTART.md) |
| 中英文目录、下载页、侧边栏的约定 | [文件与命名规范](docs/CONVENTIONS.md) |
| 只改文档内容 | 直接编辑 `docs/*.md`，推送到 `main` |
| 更新模板或托管 workflow | [升级模板](docs/UPGRADE.md) |

正文和 `_sidebar.md` 由各仓库自己维护，`update` 不会覆盖它们。修改侧边栏后运行 `update`，生成 VitePress 所需的导航配置。

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

`update` 会重写依赖清单、VitePress 配置、生成的 sidebar 和 workflow。已有 Node 项目需要先处理根 package.json 的 scripts 和依赖，详见[升级指南](docs/UPGRADE.md)。

## 日常使用

1. 往 `docs/` 增加或修改 `.md` 文件。
2. 在 `docs/_sidebar.md` 中用根绝对路径加入口，例如 `- [架构](/ARCHITECTURE.md)`。
3. 修改侧边栏后运行 `python3 /tmp/docsite/docsite.py update`，再构建预览并推送。

发版后，`update-download-page.yml` 根据 Release 数据更新下载页，再触发 `docs.yml` 重新构建站点。

## 质量检查

```bash
python3 docsite.py check .
python3 docsite.py navcheck .
python3 docsite.py update
```

`check` 校验托管文件、依赖锁、配置和下载页链路；`navcheck` 校验导航与生成 sidebar 一致性。下载页内容版本通过生成器的 `--check` 单独核对。

## 功能范围

网站使用 VitePress 默认主题和本地搜索。docsite 不提供主题系统或服务端搜索。升级需要在各仓库运行命令、检查 diff 后提交。

## 许可

MIT。
