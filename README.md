# docsite

**语言 / Language:** 中文 · [English documentation](https://redtidev1918.github.io/docsite/#/en/README.md)

零依赖的 docsify 文档站脚手架。一个 Python 脚本加一份模板，给 GitHub 仓库配上统一风格的文档站。

线上示例：[PixivFlow](https://redtidev1918.github.io/PixivFlow/) · [DAKit](https://redtidev1918.github.io/DAKit/) · [DAViewer](https://redtidev1918.github.io/DAViewer/) · [TelePost](https://redtidev1918.github.io/TelePost/) · [ReleaseGraph](https://redtidev1918.github.io/releasegraph/) · [docsite](https://redtidev1918.github.io/docsite/)

## 从哪开始

| 场景 | 看这里 |
| --- | --- |
| 给新仓库加 Pages 文档站 | [快速开始](docs/QUICKSTART.md) |
| 中英文目录、下载页、一次性文档生命周期的约定 | [文件与命名规范](docs/CONVENTIONS.md) |
| 只改文档内容 | 直接编辑 `docs/*.md`，推送到 `main` |
| 更新模板或托管 workflow | [升级模板](docs/UPGRADE.md) |

docsite 只管外壳和部署链路，Markdown 留在仓库里。正文、侧边栏结构和技术文档都不会被模板升级覆盖。

## 快速开始

在目标仓库根目录执行：

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite
python3 /tmp/docsite/docsite.py init \
  --repo owner/name \
  --name 显示名 \
  --emoji 📘 \
  --branch main
```

推送到远程后，GitHub Actions 会发布 Pages。首次部署需要在仓库 `Settings → Pages` 里确认 Source 是 GitHub Actions。

生成的站点地址是：

```text
https://<owner>.github.io/<name>/
```

`<name>` 必须和仓库名完全一致，因为 GitHub Pages 路径区分大小写。

## 会生成什么

```text
.docsite.json
docs/
├── index.html
├── _sidebar.md
├── README.md
├── QUICKSTART.md
├── download.md
└── en/
.github/workflows/docs.yml
.github/workflows/update-download-page.yml
.github/scripts/update_download_page.py
```

Markdown 由仓库自己维护；`index.html`、部署 workflow 和 vendor 资源由模板托管，不要手改。

## 日常使用

1. 往 `docs/` 增加或修改 `.md` 文件。
2. 在 `docs/_sidebar.md` 中用根绝对路径加入口，例如 `- [架构](/ARCHITECTURE.md)`。
3. 推送到默认分支，等 Actions 完成后刷新 Pages。

下载页不用手写。发版后由 `.github/workflows/update-download-page.yml` 根据 Release 数据刷新。旧仓库已有 `docs/` 时，`init` 会先备份非托管文件，不会静默覆盖正文。

## 质量检查

```bash
python3 docsite.py check .
python3 docsite.py navcheck .
python3 docsite.py lifecyclecheck .
python3 docsite.py update
```

`check` 用于发现下载页过期或漂移；`navcheck` 检查侧边栏、语言目录、重复链接和锚点；
`lifecyclecheck` 检查根目录与归档区是否混入一次性/阶段文档；`update` 只收敛托管文件，不会改 Markdown。

## 非目标

docsite 不做按语言自动跳转的路由、服务端搜索或自定义主题系统。批量升级也不做成“一键全仓”，每个仓库自己跑 `update`，diff 可见可控。

## 许可

MIT。完整规范、部署边界和升级方式见 [文档站](https://redtidev1918.github.io/docsite/)。
