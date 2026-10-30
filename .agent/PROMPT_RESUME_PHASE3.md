# 交接提示词 — docsite VitePress 迁移:阶段 3 收尾 + 阶段 4/5

> 给接任 agent 的自包含任务指令。总纲仍是 [PROMPT_VITEPRESS_MIGRATION.md](PROMPT_VITEPRESS_MIGRATION.md)(五阶段/约束/完成定义以它为准,本文只写**当前进度、未竟事项与已知坑**)。工作区上下文:STATUS / PLAN / TASKS / DECISIONS / HANDOFF / LESSONS / AUDIT。

## 0. 你的处境(2026-10-30 交接时点)

- 仓库:`redtidev1918/docsite`,本地 `D:\Code\docsite`,分支 **`feat/vitepress-engine`**(未推送)。
- **阶段 1、2 已完成并提交**:`1ba4aa7`(VitePress 基础集成+试验田+浏览器验收)、`4e957da`(sidebar 转换器+双语 nav+navcheck v2 双规则表+36 测试)。
- **阶段 3 代码已全部写完但未提交**,工作区状态:
  - 已改 `docsite.py`:模块 docstring、`_write_v2_managed`/`_v2_config`/`engine_version`/`_ensure_gitignore`、`is_managed` 增加 JSON 字段标记、`render()` 容忍缺失 themeKey、`cmd_init` 重写为 v2、`cmd_update` 引擎感知分支、`cmd_check` 增加 `_check_v2_files`、`cmd_migrate`(dry-run/备份/static.yml 停用/链接改写/linkBase 清空)、`cmd_run_docs`(build/preview/dev 包装)、argparse 全部接线。
  - 模板重构(git mv 已 staged):内容文件 `template/*.md`+`template/en/*` → `template/docs/{...}` 与 `template/docs/en/{...}`;`template/package.json` 加 `"docsite-managed-file": true` 标记(lock 无变化);新增 `template/.github/workflows/docs.yml`(Node 22 构建,阶段 1 已建)。
  - 新测试文件未跟踪:`tests/test_migration.py`(28 例)、`tests/test_build.py`(4 例)。
  - 仓库根 `package.json` 已同步模板(含标记)。
- 测试现状:`python -m unittest discover -s tests` → **56 例,3 FAIL + 1 ERROR + 1 skip**,全部在阶段 3 新测试里,**原因已逐一查明,见 §1**。
- 后台残留:无(4173 端口的 preview 任务已退出);IAB 浏览器标签页可能还开着 `http://127.0.0.1:4173/docsite/…`(死链,需预览时自己重启 preview)。

## 1. 第一步:修掉 4 个已知测试失败(都不难)

1. **ERROR `test_refuses_when_already_v2`**(`tests/test_migration.py`):fixture 直接写 `docs/.vitepress/config.mts` 但目录不存在。修:写文件前 `(self.root / "docs/.vitepress").mkdir(parents=True)`。
2. **FAIL `test_build_invokes_npm_script`**(`tests/test_build.py`):内联 JSON 字符串转义坏了(EJSONPARSE)。修:用 `json.dumps({...})` 生成假 package.json,script 写成 `"docs:build": "node -e \"require('fs').writeFileSync('built.txt','ok')\""` 的等价 JSON 形式。
3. **FAIL `test_dry_run_lists_plans_backups_and_warnings`**:两个原因——
   - 产品 bug:`cmd_migrate` 打印用 `f.relative_to(root)`,Windows 下输出反斜杠(`docs\.vitepress\config.mts`),测试期望正斜杠。修:**所有** `relative_to` 后接 `.as_posix()`(plans/backups/renames 三处循环 + md_files 改写打印处)。
   - 测试 fixture:`make_old_shell_repo` 没造根目录 `*.md`,`root_md` 警告("不再随站点发布")永远不触发。修:fixture 加 `(root / "README.md").write_text("# root\n", encoding="utf-8")`。
4. **FAIL `test_update_refreshes_managed_keeps_content`**:断言 `assertIn("render", run.stdout)` 过时,v2 分支实际打印 `VitePress(v2)托管文件刷新:`。修:改成 `assertIn("VitePress(v2)", run.stdout)`。

修完跑全套,应 **56 例全绿(1 skip 属正常:本机有 npm 时跳过"无 npm 拒绝路径"用例)**。

## 2. 第二步:阶段 3 收尾(验收口径见总纲 §3 阶段 3)

1. **docsite 自身走一遍 v2 update**:在仓库根跑 `python docsite.py update`,确认它刷新 `package.json`/`package-lock.json`/`docs/.vitepress/config.mts`/`sidebar.generated.mjs`/`docs.yml`/`docs/public/.nojekyll` 且**不碰任何用户 Markdown**。注意:docsite 自身的 config.mts 此前是手写渲染的,update 后应与 `render_config` 输出逐字一致(若有 diff,以模板渲染为准,人工核一眼 emoji/favicon/描述字段)。
2. **重建 + 浏览器抽查**:`npm run docs:build` 绿;`vitepress preview` 看 zh/en 首页正常(可选,重点留给阶段 4)。
3. **check 对 docsite 自身全绿**:本地在 feature 分支会被"非默认分支"跳过——用无 .git 的 fixture 验证:`cp -r docs .docsite.json /tmp/fx/ && python docsite.py check /tmp/fx`,确认 v2 新行(package.json/lock/docs.yml/config.mts/sidebar/nojekyll/gitignore)全 ok。
4. **migrate --dry-run 演练输出审查**(总纲阶段 3 验收项):对 `tests/test_migration.py` 的壳形态 fixture 之外,再造一个带 `cp -R themes _site` 的 static.yml,确认报告"它还把 themes 拷进站点"。
5. 更新 `.agent/`(STATUS/TASKS/HANDOFF),conventional commit 提交阶段 3(建议 `feat(engine): migrate command, engine-aware update/check, npm wrappers (phase 3)`)。

## 3. 阶段 4(完整质量门禁)——全部要求见总纲 §3,以下是本会话已探明的坑

- **截图**:IAB 后台时 `tab.screenshot()` 会"surface preparation timed out"。对策:截图前确保浏览器面板在前台/重开标签页;仍不行就用 Playwright CLI 独立跑(`npx playwright screenshot` 或写个小脚本,chromium 需先 `npx playwright install chromium`——这属于构建工具链,不算自研前端)。截图存 `.agent/shots/`,矩阵:首页/普通文档/长代码页/长表格页/下载页/英文页 × 亮/暗 × 1440/1024/390(320–430 无整体横向滚动)。
- **dead link**:目前构建零 dead link(已验证);若下游仓库只有 zh 下载页而 lang_line 链 `/en/download.md`,构建会显性失败——这是设计行为,不要加 ignoreDeadLinks。
- **子路径**:以 `base: '/PixivFlow/'` 形态构建预览验证无 404(改 `.docsite.json` 的 repo 或临时改 config.mts 的 base 再 build;验收后还原)。
- **test_build 类测试**:无 Node 环境要 skip 并明示——`test_build.py` 已用 `skipUnless(HAS_NPM)`,模式照抄。
- **下载页端到端**:本地模拟 = `template/download-page.py` 用 `--input-json` 生成到临时 docs 副本再 build;CI 端到端留到阶段 5 上线后用真实 release 验证。

## 4. 阶段 5(发布与逐步迁移)要点

- 文档改写范围与措辞见总纲 §3 阶段 5;**「零依赖/零构建」表述必须去掉**,改为「VitePress 引擎 + Python 工程管理层 + Node 22/npm ci 前提」。
- docsite 自身上线:feature 分支 → PR(不自动合并)→ 合并后 CI Node 22 构建即真实验证。
- 下游迁移顺序:先试点一个业务仓库,验收后再逐个(PixivFlow/DAViewer/TelePost…),每仓库独立 PR。**Node 项目仓库注意**:根 package.json 会被 docsite 托管文件替换(有 bak + 警示),PR 审查时必须人工合并其自定义 scripts/依赖——这条写进 UPGRADE 文档。
- 已知约束/偏差全部记录在 HANDOFF.md 阶段 1/2 条目里,UPGRADE/CONVENTIONS 改写时逐条吸收。

## 5. 红线(与总纲一致,违反即返工)

- 不写自定义主题/组件/CSS 体系;仅模板 config 层。
- Python 不做渲染/打包;构建一律 `npm run docs:*`。
- 用户 Markdown(含 `_sidebar.md`)永不静默覆盖/删除;备份先于清理;清理是构建验证后的独立人工步骤。
- v1(Docsify)仓库在 migrate 之前必须继续被 update/check/navcheck 支持。
- 不自动合并 PR、不自动批量迁移业务仓库。
- `.docsite.json` 白名单校验;token 进 JS 前必转义(现有 `render_config` 已做,别绕开它)。

## 6. 快速上手命令

```bash
git status --short          # 看未提交的阶段 3 改动
python -m unittest discover -s tests   # 修完 §1 后应 56 全绿
npm run docs:build          # 站点构建
python docsite.py migrate --dry-run    # 迁移演练(对 fixture 路径)
python docsite.py check /tmp/fx        # v2 一致性(需无 .git 的 fixture)
```
