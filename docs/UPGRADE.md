# 升级模板

**语言 / Language:** 中文 · [English](/en/UPGRADE.md)

## 刷新 VitePress 托管文件

需要 Python 3、Node.js 22+ 和 npm。在每个接入仓库的根目录执行：

```bash
git -C /tmp/docsite pull          # 更新脚手架本体
python3 /tmp/docsite/docsite.py update
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

v2 `update` 下发 package.json/lock、config.mts、docs.yml、public/.nojekyll 与下载页链路，补齐 .gitignore，并从 `_sidebar.md` 重新生成 sidebar。**Markdown 一律不碰**。配置渲染源是 `.docsite.json`，不要手改生成的 config/sidebar。

已有 Node 项目请在 `.docsite.json` 设置 `"packageMode": "merge"`，新接入也可用 `init --package-mode merge`。update 只合并 docs:* scripts 和固定版本的 VitePress 开发依赖，保留业务字段与原 lock；随后运行 `npm install` 更新锁文件。若已有同名 docs:* 命令且内容不同，会报错，需先人工合并。

默认的 managed 模式仍按模板整体更新 package.json/lock，适用于没有业务 Node 包的文档工程。替换非托管文件前会留下 `*.docsite.bak`，重复备份加序号。

依赖升级：先修改模板 package.json 的固定版本并在 template/ 运行 `npm install` 更新模板 lock；目标仓库再运行 `update` 和 `npm ci`（人工合并依赖后使用 `npm install` 重算 lock）。v2 update 自动同步 `.docsite.json` 的 engineVersion/version。

## 从 Docsify 显式迁移

迁移前提交或另存现有工作，确保 diff 与回滚基线明确。v1 在 migrate 前仍使用 Docsify 的 update/check/navcheck，不会被 update 静默切换引擎。

```bash
python3 /tmp/docsite/docsite.py migrate --dry-run
python3 /tmp/docsite/docsite.py migrate
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

- 仅识别带托管标记的 `docs/index.html` 或 `.github/pages/index.html`。
- dry-run 不写盘，列出新增/改写、备份、旧 Pages workflow 停用和发布目录变化。
- 旧外壳和 vendor 保留原件并备份；正文 hash 链接与旧 `/docs/` 前缀改写前备份，配置同样留备份。
- `.github/pages/_sidebar.md` 仅在 docs/ 缺对应文件时复制，原侧边栏保留；**update 不改 Markdown，migrate 会显式改写链接**。
- static.yml 等旧 Pages workflow 备份后停用，防止双部署；若含 `cp -R themes _site` 等额外发布任务，先人工拆分这些职责。根目录 Markdown 不再自动发布，按报告人工调整。
- `.docsite.json` 保留原字段并写入 engine/engineVersion/version:2；下载页 `linkBase: "/docs"` 清空。
- 下载页默认同时生成中英页；缺少被语言互链引用的页面会造成 dead link 构建失败，修复内容，不设置 ignoreDeadLinks。

构建、预览和线上部署确认成功后，才进行**独立的人工清理**：旧 index.html、vendor、旧外壳目录与备份。迁移命令不会自动清理旧站点文件。

## 回滚与上线顺序

对未合并 PR，丢弃明确属于迁移的已跟踪改动，并从备份恢复未提交过的文件；新生成的未跟踪文件须逐一核对后移除，**仅 git checkout 不能清掉新文件**。已合并的迁移用 revert 提交回滚，并恢复旧部署 workflow。不要同时启用两套 Pages 部署。

先合并并验证 docsite 自身站点；再选一个业务仓库试点，验证下载页真实 release → commit → dispatch → Pages；通过后逐个迁移 PixivFlow、DAViewer、TelePost。每仓库独立 PR，不自动合并或批量迁移。

## 模板事实源

v2 Pages workflow 源为 `template/.github/workflows/docs.yml`，Node 22 → npm ci → VitePress → dist 上传；v1 保留 `template/docs.yml` 与旧外壳模板供兼容。修改对应模板后由 update 下发，不在目标生成文件里手改。

## 相关校验

```bash
python3 docsite.py check --all /path/to/repos     # 托管文件是否逐字节一致
python3 docsite.py navcheck --all /path/to/repos   # 导航契约是否被破坏
```
