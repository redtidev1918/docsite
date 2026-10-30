将文档站渲染从 Docsify 切换到 VitePress 1.6.4，Python 保留工程管理层职责。新 init 默认 v2；旧仓库须显式 migrate，迁移前的 update/check/navcheck 保持 v1 兼容。

- VitePress 默认主题、亮暗、本地搜索与双语 locales；README rewrites，_sidebar.md 为唯一导航源。
- migrate 支持 dry-run、备份、hash/旧路径改写、旧 Pages workflow 停用与额外发布目录报告；旧外壳清理由构建后的独立人工步骤完成。
- update/check 管理依赖锁、渲染配置、sidebar 与下载页链路；新增 build/preview/dev npm 包装。
- Pages 改为 Node 22 + npm ci + VitePress dist；保留下载页 workflow 的显式 dispatch。补齐中英指南与 PR 验证 CI。

验证：60 个 Python 测试通过（1 skip）；npm ci、Node 22.23.4 构建零 dead link；无 .git fixture check 9/9、navcheck 全绿；旧壳 fixture 迁移后构建通过。Playwright/Edge 对 /PixivFlow/ 子路径进行了 72 次亮暗与屏宽组合检查，零整体横向溢出/同源 HTTP 错误；36 张矩阵截图及搜索截图位于 .agent/shots/。

兼容风险：v2 接管根 package.json/lock。现有 Node 项目须在各自 PR 人工合并业务 scripts/依赖；自定义字段会触发当前逐字节 check 的 DRIFT，后续 update 会重下发模板。迁移显式改写 Markdown 链接并先备份；update 不覆盖用户 Markdown。缺失翻译页的 dead link 保持显性构建失败。

回滚：未合并时恢复迁移前已跟踪文件并从备份还原未提交内容，逐一核对新增未跟踪文件；合并后用 revert 提交并恢复旧 workflow，仅启用一套 Pages 部署。

上线后：先验证 docsite Pages 与真实 release→下载页→dispatch→Pages；再从用户指定六站选一个试点，通过后逐仓库独立 PR：DAViewer、DeviantDrop、deviantart-downloader、PixivFlow、TelePost、NekoTime。此 PR 不代表远端 Pages 已上线，不自动合并或批量迁移。
