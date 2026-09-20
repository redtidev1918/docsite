# docsite

**零依赖的 docsify 文档站脚手架。**

零依赖的 docsify 文档站脚手架。一个 Python 脚本 + 一份模板，给任何 GitHub 仓库一键长出统一风格的文档站。

线上效果见：[PixivFlow](https://redtidev1918.github.io/PixivFlow/) · [DAKit](https://redtidev1918.github.io/DAKit/) · [DAViewer](https://redtidev1918.github.io/DAViewer/) · [TelePost](https://redtidev1918.github.io/TelePost/) · [ReleaseGraph](https://redtidev1918.github.io/releasegraph/) · [docsite 自己](https://redtidev1918.github.io/docsite/)

规范细节见文档站：<https://redtidev1918.github.io/docsite/>（本仓库自己也是 docsite 站点，
`docs/` 由 `docsite.py init` 生成）。

## 特性

- **纯 stdlib**：只需要 `python3`，不装包、不跑构建
- **只管壳子**：`index.html` / 部署 workflow / docsify 资源由模板托管；Markdown 是你自己的，升级永不覆盖内容
- **自带部署**：生成 GitHub Actions workflow，push `docs/` 即发布到 Pages
- **开箱即用**：明暗主题切换（跟随系统 + 记忆）、全文搜索、emoji favicon、侧边栏
- **子目录统一侧边栏**：`en/` 等子目录页面自动共用根侧边栏，不用每个目录再放一份

## 新项目接入

在**目标仓库根目录**：

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite

python3 /tmp/docsite/docsite.py init \
  --repo owner/name \
  --name 显示名 \
  --emoji 🐱 \
  --branch main
```

| 参数 | 说明 | 默认 |
| :-- | :-- | :-- |
| `--repo` | `owner/name`，必填 | — |
| `--name` | 站点显示名 | 仓库名 |
| `--emoji` | favicon 与站名前的 emoji | 📘 |
| `--description` | 页面 meta description | 「\<name\> 文档中心……」 |
| `--branch` | 触发部署的分支 | `main` |
| `--theme-key` | 主题偏好的 localStorage key | `<name 小写>-theme` |

生成：

```
.docsite.json                 # 本项目的配置（提交进仓库）
.github/workflows/docs.yml    # Pages 部署（托管，别手改）
.github/scripts/update_download_page.py    # 下载页生成器（托管，别手改）
.github/workflows/update-download-page.yml # 发版后刷新下载页（托管，别手改）
docs/
├── index.html                # docsify 外壳（托管，别手改）
├── .nojekyll
├── _sidebar.md               # 侧边栏（你的内容）
├── README.md                 # 中文首页（你的内容）
├── QUICKSTART.md             # 中文示例页（你的内容）
├── download.md               # 中文下载页（你的内容）
├── en/                       # 英文镜像（你的内容，与根同名页一一对应）
│   ├── README.md
│   ├── QUICKSTART.md
│   └── download.md
└── assets/vendor/            # docsify + 主题 + 搜索（托管）
```

推送后 workflow 自动部署；仓库 **Settings → Pages → Source 选 GitHub Actions**（首次一般自动配好）。
站点地址：`https://<owner>.github.io/<name>/`（`<name>` 必须用仓库名原样，Pages 路径区分大小写）

## 老项目接入（已经有 docs/ 或文档站）

同样在仓库根跑 `init`，它对老项目有保护：

- 外壳目录自动识别：`docs/index.html` 存在就按新形态托管；只有 `.github/pages/index.html`
  的老仓库（NekoTime / ludum / paranote / pixiv-token-getter / telepress，由 `static.yml`
  把外壳与 `docs/` 内容拼成 `_site`）就把托管外壳、`assets/vendor/` 与 `.nojekyll` 写回
  `.github/pages/`，不会在 `docs/` 里凭空长出一个 `index.html`
- 已有的 `docs/index.html`、`.github/workflows/docs.yml` 如果**不是** docsite 托管文件，会先备份成 `*.docsite.bak`，不静默覆盖
- 检测到别的文件名的 Pages workflow（如 `static.yml`）只提示不删除
- 已有的 Markdown（`README.md`、`_sidebar.md` 等）一律不动

步骤：

```bash
# 1. init（参数见上）
python3 /tmp/docsite/docsite.py init --repo owner/name --name 显示名 --emoji 🐱

# 2. 检查差异与备份
git status
#    - 核对 docs/index.html.docsite.bak（旧站若有自定义，把必要内容并回模板配置）
#    - 旧部署 workflow（如 static.yml）确认 docs.yml 部署成功后删除，避免重复部署

# 3. 侧边栏约定：链接写「根绝对路径」，子目录页面才能跳对
#    [架构](/ARCHITECTURE.md)   ✅
#    [架构](ARCHITECTURE.md)    ❌ 在 zh-CN/ 子页面会 404

git add -A && git commit -m "docs: 接入 docsite" && git push
```

> Jekyll / mkdocs 等其他构建迁过来：内容文件保留，删掉对应的构建配置（`_config.yml`、`mkdocs.yml` 等）和旧 workflow 即可，新方案不需要构建。

## 日常更新文档（最常用）

不用再跑脚本，直接改 Markdown：

1. 往 `docs/` 加 / 改 `.md` 文件
2. 在 `docs/_sidebar.md` 里加链接（根绝对路径：`- [标题](/PAGE.md)`）
3. `git commit && git push`——workflow 监听 `docs/**` 变化，一两分钟后线上更新

具体命名与目录规范见下节。

## 统一文档规范（本账号约定）

`docsite` 生成的结构默认遵循以下规范，本账号下所有仓库的文档都以它为准，避免各写各的。

### 语言与文件命名

| 位置 | 中文（默认） | 英文 |
| :-- | :-- | :-- |
| 仓库根 README | `README.md` | `README.en.md` |
| 文档站首页 | `docs/README.md` | `docs/en/README.md` |
| 文档站正文 | `docs/<PAGE>.md` | `docs/en/<PAGE>.md` |
| 下载页 | `docs/download.md` | `docs/en/download.md` |

- **中文是默认语言**：`README.md`、`docs/README.md` 一律写中文
- **英文统一用 `.en.md` 点号后缀**，禁止 `README_EN.md`、`README_CN.md`、`README.zh-CN.md`
- 文档站内禁止再用 `*.zh-CN.md` / `*.en.md` 后缀或 `docs/zh-CN/` 目录：中英分别由 `docs/` 与 `docs/en/` 两个平行目录承载，同名页一一对应
- README 顶部加语言切换行（根 README 指向 `README.en.md`）：

  ```markdown
  **语言 / Language:** 中文 · [English](README.en.md)
  ```

### 明确例外：机器生成 / 合规 / 行业约定文件

以上命名规范只约束 **README 与人工维护的 docs 内容**。机器生成、行业约定或合规类文件
（如 `CHANGELOG.md`、`THIRD_PARTY_NOTICES.md`、`LICENSE`，以及 `SECURITY.md` 等受工具链
约束的文件）**允许保留 canonical 文件名和原始语言**；翻译副本可使用 `.zh-CN.md` /
`.en.md`。**不得为了命名统一破坏生成器、包管理器或合规工具链。**

- 现存特例：`graf` 的 `CHANGELOG.md` 由 release-please 自动维护（英文、标准文件名），
  `CHANGELOG.zh-CN.md` 是中文翻译副本；`THIRD_PARTY_NOTICES.md` /
  `THIRD_PARTY_NOTICES.zh-CN.md` 同理。**这是有意保留的特例，不是技术债**
  ——强行把中文设为主文件会让 release-please 的自动变更日志反向破坏发布自动化，
  任何「清理」这类文件的 PR 都应拒绝。
- 判定口径：若一个文件的「正确文件名」由某个工具（release-please、许可证扫描器、
  GitHub 内置功能）按字面约定读取，它就属于本例外；只有纯给人看的页面才受命名规范约束。

### 侧边栏

`docs/_sidebar.md` 固定两个分组，全部使用**根绝对路径**：

```markdown
- 中文
  - [文档中心](/)
  - [快速开始](/QUICKSTART.md)
  - [📥 下载](/download.md)
- English
  - [Documentation](/en/)
  - [Quick Start](/en/QUICKSTART.md)
  - [📥 Download](/en/download.md)
```

中文页必须全部可导航；英文页未逐条列出时，至少保留 `Documentation`（`/en/`）入口。

### 下载页

每个仓库都要有 `docs/download.md`（中文）与 `docs/en/download.md`（英文）：

- 有二进制产物：按平台列表格，链接用 `releases/latest/download/<asset>`，并列出 `SHA256SUMS`
- 只有包管理器产物（npm / PyPI / Cloudflare Worker）：不编造二进制链接，改列安装命令与注册表入口
- 页面顶部给 Releases 与 CHANGELOG 链接

### 下载页生成链路（托管）

下载页由 `docsite` 统一下发，**不要各仓库自己写、也不要手改**：

| 文件 | 作用 |
| :-- | :-- |
| `.github/scripts/update_download_page.py` | 生成 `docs/download.md`（中）与 `docs/en/download.md`（英），两页共用同一份资产表 |
| `.github/workflows/update-download-page.yml` | 在 `release: published` 时调用上面的脚本，无变化不提交 |

两个文件都带 marker，便于机器识别与批量校验：

```
# docsite-managed-file: update_download_page.py
# docsite-managed-version: 1
```

**为什么要托管**：此前 6 个仓库各存一份**手改副本**——行数 146–149、md5 全不相同，而且**没有任何 workflow 真正调用它**。结果是下载页上「本页由 GitHub Actions 在每次发版时自动更新」是假的，页面长期停在旧版本（例：仓库已发 v1.12.0，页面还写着 v1.11.0）。托管后只需维护一份，`update` 统一下发。

按仓库自定义（**非托管**文件，`update` 不会覆盖）：

```json
{
  "displayName": "DAViewer",
  "previewFile": "docs/download-preview.md",
  "linkBase": ""
}
```

路径固定为 `.github/scripts/download-page.json`：

- `displayName`：页面标题里的产品名，默认取仓库名（仅当仓库名与产品显示名不一致时才需要）
- `previewFile`：手写预览片段，存在时注入第一语言页（默认中文，放应用截图等）
- `linkBase`：页面内互链的站点路径前缀。默认 `""`（Pages 直接上传 `./docs`，`docs/` 就是站点根）；若仓库用「拼接 `_site`」模式并把 `docs/` 作为子目录发布，填 `"/docs"`，否则两语言互链会 404
- `languages` / `outputs`：默认 `["zh","en"]` 与固定路径；只出中文、只出英文、自定义路径都可行
- `trackPrerelease`：默认 `false`，pre-release 不覆盖 stable 页面
- `docsWorkflow`：刷新 workflow 提交后要 dispatch 的 Pages workflow 名，默认 `docs.yml`

**生成器支持精确 tag 与机器校验**（ReleaseGraph post-release action 用它下传 exact tag，
不依赖 `release: published` 事件——GITHUB_TOKEN 创建的 Release 不会级联触发事件）：

```bash
python3 .github/scripts/update_download_page.py owner/project --tag v1.2.3   # 精确版本
python3 .github/scripts/update_download_page.py owner/project --language en  # 只出英文页
python3 .github/scripts/update_download_page.py owner/project --check        # 页面 tag vs 最新 stable
```

每个生成页带机器可读 marker（`<!-- docsite-release-tag: v1.2.3 -->`），`--check` 据此报告
`OK / STALE / MISSING / DRIFT`；**stale-write 防护**保证晚到的旧 tag runner 不会把
已指向新版本的页面回退（`--force` 可显式覆盖）。刷新 workflow 用
`workflow_dispatch`（`tag` 输入）+ `release: published` 兜底，
并在提交成功后显式 dispatch 文档站 workflow（GITHUB_TOKEN 的 push 不会触发 push 型部署）。

**批量校验一致性**（确认没有仓库掉队）：

```bash
python3 docsite.py check --all /path/to/repos   # 扫描该目录下所有 git 仓库
python3 docsite.py check .                      # 只查当前仓库
```

逐文件输出 `ok` / `MISSING` / `DRIFT`；有偏差时到对应仓库跑 `python3 docsite.py update`，看 diff 后提交即可。

### 部署 workflow

`docsite init` 生成 `.github/workflows/docs.yml`。早期接入的仓库沿用了 GitHub 默认模板名 `static.yml`——**两者内容等价，不要为了统一而改名**（改名会打断 Pages 的部署环境与权限绑定）。只需保证：

- 只保留**一个** Pages 部署 workflow，避免重复部署
- 触发分支与 `.docsite.json` 的 `branch` 一致
- 若 workflow 采用「拼接 `_site`」模式（拷贝根级 `*.md` 而非上传 `./docs`），新增的 `docs/en/` 页面需确认已被纳入拷贝范围

已做防护：`init` / `update` 在发现同一目录已有其它 Pages 部署 workflow（如历史 `static.yml`）时，**会跳过托管 `docs.yml`**，不会制造第二个部署流程。

#### Actions 版本的单一事实源

`template/docs.yml` 是**全账号 actions 版本的唯一来源**。当前统一版本：

| Action | 版本 |
| :-- | :-- |
| `actions/checkout` | `v7` |
| `actions/configure-pages` | `v6` |
| `actions/upload-pages-artifact` | `v5` |
| `actions/deploy-pages` | `v5` |

升级 Actions 时**只改这一处模板**，再由各仓库运行 `python3 docsite.py update` 收敛。不要在单个仓库里手改：`docs.yml` 是托管文件，下次 `update` 会把改动覆盖回模板版本，于是同一份版本号在仓库间反复漂移。

### 包管理器页面（npm / PyPI）

**不为注册表页面制造例外。** 统一规则只有一条：`README.md` 永远是中文默认，第一屏给出 English 入口。

| 面 | 语言 |
| :-- | :-- |
| `README.md` 正文（GitHub / 文档站） | 中文默认 + English 入口 |
| npm 包页面 | 中文（npm 直接渲染仓库根的 `README.md`，不做重定向） |
| PyPI 项目页（`pyproject.toml` 的 `readme`） | 继续指向 `README.md` |
| `description` / `keywords` | 英文（面向检索的元数据，与正文语言不冲突） |

不建议把 `pyproject.toml` 的 `readme` 指向 `README.en.md`：那会让「GitHub 中文、PyPI 英文、npm 中文」，规则反而多了一条。如果日后确实要把 **registry-facing docs = English** 做成账号级规范，应当单独设计 npm 的 publish staging，而不是在每个仓库零散加特例。

## 导航与信息架构

**导航哲学（navigation philosophy）**：

> 导航按用户任务组织，而不是按仓库文件结构组织。
> 语言是站点维度，不是导航分类。
> 首页负责介绍和分流；侧边栏负责页面导航；页内目录负责当前页面结构。
> 三者不要互相复制。
>
> Navigation follows user tasks, not repository layout.
> Locale is a site-level dimension, not a navigation category.
> Landing pages orient. Sidebars navigate. In-page TOCs structure the current page.
> Do not duplicate these responsibilities.

核心一句话：**Sidebar is navigation, not a table of contents.**
（侧边栏用于导航文档页面，不用于复刻当前页面的标题目录。）

### 职责分离

| 层 | 职责 | 不负责 |
| :-- | :-- | :-- |
| 首页（`docs/README.md` / `docs/en/README.md`） | 项目是什么、适合谁、主要入口、下载按钮 | 不充当全站目录 |
| 侧边栏（`docs/_sidebar.md` / `docs/en/_sidebar.md`） | 导航**独立页面** | 不收录首页页内锚点 |
| 页内目录（`subMaxLevel` 等） | 当前页的标题结构 | 不替代分类导航 |

README 新增 FAQ / Roadmap / Acknowledgments 等 section **不**意味着侧边栏要同步出现——
只有当它成为独立文档页面时才考虑加入。

### 可检查的 invariant（`docsite.py navcheck`）

| # | 规则 | 级别 |
| :-- | :-- | :-- |
| 1 | 根 sidebar 不包含 `/en/` 文档树（语言是站点维度）；指向仅有英文版的页面时，标注「（英文）」的单条 fallback 链接允许 | error `COMBINED_LOCALES` |
| 2 | `docs/en/` 有页面时，`docs/en/_sidebar.md` 必须存在 | error `EN_SIDEBAR_MISSING` |
| 3 | sidebar 不含页内锚点（`#` 链接） | error `ANCHOR_LINK` |
| 4 | 同一目标在同一 sidebar 不得重复 | error `DUPLICATE_LINK` |
| 5 | 顶级分类通常至少 2 个页面 | warning `SINGLE_PAGE_CATEGORY` |
| 6 | 本地链接用根绝对路径 | warning `NOT_ROOT_ABSOLUTE` |
| 7 | 英文 sidebar 指向中文页面必须标注（中文） | warning `EN_SIDEBAR_ZH_LINK` |

error 影响退出码；warning 只提示（比如项目正在扩展分类，单页面分类是过渡状态）。
「分类名字好不好」这类主观判断**不**自动检查。

### 默认信息架构

中小型项目（少于约 8~10 个独立页面）用 2~4 个分类，常用页面 1 次点击可达，最多 2 层：

```text
开始            概览 / 下载 / 快速开始
使用与配置      认证、网络、配置、命令行、故障排查……
开发            架构、API、适配器、构建、发布……
项目            参与贡献 / 安全 / 合规（仅当存在独立页面时才出现）
```

- 不要求四组全有，禁止为模板完整创建空壳页面
- 分类命名用任务型词汇（开始 / 使用与配置 / 开发 / 项目；Getting Started / Usage & Configuration / Development / Project），避免「基础信息」「技术资料」「其他」这类模糊词
- 页面标题要比分类更具体（`开发 → 架构说明`，不是 `开发 → 开发`）
- 首页在 sidebar 里叫「概览」（Overview），不叫「文档中心」——用户已经在文档站里
- 下载只保留一个 sidebar 入口（`开始 → 下载`）；首页可以再有下载按钮，这不算重复
- sidebar 不是网站地图：CHANGELOG、LICENSE、SECURITY、内部 notes 是否进入取决于是否需要经常导航，文件存在 ≠ 必须出现在 sidebar

### 语言侧边栏与 Docsify

- 每种语言一套 sidebar：`docs/_sidebar.md`（中文）与 `docs/en/_sidebar.md`（英文），各自只显示当前语言
- 语言切换放在**页面顶部**，子页面优先指向对应翻译页（`/authentication.md ↔ /en/authentication.md`）；无对应翻译时回到该语言首页；不要把语言切换塞进 sidebar 分类树
- 英文 sidebar 不放「伪英文入口」；确需 fallback 时必须标注（中文）/ Chinese only
- docsify **原生按页面所在目录取 `_sidebar.md`**：根页面读 `/_sidebar.md`，`/en/` 页面读
  `/en/_sidebar.md`——两种侧边栏都存在时**不需要 alias**。实测注意两个坑：

  - 不要配置 `/.*/_sidebar.md` 之类的通配 alias「统一侧边栏」：docsify 是先对 sidebar
    请求路径（`/en/_sidebar.md`）做 alias 改写再取文件，通配规则会把英文页面静默改写回
    中文侧边栏（且 `/en/.*/_sidebar.md` 这类模式匹配不到 `/en/_sidebar.md` 本身，救不回来）
  - 外壳不要配置 `subMaxLevel` / `maxLevel`：它们会把**当前页面的标题**动态注入 sidebar
    渲染，等于把页内目录塞回导航里。需要页内目录时，在页面正文中自建 TOC 段落

### 显式例外

确需保留页内锚点或单 sidebar 双语的仓库（如 CDN 壳站点、超长单页规范），写入仓库根
`.docsite.json`，检查器不静默忽略：

```json
{
  "navigation": {
    "allowSidebarAnchors": true,
    "allowCombinedLocales": true
  }
}
```

**schema 为白名单制**：`navigation` 下仅允许 `allowSidebarAnchors`、`allowCombinedLocales`
两个字段，且必须为布尔值。未知字段、错误类型、非法 JSON 都会被 `navcheck` 以
`NAVIGATION_SCHEMA`（error）拒绝——例外是仓库声明自己的能力边界，不是万能逃生口，
不允许长出 `ignoreEverything` 之类的字段。

**CI gate**：本仓库的 `.github/workflows/navcheck.yml` 每周与相关文件变更时，
对全部受管仓库运行 `docsite.py navcheck --all`——红即契约被破坏。

**正式治理定义（导航 contract）**：

> `docsite.py navcheck --all` 全绿，表示所有受管仓库满足 canonical 导航结构约束；
> 任何结构性例外必须由仓库通过 `.docsite.json` 显式声明，checker 不允许静默兼容。

### 特殊规范文件

沿用「机器生成 / 合规 / 行业约定文件」例外：`CHANGELOG.md`、`LICENSE`、
`THIRD_PARTY_NOTICES.md`、`SECURITY.md` 等的 canonical path 不因导航或语言目录规约被
机械移动；如需导航，直接链接即可。

## 升级 docsite 模板

模板更新后（换 docsify 版本、改样式、加功能），在每个接入仓库的根目录：

```bash
git -C /tmp/docsite pull          # 更新脚手架本体
python3 /tmp/docsite/docsite.py update
```

`update` 只重写托管部分（`index.html`、`docs.yml`、`assets/vendor/`），按 `.docsite.json` 重新渲染，**Markdown 一律不碰**。看 diff、提交、推送。
在多个仓库批量升级就是在各仓库各跑一次——刻意不做一键全仓升级，让每个仓库的 diff 可见可控。

## 已接入站点的参数参考

| 项目 | 命令要点 |
| :-- | :-- |
| PixivFlow | `--name PixivFlow --emoji 🐱 --branch master --theme-key pf-theme` |
| DAKit | `--name DAKit --emoji 🎨 --theme-key dakit-theme` |
| TelePost | `--name TelePost --emoji 📮 --theme-key tp-theme` |
| releasegraph | `--name ReleaseGraph --emoji 🕸️ --theme-key rg-theme` |

## 非目标

- 不做按语言自动跳转的多语言路由（英文由 `docs/en/` 目录承载，由侧边栏手动导航）
- 不做服务端搜索、不做自定义主题系统
- 不内置"一键批量升级所有仓库"——每个仓库自己跑一次 update，diff 可见可控
