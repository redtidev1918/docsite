# 文件与命名规范

**语言 / Language:** 中文 · [English](/en/)

docsite 生成的结构默认遵循下面这套约定，账号下所有仓库的文档以它为准。

## 语言与文件命名

| 位置 | 中文（默认） | 英文 |
| :-- | :-- | :-- |
| 仓库根 README | `README.md` | `README.en.md` |
| 文档站首页 | `docs/README.md` | `docs/en/README.md` |
| 文档站正文 | `docs/<PAGE>.md` | `docs/en/<PAGE>.md` |
| 下载页 | `docs/download.md` | `docs/en/download.md` |

- **中文是默认语言**：`README.md`、`docs/README.md` 一律写中文
- **英文统一用 `.en.md` 点号后缀**，禁止 `README_EN.md`、`README_CN.md`、`README.zh-CN.md`
- 文档站内不再用 `*.zh-CN.md` / `*.en.md` 后缀或 `docs/zh-CN/` 目录：中英分别由
  `docs/` 与 `docs/en/` 两个平行目录承载，同名页一一对应
- README 顶部加语言切换行（根 README 指向 `README.en.md`）：

  ```markdown
  **语言 / Language:** 中文 · [English](README.en.md)
  ```

## 明确例外：机器生成 / 合规 / 行业约定文件

命名规范只约束 **README 与人工维护的 docs 内容**。机器生成、行业约定或合规类文件
（`CHANGELOG.md`、`THIRD_PARTY_NOTICES.md`、`LICENSE`、`SECURITY.md` 等受工具链约束的
文件）**保留 canonical 文件名和原始语言**；翻译副本可用 `.zh-CN.md` / `.en.md`。

**不得为了命名统一破坏生成器、包管理器或合规工具链。**

- 现存特例：`Graf` 的 `CHANGELOG.md` 由 release-please 自动维护（英文、标准文件名），
  `CHANGELOG.zh-CN.md` 是中文翻译副本；`THIRD_PARTY_NOTICES.md` 同理。
  这是有意保留的特例，不是技术债——强行把中文设为主文件会让 release-please
  反向破坏发布自动化，任何「清理」这类文件的 PR 都应拒绝。
- 判定口径：若一个文件的「正确文件名」由某个工具（release-please、许可证扫描器、
  GitHub 内置功能）按字面约定读取，它就属于本例外；只有纯给人看的页面才受命名规范约束。

## 下载页生成链路（托管）

下载页由 docsite 统一下发，**不要各仓库自己写、也不要手改**：

| 文件 | 作用 |
| :-- | :-- |
| `.github/scripts/update_download_page.py` | 生成中英两份下载页，两页共用同一份资产表 |
| `.github/workflows/update-download-page.yml` | `release: published` 时调用上面的脚本，无变化不提交 |

两个文件都带 marker，便于机器识别与批量校验：

```
# docsite-managed-file: update_download_page.py
# docsite-managed-version: 1
```

**为什么要托管**：此前 6 个仓库各存一份手改副本——行数 146–149、md5 全不相同，而且
**没有任何 workflow 真正调用它**。结果是下载页上「本页由 GitHub Actions 在每次发版时
自动更新」是假的，页面长期停在旧版本（例：仓库已发 v1.12.0，页面还写着 v1.11.0）。
托管后只维护一份，`update` 统一下发。

### 按仓库自定义（非托管文件，`update` 不覆盖）

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
- `linkBase`：页面内互链的站点路径前缀。默认 `""`（Pages 直接上传 `./docs`，`docs/` 就是
  站点根）；若仓库用「拼接 `_site`」模式并把 `docs/` 作为子目录发布，填 `"/docs"`，
  否则两语言互链会 404
- `languages` / `outputs`：默认 `["zh","en"]` 与固定路径；只出中文、只出英文、
  自定义路径都可行
- `trackPrerelease`：默认 `false`，pre-release 不覆盖 stable 页面
- `docsWorkflow`：刷新 workflow 提交后要 dispatch 的 Pages workflow 名，默认 `docs.yml`

### 精确 tag 与机器校验

ReleaseGraph post-release action 用这个能力下传 exact tag，不依赖 `release: published`
事件——GITHUB_TOKEN 创建的 Release 不会级联触发事件：

```bash
python3 .github/scripts/update_download_page.py owner/project --tag v1.2.3   # 精确版本
python3 .github/scripts/update_download_page.py owner/project --language en  # 只出英文页
python3 .github/scripts/update_download_page.py owner/project --check        # 页面 tag vs 最新 stable
```

每个生成页带机器可读 marker（`<!-- docsite-release-tag: v1.2.3 -->`），`--check` 据此报告
`OK / STALE / MISSING / DRIFT`；**stale-write 防护**保证晚到的旧 tag runner 不会把已指向
新版本的页面回退（`--force` 可显式覆盖）。刷新 workflow 用 `workflow_dispatch`（`tag` 输入）
加 `release: published` 兜底，并在提交成功后显式 dispatch 文档站 workflow
（GITHUB_TOKEN 的 push 不会触发 push 型部署）。

### 下载页内容约定

每个仓库都要有 `docs/download.md` 与 `docs/en/download.md`：

- 有二进制产物：按平台列表格，链接用 `releases/latest/download/<asset>`，并列出 `SHA256SUMS`
- 只有包管理器产物（npm / PyPI / Cloudflare Worker）：不编造二进制链接，改列安装命令与注册表入口
- 页面顶部给 Releases 与 CHANGELOG 链接

## 部署 workflow

`docsite init` 生成 `.github/workflows/docs.yml`。早期接入的仓库沿用了 GitHub 默认模板名
`static.yml`——**两者内容等价，不要为了统一而改名**（改名会打断 Pages 的部署环境与权限绑定）。
只需保证：

- 只保留**一个** Pages 部署 workflow，避免重复部署
- 触发分支与 `.docsite.json` 的 `branch` 一致
- 若 workflow 采用「拼接 `_site`」模式（拷贝根级 `*.md` 而非上传 `./docs`），
  新增的 `docs/en/` 页面需确认已被纳入拷贝范围

已做防护：`init` / `update` 发现同一目录已有其它 Pages 部署 workflow（如历史 `static.yml`）
时，**会跳过托管 `docs.yml`**，不会制造第二个部署流程。

### Actions 版本的单一事实源

`template/docs.yml` 是**全账号 actions 版本的唯一来源**。升级时只改这一处模板，
再由各仓库运行 `python3 docsite.py update` 收敛。不要在单个仓库里手改：`docs.yml` 是托管
文件，下次 `update` 会把改动覆盖回模板版本，于是同一份版本号在仓库间反复漂移。

## 包管理器页面（npm / PyPI）

**不为注册表页面制造例外。** 统一规则只有一条：`README.md` 永远是中文默认，第一屏给出
English 入口。

| 面 | 语言 |
| :-- | :-- |
| `README.md` 正文（GitHub / 文档站） | 中文默认 + English 入口 |
| npm 包页面 | 中文（npm 直接渲染仓库根的 `README.md`，不做重定向） |
| PyPI 项目页（`pyproject.toml` 的 `readme`） | 继续指向 `README.md` |
| `description` / `keywords` | 英文（面向检索的元数据，与正文语言不冲突） |

不建议把 `pyproject.toml` 的 `readme` 指向 `README.en.md`：那会让「GitHub 中文、PyPI 英文、
npm 中文」，规则反而多了一条。若日后确实要把 registry-facing docs 做成英文，应当单独设计
npm 的 publish staging，而不是在每个仓库零散加特例。
