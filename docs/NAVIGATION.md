# 导航契约

**语言 / Language:** 中文 · [English](/en/)

## 哲学

> 导航按用户任务组织，而不是按仓库文件结构组织。
> 语言是站点维度，不是导航分类。
> 首页负责介绍和分流；侧边栏负责页面导航；页内目录负责当前页面结构。
> 三者不要互相复制。

核心一句话：**Sidebar is navigation, not a table of contents.**

## 职责分离

| 层 | 职责 | 不负责 |
| :-- | :-- | :-- |
| 首页（`docs/README.md` / `docs/en/README.md`） | 项目是什么、适合谁、主要入口、下载按钮 | 不充当全站目录 |
| 侧边栏（`docs/_sidebar.md` / `docs/en/_sidebar.md`） | 导航**独立页面** | 不收录首页页内锚点 |
| 页内目录 | 当前页的标题结构 | 不替代分类导航 |

README 新增 FAQ / Roadmap / Acknowledgments 等 section **不**意味着侧边栏要同步出现；
只有它成为独立文档页面时才考虑加入。

## 可检查的 invariant（`docsite.py navcheck`）

| # | 规则 | 级别 |
| :-- | :-- | :-- |
| 1 | 根 sidebar 不包含 `/en/` 文档树（语言是站点维度）；指向仅有英文版的页面时，标注「（英文）」的单条 fallback 链接允许 | error `COMBINED_LOCALES` |
| 2 | `docs/en/` 有页面时，`docs/en/_sidebar.md` 必须存在 | error `EN_SIDEBAR_MISSING` |
| 3 | sidebar 不含页内锚点（`#` 链接） | error `ANCHOR_LINK` |
| 4 | 同一目标在同一 sidebar 不得重复 | error `DUPLICATE_LINK` |
| 5 | 顶级分类通常至少 2 个页面（语言入口「中文 / English」这类分类不在此列） | warning `SINGLE_PAGE_CATEGORY` |
| 6 | 本地链接用根绝对路径 | warning `NOT_ROOT_ABSOLUTE` |
| 7 | 英文 sidebar 指向中文页面必须标注（中文）：逐条标注，或整类挂在「中文 / Chinese」分类下 | warning `EN_SIDEBAR_ZH_LINK` |
| 8 | sidebar 链接必须指向站点里真实发布的页面（按发布布局判定：新形态站点根是 `docs/`，壳形态是 `.github/pages` + 根 `*.md` + `docs/`） | error `BROKEN_SIDEBAR_LINK` |

error 影响退出码；warning 只提示（比如项目正在扩展分类，单页面分类是过渡状态）。
「分类名字好不好」这类主观判断**不**自动检查。

英文前缀跟着布局走：新形态是 `/en/…`，`.github/pages` 壳形态（`static.yml` 拼接发布）
的英文页在 `/docs/en/…`；指向仓库根的 `README.en.md` 这类 `.en.md` 文件同样算英文内容。

## 默认信息架构

中小型项目（少于约 8~10 个独立页面）用 2~4 个分类，常用页面 1 次点击可达，最多 2 层：

```text
开始            概览 / 下载 / 快速开始
使用与配置      认证、网络、配置、命令行、故障排查……
开发            架构、API、适配器、构建、发布……
项目            参与贡献 / 安全 / 合规（仅当存在独立页面时才出现）
```

- 不要求四组全有，禁止为模板完整创建空壳页面
- 分类命名用任务型词汇（开始 / 使用与配置 / 开发 / 项目；
  Getting Started / Usage & Configuration / Development / Project），
  避免「基础信息」「技术资料」「其他」这类模糊词
- 页面标题要比分类更具体（`开发 → 架构说明`，不是 `开发 → 开发`）
- 首页在 sidebar 里叫「概览」（Overview），不叫「文档中心」，因为用户已经在文档站里
- 下载只保留一个 sidebar 入口（`开始 → 下载`）；首页可以再有下载按钮，这不算重复
- sidebar 不是网站地图：CHANGELOG、LICENSE、SECURITY、内部 notes 是否进入取决于
  是否需要经常导航，文件存在 ≠ 必须出现在 sidebar

## 语言侧边栏与 docsify

- 每种语言一套 sidebar：`docs/_sidebar.md`（中文）与 `docs/en/_sidebar.md`（英文），
  各自只显示当前语言
- 语言切换放在**页面顶部**，子页面优先指向对应翻译页
  （`/authentication.md ↔ /en/authentication.md`）；无对应翻译时回到该语言首页；
  不要把语言切换塞进 sidebar 分类树
- 英文 sidebar 不放「伪英文入口」；确需 fallback 时必须标注（中文）/ Chinese only

docsify **原生按页面所在目录取 `_sidebar.md`**：根页面读 `/_sidebar.md`，`/en/` 页面读
`/en/_sidebar.md`。两种侧边栏都存在时**不需要 alias**。实测注意两个坑：

- 不要配置 `/.*/_sidebar.md` 之类的通配 alias「统一侧边栏」：docsify 先对 sidebar 请求路径
  （`/en/_sidebar.md`）做 alias 改写再取文件，通配规则会把英文页面静默改写回中文侧边栏
  （且 `/en/.*/_sidebar.md` 这类模式匹配不到 `/en/_sidebar.md` 本身，救不回来）
- 外壳不要配置 `subMaxLevel` / `maxLevel`：它们会把**当前页面的标题**动态注入 sidebar 渲染，
  等于把页内目录塞回导航里。需要页内目录时，在页面正文中自建 TOC 段落

## 显式例外

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
`NAVIGATION_SCHEMA`（error）拒绝；例外是仓库声明自己的能力边界，不是万能逃生口，
不允许长出 `ignoreEverything` 之类的字段。

## CI gate

本仓库的 `.github/workflows/navcheck.yml` 每周与相关文件变更时，对全部受管仓库运行
`docsite.py navcheck --all`，红即契约被破坏。

> `docsite.py navcheck --all` 全绿，表示所有受管仓库满足 canonical 导航结构约束；
> 任何结构性例外必须由仓库通过 `.docsite.json` 显式声明，checker 不允许静默兼容。

## 特殊规范文件

沿用「机器生成 / 合规 / 行业约定文件」例外：`CHANGELOG.md`、`LICENSE`、
`THIRD_PARTY_NOTICES.md`、`SECURITY.md` 等的 canonical path 不因导航或语言目录规约被机械移动；
如需导航，直接链接即可。
