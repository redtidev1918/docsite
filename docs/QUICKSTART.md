# 快速开始

**语言 / Language:** 中文 · [English](/en/QUICKSTART.md)

## 新仓库接入

前提：Python 3、Node.js 22+ 和 npm。Python 工程管理层仅用标准库，VitePress 网站需要安装依赖并构建。

在**目标仓库根目录**执行：

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite

python3 /tmp/docsite/docsite.py init \
  --repo owner/name \
  --name 显示名 \
  --emoji 🐱 \
  --branch main
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

| 参数 | 说明 | 默认 |
| :-- | :-- | :-- |
| `--repo` | `owner/name`，必填 | — |
| `--name` | 站点显示名 | 仓库名 |
| `--emoji` | favicon 与站名前的 emoji | 📘 |
| `--description` | 页面 meta description | 「\<name\> 文档中心……」 |
| `--branch` | 触发部署的分支 | `main` |
| `--theme-key` | 仅保留给旧 Docsify 配置兼容；VitePress 使用默认主题偏好 | 不设置 |

生成的东西分两类：

```
托管（别手改）     package.json · package-lock.json
                docs/.vitepress/config.mts · sidebar.generated.mjs
                docs/public/.nojekyll
                .github/workflows/docs.yml
                .github/scripts/update_download_page.py
                .github/workflows/update-download-page.yml
你的内容         docs/README.md · docs/_sidebar.md · docs/download.md
                docs/en/ 下同名页
```

推送后 workflow 自动部署。仓库 **Settings → Pages → Source** 选 GitHub Actions
（首次 `configure-pages` 一般会自动配好）。站点地址：`https://<owner>.github.io/<name>/`

## 老仓库接入

已有 docsite 配置或托管 Docsify 外壳时，使用显式迁移，见[升级与回滚](/UPGRADE.md)：

```bash
python3 /tmp/docsite/docsite.py migrate --dry-run
python3 /tmp/docsite/docsite.py migrate
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

接入后：

1. 检查 diff、`*.docsite.bak`、链接改写和停用的旧 workflow。
2. 已有 Node 项目的根 package.json 会被接管；必须人工合并业务 scripts/依赖。
3. 构建与预览成功后再人工清理旧外壳，每仓库独立 PR。

全新 `init` 保留已有 Markdown，只对缺失页面填入骨架；首次接管非托管配置先备份。若有其它 Pages workflow，会跳过生成 docs.yml，须先解决部署职责冲突。

## 日常改文档

直接编辑 Markdown；导航源有变化时重新生成 sidebar：

1. 在 `docs/` 加或改 `.md`
2. 在 `docs/_sidebar.md` 里加链接（**根绝对路径**：`- [标题](/PAGE.md)`）
3. `python3 /tmp/docsite/docsite.py update`，再运行 `build` / `preview`。
4. 核对 diff 后提交推送，Node 22 的 CI 安装依赖并构建部署。

只编辑 `_sidebar.md`，不要手改 `sidebar.generated.mjs`。默认主题提供亮暗、本地搜索和页面目录；首页由 README.md 重写为 `/`，英文首页为 `/en/`。

## 检查一致性

```bash
python3 docsite.py check --all /path/to/repos   # 扫描该目录下所有 git 仓库
python3 docsite.py check .                      # 只查当前仓库
```

逐文件输出 `ok` / `MISSING` / `DRIFT`。有偏差就到对应仓库跑 `python3 docsite.py update`，
看 diff 后提交。
