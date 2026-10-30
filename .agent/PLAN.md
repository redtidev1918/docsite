# PLAN — docsite 视觉设计与文档体验系统级升级

> 总体计划,经仓库所有者确认。范围:**P0 + P1**(P2 暂不做)。任务拆解见 [TASKS.md](TASKS.md),关键决策见 [DECISIONS.md](DECISIONS.md)。

## 目标

保留 Docsify + Python 轻量生成器的工程定位,对生成站点的视觉设计系统做一次集中升级,使其从「统一部署文档的脚手架」升级为「能生成现代开源项目官网质感的文档站生成器」。

风格方向:**首页参考 VitePress(Hero 区 + 主操作按钮),正文页参考 Starlight(阅读体验优先)**。不照搬、不迁移技术栈。

## 分阶段内容

### P0 — 必做

1. **统一设计系统**(CSS Custom Properties)
   - 品牌/交互色、背景/文字/边框色、亮暗主题语义色、字体字号行高、间距圆角阴影、响应式断点
   - 推荐基线:主色 `#2563EB`;正文 16px / 行高 1.7–1.8;正文宽 780–860px;8px 间距体系;卡片圆角 10–12px
   - 深色模式单独设计语义色,不做简单反色;亮暗均校验对比度
2. **首页重构**
   - Hero 区:项目名、主标题、简介、快速开始主按钮、GitHub/下载次按钮、功能卡片
   - 项目特定内容(名称、安装命令、功能)不得硬编码;由配置或 Markdown 提供
   - 普通 Markdown 首页必须继续正常显示(渐进增强)
3. **文档正文排版**
   - H1–H6、正文链接、代码块/行内代码、表格列表引用、图片分割线、Note/Tip/Warning/Danger、标题锚点
   - 长表格移动端横向滚动,正文不整体横向溢出
4. **导航体验**
   - 侧边栏层级/分组间距/当前页高亮/Hover 与 Focus/移动端展开关闭/长标题换行/键盘操作
   - 不破坏 Docsify 路由与中英双语侧边栏

### P1 — 增强

1. **下载页视觉**:保留自动生成逻辑,改善版本/平台/校验信息的表达;无 Release、无资产、网络错误均需降级;不凭文件名猜平台、不造不存在的资产链接
2. **配置扩展**:`.docsite.json` 新增 `appearance`(accentColor / theme / homeLayout);所有新字段有默认值,旧配置零修改可用;严格校验 + HTML/JS 转义防注入
3. **阅读辅助**:右侧页面目录(宽屏)、标题锚点、代码复制按钮(键盘可达 + 成功反馈)、上一篇/下一篇

## 明确不做

- 不迁移 VitePress / Docusaurus,不引入 React/Vue 工程或 npm 构建链
- 不加大型动画库、复杂背景特效、多主题市场、可视化配置编辑器
- 不自动合并 PR,不自动批量升级下游业务仓库

## 关键工程约束

- **改造模板源与生成器**(`template/` + `docsite.py`),不直接改各项目已生成的 `docs/index.html`
- **资源复制**:`copy_vendor()` 目前只复制 `template/assets/vendor/`,新增 `assets/styles/` 与 `assets/scripts/` 不会自动发布,必须同步调整复制/清单/检查逻辑(init、update、check 三处)
- **不覆盖用户 Markdown**:update 只刷新工具托管的外壳文件
- 保留:中英独立侧边栏、Hash 路由、Docsify 搜索、自动下载页、GitHub Pages 子路径兼容、历史站点外壳目录兼容
- **禁止重新引入通配 sidebar alias**(曾导致英文文档读中文侧边栏)
- 样式从 `index.html` 内联迁出到独立 CSS 文件;`prefers-color-scheme` 跟随系统 + 用户手动设置持久化,切换不闪白
- `prefers-reduced-motion` 尊重;不新增外部 CDN 运行时依赖

## 目标文件结构

```
template/
├── index.html
├── assets/
│   ├── styles/      # tokens.css / layout.css / components.css / themes.css
│   ├── scripts/     # theme.js / enhancements.js
│   └── vendor/      # 现有第三方资源
└── ...
```

## 验收

- Python 现有测试全过;init / update / check / navcheck 正常;新旧配置兼容
- 中英文首页与正文可访问;路由、侧边栏、搜索正常;下载页不回归
- 亮/暗/系统跟随主题正常;320–1920px 断点无横向溢出;WCAG AA 对比度
- 优先真实浏览器截图核验,不只看 CSS 代码;环境缺失时明确报告未验证项

## 后续推广

升级完成后,下游仓库(PixivFlow、TelePost、DAViewer 等)各自执行原有 `docsite.py update` 流程即可逐步应用新版模板。
