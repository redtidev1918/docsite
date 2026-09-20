# docsite

**语言 / Language:** 中文 · [English](/en/)

零依赖的 docsify 文档站脚手架。一个 Python 脚本加一份模板，给任何 GitHub 仓库长出统一风格的文档站。

- [快速开始](/QUICKSTART.md) —— 三分钟把站点接到一个仓库上
- [📥 获取](/download.md) —— 没有安装包，就一个 `.py` 文件
- [文件与命名规范](/CONVENTIONS.md) —— 中英目录、下载页生成链路
- [导航契约](/NAVIGATION.md) —— 侧边栏和语言目录的硬规则
- [升级模板](/UPGRADE.md) —— 模板更新后各仓库怎么收敛

GitHub 仓库：<https://github.com/redtidev1918/docsite>

## 它解决什么

账号里十几个仓库各写各的文档站，就会出现十几份互不兼容的 `index.html`、各不相同的
部署 workflow、长期停在旧版本的下载页。docsite 只做一件事：把这些**壳子**收进模板，
把 Markdown 留给仓库自己。

## 设计取舍

| 选择 | 原因 |
| :-- | :-- |
| 纯 stdlib | 接入仓库不需要先装依赖，CI 里 `python3` 就能跑 |
| 只管壳子 | `index.html` / 部署 workflow / vendor 由模板托管；Markdown 归仓库，升级永不覆盖内容 |
| 不下发内容 | 唯一的例外是下载页——它由 release 数据生成，手写必然过期 |
| 不做批量升级 | 刻意让每个仓库各跑一次 `update`，diff 可见可控 |

## 非目标

- 不做按语言自动跳转的多语言路由（英文由 `docs/en/` 承载，侧边栏手动导航）
- 不做服务端搜索、不做自定义主题系统
- 不内置「一键批量升级所有仓库」
