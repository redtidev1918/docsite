# docsite

零依赖的 docsify 文档站脚手架。一个 Python 脚本 + 一份模板，给任何 GitHub 仓库一键长出统一风格的文档站。

线上效果见：[PixivFlow](https://redtidev1918.github.io/PixivFlow/) · [dakit](https://redtidev1918.github.io/dakit/) · [TelePost](https://redtidev1918.github.io/TelePost/) · [ReleaseGraph](https://redtidev1918.github.io/releasegraph/)

## 特性

- **纯 stdlib**：只需要 `python3`，不装包、不跑构建
- **只管壳子**：`index.html` / 部署 workflow / docsify 资源由模板托管；Markdown 是你自己的，升级永不覆盖内容
- **自带部署**：生成 GitHub Actions workflow，push `docs/` 即发布到 Pages
- **开箱即用**：明暗主题切换（跟随系统 + 记忆）、全文搜索、emoji favicon、侧边栏

## 用法

在**目标仓库根目录**：

```bash
# 1. 拿到本仓库
git clone https://github.com/redtidev1918/docsite.git /tmp/docsite

# 2. 初始化（可反复试，内容文件已存在时不会覆盖）
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
.docsite.json                 # 本项目的配置
.github/workflows/docs.yml    # Pages 部署（托管）
docs/
├── index.html                # docsify 外壳（托管）
├── .nojekyll
├── _sidebar.md               # 侧边栏（你的，只在缺失时创建骨架）
├── README.md                 # 首页（你的）
├── QUICKSTART.md             # 示例页（你的）
└── assets/vendor/            # docsify + 主题 + 搜索（托管）
```

推送后 workflow 自动部署；仓库 **Settings → Pages → Source 选 GitHub Actions**（首次一般会自动配好）。
站点地址：`https://<owner>.github.io/<name>/`

## 写文档

- 往 `docs/` 加 Markdown，在 `docs/_sidebar.md` 里加链接即可
- 首页是 `docs/README.md`
- 子目录页面（如 `zh-CN/`）自动共用根 `_sidebar.md`（模板用 `alias` 强制）；因此侧边栏链接一律写**根绝对路径**，如 `[快速开始](/zh-CN/quick-start.md)`，不要写相对路径
- 各语言文档内正文的相互链接仍用普通相对路径即可（如 `[English](../)`)



## 升级模板

模板更新后，在每个接入的仓库根目录跑：

```bash
python3 /tmp/docsite/docsite.py update
```

只重写三个托管部分（`index.html`、workflow、vendor），按 `.docsite.json` 重新渲染；**Markdown 一律不碰**。看 diff、提交、推送。

## 升级 docsify

替换 `template/assets/vendor/` 里的文件并提交本仓库，然后各项目执行 `update`。

## 非目标

- 不做多版本/多语言路由、不做服务端搜索、不做自定义主题系统
- 不内置"一键批量升级所有仓库"——每个仓库自己跑一次 update，diff 可见可控
