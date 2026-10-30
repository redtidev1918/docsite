# 升级模板

**语言 / Language:** 中文 · [English](/en/UPGRADE.md)

## 刷新 VitePress 托管文件

需要 Python 3、Node.js 22+ 和 npm。在每个接入仓库的根目录执行：

```bash
git -C /tmp/docsite pull          # 更新 docsite
python3 /tmp/docsite/docsite.py update
npm ci
python3 /tmp/docsite/docsite.py build
python3 /tmp/docsite/docsite.py preview
```

v2 的 `update` 会重写 package.json/lock、config.mts、docs.yml、public/.nojekyll 和下载页脚本，补齐 .gitignore，并从 `_sidebar.md` 生成导航。正文和 `_sidebar.md` 不会被覆盖。站点配置改 `.docsite.json`，导航改 `_sidebar.md`。

已有 Node 项目需要注意：docsite 会替换根 package.json 和 lock。替换非托管文件前会留下 `*.docsite.bak`，重复备份加序号。

需要保留的业务 scripts、依赖和锁文件要手动合并，再安装和构建。合并后的自定义字段会让 `check` 报 DRIFT，下次 update 也会再次替换这些文件。当前版本尚不能直接保留已有 Node 工程的包配置，接入前请先检查这一点。

依赖升级：先修改模板 package.json 的固定版本并在 template/ 运行 `npm install` 更新模板 lock；目标仓库再运行 `update` 和 `npm ci`（人工合并依赖后使用 `npm install` 重算 lock）。v2 update 自动同步 `.docsite.json` 的 engineVersion/version。

## 从 Docsify 迁移

迁移前先提交或另存现有改动。旧站点可以继续使用 v1 的 update/check/navcheck；只有 migrate 会切换到 VitePress。

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
- `.github/pages/_sidebar.md` 仅在 docs/ 缺对应文件时复制，原侧边栏保留。migrate 会改写正文和导航中的旧链接，update 不会。
- static.yml 等旧 Pages workflow 备份后停用，防止双部署；若含 `cp -R themes _site` 等额外发布任务，先人工拆分这些职责。根目录 Markdown 不再自动发布，按报告人工调整。
- `.docsite.json` 保留原字段并写入 engine/engineVersion/version:2；下载页 `linkBase: "/docs"` 清空。
- 下载页默认同时生成中英页；缺少被语言互链引用的页面会造成 dead link 构建失败，修复内容，不设置 ignoreDeadLinks。

构建、预览和线上部署成功后，再手动删除旧 index.html、vendor、旧外壳目录和备份。迁移命令会保留这些文件。

## 回滚与上线顺序

尚未合并时，可以恢复迁移前的已跟踪文件，再从备份还原未提交的内容。新增的未跟踪文件需要逐一检查并删除，git checkout 不会清掉它们。已经合并的迁移用 revert 提交回滚，同时恢复旧 workflow。保留一套生效的 Pages 部署即可。

迁移多个仓库时，先选一个试点，检查线上页面和下载页的 release → commit → dispatch → Pages 流程。确认正常后，再逐个迁移其余仓库，每个仓库单独提交 PR。

## 模板位置

v2 的 Pages 模板在 `template/.github/workflows/docs.yml`，使用 Node 22 安装依赖、构建并上传 dist。v1 使用 `template/docs.yml` 和旧外壳模板。修改对应模板，再运行 update 同步到目标仓库。

## 相关校验

```bash
python3 docsite.py check --all /path/to/repos     # 托管文件是否逐字节一致
python3 docsite.py navcheck --all /path/to/repos   # 检查导航规则
```
