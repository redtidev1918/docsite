#!/usr/bin/env python3
"""docsite — 一行依赖都没有的 docsify 文档站脚手架。

    python3 docsite.py init --repo owner/name [--name 名] [--emoji 📘] [--branch main]
    python3 docsite.py update
    python3 docsite.py check [仓库路径 ...] [--all 父目录]
    python3 docsite.py navcheck [仓库路径 ...] [--all 父目录]

init      在当前仓库生成 docs/ 与 Pages 部署 workflow。
update    只刷新托管文件（index.html / workflow / vendor / 下载页生成链路），
          永远不动你写的 Markdown。
check     校验各仓库的「下载页生成链路」是否与模板逐字节一致（缺文件 / 被手改 / 版本落后）。
navcheck  校验导航信息架构规约（确定性规则：语言侧边栏分离、无页内锚点、
          无重复链接、en 侧边栏存在；单页面分类等软规则仅 warning）。

统一文档规范：中文为默认（README.md / docs/），英文镜像放 README.en.md / docs/en/；
语言是站点维度——docs/_sidebar.md 与 docs/en/_sidebar.md 各自只显示当前语言。
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
EN_CONTENT_FILES = ["_sidebar.md", "README.md", "QUICKSTART.md", "download.md"]
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


def other_pages_workflow(dst):
    """返回同一目录下另一个 Pages 部署 workflow 的文件名（没有则 None）。

    历史仓库沿用了 GitHub 默认模板名 static.yml。此时不再写入托管的 docs.yml，
    否则同一个仓库会出现两个 Pages 部署工作流，互相覆盖。
    """
    wf_dir = dst.parent
    if not wf_dir.is_dir():
        return None
    for f in sorted(wf_dir.glob("*.y*ml")):
        if f.name == dst.name:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        if "upload-pages-artifact" in text or "deploy-pages" in text:
            return f.name
    return None


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
        if d.name == "docs.yml":
            other = other_pages_workflow(d)
            if other:
                print(f"  = 已有 Pages workflow {other}，跳过托管 {dst}（避免重复部署）")
                continue
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
        d = Path(dst)
        if d.name == "docs.yml":
            other = other_pages_workflow(d)
            if other:
                print(f"  = 已有 Pages workflow {other}，跳过托管 {dst}（避免重复部署）")
                continue
        text = render((TEMPLATE / tpl).read_text(encoding="utf-8"), cfg)
        write_file(d, text, overwrite=True)
        print(f"  ~ {dst}")

    copy_vendor(overwrite=True)
    write_file(Path("docs/.nojekyll"), "", overwrite=True)
    print("  ~ docs/assets/vendor/ 已同步")
    print("完成。Markdown 内容未改动，检查 diff 后提交即可。")


def cmd_check(args):
    """跨仓库校验下载页生成链路是否与模板一致。

    只有这几个文件要求完全相同；index.html 等允许各仓库有差异，故不参与比对。

    语言命名规范只约束人工维护的 README / docs 内容。机器生成、行业约定或合规类
    文件（CHANGELOG.md、THIRD_PARTY_NOTICES.md、LICENSE、SECURITY.md 等）允许保留
    canonical 文件名与原始语言，翻译副本可用 .zh-CN.md / .en.md —— 不视为违规，
    本检查器也因此不扫描它们（graf 的 CHANGELOG*.md 是有意保留的特例，不是技术债）。
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
        # 不是文档站（既无 docs/ 也无 .github/pages/）：例如 docsite 脚手架自身。
        if not (root / "docs").is_dir() and not (root / ".github" / "pages").is_dir():
            rows.append((root.name, "—", "skipped", "不是文档站"))
            continue
        # 未采用托管生成器：下载页为手写，不参与比对（约定允许 npm/PyPI 类仓库手写）。
        if not any((root / dst).exists() for dst in SYNCED.values()):
            rows.append((root.name, "—", "n/a", "未使用托管生成器（手写下载页）"))
            continue
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
    marks = {"ok": "✅", "n/a": "➖", "skipped": "➖"}
    for name, dst, status, note in rows:
        mark = marks.get(status, "❌")
        print(f"{mark} {name:<{w1}}  {dst:<{w2}}  {status:<16} {note}")

    bad = [r for r in rows if r[2] not in ("ok", "n/a", "skipped")]
    checked = [r for r in rows if r[2] not in ("n/a", "skipped")]
    print(f"\n{len(checked) - len(bad)}/{len(checked)} 一致"
          f"（{len(rows) - len(checked)} 项不参与比对）")
    if bad:
        print("修复：在对应仓库根运行 `python3 docsite.py update`，检查 diff 后提交。")
        return 1
    return 0


NAV_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _nav_config(root):
    """读取仓库的显式导航例外配置（.docsite.json 的 navigation 字段）。

    未配置时全部为 False：检查器按默认规约执行，绝不静默忽略。
    """
    cfg = root / ".docsite.json"
    nav = {}
    if cfg.exists():
        try:
            nav = json.loads(cfg.read_text(encoding="utf-8")).get("navigation") or {}
        except json.JSONDecodeError:
            pass
    return {
        "allowSidebarAnchors": bool(nav.get("allowSidebarAnchors")),
        "allowCombinedLocales": bool(nav.get("allowCombinedLocales")),
    }


def _sidebar_items(text):
    """解析 sidebar：返回 [(indent, label, target)]。

    target 仅在条目是真正的 Markdown 链接（含 `](`）时非 None；
    纯分类标题（如 `- Production (Serverless)`）target 为 None，避免括号误判。
    外部链接返回其 URL。
    """
    items = []
    for line in text.splitlines():
        m = re.match(r"^(\s*)-\s+(.*)$", line)
        if not m:
            continue
        indent = len(m.group(1)) // 2
        label = m.group(2)
        lm = re.match(r"^(.*\])\(([^)]+)\)\s*$", label)
        if lm:
            items.append((indent, lm.group(1)[1:-1].strip(), lm.group(2).strip()))
        else:
            items.append((indent, label, None))
    return items


def _is_external(target):
    return target.startswith(("http://", "https://", "mailto:"))


def _navcheck_sidebar(name, path, is_en, cfg, issues):
    text = path.read_text(encoding="utf-8", errors="ignore")
    items = _sidebar_items(text)
    seen = {}
    # 分类密度：统计每个顶级分类下的直接子条目（内部页与外部链接都算）
    roots = []
    current = None
    for indent, label, target in items:
        if target is None and indent == 0:
            current = (label, [])
            roots.append(current)
        elif current is not None and indent >= 1 and target is not None:
            current[1].append(target)
        elif target is not None:
            current = None  # 顶级裸链接页，不算分类

    for indent, label, target in items:
        if target is None or _is_external(target):
            continue
        # 锚点被显式允许时（如 CDN 壳的单 README 站点），仅锚点不同的两项是合法的不同导航项
        key = target if cfg["allowSidebarAnchors"] else target.split("#")[0].rstrip("/") or "/"
        if key in seen:
            issues.append((name, "DUPLICATE_LINK", f"`{target}` 与 `{seen[key]}` 重复", "error"))
        else:
            seen[key] = target
        if "#" in target and not cfg["allowSidebarAnchors"]:
            issues.append((name, "ANCHOR_LINK", f"`{target}` —— 侧边栏不做页内目录", "error"))
        if not target.startswith("/"):
            issues.append((name, "NOT_ROOT_ABSOLUTE", f"`{target}` 非根绝对路径", "warning"))
        if is_en and not target.startswith("/en/"):
            if not re.search(r"中文|Chinese", label):
                issues.append((name, "EN_SIDEBAR_ZH_LINK",
                               f"`{label}` 指向非 /en/ 页面且未标注（中文）", "warning"))
    if not is_en and not cfg["allowCombinedLocales"]:
        for indent, label, target in items:
            # 标注「（英文）」的单条 fallback 链接允许（规则 20 的对称场景：
            # 页面仅有英文版时，中文侧边栏可显式标注后指向它）；整棵英文树仍然禁止
            if (target and not _is_external(target) and target.startswith("/en/")
                    and not re.search(r"英文|English", label)):
                issues.append((name, "COMBINED_LOCALES",
                               f"`{label}` —— 语言是站点维度，英文树应放 /en/_sidebar.md；"
                               "确需指向英文页必须在标题中标注（英文）", "error"))
                break
    for label, children in roots:
        if len(children) == 1:
            issues.append((name, "SINGLE_PAGE_CATEGORY",
                           f"「{label}」只有 1 个页面，考虑并入相邻分类", "warning"))
    if not is_en and not cfg["allowCombinedLocales"]:
        for indent, label, target in items:
            # 标注「（英文）」的单条 fallback 链接允许（规则 20 的对称场景：
            # 页面仅有英文版时，中文侧边栏可显式标注后指向它）；整棵英文树仍然禁止
            if target and target.startswith("/en/") and not re.search(r"英文|English", label):
                issues.append((name, "COMBINED_LOCALES",
                               f"`{label}` —— 语言是站点维度，英文树应放 /en/_sidebar.md；"
                               "确需指向英文页必须在标题中标注（英文）", "error"))
                break
    for label, children in roots:
        if len(children) == 1:
            issues.append((name, "SINGLE_PAGE_CATEGORY",
                           f"「{label}」只有 1 个页面，考虑并入相邻分类", "warning"))


def cmd_navcheck(args):
    """校验导航信息架构规约（确定性规则；主观的「分类好不好」不在检查范围）。

    error（返回非零）：
      COMBINED_LOCALES   根 sidebar 出现 /en/ 文档树（语言是站点维度，不是导航分类）
      EN_SIDEBAR_MISSING 有 docs/en/ 页面但缺 docs/en/_sidebar.md
      ANCHOR_LINK        sidebar 出现页内锚点（首页目录混入导航；可用
                         .docsite.json navigation.allowSidebarAnchors 显式豁免）
      DUPLICATE_LINK     同一目标在同一 sidebar 出现多次
      GLOBAL_SIDEBAR_ALIAS  index.html 用 '/.*/_sidebar.md' 通配 alias 强制根侧边栏
                         （破坏分语言导航，docsify 原生按目录解析即可，无需 alias）
    warning（仅提示，不影响退出码）：
      SINGLE_PAGE_CATEGORY 顶级分类只有 1 个页面
      NOT_ROOT_ABSOLUTE   本地链接未用根绝对路径
      EN_SIDEBAR_ZH_LINK  英文 sidebar 指向中文页面且未标注（中文）
      HEADING_INJECTION   index.html 配置 subMaxLevel，页内标题被注入 sidebar 渲染
    例外必须写入仓库 .docsite.json 的 navigation 字段，检查器不静默忽略。
    """
    if args.all:
        base = Path(args.all)
        if not base.is_dir():
            sys.exit(f"{base} 不是目录")
        roots = sorted(p for p in base.iterdir() if (p / ".git").is_dir())
    else:
        roots = [Path(p) for p in (args.paths or ["."])]

    any_error = False
    checked = 0
    for root in roots:
        zh = root / "docs/_sidebar.md"
        if not zh.is_file():
            zh = root / ".github/pages/_sidebar.md"
        if not zh.is_file():
            continue  # 无导航的仓库（如 docsite 自身）不参与
        checked += 1
        cfg = _nav_config(root)
        issues = []
        _navcheck_sidebar(root.name, zh, is_en=False, cfg=cfg, issues=issues)
        en = root / "docs/en/_sidebar.md"
        en_pages = [p for p in (root / "docs/en").glob("*.md")] if (root / "docs/en").is_dir() else []
        # 英文内容在根 README.en.md 的 CDN 壳仓（已声明 allowCombinedLocales）不要求 en sidebar
        if en_pages and not en.is_file() and not cfg["allowCombinedLocales"]:
            issues.append((f"{root.name}/en", "EN_SIDEBAR_MISSING",
                           "docs/en/ 有页面但没有 docs/en/_sidebar.md", "error"))
        elif en.is_file():
            _navcheck_sidebar(f"{root.name}/en", en, is_en=True, cfg=cfg, issues=issues)

        # 明显旧结构：外壳配置检查（确定性）
        shell = root / "docs/index.html"
        if shell.is_file():
            stext = shell.read_text(encoding="utf-8", errors="ignore")
            # 匹配真实配置形态（键: 值），避免把文档/注释里的反例文字误报
            if re.search(r"/\.\*/_sidebar\.md\s*['\"]\s*:\s*['\"]/_sidebar\.md", stext):
                issues.append((root.name, "GLOBAL_SIDEBAR_ALIAS",
                               "index.html 配置了 '/.*/_sidebar.md' 通配 alias，会把 /en/ 页面"
                               "静默改写回根侧边栏，破坏分语言导航", "error"))
            if re.search(r"subMaxLevel\s*:", stext):
                issues.append((root.name, "HEADING_INJECTION",
                               "index.html 配置了 subMaxLevel，当前页标题会被注入 sidebar 渲染", "warning"))

        if not issues:
            print(f"✅ {root.name}")
            continue
        errors = [i for i in issues if i[3] == "error"]
        warns = [i for i in issues if i[3] == "warning"]
        for name, rule, note, level in issues:
            mark = "❌" if level == "error" else "⚠️ "
            print(f"{mark} {name:<22} {rule:<20} {note}")
        if errors:
            any_error = True

    print(f"\n{checked} 个仓库参与导航检查；error 以 ❌ 标出，warning 仅提示。")
    if any_error:
        print("修复参考：docsite README「导航与信息架构」；显式例外写入 .docsite.json 的 navigation 字段。")
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

    n = sub.add_parser("navcheck", help="校验导航信息架构规约（确定性规则）")
    n.add_argument("paths", nargs="*", help="仓库路径，默认当前目录")
    n.add_argument("--all", help="扫描该目录下所有 git 仓库")
    n.set_defaults(func=cmd_navcheck)

    args = p.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
