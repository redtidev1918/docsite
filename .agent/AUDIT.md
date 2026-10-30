# AUDIT — P0-1 现状审计

> 2026-10-30 完成于 `main@9dd3caa`。为 P0-2 起的实施提供事实基础;行号以该提交为准。
> 结论先行:**用户的方案与仓库机制完全兼容,新增 styles/scripts 是纯叠加性改动,无破坏性风险点;雷区集中在 navcheck 规则与下载页测试断言。**

## 1. 文件管辖矩阵(谁拥有哪个文件)

| 类别 | 文件 | 机制 |
| :-- | :-- | :-- |
| 托管·渲染 | `<shell>/index.html`、`.github/workflows/docs.yml` | `managed_files()`(docsite.py:57),`@@TOKEN@@` 渲染,init/update **总是覆盖** |
| 托管·逐字节 | `.github/scripts/update_download_page.py`、`.github/workflows/update-download-page.yml` | `SYNCED`(docsite.py:39),无 token,`check` 按字节比对 |
| 托管·复制 | `<shell>/assets/vendor/*`、`<shell>/.nojekyll` | `copy_vendor()`(docsite.py:163),update 总是覆盖 |
| 用户内容 | `docs/{_sidebar,README,QUICKSTART,download}.md` 及 `docs/en/` 同名 | `CONTENT_FILES`(docsite.py:34),init 仅缺失时创建,**update 永不覆盖** |
| 仓库自有 | `.docsite.json`、`.github/scripts/download-page.json` | init 写一次/用户自建,工具只读 |

- 外壳目录 `shell_dir()`(docsite.py:49):`docs/index.html` 存在 → docs/;否则老形态 `.github/pages/`。vendor 与 .nojekyll 跟着外壳走。
- 托管标记 `is_managed()`(docsite.py:107):前 400 字符含 `docsite: managed file` 或全文含 `docsite-managed-file:`。

## 2. 渲染与配置

- `render()`(docsite.py:66):`@@([A-Z_]+)@@` 正则替换,现有 token:NAME / EMOJI / DESCRIPTION / THEME_KEY / REPO / BRANCH。**无任何 HTML/JS/CSS 转义** —— 新增 `appearance.accentColor` 等值会进入 HTML/CSS 上下文,必须先严格校验(白名单/hex 正则),对应 D-005。
- `.docsite.json` 现有字段:`repo` `name` `emoji` `description` `branch` `themeKey` `version: 1`,可选 `navigation{allowSidebarAnchors, allowCombinedLocales}`(白名单 + 布尔,navcheck 以 `NAVIGATION_SCHEMA` error 拒绝未知字段)。
- `with_defaults()`(docsite.py:94):缺 `repo`/`name` 时从 git remote 推导 —— 老仓库只写 `navigation` 也能 update。新字段必须同样 `setdefault`,不动已写死的值。
- 官方 dogfood 配置见根 `.docsite.json`(themeKey=`docsite-theme`)。

## 3. 资源复制改动点(→ TASKS P0-7)

- `copy_vendor()`(docsite.py:163-170)只遍历 `template/assets/vendor/`。**已确认:新增 `assets/styles/`、`assets/scripts/` 不会被发布**。
- 改法:泛化为遍历 `template/assets/*` 各子目录(vendor/styles/scripts 一视同仁),目标 `<shell>/assets/<子目录>/`;`cmd_init`(docsite.py:230)与 `cmd_update`(docsite.py:259)各有一处 `copy_vendor(overwrite=True)` 调用,改函数内部即可,两处自动生效。
- `cmd_check` 只比对 `SYNCED` 两文件,不校验资源目录 —— 新资源暂不纳入 check(可留 P2)。
- `tests/test_shell_dir.py:60,71` 断言 `assets/vendor/docsify.min.js` 存在:新目录是叠加,不破坏该断言。

## 4. navcheck 硬约束(P0-6 / P1-3 的雷区)

| 规则 | 级别 | 对升级的直接影响 |
| :-- | :-- | :-- |
| `GLOBAL_SIDEBAR_ALIAS` | error | index.html 严禁出现 `'/.*/_sidebar.md': '/_sidebar.md'` 形态 → 不加任何 alias |
| `HEADING_INJECTION` | warning | index.html 严禁 `subMaxLevel:` → **右侧 TOC 必须走 enhancements.js 自建 DOM**,不能走 sidebar 注入 |
| `ANCHOR_LINK` | error | sidebar 不能出现 `#` 锚点 → 上一篇/下一篇也走正文注入 |
| `BROKEN_SIDEBAR_LINK` | error | 按 `published_paths()`(docsite.py:423)判定;新形态站点根=docs/ 全部文件 → 新增 `docs/assets/*` 自动成为已发布路径,无副作用 |
| 壳形态英文前缀 | — | `en_prefix` 由 `.github/pages/index.html` 是否存在决定(`/en/` vs `/docs/en/`)→ enhancements.js 的链接生成要兼容两种前缀 |

## 5. 主题机制现状(P0-2 / P0-4 起点)

- 头部内联脚本(index.html:11-18):读 `localStorage['@@THEME_KEY@@']` → 设 `data-theme` attr → `document.write` 追加 dark.css(防闪白)。
- 底部内联(index.html:70-90):切换 `#theme-css` 的 href 在 `vendor/vue.css ↔ vendor/dark.css` 间换文件 + 按钮 🌙/☀️。
- 主题 = 两个完整的 docsify 官方压缩 CSS,靠**换整个文件**切换;两者大量使用 `var(--theme-color, #ea6f5a)` 回退 —— **docsify 原生认 `--theme-color` 作为品牌色钩子**,`accentColor` 可直接映射到它,连带链接/进度条/侧边栏激活色一起变。
- vendor CSS 顶部 `@import` Google Fonts(Source Sans Pro / Roboto Mono)—— 既有外部依赖,非本次新增;设计系统改系统字体栈即可覆盖。
- 视觉短板确认:正文 `max-width:80%`(非固定阅读宽度)、正文 15px/行高 1.6rem、sidebar 300px 无分组层级与当前页强化、提示框仅 `p.tip`/`p.warn` 两态、无复制按钮/TOC/上下篇、移动端全靠 docsify 缺省行为。

## 6. 测试基线(2026-10-30,main@9dd3caa)

- `python -m unittest discover -s tests` → **19 tests OK**(2.2s)。
- `test_shell_dir.py` 钉住:shell 形态识别、update 后 vendor docsify.min.js 存在、index.html 含 marker、`docs/README.md` 原样、通配 alias 必须被 navcheck 打红、壳形态英文前缀 `/docs/en/`。
- `test_download_generator.py` 13 例全 hermetic(`--input-json` 不联网):P1-1 改下载页时必须保住既有断言字符串 —— `## 最新版本:\`v1.2.3\``、`Linux · x64`、marker `<!-- docsite-release-tag: … -->`、`没有附带二进制资产` 等。**视觉只能加壳层,动了这些文案结构就要同步改测试并明说**。

## 7. workflow 事实

- `template/docs.yml`:push 触发 paths 为 `docs/**` + 自身 → 新增 `docs/assets/{styles,scripts}/**` 自动触发部署 ✅;老壳仓库由各自 static.yml 拼 `_site`,外壳资源在 `.github/pages/assets/`,沿用 `copy_vendor` 泛化后同样落地。
- `update-download-page.yml`:`release: published` → 生成双语文档页(带 stale-write 防护)→ dispatch `docs.yml`。
- `navcheck.yml`:定期 + 相关文件变更时对全部受管仓库跑 `navcheck --all`,CI 红即契约破坏。

## 8. 文档承诺需同步(→ 收尾 F-1)

- `docs/UPGRADE.md:12` 「update 只重写托管部分(index.html、docs.yml、assets/vendor/、下载页生成链路)」→ 需补 `assets/styles/`、`assets/scripts/`。
- `docs/CONVENTIONS.md` 下载页/托管文件表格、根 `README.md` 模板结构描述、`docs/QUICKSTART.md` 生成文件清单 —— 均需在 P1-2 落地后更新。
- 中英双语两套都要改(LESSONS 已记录)。

## 9. 遗留设计决策(进入 P0-2 前敲定,定后写入 DECISIONS.md)

- **D-006(待定)主题策略**:A) 保留 vendored vue.css/dark.css 作底,自家 `tokens/themes/components` 叠加覆盖 —— 风险低、见效快,`--theme-color` 钩子现成;B) 自研完整主题替换 vendor 两文件 —— 完全掌控但需覆盖 search 弹窗/cover/app-nav/进度条全部 docsify UI,工作量大。**倾向 A 起步**,B 作为后续演进。
- **D-007(待定)首页 Hero 路径**:docsify 原生 `coverpage`(纯 Markdown、零 JS,但 cover 与正文二选一)vs `enhancements.js` 检测首页路由注入 Hero DOM(与 P1-3 同一脚本,`README.md` 保持普通渲染,符合「渐进增强、普通首页不回归」)。**倾向 JS 注入 + 配置驱动**。
- **配置注入方式**:`appearance` 值可继续走 `@@TOKEN@@`,也可由 index.html 输出 `<script type="application/json" id="docsite-config">` 供 theme.js/enhancements.js 读取,避免 token 继续扩散。**倾向后者**(JSON 一次注入,JS 侧统一解析,天然避开多上下文转义问题)。待 P1-2 定。
