# TASKS — 任务清单(VitePress 迁移)

> 对应 [PLAN v2](PLAN.md) 五阶段。开始一项前把状态改为 `🔄 in_progress`,完成后改为 `✅ done` 并同步更新 [STATUS.md](STATUS.md)。每完成一个阶段在 [HANDOFF.md](HANDOFF.md) 追加交接记录。

**图例:** ⬜ pending · 🔄 in_progress · ✅ done · ⏸ blocked

## 阶段 1 — VitePress 基础集成

- ✅ 1-1 `template/package.json` + 提交 `package-lock.json`(固定 VitePress 版本,记录到 `engineVersion`)
- ✅ 1-2 `template/docs/.vitepress/config.mts` 模板:`base` 动态渲染(仓库名)、默认主题、亮暗、本地搜索、`.nojekyll` 经 `public/` 保留
- ✅ 1-3 `template/.github/workflows/docs.yml` 改造:Node 22 → `npm ci` → `vitepress build` → 上传 `docs/.vitepress/dist`(保留权限/并发/触发分支)
- ✅ 1-4 docsite 自身作为试验田接入(临时双轨:新 workflow 构建验证通过后再切换;旧壳文件已清理)
- ✅ 1-5 本地 `vitepress build` + 真实浏览器验收;子路径下无资源 404(截图补录推迟到阶段 4 视觉门禁)

## 阶段 2 — 兼容现有文档规范

- ✅ 2-1 `rewrites` 实现 `README.md→index.md`、`en/README.md→en/index.md`
- ✅ 2-2 `_sidebar.md` → `sidebar.generated.mjs` 转换器(Python,保留分类/排序/缩进/语言隔离;update 时重新生成)
- ✅ 2-3 VitePress `locales`(root zh-CN / en);语言切换优先对应翻译页,无翻译回退语言首页
- ✅ 2-4 下载页生成链路回归(`download-page.py` 原样保留,输出路径/链接在新路由下可用)
- ✅ 2-5 navcheck 升级:Docsify 专属规则(alias/subMaxLevel)退役,改为 VitePress 路由校验(sidebar 目标、.md 链接、双语镜像)

## 阶段 3 — 迁移与升级管理

- ✅ 3-1 `migrate` 命令:`--dry-run`、备份受管 Docsify 文件、生成 VitePress 配置、转换导航
- ✅ 3-2 旧结构识别:`.github/pages/` 外壳、旧 `static.yml`(先识别是否承担其他部署,不盲目删)、带托管标记的 `index.html` 才允许清理
- ✅ 3-3 旧链接扫描:正文/导航中的 `#/` Hash 路由迁移为 VitePress 路径
- ✅ 3-4 `update` 语义扩展:托管文件清单加入 VitePress 配置/依赖/workflow;仍永不覆盖用户 Markdown
- ✅ 3-5 `check` 扩展:依赖锁文件一致性、sidebar 生成结果与 `_sidebar.md` 一致、下载页链路
- ✅ 3-6 `build`/`preview`/`dev` 包装命令(调用 VitePress CLI,Python 不做渲染)

## 阶段 4 — 完整质量门禁

- ⬜ 4-1 Python 测试全量通过(含新增 test_vitepress_config / test_migration / test_build)
- ⬜ 4-2 VitePress 构建成功、无 dead link(中英文)
- ⬜ 4-3 下载页自动更新端到端(release → 生成 → dispatch → 部署)
- ⬜ 4-4 子路径部署验证(PixivFlow 形态的 base)
- ⬜ 4-5 Playwright/浏览器截图:首页、普通文档、长代码、长表格、下载页、英文页、暗色;320/390/768/1024/1440 无横向滚动
- ⬜ 4-6 `migrate --dry-run` 对一个旧壳仓库的演练输出审查

## 阶段 5 — 发布与逐步迁移

- ⬜ 5-1 中英文档更新(README/QUICKSTART/CONVENTIONS/NAVIGATION/UPGRADE;「零构建」表述改为新架构说明)
- ⬜ 5-2 docsite 自身站点切换 VitePress 并上线 Pages
- ⬜ 5-3 选一个业务仓库试点迁移,验收(备份可回滚)
- ⬜ 5-4 逐个迁移 PixivFlow/DAViewer/TelePost 等(每个仓库 diff 可见可控,不批量)
- ⬜ 5-5 整理提交、创建 PR(不自动合并)

## 已归档(不再执行)

- ~~原 P0/P1 视觉升级任务~~ → 由本计划取代;成果存档 `archive/docsify-custom-theme`
