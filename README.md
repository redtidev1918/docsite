# docsite

零依赖的 docsify 文档站脚手架。一个 Python 脚本 + 一份模板，给任何 GitHub 仓库一键长出统一风格的文档站。

线上效果见：[PixivFlow](https://redtidev1918.github.io/PixivFlow/) · [dakit](https://redtidev1918.github.io/dakit/) · [TelePost](https://redtidev1918.github.io/TelePost/) · [ReleaseGraph](https://redtidev1918.github.io/releasegraph/)

## 特性

- **纯 stdlib**：只需要 `python3`，不装包、不跑构建
- **只管壳子**：`index.html` / 部署 workflow / docsify 资源由模板托管；Markdown 是你自己的，升级永不覆盖内容
- **自带部署**：生成 GitHub Actions workflow，push `docs/` 即发布到 Pages
- **开箱即用**：明暗主题切换（跟随系统 + 记忆）、全文搜索、emoji favicon、侧边栏
- **子目录统一侧边栏**：`zh-CN/`、`en/` 等子目录页面自动共用根侧边栏，不用每个目录再放一份

## 新项目接入

在**目标仓库根目录**：

```bash
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite

python3 /tmp/docsite/docsite.py init \
  --repo owner/name \
  --name 显示名 \
  --emoji 🐱 \
  --branch main
```

| 参数 | 说明 | 默认 |
| :-- | :-- | :-- |
| `--repo` | `owner/name`，必填 | — |
| `--name` | 站点显示名 | 仓库名 |
| `--emoji` | favicon 与站名前的 emoji | 📘 |
| `--description` | 页面 meta description | 「\<name\> 文档中心……」 |
| `--branch` | 触发部署的分支 | `main` |
| `--theme-key` | 主题偏好的 localStorage key | `<name 小写>-theme` |

生成：

```
.docsite.json                 # 本项目的配置（提交进仓库）
.github/workflows/docs.yml    # Pages 部署（托管，别手改）
docs/
├── index.html                # docsify 外壳（托管，别手改）
├── .nojekyll
├── _sidebar.md               # 侧边栏（你的内容）
├── README.md                 # 首页（你的内容）
├── QUICKSTART.md             # 示例页（你的内容）
└── assets/vendor/            # docsify + 主题 + 搜索（托管）
```

推送后 workflow 自动部署；仓库 **Settings → Pages → Source 选 GitHub Actions**（首次一般自动配好）。
站点地址：`https://<owner>.github.io/<name>/`

## 老项目接入（已经有 docs/ 或文档站）

同样在仓库根跑 `init`，它对老项目有保护：

- 已有的 `docs/index.html`、`.github/workflows/docs.yml` 如果**不是** docsite 托管文件，会先备份成 `*.docsite.bak`，不静默覆盖
- 检测到别的文件名的 Pages workflow（如 `static.yml`）只提示不删除
- 已有的 Markdown（`README.md`、`_sidebar.md` 等）一律不动

步骤：

```bash
# 1. init（参数见上）
python3 /tmp/docsite/docsite.py init --repo owner/name --name 显示名 --emoji 🐱

# 2. 检查差异与备份
git status
#    - 核对 docs/index.html.docsite.bak（旧站若有自定义，把必要内容并回模板配置）
#    - 旧部署 workflow（如 static.yml）确认 docs.yml 部署成功后删除，避免重复部署

# 3. 侧边栏约定：链接写「根绝对路径」，子目录页面才能跳对
#    [架构](/ARCHITECTURE.md)   ✅
#    [架构](ARCHITECTURE.md)    ❌ 在 zh-CN/ 子页面会 404

git add -A && git commit -m "docs: 接入 docsite" && git push
```

> Jekyll / mkdocs 等其他构建迁过来：内容文件保留，删掉对应的构建配置（`_config.yml`、`mkdocs.yml` 等）和旧 workflow 即可，新方案不需要构建。

## 日常更新文档（最常用）

不用再跑脚本，直接改 Markdown：

1. 往 `docs/` 加 / 改 `.md` 文件
2. 在 `docs/_sidebar.md` 里加链接（根绝对路径：`- [标题](/PAGE.md)`）
3. `git commit && git push`——workflow 监听 `docs/**` 变化，一两分钟后线上更新

多语言就建子目录（`docs/zh-CN/`、`docs/en/`），根侧边栏统一列链接；正文内部互链用普通相对路径（如 `[English](../)`）。

## 升级 docsite 模板

模板更新后（换 docsify 版本、改样式、加功能），在每个接入仓库的根目录：

```bash
git -C /tmp/docsite pull          # 更新脚手架本体
python3 /tmp/docsite/docsite.py update
```

`update` 只重写托管部分（`index.html`、`docs.yml`、`assets/vendor/`），按 `.docsite.json` 重新渲染，**Markdown 一律不碰**。看 diff、提交、推送。
在多个仓库批量升级就是在各仓库各跑一次——刻意不做一键全仓升级，让每个仓库的 diff 可见可控。

## 已接入站点的参数参考

| 项目 | 命令要点 |
| :-- | :-- |
| PixivFlow | `--name PixivFlow --emoji 🐱 --branch master --theme-key pf-theme` |
| dakit | `--name DAKit --emoji 🎨 --theme-key dakit-theme` |
| TelePost | `--name TelePost --emoji 📮 --theme-key tp-theme` |
| releasegraph | `--name ReleaseGraph --emoji 🕸️ --theme-key rg-theme` |

## 非目标

- 不做多版本/多语言路由、不做服务端搜索、不做自定义主题系统
- 不内置"一键批量升级所有仓库"——每个仓库自己跑一次 update，diff 可见可控
