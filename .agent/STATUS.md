# STATUS — 项目状态快照

> 每次会话结束或阶段性进展后更新本文件。先读这里,再读 [PLAN.md](PLAN.md) 和 [TASKS.md](TASKS.md)。

**最后更新:** 2026-10-30(docsite 已合并上线;跨仓库导航鉴权修复已验收)

## 项目健康度

| 项 | 状态 |
| --- | --- |
| 分支 | main 已合并 PR #11(d435f6a);当前修复分支 codex/fix-navcheck-private-repos |
| 测试 | 60 例通过(1 skip),v1 兼容断言保持通过 |
| 构建 | main 测试与 Pages 部署 CI 成功;线上中英六条路由 200、搜索/移动暗色可用 |
| 下游站点 | PixivFlow · DAKit · DAViewer · TelePost · ReleaseGraph 仍在 Docsify(阶段 5 逐个迁移);docsite 自身已切 VitePress(试验田) |

## 当前阶段

**阶段 1–4 ✅ 完成;阶段 5 [PR #11](https://github.com/redtidev1918/docsite/pull/11) 已按用户明确指令合并上线。跨仓库 navcheck 的私有仓库克隆鉴权修复已在独立分支真实运行通过。**

- 阶段 3:init v2/update 引擎感知/check v2/migrate/build-preview-dev 完成,模板内容移入 template/docs/。
- 测试:60 例通过(1 skip),自身与旧壳迁移 fixture 构建成功,最终无 .git 副本 check 9/9、navcheck 全绿。
- 浏览器:36 张最终文档截图+搜索截图;72 次亮暗/宽度组合无整体横向滚动,子路径无资源错误。报告见 shots/report.json。

## 下一步

1. 审查跨仓库导航鉴权修复 PR;分支 workflow_dispatch 已全绿。
2. 验证 release → 双语下载页 → 显式 dispatch → Pages 的真实链路。
3. 用户已指定上线后重建六站:DAViewer、DeviantDrop、deviantart-downloader、PixivFlow、TelePost、NekoTime。先试点一个,再逐仓库独立 PR。

## 进行中 / 阻塞

- 进行中:导航 CI 修复 PR 交付,后续按六站重建范围推进试点。
- 旧 preview(4173)已关闭,其占用 esbuild 导致的 npm ci EPERM 已修复并重装成功。截图使用系统 Edge。
