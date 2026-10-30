# TASKS — 任务清单

> 执行顺序自上而下。开始一项前把状态改为 `🔄 in_progress`,完成后改为 `✅ done` 并同步更新 [STATUS.md](STATUS.md)。每完成一个阶段在 [HANDOFF.md](HANDOFF.md) 追加交接记录。

**图例:** ⬜ pending · 🔄 in_progress · ✅ done · ⏸ blocked

## P0 — 设计系统与核心体验

- ⬜ P0-1 现状审计:完整阅读 `docsite.py`(init/update/check/navcheck)、`template/`、`tests/`、`docs/*.md`(README/QUICKSTART/CONVENTIONS/NAVIGATION/UPGRADE),列出工具托管文件与用户文件清单
- ⬜ P0-2 建立 `template/assets/styles/`:`tokens.css`(色彩/字体/间距/圆角/阴影/断点变量)、`themes.css`(亮暗语义色,`prefers-color-scheme` + 手动覆盖)
- ⬜ P0-3 `layout.css` + `components.css`:正文排版(H1–H6/代码块/表格/提示框/图片)、阅读宽度、侧边栏、移动端断点
- ⬜ P0-4 `template/assets/scripts/theme.js`:主题切换迁移出 `index.html` 内联脚本,无闪白、localStorage 兼容既有偏好
- ⬜ P0-5 首页 Hero:项目名/主标题/简介/快速开始主按钮/GitHub 次按钮/功能卡片;内容由配置或 Markdown 提供,普通 Markdown 首页不回归
- ⬜ P0-6 导航:当前页高亮、分组间距、Hover/Focus、移动端展开关闭、长标题换行、键盘可达
- ⬜ P0-7 `docsite.py` 资源复制扩展:`copy_vendor()` → 覆盖 `assets/styles/` 与 `assets/scripts/`,init/update/check/清单逻辑同步

## P1 — 增强与配置

- ⬜ P1-1 下载页视觉:版本/平台/校验信息卡片化;无 Release/无资产/网络错误降级不回归
- ⬜ P1-2 `.docsite.json` 扩展:`appearance.accentColor` / `theme` / `homeLayout`,默认值 + 严格校验 + 转义防注入;旧配置零修改可用
- ⬜ P1-3 阅读辅助:宽屏右侧目录、标题锚点、代码复制按钮(键盘 + 成功反馈)、上一篇/下一篇
- ⬜ P1-4 `enhancements.js`:纯原生 JS,尊重 `prefers-reduced-motion`

## 验收

- ⬜ A-1 Python 测试全过;init/update/check/navcheck 四命令手动跑通;新旧配置兼容
- ⬜ A-2 中英文首页/正文/路由/侧边栏/搜索验证;下载页生成不回归
- ⬜ A-3 亮/暗/系统主题切换;320/360/390/768/1024/1440/1920px 断点;无整体横向滚动
- ⬜ A-4 真实浏览器截图核验(优先),记录未验证项;WCAG AA 对比度抽查
- ⬜ A-5 GitHub Pages 子路径部署验证

## 收尾

- ⬜ F-1 更新中英文文档(README/QUICKSTART/CONVENTIONS 等)中涉及配置与模板结构的部分
- ⬜ F-2 视觉前后对比截图、资源体积变化、兼容性风险记录进 [HANDOFF.md](HANDOFF.md)
- ⬜ F-3 整理提交并创建 PR(**不自动合并、不批量升级下游仓库**)
