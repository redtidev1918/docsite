# 快速开始

**语言 / Language:** 中文 · [English](/en/QUICKSTART.md)

## 新仓库接入

在**目标仓库根目录**执行：

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

生成的东西分两类：

```
托管（别手改）     docs/index.html · docs/assets/vendor/
                .github/workflows/docs.yml
                .github/scripts/update_download_page.py
                .github/workflows/update-download-page.yml
你的内容         docs/README.md · docs/_sidebar.md · docs/download.md
                docs/en/ 下同名页
```

推送后 workflow 自动部署。仓库 **Settings → Pages → Source** 选 GitHub Actions
（首次 `configure-pages` 一般会自动配好）。站点地址：`https://<owner>.github.io/<name>/`

## 老仓库接入

已经有 `docs/` 或别的文档站时，`init` 有保护：

- 已有的 `docs/index.html`、`.github/workflows/docs.yml` 如果**不是** docsite 托管版本，
  先备份成 `*.docsite.bak`，不静默覆盖
- 检测到别的文件名的 Pages workflow（如 `static.yml`）只提示、不删除
- 已有 Markdown 一律不动

接入后：

1. 检查 `git status`，核对 `docs/index.html.docsite.bak` 里的自定义配置是否需要并回模板
2. `docs.yml` 部署成功后再删旧的部署 workflow，避免重复部署
3. 见 [导航契约](/NAVIGATION.md) 调整侧边栏

## 日常改文档

不用再跑脚本，直接改 Markdown：

1. 在 `docs/` 加或改 `.md`
2. 在 `docs/_sidebar.md` 里加链接（**根绝对路径**：`- [标题](/PAGE.md)`）
3. `git commit && git push`——workflow 监听 `docs/**`，一两分钟后线上更新

侧边栏写成相对路径（`[标题](PAGE.md)`）时，在 `docs/en/` 子页面上会 404。

## 检查一致性

```bash
python3 docsite.py check --all /path/to/repos   # 扫描该目录下所有 git 仓库
python3 docsite.py check .                      # 只查当前仓库
```

逐文件输出 `ok` / `MISSING` / `DRIFT`。有偏差就到对应仓库跑 `python3 docsite.py update`，
看 diff 后提交。
