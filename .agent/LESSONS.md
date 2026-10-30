# LESSONS — 经验教训

> 记录项目特有的、代码/文档里不易看出的坑与约定。发现新坑追加到对应分组;过时条目注明并保留。

## 架构决策(2026-10-30 最重要的教训)

- **引擎 vs 主题的选择要在写第一行 CSS 之前定。**「在默认主题上美化」永远受默认质感拖累(第一轮被否);「完整自研主题」则意味着长期维护一整套前端皮肤(第二轮实现成功仍被否)。两轮合计约一天工作量归档于 `archive/docsify-custom-theme`。最终正解是换引擎(D-009):VitePress 原生就有全部所需能力。
- **验收要用真实浏览器截图,且要尽早看第一张截图。** 第一轮叠加方案在写完所有 CSS 后才第一次截图,发现默认主题质感未摆脱,返工成本最大。正确顺序:先出一页真实渲染 → 所有者确认方向 → 再铺开实现。
- **配置注入用 JSON 一次注入(`window.DOCSITE = {...}`)+ `textContent` 构建 DOM**,天然避开 XSS 与多上下文转义;直接拼 HTML 字符串的方案不要用。

## 生成器 / 资源发布

- **`copy_vendor()` 只复制 `template/assets/vendor/`**(所有者确认)。新增 `assets/styles/`、`assets/scripts/` 不会自动发布到目标站点,需同步调整复制逻辑及 update/check 的托管文件清单,否则本地模板改了、下游站点拿不到。
- **`docs/` 中的文件分两类:** 工具托管的外壳文件(index.html、vendor 资源、托管 workflow)与用户维护的 Markdown。update 只能刷新前者,覆盖用户 Markdown 是破坏性事故。
- 模板升级的推广路径是各下游仓库执行 `docsite.py update`,因此模板任何结构性改动(新增文件、改引用路径)都必须同时过一遍 init(新站点)与 update(老站点)两条链路。

## 平台

- **Windows 路径分隔符:** 路径进入配置/发布清单前需 `as_posix()` 处理,否则 navcheck 等在 Windows 上误报(commit b740411 的修复)。Windows 是本项目的主要开发平台之一,任何新路径逻辑都要在 Windows 上验证。

## Docsify 约定

- **中英文独立侧边栏是刻意设计**,历史上的通配 sidebar alias 导致英文文档读到中文侧边栏,已移除——不许以任何理由回归(见 [DECISIONS.md](DECISIONS.md) 与 PLAN.md 工程约束)。
- Docsify 用 Hash 路由;GitHub Pages 子路径(`/repo/`)部署与历史站点外壳目录兼容必须保留。

## 协作流程

- 仓库文档中英文双语,改文档时两套都要同步,否则 Pages 上的英文页与中文页会漂移。
- 提交风格:conventional commits(`fix:`、`docs:` 等前缀,见近期提交历史)。
