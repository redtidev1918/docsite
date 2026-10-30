# 导航规则

**语言 / Language:** 中文 · [English](/en/NAVIGATION.md)

侧边栏按读者要找的内容分组。中文和英文各用一份侧边栏，通过页面顶部的菜单切换语言。

## 首页、侧边栏和页内目录

| 层 | 职责 | 不负责 |
| :-- | :-- | :-- |
| 首页（`docs/README.md` / `docs/en/README.md`） | 项目是什么、适合谁、主要入口、下载按钮 | 不充当全站目录 |
| 侧边栏（`docs/_sidebar.md` / `docs/en/_sidebar.md`） | 链接独立页面 | 不收录首页页内锚点 |
| 页内目录 | 当前页的标题结构 | 不替代分类导航 |

README 里新增 FAQ、路线图或致谢小节时，不用同步添加侧边栏入口；拆成独立页面后再添加。

## navcheck 检查项

| # | 规则 | 级别 |
| :-- | :-- | :-- |
| 1 | 根 sidebar 不包含整组 `/en/` 页面；可以单独链接仅有英文版的页面，并标注“（英文）” | error `COMBINED_LOCALES` |
| 2 | `docs/en/` 有页面时，`docs/en/_sidebar.md` 必须存在 | error `EN_SIDEBAR_MISSING` |
| 3 | sidebar 不含页内锚点（`#` 链接） | error `ANCHOR_LINK` |
| 4 | 同一目标在同一 sidebar 不得重复 | error `DUPLICATE_LINK` |
| 5 | 顶级分类通常至少 2 个页面（语言入口「中文 / English」这类分类不在此列） | warning `SINGLE_PAGE_CATEGORY` |
| 6 | 本地链接用根绝对路径 | warning `NOT_ROOT_ABSOLUTE` |
| 7 | 英文 sidebar 指向中文页面必须标注（中文）：逐条标注，或整类挂在「中文 / Chinese」分类下 | warning `EN_SIDEBAR_ZH_LINK` |
| 8 | v2 sidebar 链接必须对应 docs/ 下真实页面；`/` 对应 README.md、`.md` 后缀转换为 VitePress 路径 | error `BROKEN_SIDEBAR_LINK` |
| 9 | sidebar.generated.mjs 必须与 _sidebar.md 再生成结果一致 | error `SIDEBAR_STALE` |

error 会使命令失败，warning 只提示。分类名称是否合适仍需自己检查。

v2 英文前缀固定为 `/en/…`，用户只维护两种语言的 `_sidebar.md`，修改后运行 update。旧 v1 未迁移时仍按旧发布布局校验；其壳形态英文页在 `/docs/en/…`。

## 分类示例

页面不多时，可以用两到四个分类，最多两层：

```text
开始            概览 / 下载 / 快速开始
使用与配置      认证、网络、配置、命令行、故障排查……
开发            架构、API、适配器、构建、发布……
项目            参与贡献 / 安全 / 合规（仅当存在独立页面时才出现）
```

按已有内容选择分类，不用凑齐四组。名称尽量具体，如“开发 → 架构说明”。首页入口用“概览”，下载页在侧边栏放一处即可。CHANGELOG、LICENSE、SECURITY 等文件按阅读需要添加，不必把仓库里的每个文件都列出来。

## VitePress 语言与侧边栏

- 每种语言一套 sidebar：`docs/_sidebar.md`（中文）与 `docs/en/_sidebar.md`（英文），
  各自只显示当前语言
- 语言切换放在页面顶部，子页面优先指向对应翻译页
  （`/authentication.md ↔ /en/authentication.md`）；无对应翻译时回到该语言首页；
  不要把语言切换塞进 sidebar 分类树
- 英文 sidebar 引用中文页时，标注“（中文）”或 Chinese only

VitePress config 导入生成 sidebar；保留分类、顺序与两级缩进，外链原样保留，Markdown 链接去掉 .md 后缀。README.md 通过 rewrites 成为首页。语言菜单使用 locales；有对应翻译时切到同一页面。应实际检查缺翻译时的回退行为，并补齐正文中的语言链接以避免 dead link。

V2 不再使用 Docsify alias/subMaxLevel，GLOBAL_SIDEBAR_ALIAS 与 HEADING_INJECTION 仅在旧 v1 规则表中保留；页面目录由默认主题 outline 提供。本地搜索不依赖外部服务。

## 配置例外

如果站点需要页内锚点，或需要在同一侧边栏放中英文页面，在 `.docsite.json` 中设置：

```json
{
  "navigation": {
    "allowSidebarAnchors": true,
    "allowCombinedLocales": true
  }
}
```

`navigation` 只接受这两个布尔字段。未知字段、错误类型和非法 JSON 会报 `NAVIGATION_SCHEMA` 错误。

## CI 检查

`.github/workflows/navcheck.yml` 每周及相关文件变更时，对清单中的仓库运行 `navcheck --all`。检查失败时，先看日志中的规则名和文件路径。

## 固定文件名

`CHANGELOG.md`、`LICENSE`、`THIRD_PARTY_NOTICES.md`、`SECURITY.md` 保留原路径，需要导航时直接链接。命名说明见[文件规范](/CONVENTIONS.md)。
