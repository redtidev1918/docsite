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
  这是有意保留的特例，不是技术债；强行把中文设为主文件会让 release-please
  反向破坏发布自动化，任何「清理」这类文件的 PR 都应拒绝。
- 判定口径：若一个文件的「正确文件名」由某个工具（release-please、许可证扫描器、
  GitHub 内置功能）按字面约定读取，它就属于本例外；只有纯给人看的页面才受命名规范约束。

## 一次性与阶段文档生命周期

仓库根目录、`docs/` 用户文档区和 Agent 规范区**只放长期有效内容**。一次性报告、
阶段快照、交接/状态文、审计/验证结果不是长期记忆，默认不允许进入仓库。

| 类别 | 位置 | 生命周期 |
| :-- | :-- | :-- |
| 用户文档 | `docs/`（用户文档站）/ 根 README | 持续更新，旧页面原地覆盖，不叠加 `-v2/-final/-postfix` 副本 |
| 决策/证据记录 | `docs/architecture/`、`docs/adr/`、`docs/incidents/` | 保持不可变记录，Status 写当前状态，完成后如实标记，不删除事实 |
| 一次性/阶段文档 | 工作区归档或 `docs/archive/` | 任务完成后删除；确需保留时进 `docs/archive/` 并带生命周期块 |

### 默认纪律

1. **任务完成后丢弃**：一次性报告、阶段状态、交接快照、dry-run/审计输出默认不进仓库，
   保留在工作区临时目录或任务记录中；无长期用途的完成任务后直接删除。
2. **现状文档原地更新**：`current-state`、roadmap 状态、发布门禁等阶段信息只维护唯一
   当前文件；禁止通过新增 `*-2026-09-12.md`、`*-final.md`、`*-postfix.md` 之类文件保存阶段。
3. **确需保留时归档**：取证、ADR、事故记录、已完成但仍有参考价值的设计稿放到
   `docs/archive/`（无文档站的仓库也可用根 `archive/`），不进入用户侧边栏。
4. **归档文件必须有生命周期块**，便于索引和自动化清理：

   ```markdown
   <!-- doc-lifecycle: archive -->
   Doc-Type: phase-report        # one-off | phase-report | audit | incident | handoff | runbook | decision | evidence
   Status: complete              # complete | superseded | archived
   Effective: 2026-09-12
   Expires: 2027-09-12
   Superseded-By: docs/README.md # 可选，指代当前事实源
   ---
   ```

5. **过期即清理或续期**：`Expires` 已过的归档文件必须删除或更新后再保留；
   `docsite.py lifecyclecheck` 会把过期归档当作 error。

### 机器检查

```bash
python3 /path/to/docsite/docsite.py lifecyclecheck <仓库路径...>
python3 /path/to/docsite/docsite.py lifecyclecheck --all /path/to/code
```

检查项：

| 规则 | 说明 | 级别 |
| :-- | :-- | :-- |
| `ROOT_TRANSIENT_DOC` | 仓库根出现规范白名单之外的 Markdown | error |
| `TRANSIENT_DOC_NOT_ARCHIVED` | 用户文档区出现带日期或 status/handoff/report/dryrun 等信号的文件且未归档 | error |
| `ARCHIVE_METADATA` | 归档文件缺 `Doc-Lifecycle` 块或头部字段非法 | error |
| `ARCHIVE_EXPIRED` | 归档文件 `Expires` 已过 | error |
| `ARCHIVE_IN_SIDEBAR` | 归档内容被放进用户侧边栏 | error |

本仓库的 `.github/workflows/doclifecycle.yml` 每周及规范变更时对全部受管仓库运行该检查；
其余仓库接入时直接使用同一个 `docsite.py lifecyclecheck` 即可。

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

**为什么要托管**：此前 6 个仓库各存一份手改副本，行数 146–149、md5 全不相同，而且
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
事件，因为 GITHUB_TOKEN 创建的 Release 不会级联触发事件：

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
`static.yml`。**两者内容等价，不要为了统一而改名**（改名会打断 Pages 的部署环境与权限绑定）。
要求：

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
