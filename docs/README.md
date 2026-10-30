# docsite

**语言 / Language:** 中文 · [English](/en/)

轻量级开源项目文档网站生成器：VitePress 引擎 + Python 工程管理层 + GitHub Pages 托管。

需要 Python 3、Node.js 22+ 和 npm；先 `npm ci`，再 `npm run docs:build`。

- [快速开始](/QUICKSTART.md)：三分钟把站点接到一个仓库上
- [📥 获取](/download.md)：没有安装包，就一个 `.py` 文件
- [文件与命名规范](/CONVENTIONS.md)：中英目录、下载页生成链路
- [导航契约](/NAVIGATION.md)：侧边栏和语言目录的硬规则
- [升级模板](/UPGRADE.md)：模板更新后各仓库怎么收敛

GitHub 仓库：<https://github.com/redtidev1918/docsite>

## 它解决什么

统一各仓库的配置、构建部署与下载页自动更新。主题、渲染、本地搜索、亮暗和语言切换由 VitePress 提供，Markdown 留在各仓库。

## 设计取舍

| 选择 | 原因 |
| :-- | :-- |
| Python 标准库管理层 | 初始化、升级、检查和迁移无需 Python 第三方依赖；构建需要 Node 22+ 与 npm ci |
| 默认 VitePress 引擎 | 依赖锁、config、sidebar 和 workflow 托管；正文与 _sidebar.md 永不被 update 覆盖 |
| 不下发内容 | 下载页是唯一的例外：它由 release 数据生成，手写必然过期 |
| 不做批量升级 | 每个仓库各跑一次 `update`，diff 可见可控 |

## 非目标

- 双语页面由 VitePress locales 和独立侧边栏组织，首页仍写在 README.md
- 不做服务端搜索、不做自定义主题系统
- 不内置「一键批量升级所有仓库」
