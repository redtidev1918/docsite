# docsite

**语言 / Language:** 中文 · [English](/en/)

docsite 给 GitHub 仓库生成文档站。正文放在 `docs/`，用 VitePress 构建，再由 GitHub Actions 发布到 Pages。

需要 Python 3、Node.js 22+ 和 npm；先 `npm ci`，再 `npm run docs:build`。

- [快速开始](/QUICKSTART.md)：初始化、构建和部署
- [获取 docsite](/download.md)：克隆源码或固定版本
- [文件与命名规范](/CONVENTIONS.md)：中英目录、下载页生成链路
- [导航规则](/NAVIGATION.md)：侧边栏写法和检查项
- [升级模板](/UPGRADE.md)：更新配置、迁移旧站和回滚

GitHub 仓库：<https://github.com/redtidev1918/docsite>

## 日常维护

平时直接改 Markdown。侧边栏改完后运行 `update`，再构建预览。发版时，workflow 会根据 Release 数据更新下载页，并触发站点重建。

## 哪些文件会被更新

| 文件 | 维护方式 |
| :-- | :-- |
| 正文、_sidebar.md | 自己编辑，update 不覆盖 |
| package.json/lock、VitePress 配置、生成的 sidebar、workflow | update 按模板重写 |
| 下载页 | 发版 workflow 根据 Release 数据生成 |

网站使用 VitePress 默认主题，支持亮暗切换、本地搜索和中英文页面。docsite 不提供自定义主题或服务端搜索。
