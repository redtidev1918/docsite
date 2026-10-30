# STATUS — 项目状态快照

> 每次会话结束或阶段性进展后更新本文件。先读这里,再读 [PLAN.md](PLAN.md) 和 [TASKS.md](TASKS.md)。

**最后更新:** 2026-10-30(阶段 1 完成)

## 项目健康度

| 项 | 状态 |
| --- | --- |
| 分支 | `feat/vitepress-engine`(阶段 1 已完成待提交合入);`main` @7c19a4e;归档 `archive/docsify-custom-theme`(@db1916f) |
| 测试 | 19 个基线测试通过(Docsify 链路断言仍有效);VitePress 新测试待阶段 4 |
| 构建 | docsite 自身 VitePress 1.6.4 构建成功(zh+en);CI Node 22 构建待推送验证 |
| 下游站点 | PixivFlow · DAKit · DAViewer · TelePost · ReleaseGraph 仍在 Docsify(阶段 5 逐个迁移);docsite 自身已切 VitePress(试验田) |

## 当前阶段

**计划 v2 阶段 1(VitePress 基础集成)✅ 完成,进入阶段 2(兼容现有文档规范)。**

- 阶段 1 结论:构建/预览/浏览器验收全过,细节与偏差见 [HANDOFF.md](HANDOFF.md) 最新条目
- 重要取证:旧 `docs/index.html` 与 VitePress 构建不冲突(可备份→构建→再清理);`docs/assets` 不会泄入 dist

## 下一步

1. 阶段 2:sidebar 转换器(`_sidebar.md` → `sidebar.generated.mjs`)、locales/nav、navcheck 规则重写
2. 注意:阶段 3 完成前**不要**在 docsite 仓库运行旧 `update`(会下发 Docsify 壳)

## 进行中 / 阻塞

- 进行中:阶段 2(同会话继续)
- 无阻塞
