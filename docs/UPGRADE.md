# 升级模板

**语言 / Language:** 中文 · [English](/en/)

模板更新后（换 docsify 版本、改样式、加功能），在**每个接入仓库的根目录**执行：

```bash
git -C /tmp/docsite pull          # 更新脚手架本体
python3 /tmp/docsite/docsite.py update
```

`update` 只重写托管部分（`index.html`、`docs.yml`、`assets/vendor/`、下载页生成链路），
按 `.docsite.json` 重新渲染，**Markdown 一律不碰**。看 diff、提交、推送。

外壳目录按现状识别：`docs/index.html` 或老形态的 `.github/pages/index.html`（`static.yml`
拼接发布的那批仓库）。托管外壳、vendor 资源与 `.nojekyll` 都跟着外壳目录走；
`.docsite.json` 只声明了 `navigation` 时，站点名与 emoji 由 git remote 推导。

多个仓库批量升级就是在各仓库各跑一次，刻意不做「一键全仓升级」，让每个仓库的 diff
可见可控。

## 升级 Actions 版本

`template/docs.yml` 是全账号 actions 版本的唯一来源。只改这一处模板，再让各仓库跑
`update` 收敛；不要在单个仓库里手改，否则下次 `update` 会把它覆盖回模板版本，
同一份版本号在仓库间反复漂移。

## 相关校验

```bash
python3 docsite.py check --all /path/to/repos     # 托管文件是否逐字节一致
python3 docsite.py navcheck --all /path/to/repos   # 导航契约是否被破坏
```
