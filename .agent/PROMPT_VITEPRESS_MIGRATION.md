# 实施提示词 — docsite V2:Docsify → VitePress 引擎迁移

> 本文档是给执行代理的完整任务指令,自包含;按阶段顺序执行,每阶段验收后再进下一阶段。工作区上下文见同目录 STATUS/PLAN/TASKS/DECISIONS/HANDOFF/LESSONS/AUDIT。

## 0. 角色与总目标

你在 `redtidev1918/docsite` 仓库内工作(本地路径以会话为准,git 默认分支 `main`)。任务:把 docsite 从「零依赖 Docsify 脚手架」迁移为「轻量级开源项目文档网站生成器」——**渲染引擎由 Docsify 换成 VitePress,docsite 保持 Python CLI 管理层定位**。

一句话分工:**VitePress 管网站(渲染/路由/主题/搜索/导航),docsite 管工程(init/update/check/navcheck/migrate/build/preview、配置、下载页、质量检查),GitHub Pages 管托管。**

绝对禁止:
- 维护自制前端主题(不写自定义 CSS 主题体系;仅允许极少量 CSS 变量级微调,如品牌色)
- 复制 Docsify vendor、保留手写 `index.html` 外壳、手写导航/搜索组件
- Python 里做 Markdown 渲染、HTML 生成或资源打包(构建一律调用 VitePress CLI)
- 引入 Algolia 或任何外部搜索服务
- 迁移过程中静默覆盖或删除任何用户内容
- 自动合并 PR、自动批量迁移业务仓库

## 1. 仓库现状(2026-10-30 审计结论,执行前可复核)

- 生成器 `docsite.py`(~675 行,纯标准库):`init` / `update` / `check` / `navcheck` 四个子命令。
- **文件管辖**(必须延续的契约):
  - 托管·渲染:`<shell>/index.html`、`.github/workflows/docs.yml`(模板 `@@TOKEN@@` 渲染,update 总是覆盖)
  - 托管·逐字节:`download-page.py`→`.github/scripts/update_download_page.py`、`update-download-page.yml`(SYNCED,check 按字节比对)
  - 托管·复制:`assets/vendor/*`、`.nojekyll`
  - **用户内容(update 永不覆盖):`docs/{_sidebar,README,QUICKSTART,download}.md` 及 `docs/en/` 同名**
  - 仓库自有:`.docsite.json`、`.github/scripts/download-page.json`
- 外壳两种形态:新 `docs/index.html`;旧 `.github/pages/`(static.yml 拼接 `_site` 发布,NekoTime/ludum/paranote/pixiv-token-getter/telepress)。
- `.docsite.json` 现有字段:`repo/name/emoji/description/branch/themeKey/version:1` + 可选 `navigation{allowSidebarAnchors,allowCombinedLocales}`(白名单校验)。
- `render()` 做 `@@TOKEN@@` 正则替换,**无转义**——新配置值必须先白名单校验再进模板(D-005)。
- `write_file()` 已用 `newline=""` 保证跨平台 LF 字节稳定;SYNCED 字件依赖字节一致。
- navcheck 现有 Docsify 专属规则(`GLOBAL_SIDEBAR_ALIAS`、`HEADING_INJECTION`)在 VitePress 下**退役**,规则表需重写而非保留。
- 测试:`tests/test_download_generator.py`(13 例,hermetic `--input-json`,断言下载页文案结构如 `## 最新版本:\`v1.2.3\``、`Linux · x64`、`<!-- docsite-release-tag: … -->`)+ `tests/test_shell_dir.py`(6 例,外壳形态/alias 红线/published_paths)。
- 下载页链路:`release: published` → `update_download_page.py` 生成双语页(stale-write 防护 + `--check`)→ 显式 dispatch `docs.yml`(GITHUB_TOKEN push 不触发 push 型部署,必须保留)。
- 决策历史:D-001~D-008 已废止/归档(自研主题两轮成果在 `archive/docsify-custom-theme` 分支,仅供参考);**现行决策是 D-009(本迁移)**;D-004(只改模板源)、D-005(配置向后兼容)继续有效。

## 2. 目标架构与仓库结构

```
docsite/
├── README.md / README.en.md        (中英文档,内容定位需更新)
├── pyproject.toml                  (可选,便于 pipx/依赖元数据)
├── docsite.py                      (CLI:init/update/check/navcheck/migrate/build/preview/dev)
├── .agent/                         (既有工作区,持续维护)
├── template/
│   ├── package.json                (devDependencies: vitepress 固定版本)
│   ├── package-lock.json           (提交,保证 npm ci 可重复)
│   ├── .gitignore                  (node_modules、dist)
│   ├── .github/workflows/docs.yml  (Node 22 构建 + Pages 部署)
│   └── docs/
│       ├── .vitepress/
│       │   ├── config.mts          (@@TOKEN@@ 渲染:base/title/locales/search)
│       │   └── sidebar.generated.mjs(由 update 从 _sidebar.md 生成,带托管标记)
│       ├── public/.nojekyll
│       ├── README.md QUICKSTART.md download.md _sidebar.md
│       └── en/README.md en/QUICKSTART.md en/download.md en/_sidebar.md
├── docs/                           (本仓库自身内容,迁移后同结构)
└── tests/                          (现有 + test_vitepress_config/test_migration/test_build)
```

不再存在:自制 `index.html`、`assets/vendor/`(docsify/search/主题 CSS)、主题 JS。本仓库现有的 `docs/index.html`、`docs/assets/` 属于托管文件,`migrate` 时按标记备份后清理。

## 3. 分阶段任务(每阶段有硬验收)

### 阶段 1 — VitePress 基础集成(最高优先级)

1. `template/package.json`:`"devDependencies": {"vitepress": "<锁定版本>"}` + `"scripts": {"docs:dev": "vitepress dev docs", "docs:build": "vitepress build docs", "docs:preview": "vitepress preview docs"}`;本地 `npm install` 生成并提交 `package-lock.json`;实际版本号写入 `.docsite.json` 的 `engineVersion`(不写 `1.x` 这种模糊值)。
2. `template/docs/.vitepress/config.mts`(模板文件,含托管标记注释):`base` 用 `@@BASE@@` token 由仓库名渲染(`/<repo>/`,根域名站点为 `/`);`title`/`description` 用现有 token;默认主题 + 亮暗(`appearance` 默认随系统)+ `local search`;`locales` 骨架先就位(root zh-CN);`rewrites` 见阶段 2;忽略 `**/_sidebar.md` 不作为页面(srcExclude)。
3. `template/.github/workflows/docs.yml` 改造:保留现有 triggers/permissions/concurrency/environment 结构,steps 改为 checkout → setup-node@v6(node-version: 22, cache: npm)→ configure-pages → `npm ci` → `npm run docs:build` → upload-pages-artifact(path: `docs/.vitepress/dist`)→ deploy-pages。`public/.nojekyll` 保证 Jekyll 跳过。**下载页 workflow 对 docs.yml 的显式 dispatch 链路必须原样可用。**
4. docsite 自身试验田:在 feature 分支对本仓库接入上述结构(内容先双轨并存,新构建通过后再清理旧 Docsify 文件)。
5. 验收:`npm run docs:build` 成功;本地 `vitepress preview` + 真实浏览器确认首页/文档/亮暗/搜索可用;以子路径 base(模拟 `/<repo>/`)预览验证无资源 404。

### 阶段 2 — 兼容现有文档规范

1. `rewrites: { 'README.md': 'index.md', 'en/README.md': 'en/index.md' }`——首页内容源仍是 `docs/README.md` / `docs/en/README.md`,访问 `/` 与 `/en/`。
2. **Sidebar 转换器**(Python,docsite.py 内):解析 `_sidebar.md`(现有 `_sidebar_items()` 可复用),生成 `sidebar.generated.mjs`,结构:

   ```js
   // docsite: managed file — generated from _sidebar.md, do not edit.
   export default { '/': [{ text: '开始', items: [{ text: '概览', link: '/' }, …] }], '/en/': […] }
   ```

   - 保留分类、顺序、两级缩进;链接目标去掉 `.md` 后缀转 VitePress 路径(`/QUICKSTART.md`→`/QUICKSTART`);外部链接保留。
   - `config.mts` 动态 import 该文件;`init`/`update` 时重新生成;用户永远只维护 `_sidebar.md`。
3. `locales`:root(zh-CN)与 en(`link: '/en/'`);各语言 `label` 用于右上角切换;`docOptions`/`outline`/`nav` 按默认主题配置;中英文 nav 顶部各含「首页/下载/GitHub」。
4. 语言切换对照:VitePress locales 自带切换回对应路径,行为符合「优先对应翻译页」;不需要额外代码,但要在验收里验证。
5. 下载页生成器**原样保留**;检查其输出链接(`releases/latest/download/...`、页面互链 `{base}/en/download.md` → 需调整为无 `.md` 的路由或保留 .md 均可,以 VitePress 实际行为为准并在 tests 钉住)。
6. navcheck 升级:规则表重写——保留「语言是站点维度、根 sidebar 不混 /en/ 树、无重复链接、链接指向真实页面(改为校验 docs/ 下文件存在)、.docsite.json navigation 白名单」;Docsify 专属(alias/subMaxLevel/published_paths 壳形态)退役;sidebar 校验对象改为 `_sidebar.md` ↔ 生成文件一致性。
7. 验收:现有 zh/en Markdown 不改内容即可正确展示;中英侧边栏独立正确;`check`/`navcheck` 对 docsite 自身全绿。

### 阶段 3 — 迁移与升级管理

1. `migrate [路径] [--dry-run]`:
   - 检测旧形态(`docs/index.html` 或 `.github/pages/index.html` 含 docsite 托管标记)。
   - `--dry-run`:只打印将新增/修改/备份/删除的文件清单,不写盘。
   - 执行:备份受管 Docsify 文件(`*.docsite.bak`,沿用 init 的既有惯例)→ 写入 VitePress 结构(package.json/config/sidebar/workflow)→ 扫描并改写正文与导航中的 `#/` Hash 链接为路径链接 → 生成新 `.docsite.json` 字段(`engine/engineVersion/version: 2`,保留原有字段)。**失败时不清删任何原文件;旧文件清理只在构建成功后作为独立步骤提示用户确认。**
2. 旧 `static.yml` 识别:含 upload-pages-artifact/deploy-pages 即为 Pages 部署;检测其是否还拷贝 docs 之外的目录(解析 `cp -R`),报告用途,**不自动删除**;新旧 workflow 禁止同时生效(沿用 `other_pages_workflow()` 逻辑,迁移时二选一)。
3. `update` 语义扩展:托管清单加入 `package.json`(锁定版本下发)、`config.mts`、`docs.yml`、生成 sidebar;仍永不覆盖用户 Markdown;npm 依赖版本升级 = 改模板 package.json + 各仓库 update + npm install 更新 lock(文档写明)。
4. `check` 扩展:SYNCED 下载链路照旧;新增 lock 文件存在性、`sidebar.generated.mjs` 与 `_sidebar.md` 一致性(重新生成后 diff)、config.mts 渲染 token 无残留。
5. `build`/`preview`/`dev`:包装 `npm run docs:*`(检测 Node 环境,缺失时给出清晰指引),不重复实现。
6. 验收:对一个旧壳仓库(可临时构造 fixture)跑 `migrate --dry-run` 输出合理;执行后 build 成功、diff 可审查、`.docsite.bak` 存在、可回滚(git checkout 即回)。

### 阶段 4 — 完整质量门禁

- Python:`python -m unittest discover -s tests` 全绿(保留并迁移现有断言;新增 test_vitepress_config / test_migration / test_build——build 类测试在无 Node 环境时 skip 并明示)。
- `vitepress build` 对 docsite 自身零 dead link(zh+en)。
- 下载页端到端:release 事件 → 生成 → dispatch → 部署(CI 或本地模拟)。
- 子路径:以 `base: '/PixivFlow/'` 形态构建预览,资源无 404。
- 浏览器验收(必须真实渲染截图,存 `.agent/shots/`):首页、普通文档页、长代码页、长表格页、下载页、英文页 × 亮/暗 × 1440/1024/390(320–430 无整体横向滚动)。
- 产出视觉验收结论写入 HANDOFF;不允许以「CI 绿」代替「看过真实网站」。

### 阶段 5 — 发布与逐步迁移

1. 中英文档全面更新:README(定位改为「文档网站生成器」,去掉「零构建」表述,写明 Node 22 + npm ci 前提)、QUICKSTART、CONVENTIONS(托管文件表)、NAVIGATION(navcheck 新规则)、UPGRADE(update 新语义 + migrate 指南)。
2. docsite 自身切换 VitePress 上线 Pages(先 feature 分支验证,PR 合并)。
3. 试点一个业务仓库 → 验收 → 再逐个迁移 PixivFlow/DAViewer/TelePost 等;每仓库独立 PR、diff 可见可控。
4. 最终交付 PR(不自动合并);报告:架构变化、功能对照、测试结果、兼容风险、回滚方案、下游迁移顺序建议。

## 4. 全程约束(每阶段都适用)

1. 托管文件一律带标记(`docsite: managed file` 注释或 marker),`is_managed()` 惯例延续。
2. 用户 Markdown(`_sidebar.md`、README、QUICKSTART、download.md 及 en 镜像)永不静默覆盖/删除;备份先于清理。
3. `.docsite.json` 白名单校验 + 默认值;v1 旧配置在 migrate 之前必须继续被现有命令支持(向后兼容)。
4. 渲染 token 进入模板前校验(base 由 repo 推导;禁止把未校验的用户字符串拼进 config.mts 的 JS 上下文,必要时 json.dumps 转义)。
5. 提交遵循 conventional commits,按阶段分组;每阶段结束更新 `.agent/`(STATUS/TASKS/HANDOFF),重大取舍写 DECISIONS。
6. 遇到与本文档冲突的仓库现实,以「不破坏用户内容、可回滚、可审查」为最高原则,并在 HANDOFF 记录偏差与理由。

## 5. 完成定义

PLAN v2 五阶段全部验收通过;docsite 自身站点运行在 VitePress + GitHub Pages(子路径正确);`migrate` 可将旧 Docsify 仓库安全迁移;中英文档同步;PR 就绪待所有者审查。
