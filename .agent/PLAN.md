# PLAN v2 — 引擎迁移:Docsify → VitePress(docsite V2)

> 2026-10-30 所有者定案(D-009),取代原「视觉设计升级」计划。任务拆解见 [TASKS.md](TASKS.md);执行提示词见 [PROMPT_VITEPRESS_MIGRATION.md](PROMPT_VITEPRESS_MIGRATION.md)。

## 定位

docsite 不再是「Docsify 主题美化工具」,而是**轻量级开源项目文档网站生成器**:Python CLI 管理层 + VitePress 渲染引擎 + GitHub Pages 托管。

- **VitePress 负责:** 渲染、路由、默认主题(亮暗)、本地搜索、locales、页面目录、代码复制。
- **docsite 负责:** init/update/check/navcheck/migrate/build/preview、`.docsite.json` 配置、`_sidebar.md` → sidebar 配置转换、下载页生成链路、模板下发与质量检查。
- **不做:** 自制前端主题、复制 vendor、手写导航组件、Algolia 等外部搜索。

## 关键设计

| 项 | 方案 |
| --- | --- |
| 首页 | `rewrites: {'README.md': 'index.md', 'en/README.md': 'en/index.md'}`,内容零改动 |
| 导航 | `_sidebar.md` 是唯一导航源;Python 生成 `.vitepress/sidebar.generated.mjs`(分类/排序/语言隔离) |
| 国际化 | VitePress `locales`(root=zh-CN,en=/en/);子页面优先切到对应翻译页,无翻译回退语言首页 |
| 搜索 | VitePress 内置 local search |
| 子路径 | `base` 由 `.docsite.json` 仓库名动态渲染,绝不写死 `/` |
| 部署 | Node 22 + `npm ci`(锁 package-lock.json)+ `vitepress build` → `docs/.vitepress/dist` → Pages;保留权限/并发/触发分支/下载页显式 dispatch |
| 配置 | `.docsite.json`:`engine: "vitepress"`、`engineVersion`、`version: 2`;旧配置零修改可用(D-005) |
| 迁移安全 | `migrate --dry-run` 只列文件;执行时备份受管 Docsify 文件;仅清理带托管标记的 `index.html`;旧 `static.yml` 先识别用途再决定去留;失败不删原文件 |

## 五个阶段(每阶段验收后才进下一阶段)

1. **VitePress 基础集成** — 依赖锁定、`config.mts` 模板、默认主题+搜索+亮暗、Pages 构建部署、子路径验证。验收:docsite 自身生成完整 VitePress 站。
2. **兼容现有文档规范** — README rewrites、`_sidebar.md` 转换、locales、下载页生成器保留、navcheck 升级。验收:现有 Markdown 不大规模重写即可正确展示。
3. **迁移与升级管理** — `migrate` 命令、旧文件识别、备份与安全迁移、依赖锁检查、update 不覆盖用户 Markdown。验收:旧项目可安全迁移、可审查、可回滚。
4. **完整质量门禁** — Python 测试、构建测试、中英路由、链接检查、下载页测试、子路径测试、Playwright 截图(首页/文档/长代码/长表格/下载页/英文页/暗色)、移动端 320–430px。验收:以真实生成的网站为准,不以 CI 绿代替。
5. **发布与逐步迁移** — 文档更新(放弃「零构建」表述)、docsite 自身迁移上线、一个业务仓库试点、再逐个迁移 PixivFlow/DAViewer/TelePost 等。验收:无批量部署冲突、不丢历史文档、不破坏下载页。

## 阻断级风险清单

Docsify Hash 路由旧链接(`/#/`)迁移、Markdown 相对链接与资源引用、Pages 子路径 base、`_sidebar.md` 单一来源、首页 rewrites、旧外壳清理需托管标记、旧 `static.yml` 用途识别、package-lock 固定、下载页 dispatch 链路、用户内容永不静默覆盖。

## 历史包袱

- 自研 Docsify 主题(两轮)已归档:`archive/docsify-custom-theme`(db1916f),仅作参考,不再维护。
- 旧壳仓库(`.github/pages/` + static.yml 拼接)由 `migrate` 统一到新结构,不做双引擎长期共存。
