# 文件与命名规范

**语言 / Language:** 中文 · [English](/en/CONVENTIONS.md)

这份文档说明 docsite 的文件布局、命名和下载页配置。

## 文件由谁维护

Python 脚本更新配置和检查文件，VitePress 构建网站。构建前需要 Node.js 22+ 和 `npm ci`。

| 类别 | 文件 | 更新规则 |
| :-- | :-- | :-- |
| 托管依赖 | package.json / package-lock.json | 默认按模板下发；packageMode: merge 保留 Node 工程字段 |
| 托管渲染 | docs/.vitepress/config.mts、.github/workflows/docs.yml | 从 .docsite.json 渲染 |
| 托管生成 | docs/.vitepress/sidebar.generated.mjs | 从两种语言的 _sidebar.md 生成 |
| 托管复制 | docs/public/.nojekyll、下载页生成器/workflow | update 同步 |
| 用户内容 | docs/*.md、docs/en/*.md（含 _sidebar.md） | update 不覆盖；init 只创建缺失的示例页 |
| 仓库配置 | .docsite.json、.github/scripts/download-page.json | 自己维护；migrate 升级字段前会备份 |

README.md 与 en/README.md 发布为 `/` 与 `/en/`；`_sidebar.md` 只用于生成导航，不作为页面发布。尚未迁移的 v1 仓库继续使用旧 Docsify 模板。

`.docsite.json` 顶层接受 repo/name/emoji/description/branch/themeKey/version/engine/engineVersion/navigation/packageMode；未知字段和错误类型会报错。packageMode 可设 managed（默认，整体托管依赖文件）或 merge（保留已有 Node 项目，只合并 docs scripts 与 VitePress 依赖）。旧配置缺少的字段会使用默认值，navigation 的两个开关见[导航规则](/NAVIGATION.md)。

## 语言与文件命名

| 位置 | 中文（默认） | 英文 |
| :-- | :-- | :-- |
| 仓库根 README | `README.md` | `README.en.md` |
| 文档站首页 | `docs/README.md` | `docs/en/README.md` |
| 文档站正文 | `docs/<PAGE>.md` | `docs/en/<PAGE>.md` |
| 下载页 | `docs/download.md` | `docs/en/download.md` |

- 中文是默认语言，写在 `README.md` 和 `docs/README.md`
- 仓库根的英文 README 用 `README.en.md`，不使用 `README_EN.md`、`README_CN.md` 或 `README.zh-CN.md`
- 文档站内不再用 `*.zh-CN.md` / `*.en.md` 后缀或 `docs/zh-CN/` 目录：中英分别由
  `docs/` 与 `docs/en/` 两个平行目录承载，同名页一一对应
- README 顶部加语言切换行（根 README 指向 `README.en.md`）：

  ```markdown
  **语言 / Language:** 中文 · [English](README.en.md)
  ```

## 保留原名的文件

上面的命名约定用于 README 和手写文档。`CHANGELOG.md`、`THIRD_PARTY_NOTICES.md`、`LICENSE`、`SECURITY.md` 等文件保留原名和原始语言，翻译副本可用 `.zh-CN.md` / `.en.md`。

例如 Graf 的英文 `CHANGELOG.md` 由 release-please 维护，中文翻译另存为 `CHANGELOG.zh-CN.md`。包管理器、许可证扫描器或 GitHub 按固定路径读取的文件也按此处理。

## 下载页

`update` 会同步以下文件。项目自己的配置放在 download-page.json，避免修改脚本后被覆盖。

| 文件 | 作用 |
| :-- | :-- |
| `.github/scripts/update_download_page.py` | 生成中英两份下载页，两页共用同一份资产表 |
| `.github/workflows/update-download-page.yml` | `release: published` 时调用上面的脚本，无变化不提交 |

两个文件都带 marker，便于机器识别与批量校验：

```
# docsite-managed-file: update_download_page.py
# docsite-managed-version: 1
```

### 项目配置

路径固定为 `.github/scripts/download-page.json`：

```json
{
  "displayName": "DAViewer",
  "previewFile": "docs/download-preview.md",
  "linkBase": ""
}
```

- `displayName`：页面标题里的产品名，默认取仓库名（仅当仓库名与产品显示名不一致时才需要）
- `previewFile`：手写预览片段，存在时注入第一语言页（默认中文，放应用截图等）
- `previewFiles`：按语言指定预览片段，如 `{"en":"docs/en/download-preview.md"}`；对应语言优先使用这份文件
- `linkBase`：v2 使用 `""`，由 VitePress base 处理仓库子路径；`"/docs"` 仅适用于旧 v1 拼接发布，迁移时会清空
- `languages` / `outputs`：默认 `["zh","en"]` 与固定路径；自定义路径必须同时满足页面互链与导航，缺翻译页时构建会因 dead link 失败
- `trackPrerelease`：默认 `false`，pre-release 不覆盖 stable 页面
- `docsWorkflow`：刷新 workflow 提交后要 dispatch 的 Pages workflow 名，默认 `docs.yml`

### 指定版本和检查更新

ReleaseGraph 可以传入具体 tag。使用 GITHUB_TOKEN 创建 Release 时，需要主动调用 workflow，不能依赖 `release: published` 触发后续任务。

```bash
python3 .github/scripts/update_download_page.py owner/project --tag v1.2.3   # 精确版本
python3 .github/scripts/update_download_page.py owner/project --language en  # 只出英文页
python3 .github/scripts/update_download_page.py owner/project --check        # 页面 tag vs 最新 stable
```

生成页会记录 tag，如 `<!-- docsite-release-tag: v1.2.3 -->`。`--check` 返回 `OK / STALE / MISSING / DRIFT`。旧 tag 的任务晚到时不会覆盖较新的页面，除非使用 `--force`。

更新 workflow 支持 `workflow_dispatch` 的 tag 输入和 `release: published`。提交下载页后，它会主动触发文档构建，因为 GITHUB_TOKEN 的 push 不会触发 push 型部署。

### 下载页内容约定

每个仓库都要有 `docs/download.md` 与 `docs/en/download.md`：

- 有二进制产物：按平台列表格，链接用 `releases/latest/download/<asset>`，并列出 `SHA256SUMS`
- 通过 npm、PyPI 或 Cloudflare Worker 发布：列出安装命令与注册表入口
- 页面顶部给 Releases 与 CHANGELOG 链接

## 部署 workflow

v2 生成 `.github/workflows/docs.yml`：Node 22 → npm ci → npm run docs:build → 上传 docs/.vitepress/dist → Pages。要求：

- 只保留一个 Pages 部署 workflow，避免重复部署
- 触发分支与 `.docsite.json` 的 `branch` 一致
- `public/.nojekyll` 保留在 dist；根级 Markdown 不会自动纳入站点

`init` / `update` 发现其它 Pages workflow（如 static.yml）时，会跳过 docs.yml。

迁移时旧 static.yml 会被备份并停用。迁移报告会列出它额外拷贝的目录；如果还要发布这些内容，需要单独处理。

### 更新 Actions 版本

v2 的模板是 `template/.github/workflows/docs.yml`，v1 的模板是 `template/docs.yml`。修改对应模板，再到各仓库运行 `update`。直接修改生成的 docs.yml 会被下次 update 覆盖。

## 包管理器页面（npm / PyPI）

npm 和 PyPI 页面沿用中文 README，开头放英文链接。

| 面 | 语言 |
| :-- | :-- |
| `README.md` 正文（GitHub / 文档站） | 中文默认 + English 入口 |
| npm 包页面 | 中文（npm 直接渲染仓库根的 `README.md`，不做重定向） |
| PyPI 项目页（`pyproject.toml` 的 `readme`） | 继续指向 `README.md` |
| `description` / `keywords` | 英文（面向检索的元数据，与正文语言不冲突） |

`pyproject.toml` 的 `readme` 继续指向 README.md。若包页面需要英文介绍，在发布流程中另行处理。
