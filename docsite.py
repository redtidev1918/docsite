#!/usr/bin/env python3
"""docsite — 一行依赖都没有的 docsify 文档站脚手架。

    python3 docsite.py init --repo owner/name [--name 名] [--emoji 📘] [--branch main]
    python3 docsite.py update
    python3 docsite.py check [仓库路径 ...] [--all 父目录]

init   在当前仓库生成 docs/ 与 Pages 部署 workflow。
update 只刷新托管文件（index.html / workflow / vendor / 下载页生成链路），
       永远不动你写的 Markdown。
check  校验各仓库的「下载页生成链路」是否与模板逐字节一致（缺文件 / 被手改 / 版本落后）。

统一文档规范：中文为默认（README.md / docs/），英文镜像放 README.en.md / docs/en/。
配置存在仓库根的 .docsite.json；模板取自本脚本旁边的 template/ 目录。
"""
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent / "template"
CONFIG = Path(".docsite.json")

# init 时创建、但 update 永不覆盖的内容文件（docs/ 根 = 中文）
CONTENT_FILES = ["_sidebar.md", "README.md", "QUICKSTART.md", "download.md"]
# 英文镜像内容（docs/en/ 下同名文件）
EN_CONTENT_FILES = ["README.md", "QUICKSTART.md", "download.md"]
# 托管且要求「跨仓库逐字节一致」的文件（下载页生成链路）。
# 不含模板 token，因此可直接比对；docsite.py check 用它做一致性校验。
SYNCED = {
    "download-page.py": ".github/scripts/update_download_page.py",
    "update-download-page.yml": ".github/workflows/update-download-page.yml",
}
# init/update 都由模板渲染的托管文件
MANAGED = {
    "index.html": "docs/index.html",
    "docs.yml": ".github/workflows/docs.yml",
    **SYNCED,
}
VENDOR_DIR = Path("docs/assets/vendor")


def render(text, cfg):
    tokens = {
        "NAME": cfg["name"],
        "EMOJI": cfg["emoji"],
        "DESCRIPTION": cfg.get(
            "description",
            f"{cfg['name']} 文档中心。内容直接来自仓库里的 Markdown，与代码同步更新。",
        ),
        "THEME_KEY": cfg["themeKey"],
        "REPO": cfg["repo"],
        "BRANCH": cfg["branch"],
    }
    def sub(m):
        return tokens[m.group(1)]
    return re.sub(r"@@([A-Z_]+)@@", sub, text)


def is_managed(path):
    """判断已有文件是否为 docsite 下发（两种标记：外壳用注释串，脚本用 marker 行）。"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    return "docsite: managed file" in text[:400] or "docsite-managed-file:" in text


def write_file(path, text, overwrite):
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def copy_vendor(overwrite):
    src = TEMPLATE / "assets" / "vendor"
    VENDOR_DIR.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        dst = VENDOR_DIR / f.name
        if overwrite or not dst.exists():
            shutil.copy2(f, dst)


def cmd_init(args):
    if CONFIG.exists():
        sys.exit(f"{CONFIG} 已存在；要刷新托管文件请用 update")
    name = args.name or args.repo.split("/")[-1]
    default_desc = f"{name} 文档中心。内容直接来自仓库里的 Markdown，与代码同步更新。"
    cfg = {
        "repo": args.repo,
        "name": name,
        "emoji": args.emoji,
        "description": args.description or default_desc,
        "branch": args.branch,
        "themeKey": (args.theme_key or f"{name.lower()}-theme"),
        "version": 1,
    }

    write_file(CONFIG, json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", True)

    # 内容骨架：只在缺失时创建（docs/ 根 = 中文）
    for name_ in CONTENT_FILES:
        text = render((TEMPLATE / name_).read_text(encoding="utf-8"), cfg)
        if write_file(Path("docs") / name_, text, overwrite=False):
            print(f"  + docs/{name_}")

    # 英文镜像：docs/en/
    for name_ in EN_CONTENT_FILES:
        src = TEMPLATE / "en" / name_
        if not src.exists():
            continue
        text = render(src.read_text(encoding="utf-8"), cfg)
        if write_file(Path("docs") / "en" / name_, text, overwrite=False):
            print(f"  + docs/en/{name_}")

    # 老项目接入：已有的非 docsite 托管文件先备份，不静默覆盖
    for tpl, dst in MANAGED.items():
        d = Path(dst)
        if d.exists() and not is_managed(d):
            bak = Path(str(d) + ".docsite.bak")
            shutil.copy2(d, bak)
            print(f"  ! {dst} 已存在（非 docsite 托管），已备份为 {bak}，核对后删除")
        text = render((TEMPLATE / tpl).read_text(encoding="utf-8"), cfg)
        write_file(d, text, overwrite=True)
        print(f"  + {dst}")

    # 老项目可能用别的文件名部署 Pages（如 static.yml），不删，只提示
    wf_dir = Path(".github/workflows")
    if wf_dir.exists():
        for wf in sorted(wf_dir.glob("*.yml")):
            if wf.name == "docs.yml":
                continue
            txt = wf.read_text(encoding="utf-8", errors="ignore")
            if "deploy-pages" in txt or "upload-pages-artifact" in txt:
                print(f"  ! 发现另一个 Pages workflow：{wf}，确认新流程正常后请删除，避免重复部署")

    copy_vendor(overwrite=True)
    write_file(Path("docs/.nojekyll"), "", overwrite=True)
    print(f"  + docs/assets/vendor/（docsify + 主题 + 搜索）")

    print(f"""
完成。接下来：
  1. 在 docs/ 里写 Markdown，把页面加进 docs/_sidebar.md
  2. git add -A && git commit && git push
  3. 推送后 workflow 自动部署；仓库 Settings → Pages 选 GitHub Actions
     （首次 configure-pages 一般会自动设好）
站点地址：https://{cfg['repo'].split('/')[0]}.github.io/{cfg['repo'].split('/')[1]}/
以后升级模板：python3 /path/to/docsite/docsite.py update""")


def cmd_update(_args):
    if not CONFIG.exists():
        sys.exit("找不到 .docsite.json，请先在仓库根运行 init")
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

    for tpl, dst in MANAGED.items():
        text = render((TEMPLATE / tpl).read_text(encoding="utf-8"), cfg)
        write_file(Path(dst), text, overwrite=True)
        print(f"  ~ {dst}")

    copy_vendor(overwrite=True)
    write_file(Path("docs/.nojekyll"), "", overwrite=True)
    print("  ~ docs/assets/vendor/ 已同步")
    print("完成。Markdown 内容未改动，检查 diff 后提交即可。")


def cmd_check(args):
    """跨仓库校验下载页生成链路是否与模板一致。

    只有这几个文件要求完全相同；index.html 等允许各仓库有差异，故不参与比对。
    """
    if args.all:
        base = Path(args.all)
        if not base.is_dir():
            sys.exit(f"{base} 不是目录")
        roots = sorted(p for p in base.iterdir() if (p / ".git").is_dir())
    else:
        roots = [Path(p) for p in (args.paths or ["."])]

    rows = []
    for root in roots:
        for tpl, dst in SYNCED.items():
            tpl_path = TEMPLATE / tpl
            if not tpl_path.exists():
                rows.append((root.name, dst, "TEMPLATE_MISSING", "-"))
                continue
            want = tpl_path.read_text(encoding="utf-8").rstrip()
            target = root / dst
            if not target.exists():
                rows.append((root.name, dst, "MISSING", "-"))
                continue
            got = target.read_text(encoding="utf-8", errors="ignore")
            if got.rstrip() == want:
                rows.append((root.name, dst, "ok", ""))
            else:
                note = "被手改或版本落后" if "docsite-managed-file:" in got else "缺少 docsite marker"
                rows.append((root.name, dst, "DRIFT", note))

    if not rows:
        print("没有可比对的仓库")
        return 0

    w1 = max(len(r[0]) for r in rows)
    w2 = max(len(r[1]) for r in rows)
    for name, dst, status, note in rows:
        mark = "✅" if status == "ok" else "❌"
        print(f"{mark} {name:<{w1}}  {dst:<{w2}}  {status:<16} {note}")

    bad = [r for r in rows if r[2] != "ok"]
    print(f"\n{len(rows) - len(bad)}/{len(rows)} 一致")
    if bad:
        print("修复：在对应仓库根运行 `python3 docsite.py update`，检查 diff 后提交。")
        return 1
    return 0


def main():
    if not TEMPLATE.exists():
        sys.exit(f"找不到模板目录 {TEMPLATE}")
    p = argparse.ArgumentParser(description="docsify 文档站脚手架")
    sub = p.add_subparsers(dest="cmd", required=True)

    i = sub.add_parser("init", help="在当前仓库初始化文档站")
    i.add_argument("--repo", required=True, help="GitHub 仓库，形如 owner/name")
    i.add_argument("--name", help="站点显示名，默认取仓库名")
    i.add_argument("--emoji", default="📘", help="favicon 与站名 emoji，默认 📘")
    i.add_argument("--description", help="meta description，默认「<name> 文档中心……」")
    i.add_argument("--branch", default="main", help="触发部署的分支，默认 main")
    i.add_argument("--theme-key", help="localStorage 主题 key，默认 <name>-theme")
    i.set_defaults(func=cmd_init)

    u = sub.add_parser("update", help="按最新模板刷新托管文件")
    u.set_defaults(func=cmd_update)

    c = sub.add_parser("check", help="校验下载页生成链路是否与模板一致")
    c.add_argument("paths", nargs="*", help="仓库路径，默认当前目录")
    c.add_argument("--all", help="扫描该目录下所有 git 仓库")
    c.set_defaults(func=cmd_check)

    args = p.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
