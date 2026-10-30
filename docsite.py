#!/usr/bin/env python3
"""docsite — 轻量级文档网站生成器:VitePress 管渲染,本脚本管工程。

    python3 docsite.py init --repo owner/name [--name 名] [--emoji 📘] [--branch main]
    python3 docsite.py update
    python3 docsite.py migrate [路径] [--dry-run]
    python3 docsite.py build | preview | dev
    python3 docsite.py check [仓库路径 ...] [--all 父目录]
    python3 docsite.py navcheck [仓库路径 ...] [--all 父目录]

分工:VitePress 管网站(渲染/路由/主题/搜索/导航),docsite 管工程(init/update/
migrate/build/preview、配置、下载页、质量检查),GitHub Pages 管托管。

init      接入 VitePress(v2):依赖清单、config、部署 workflow、内容骨架。
update    只刷新托管文件(package.json/lock、config.mts、sidebar、workflow、下载页链路),
          永远不动你写的 Markdown。
migrate   把 docsite 托管的 Docsify 旧形态安全迁移到 v2(备份先行、--dry-run、
          `#/` hash 链接与壳形态 /docs/ 前缀改写;旧文件清理是构建验证后的独立人工步骤)。
build/preview/dev   包装 npm run docs:*(渲染交给 VitePress CLI)。
check     托管文件与模板一致性(下载页链路逐字节;v2 另查依赖/渲染/生成一致性)。
navcheck  导航信息架构规约(v2 与 v1 双规则表;语言是站点维度、无重复、链接指真实页面)。

统一文档规范:中文为默认(docs/),英文镜像放 docs/en/;语言是站点维度——
docs/_sidebar.md 与 docs/en/_sidebar.md 各自只显示当前语言;侧边栏只维护
_sidebar.md,docs/.vitepress/sidebar.generated.mjs 由 update 重新生成。
配置存在仓库根的 .docsite.json(v2 含 engine/engineVersion);模板取自本脚本
旁边的 template/ 目录。旧 Docsify 形态(docs/ 或 .github/pages/ 外壳)在
migrate 之前继续被 update/check/navcheck 支持(向后兼容,D-005)。
"""
import argparse
import json
import re
import shutil
import subprocess
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
# 站点外壳放哪：新仓库用 docs/ 自身；老仓库（NekoTime / ludum / paranote /
# pixiv-token-getter / telepress）把 docsify 外壳放在 .github/pages/，由 static.yml
# 把外壳与 docs/ 内容拼成 _site 再发布。两种形态都由 init/update 托管。
SHELL_DIRS = (Path("docs"), Path(".github/pages"))


def shell_dir():
    return next((d for d in SHELL_DIRS if (d / "index.html").is_file()), SHELL_DIRS[0])


def vendor_dir():
    return shell_dir() / "assets" / "vendor"


def managed_files():
    """init/update 都由模板渲染的托管文件；index.html 跟随实际外壳目录。"""
    return {
        "index.html": shell_dir() / "index.html",
        "docs.yml": Path(".github/workflows/docs.yml"),
        **{tpl: Path(dst) for tpl, dst in SYNCED.items()},
    }


def render(text, cfg):
    tokens = {
        "NAME": cfg["name"],
        "EMOJI": cfg["emoji"],
        "DESCRIPTION": cfg.get(
            "description",
            f"{cfg['name']} 文档中心。内容直接来自仓库里的 Markdown，与代码同步更新。",
        ),
        # v2 配置不再写 themeKey(Docsify 专属);模板用到时给空串
        "THEME_KEY": cfg.get("themeKey", ""),
        "REPO": cfg["repo"],
        "BRANCH": cfg.get("branch", "main"),
    }
    def sub(m):
        return tokens[m.group(1)]
    return re.sub(r"@@([A-Z_]+)@@", sub, text)


# ---------------------------------------------------------------------------
# VitePress(v2 引擎)托管文件的渲染与生成。
# config.mts 的 token 全部处于 JS 单引号字符串上下文,一律转义(D-005:
# 未校验的用户字符串不得拼进 JS);base 由 repo 推导,不接受配置覆盖。
VP_CONFIG_REL = Path("docs/.vitepress/config.mts")
VP_SIDEBAR_REL = Path("docs/.vitepress/sidebar.generated.mjs")
VP_SIDEBAR_HEADER = (
    "// docsite: managed file — generated from _sidebar.md, do not edit.\n"
    "// 导航只维护 docs/_sidebar.md 与 docs/en/_sidebar.md;"
    "运行 `python3 docsite.py update` 会按它们重新生成本文件。\n"
)


def _js_escape(s):
    """JS 单引号字符串上下文的最小转义(config.mts 里的 '@@TOKEN@@')。"""
    return s.replace("\\", "\\\\").replace("'", "\\'").replace("\r", "").replace("\n", "\\n")


def _base_for(repo):
    """GitHub Pages 路径:用户/组织站点 <owner>.github.io 部署在根,其余挂 /<repo>/。"""
    name = repo.split("/")[-1]
    return "/" if name.endswith(".github.io") else f"/{name}/"


def render_config(text, cfg):
    """渲染 config.mts 模板;token 值先过单引号转义再进模板。"""
    tokens = {
        "NAME": cfg["name"],
        "EMOJI": cfg["emoji"],
        "DESCRIPTION": cfg.get(
            "description",
            f"{cfg['name']} 文档中心。内容直接来自仓库里的 Markdown，与代码同步更新。",
        ),
        "REPO": cfg["repo"],
        "BASE": _base_for(cfg["repo"]),
    }
    def sub(m):
        return _js_escape(tokens[m.group(1)])
    return re.sub(r"@@([A-Z_]+)@@", sub, text)


def _vp_link(target):
    """Docsify 侧边栏链接 → VitePress 路由:根绝对 .md 去后缀;外部链接原样。"""
    if target is None or _is_external(target):
        return target
    page, _, anchor = target.partition("#")
    if page.endswith(".md"):
        page = page[: -len(".md")]
    return f"{page}#{anchor}" if anchor else page


def _vitepress_sidebar(items):
    """_sidebar_items() 的条目 → VitePress SidebarItem 树。

    规范形态是两级:顶级分类(无链接)成组,其余条目为叶子归入最近的组;
    更深的层级按同规则嵌套(防御性处理,规范本身不使用)。
    """
    root = []
    stack = [root]
    for indent, label, target in items:
        depth = min(indent, len(stack) - 1)
        del stack[depth + 1:]
        if target is None:
            group = {"text": label, "items": []}
            stack[depth].append(group)
            stack.append(group["items"])
        else:
            stack[depth].append({"text": label, "link": _vp_link(target)})
    return root


def sidebar_module_text(root):
    """由 docs/_sidebar.md(+ docs/en/_sidebar.md)生成 sidebar.generated.mjs 全文。"""
    root = Path(root)
    tree = {}
    for prefix, rel in (("/", "docs/_sidebar.md"), ("/en/", "docs/en/_sidebar.md")):
        path = root / rel
        if path.is_file():
            tree[prefix] = _vitepress_sidebar(
                _sidebar_items(path.read_text(encoding="utf-8", errors="ignore")))
    return (VP_SIDEBAR_HEADER
            + "export default " + json.dumps(tree, ensure_ascii=False, indent=2) + "\n")


def write_sidebars(root="."):
    """重新生成 docs/.vitepress/sidebar.generated.mjs(init/update 与迁移时调用)。"""
    root = Path(root)
    dst = root / VP_SIDEBAR_REL
    dst.parent.mkdir(parents=True, exist_ok=True)
    write_file(dst, sidebar_module_text(root), overwrite=True)
    return dst


def is_vitepress(root):
    """仓库是否已是 VitePress(v2)形态:以 config.mts 在场为准(比配置字段更实在)。"""
    return (Path(root) / VP_CONFIG_REL).is_file()


# v2 托管文件:模板相对路径 → 仓库相对路径。
# package.json/lock 逐字节下发(无 token),全仓库版本一致;config.mts/docs.yml 渲染。
V2_MANAGED = {
    "package.json": Path("package.json"),
    "package-lock.json": Path("package-lock.json"),
    ".github/workflows/docs.yml": Path(".github/workflows/docs.yml"),
}
GITIGNORE_ENTRIES = ["node_modules/", "docs/.vitepress/dist/", "docs/.vitepress/cache/"]


def engine_version():
    """模板锁定的 VitePress 版本(写进各仓库 .docsite.json 的 engineVersion)。"""
    pkg = json.loads((TEMPLATE / "package.json").read_text(encoding="utf-8"))
    return pkg["devDependencies"]["vitepress"]


def _ensure_gitignore(root):
    """把 node/dist/cache 三行补进 .gitignore(已有条目不重复,不覆盖用户内容)。"""
    gi = Path(root) / ".gitignore"
    lines = gi.read_text(encoding="utf-8").splitlines() if gi.is_file() else []
    missing = [e for e in GITIGNORE_ENTRIES if e not in lines]
    if not missing:
        return []
    add = ([""] if lines and lines[-1].strip() else []) + missing
    with gi.open("a", encoding="utf-8", newline="") as f:
        f.write("\n".join(add) + "\n")
    return missing


def _write_v2_managed(cfg, root=".", verbose=True):
    """写入 v2 托管文件(init/update/migrate 共用);用户 Markdown 永不触碰。"""
    root = Path(root)
    wrote = []
    # init/update/migrate 都保护首次接管的文件;已有备份不可被静默覆盖。
    for rel in list(V2_MANAGED.values()) + [VP_CONFIG_REL, VP_SIDEBAR_REL] + [Path(p) for p in SYNCED.values()]:
        target = root / rel
        template_rel = next((tpl for tpl, dst in V2_MANAGED.items() if dst == rel), None)
        same_template = template_rel and target.is_file() and target.read_bytes() == (TEMPLATE / template_rel).read_bytes()
        if target.is_file() and not is_managed(target) and not same_template:
            _backup_file(target)
    # package.json/lock 逐字节下发(无 token),保证全仓库依赖版本一致
    for tpl in ("package.json", "package-lock.json"):
        rel = V2_MANAGED[tpl]
        write_file(root / rel, (TEMPLATE / tpl).read_text(encoding="utf-8"), overwrite=True)
        wrote.append(rel)

    # 部署 workflow:同目录已有别的 Pages workflow(如 static.yml)时跳过,避免双部署
    wf_dst = root / V2_MANAGED[".github/workflows/docs.yml"]
    other = other_pages_workflow(wf_dst)
    if other:
        print(f"  = 已有 Pages workflow {other},跳过托管 {wf_dst}(避免重复部署;"
              "删除旧 workflow 后重新运行即可下发)")
    else:
        src = TEMPLATE / ".github/workflows/docs.yml"
        write_file(wf_dst, render(src.read_text(encoding="utf-8"), cfg), overwrite=True)
        wrote.append(V2_MANAGED[".github/workflows/docs.yml"])

    # config.mts 走 JS 转义渲染;sidebar 由 _sidebar.md 重新生成
    write_file(root / VP_CONFIG_REL,
               render_config((TEMPLATE / "docs/.vitepress/config.mts").read_text(encoding="utf-8"), cfg),
               overwrite=True)
    wrote.append(VP_CONFIG_REL)
    write_sidebars(root)
    wrote.append(VP_SIDEBAR_REL)
    write_file(root / "docs/public/.nojekyll", "", overwrite=True)
    wrote.append(Path("docs/public/.nojekyll"))
    for tpl, rel in SYNCED.items():
        write_file(root / rel, (TEMPLATE / tpl).read_text(encoding="utf-8"), overwrite=True)
        wrote.append(Path(rel))
    added_gi = _ensure_gitignore(root)

    if verbose:
        for rel in wrote:
            print(f"  ~ {rel}")
        for entry in added_gi:
            print(f"  + .gitignore: {entry}")
        print("  依赖清单已按模板锁定;提交前运行 `npm install`(或 npm ci)同步本地 node_modules")
    return wrote


def _v2_config(cfg):
    """v2 配置字段:engine/engineVersion 固定,version 升 2(其余字段原样保留)。"""
    out = dict(cfg)
    out["engine"] = "vitepress"
    out["engineVersion"] = engine_version()
    out["version"] = 2
    return out


def origin_slug():
    """从 git remote 推断 owner/name；老仓库的 .docsite.json 可能只声明 navigation。"""
    try:
        out = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], text=True, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?\s*$", out.strip())
    return f"{m.group(1)}/{m.group(2)}" if m else None


def with_defaults(cfg):
    """补全渲染所需字段；缺失值按 git remote / 仓库名推导，绝不覆盖已写死的配置。"""
    slug = cfg.get("repo") or origin_slug() or "owner/name"
    name = cfg.get("name") or slug.split("/")[-1]
    cfg.setdefault("repo", slug)
    cfg.setdefault("name", name)
    cfg.setdefault("emoji", "📘")
    cfg.setdefault("description", f"{name} 文档中心。内容直接来自仓库里的 Markdown，与代码同步更新。")
    cfg.setdefault("themeKey", f"{name.lower().replace(' ', '-')}-theme")
    cfg.setdefault("branch", "main")
    return cfg


def is_managed(path):
    """判断已有文件是否为 docsite 下发。

    三种标记:注释串(`docsite: managed file`)、脚本 marker 行
    (`docsite-managed-file:`)、package.json 的 JSON 字段(`"docsite-managed-file"`)。
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    return ("docsite: managed file" in text[:400]
            or "docsite-managed-file:" in text
            or '"docsite-managed-file"' in text[:400])


def default_branch(root):
    """origin/HEAD 指向的分支名；远端信息缺失时返回 None（不猜）。"""
    try:
        ref = subprocess.check_output(
            ["git", "-C", str(root), "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return ref.split("/", 1)[1] if "/" in ref else ref


def off_default_branch(root):
    """本地 checkout 停在功能分支时返回分支名——这种漂移是本地状态，不是仓库问题。
    托管文件只保证默认分支一致（CI 就是克隆默认分支跑）。"""
    try:
        current = subprocess.check_output(
            ["git", "-C", str(root), "symbolic-ref", "--short", "HEAD"],
            text=True, stderr=subprocess.DEVNULL).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None  # detached HEAD 或不是 git 仓库，不在这里判断
    default = default_branch(root)
    return current if default and current != default else None


def write_file(path, text, overwrite):
    if path.exists() and not overwrite:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    # newline="":不做平台换行翻译,托管文件跨平台字节一致(SYNCED 依赖这一点)
    path.write_text(text, encoding="utf-8", newline="")
    return True


def _backup_file(path):
    """保留所有历史备份,重复执行也不覆盖原始内容。"""
    backup = Path(str(path) + ".docsite.bak")
    serial = 1
    while backup.exists():
        backup = Path(str(path) + f".{serial}.docsite.bak")
        serial += 1
    shutil.copy2(path, backup)
    print(f"  ! {path} 已备份为 {backup};请核对并合并自定义 scripts/依赖等字段")
    return backup


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
    target = vendor_dir()
    target.mkdir(parents=True, exist_ok=True)
    for f in src.iterdir():
        dst = target / f.name
        if overwrite or not dst.exists():
            shutil.copy2(f, dst)


def cmd_init(args):
    if CONFIG.exists():
        sys.exit(f"{CONFIG} 已存在；要刷新托管文件请用 update")
    # 已有 docsite 托管的 Docsify 旧壳:那是迁移场景,不是全新接入
    for legacy in (Path("docs/index.html"), Path(".github/pages/index.html")):
        if legacy.is_file() and is_managed(legacy):
            sys.exit(f"检测到旧 Docsify 外壳 {legacy}；请改用 `python3 docsite.py migrate`")
    name = args.name or args.repo.split("/")[-1]
    default_desc = f"{name} 文档中心。内容直接来自仓库里的 Markdown，与代码同步更新。"
    cfg = _v2_config({
        "repo": args.repo,
        "name": name,
        "emoji": args.emoji,
        "description": args.description or default_desc,
        "branch": args.branch,
    })
    if args.theme_key:
        cfg["themeKey"] = args.theme_key  # v1 兼容参数,仅为显式传入时保留

    write_file(CONFIG, json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", True)

    # 内容骨架:只在缺失时创建(docs/ 根 = 中文,镜像在 docs/en/)
    for base in (Path("docs"), Path("docs/en")):
        src_dir = TEMPLATE / "docs" if base == Path("docs") else TEMPLATE / "docs/en"
        for src in sorted(src_dir.glob("*.md")):
            text = render(src.read_text(encoding="utf-8"), cfg)
            if write_file(base / src.name, text, overwrite=False):
                print(f"  + {base / src.name}")

    _write_v2_managed(cfg)

    print(f"""
完成。接下来：
  1. npm install        （或 npm ci;需要 Node.js 22+）
  2. 在 docs/ 里写 Markdown，把页面加进 docs/_sidebar.md
  3. python3 docsite.py build && python3 docsite.py preview   本地验收
  4. git add -A && git commit && git push
     推送后 workflow 自动构建部署；仓库 Settings → Pages 选 GitHub Actions
站点地址：https://{cfg['repo'].split('/')[0]}.github.io/{cfg['repo'].split('/')[1]}/
以后升级模板：python3 /path/to/docsite/docsite.py update""")


def cmd_update(_args):
    if not CONFIG.exists():
        sys.exit("找不到 .docsite.json，请先在仓库根运行 init")
    cfg = with_defaults(json.loads(CONFIG.read_text(encoding="utf-8")))

    if is_vitepress("."):
        print("VitePress(v2)托管文件刷新:")
        _write_v2_managed(cfg)
        print("完成。Markdown 内容未改动，检查 diff 后提交即可。")
        return

    for tpl, d in managed_files().items():
        if d.name == "docs.yml":
            other = other_pages_workflow(d)
            if other:
                print(f"  = 已有 Pages workflow {other}，跳过托管 {d}（避免重复部署）")
                continue
        text = render((TEMPLATE / tpl).read_text(encoding="utf-8"), cfg)
        write_file(d, text, overwrite=True)
        print(f"  ~ {d}")

    copy_vendor(overwrite=True)
    write_file(shell_dir() / ".nojekyll", "", overwrite=True)
    print(f"  ~ {vendor_dir()}/ 已同步")
    print("完成。Markdown 内容未改动，检查 diff 后提交即可。")


def _check_v2_files(root):
    """v2 仓库的托管文件一致性:逐字节(依赖清单)、再渲染(workflow/config)、
    再生成(sidebar)、token 无残留、.nojekyll 与 .gitignore 就位。"""
    rows = []
    cfg = with_defaults(json.loads((root / CONFIG).read_text(encoding="utf-8")))

    for tpl in ("package.json", "package-lock.json"):
        rel = str(V2_MANAGED[tpl])
        want = (TEMPLATE / tpl).read_text(encoding="utf-8")
        target = root / V2_MANAGED[tpl]
        if not target.is_file():
            rows.append((root.name, rel, "MISSING", "-"))
        elif target.read_text(encoding="utf-8", errors="ignore") != want:
            rows.append((root.name, rel, "DRIFT", "被手改或版本落后"))
        else:
            rows.append((root.name, rel, "ok", ""))

    # docs.yml:再渲染逐字比对(存在性由下发保证;被别的 Pages workflow 挡住时会缺失)
    wf_rel = str(V2_MANAGED[".github/workflows/docs.yml"])
    wf_dst = root / V2_MANAGED[".github/workflows/docs.yml"]
    if other_pages_workflow(wf_dst):
        rows.append((root.name, wf_rel, "n/a", "存在其他 Pages workflow,docs.yml 未下发"))
    elif not wf_dst.is_file():
        rows.append((root.name, wf_rel, "MISSING", "-"))
    elif wf_dst.read_text(encoding="utf-8", errors="ignore") != \
            render((TEMPLATE / ".github/workflows/docs.yml").read_text(encoding="utf-8"), cfg):
        rows.append((root.name, wf_rel, "DRIFT", "被手改或版本落后"))
    else:
        rows.append((root.name, wf_rel, "ok", ""))

    # config.mts:再渲染逐字比对 + token 无残留
    cfg_dst = root / VP_CONFIG_REL
    want_cfg = render_config((TEMPLATE / "docs/.vitepress/config.mts").read_text(encoding="utf-8"), cfg)
    if not cfg_dst.is_file():
        rows.append((root.name, VP_CONFIG_REL.as_posix(), "MISSING", "-"))
    else:
        got_cfg = cfg_dst.read_text(encoding="utf-8", errors="ignore")
        if "@@" in got_cfg:
            rows.append((root.name, VP_CONFIG_REL.as_posix(), "DRIFT", "渲染 token 残留(未渲染的 @@TOKEN@@)"))
        elif got_cfg != want_cfg:
            rows.append((root.name, VP_CONFIG_REL.as_posix(), "DRIFT", "与模板渲染结果不一致"))
        else:
            rows.append((root.name, VP_CONFIG_REL.as_posix(), "ok", ""))

    # sidebar.generated.mjs ↔ _sidebar.md 一致性
    gen = root / VP_SIDEBAR_REL
    if not gen.is_file():
        rows.append((root.name, VP_SIDEBAR_REL.as_posix(), "MISSING", "-"))
    elif gen.read_text(encoding="utf-8", errors="ignore") != sidebar_module_text(root):
        rows.append((root.name, VP_SIDEBAR_REL.as_posix(), "DRIFT", "与 _sidebar.md 不一致,运行 update"))
    else:
        rows.append((root.name, VP_SIDEBAR_REL.as_posix(), "ok", ""))

    if not (root / "docs/public/.nojekyll").is_file():
        rows.append((root.name, "docs/public/.nojekyll", "MISSING", "-"))
    else:
        rows.append((root.name, "docs/public/.nojekyll", "ok", ""))
    gi = root / ".gitignore"
    gi_lines = gi.read_text(encoding="utf-8").splitlines() if gi.is_file() else []
    miss_gi = [e for e in GITIGNORE_ENTRIES if e not in gi_lines]
    if miss_gi:
        rows.append((root.name, ".gitignore", "DRIFT", f"缺 {', '.join(miss_gi)}"))
    else:
        rows.append((root.name, ".gitignore", "ok", ""))
    return rows


def cmd_check(args):
    """跨仓库校验托管链路与模板一致。

    下载页生成链路(v1/v2 通用):逐字节一致。VitePress(v2)仓库另查:
    依赖清单逐字节、workflow/config 再渲染、sidebar 再生成、token 无残留、
    .nojekyll 与 .gitignore 就位。index.html 等允许各仓库有差异,不参与比对。

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
        branch = off_default_branch(root)
        if branch:
            rows.append((root.name, "—", "skipped", f"本地在 {branch}，非默认分支；以 CI/远端为准"))
            continue
        # 不是文档站（既无 docs/ 也无 .github/pages/）：例如 docsite 脚手架自身。
        if not (root / "docs").is_dir() and not (root / ".github" / "pages").is_dir():
            rows.append((root.name, "—", "skipped", "不是文档站"))
            continue
        if is_vitepress(root):
            rows.extend(_check_v2_files(root))
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

    # Release-tag 一致性：委托给生成器自己的 --check（OK / STALE / MISSING / DRIFT）。
    tag_problems = 0
    for root in roots:
        gen = root / ".github/scripts/update_download_page.py"
        if not gen.is_file():
            continue
        try:
            out = subprocess.check_output(
                ["git", "-C", str(root), "remote", "get-url", "origin"],
                text=True, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        m = re.search(r"(?:github\.com[:/])([^/]+)/([^/.]+)", out)
        if not m:
            continue
        repo = f"{m.group(1)}/{m.group(2)}"
        print(f"\n{root.name}: 下载页 vs {repo} 最新 stable Release")
        try:
            code = subprocess.call([sys.executable, str(gen), repo, "--check"],
                                   cwd=str(root))
        except FileNotFoundError:
            code = 1
        if code != 0:
            tag_problems = 1
    return tag_problems


NAV_LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


_NAVIGATION_FIELDS = {"allowSidebarAnchors", "allowCombinedLocales"}


def _nav_config(root):
    """读取仓库的显式导航例外配置（.docsite.json 的 navigation 字段）。

    schema 为白名单制：仅允许上面两个字段，且必须为布尔值；未知字段、错误类型、
    整个文件非法 JSON 都属于「配置非法」，由调用方按 error 上报——
    不给「万能逃生口」留生长空间。未配置时全部为 False，绝不静默忽略。
    """
    path = root / ".docsite.json"
    cfg = {"allowSidebarAnchors": False, "allowCombinedLocales": False}
    problems = []
    if not path.exists():
        return cfg, problems
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return cfg, [f".docsite.json 不是合法 JSON（{e}）"]
    nav = doc.get("navigation")
    if nav is None:
        return cfg, problems
    if not isinstance(nav, dict):
        return cfg, [".docsite.json 的 navigation 必须是对象"]
    for key, value in nav.items():
        if key not in _NAVIGATION_FIELDS:
            problems.append(f"navigation.{key} 不是允许的字段（白名单：{', '.join(sorted(_NAVIGATION_FIELDS))}）")
        elif not isinstance(value, bool):
            problems.append(f"navigation.{key} 必须是布尔值")
        else:
            cfg[key] = value
    return cfg, problems


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


def published_paths(root):
    """站点实际会发布的路径集合，用来判定侧边栏链接是否指向真实存在的页面。

    新形态：upload-pages-artifact 直接上传 docs/，站点根就是 docs/。
    老形态：static.yml 把 .github/pages/（外壳）+ 仓库根 *.md + docs/ 拼成 _site；
            NekoTime、ludum 这类还会额外 cp -R 一些目录进 _site，所以顺带解析
            workflow 里的 `cp -R <src> _site`。
    """
    shell = root / ".github" / "pages"
    out = set()
    if shell.is_dir():
        out |= {"/" + str(p.relative_to(shell)) for p in shell.rglob("*") if p.is_file()}
        out |= {"/" + p.name for p in root.glob("*.md")}
        out |= _copied_into_site(root)
    docs = root / "docs"
    if docs.is_dir():
        prefix = "/docs/" if shell.is_dir() else "/"
        out |= {prefix + p.relative_to(docs).as_posix() for p in docs.rglob("*") if p.is_file()}
    return out


def _copied_into_site(root):
    """解析 workflow 里 `cp <src...> _site[/dest]`：外壳之外的目录（themes/tool、
    examples/cocos/*.md）也会被发布，链接判定得认这些路径。"""
    out = set()
    wf_dir = root / ".github" / "workflows"
    for wf in wf_dir.glob("*.y*ml") if wf_dir.is_dir() else []:
        for line in wf.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line.startswith("cp ") or "_site" not in line:
                continue
            parts = [p for p in line.split() if not p.startswith("-")]
            if len(parts) < 3 or not parts[-1].startswith("_site"):
                continue
            base = parts[-1][len("_site"):].strip("/")
            for src in parts[1:-1]:
                hits = list(root.glob(src)) if "*" in src else [root / src.rstrip("/")]
                for hit in hits:
                    if not hit.exists():
                        continue
                    files = [f for f in hit.rglob("*") if f.is_file()] if hit.is_dir() else [hit]
                    for f in files:
                        rel = str(f.relative_to(root).as_posix()) if hit.is_dir() else f.name
                        out.add("/" + f"{base}/{rel}" if base else "/" + rel)
    return out


def _check_sidebar_targets(name, path, root, issues, published):
    for _indent, label, target in _sidebar_items(path.read_text(encoding="utf-8", errors="ignore")):
        if target is None or _is_external(target):
            continue
        page = target.split("#")[0]
        if not page or page.endswith("/"):
            continue
        if page not in published:
            issues.append((name, "BROKEN_SIDEBAR_LINK",
                           f"「{label}」-> `{target}` 在站点里不存在（未发布的路径）", "error"))


def _check_vp_targets(name, path, root, issues):
    """v2(VitePress):侧边栏链接必须指向 docs/ 下真实存在的页面。

    路由对照:rewrites 把 README.md 映射为 index,故 `/` 查 docs/README.md、
    `/en/` 查 docs/en/README.md;`.md` 后缀可有可无(转换器已去后缀)。
    """
    root = Path(root)
    for _indent, label, target in _sidebar_items(path.read_text(encoding="utf-8", errors="ignore")):
        if target is None or _is_external(target):
            continue
        page = target.split("#")[0]
        if not page.startswith("/"):
            continue  # 相对链接交给 NOT_ROOT_ABSOLUTE 提示
        rel = page.strip("/")
        if rel in ("", "en"):
            ok = (root / "docs" / rel / "README.md").is_file()
        else:
            if not rel.endswith(".md"):
                rel += ".md"
            ok = (root / "docs" / rel).is_file()
        if not ok:
            issues.append((name, "BROKEN_SIDEBAR_LINK",
                           f"「{label}」-> `{target}` 在 docs/ 下不存在（VitePress 路由）", "error"))


def _check_sidebar_consistency(name, root, issues):
    """v2:sidebar.generated.mjs 必须与 _sidebar.md 的再生成结果逐字一致。"""
    got = Path(root) / VP_SIDEBAR_REL
    if not got.is_file():
        issues.append((name, "SIDEBAR_STALE",
                       f"缺少 {VP_SIDEBAR_REL}；运行 update 重新生成", "error"))
        return
    if got.read_text(encoding="utf-8", errors="ignore") != sidebar_module_text(root):
        issues.append((name, "SIDEBAR_STALE",
                       "sidebar.generated.mjs 与 _sidebar.md 不一致；运行 update 重新生成", "error"))


def _navcheck_sidebar(name, path, is_en, cfg, issues, en_prefix="/en/"):
    text = path.read_text(encoding="utf-8", errors="ignore")
    items = _sidebar_items(text)
    seen = {}
    # 语言入口是切换器不是内容分类：「中文」/「English」这类分类允许只有 1 个页面，
    # 也不要求它下面的条目逐条再标注语言（分类标题已经写明了）。
    lang_category = re.compile(r"中文|Chinese|英文|English")
    # 分类密度：统计每个顶级分类下的直接子条目（内部页与外部链接都算）
    roots = []
    current = None
    for indent, label, target in items:
        if target is None and indent == 0:
            current = None if lang_category.search(label) else (label, [])
            if current:
                roots.append(current)
        elif current is not None and indent >= 1 and target is not None:
            current[1].append(target)
        elif target is not None:
            current = None  # 顶级裸链接页，不算分类

    in_lang_category = False
    for indent, label, target in items:
        if target is None:
            if indent == 0:
                in_lang_category = bool(lang_category.search(label))
            continue
        if _is_external(target):
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
        if is_en:
            # 壳形态（.github/pages）把 docs/ 挂在 /docs/ 下，英文前缀就是 /docs/en/；
            # 指向仓库根 README.en.md 这类英文文件（.en.md）也算英文内容。
            if not target.startswith(en_prefix) and not re.search(r"\.en\.md(?:#|$)", target) \
                    and not re.search(r"中文|Chinese|文档", label) and not in_lang_category:
                issues.append((name, "EN_SIDEBAR_ZH_LINK",
                               f"`{label}` 指向非 {en_prefix} 页面且未标注（中文）", "warning"))
    if not is_en and not cfg["allowCombinedLocales"]:
        for indent, label, target in items:
            # 标注「（英文）」的单条 fallback 链接允许（规则 20 的对称场景：
            # 页面仅有英文版时，中文侧边栏可显式标注后指向它）；整棵英文树仍然禁止
            if (target and not _is_external(target) and target.startswith(en_prefix)
                    and not re.search(r"英文|English", label)):
                issues.append((name, "COMBINED_LOCALES",
                               f"`{label}` —— 语言是站点维度，英文树应放 /en/_sidebar.md；"
                               "确需指向英文页必须在标题中标注（英文）", "error"))
                break
    for label, children in roots:
        if len(children) == 1:
            issues.append((name, "SINGLE_PAGE_CATEGORY",
                           f"「{label}」只有 1 个页面，考虑并入相邻分类", "warning"))


# Docsify hash 路由链接:`](#/page)` / `](#/)`(普通 `](#anchor)` 是页内锚点,不动)
HASH_LINK = re.compile(r"\]\(#/([^)\s]*)\)")


def _rewrite_hash_links(text):
    """docsify 的 `#/` hash 路由 → 根绝对路径链接;返回(新文本, 替换次数)。"""
    count = 0
    def sub(m):
        nonlocal count
        count += 1
        target = m.group(1)
        return f"](/{target})"
    return HASH_LINK.sub(sub, text), count


def _strip_docs_prefix(text):
    """壳形态链接 `/docs/...` → `/...`(docs/ 在新形态就是站点根);返回(新文本, 次数)。"""
    return text.replace("](/docs/", "](/"), text.count("](/docs/")


def _collect_md(root):
    """docs/ 下的 Markdown(用户内容 + sidebar 源),不含 .vitepress 托管目录。"""
    docs = Path(root) / "docs"
    if not docs.is_dir():
        return []
    return [p for p in sorted(docs.rglob("*.md")) if ".vitepress" not in p.parts]


def _analyze_pages_workflow(root):
    """识别旧 Pages workflow(static.yml 等):是否还拷贝 docs 之外的目录。"""
    root = Path(root)
    findings = []
    for wf in sorted((root / ".github/workflows").glob("*.y*ml")):
        if wf.name == "docs.yml":
            continue
        text = wf.read_text(encoding="utf-8", errors="ignore")
        if "upload-pages-artifact" not in text and "deploy-pages" not in text:
            continue
        # 支持 block run 和单行 run: cp -R ...;只报告来源,不执行 shell。
        copies = sorted({m.group(1).strip("\"'") for m in re.finditer(
            r"(?:^|[;|&]\s*|run:\s*)\s*cp\s+(?:-[\w-]+\s+)*([^\s;|&]+)", text, re.M)})
        findings.append((wf, copies))
    return findings


def cmd_migrate(args):
    """把 docsite 托管的 Docsify 旧形态迁移到 VitePress(v2)。

    步骤:备份受管 Docsify 文件 → 写入 VitePress 结构 → 改写 `#/` hash 链接与
    壳形态 `/docs/` 前缀 → .docsite.json 升级(engine/version: 2)。
    --dry-run 只打印计划不写盘;失败不清删任何原文件;旧文件清理是构建验证
    通过后的独立人工步骤(提示,不自动执行)。
    """
    root = Path(args.path or ".")
    cfg_path = root / CONFIG
    if not cfg_path.is_file():
        sys.exit(f"{root} 没有 .docsite.json;仅迁移 docsite 托管仓库(手写站点不在此列)")
    if is_vitepress(root):
        sys.exit("已是 VitePress(v2)形态;要刷新托管文件请用 update")

    # 旧形态检测:两种壳,必须含托管标记(手写 docsify 站不迁)
    shells = [p for p in (root / "docs/index.html", root / ".github/pages/index.html")
              if p.is_file() and is_managed(p)]
    if not shells:
        sys.exit("未检测到 docsite 托管的 Docsify 外壳"
                 "(docs/index.html 或 .github/pages/index.html 含托管标记)")
    shell_form = (root / ".github/pages/index.html") in shells

    cfg = with_defaults(json.loads(cfg_path.read_text(encoding="utf-8")))
    new_cfg = _v2_config(cfg)

    # ---- 迁移计划(全部先算后写;--dry-run 在此输出并退出) ----
    plans = []      # ('~', rel, note) 修改/新增
    backups = []    # ('!', bak_rel, src_rel)
    renames = []    # ('>', new_rel, old_rel)
    warnings = []   # ('!', text)

    # 1. 备份受管 Docsify 文件(旧壳 index.html + vendor;static.yml/旧 docs.yml 见下)
    for shell in shells:
        vendor = shell.parent / "assets" / "vendor"
        managed = [shell] + (sorted(vendor.iterdir()) if vendor.is_dir() else [])
        for f in managed:
            backups.append((f"{f.relative_to(root).as_posix()}.docsite.bak", f.relative_to(root).as_posix()))
    old_wf = root / ".github/workflows/docs.yml"
    if old_wf.is_file() and is_managed(old_wf):
        backups.append(("docs.yml.docsite.bak", Path(".github/workflows/docs.yml")))

    # 2. 旧 Pages workflow(static.yml 等):解析 cp 拷贝物,报告;改名停用(等效备份)
    for wf, copies in _analyze_pages_workflow(root):
        extra = f";它还把 {', '.join(c for c in copies if c != 'docs' and c != '.github/pages')} 拷进站点" \
            if any(c not in ("docs", ".github/pages") for c in copies) else ""
        renames.append((f"{wf.relative_to(root).as_posix()}.docsite.bak", wf.relative_to(root).as_posix()))
        warnings.append(f"{wf.name} 是旧 Pages 部署{extra};已改名停用(备份即改名产物)。"
                        "确认新部署正常后删除备份;若它还承担其他发布任务,请先人工拆分")

    # 3. 链接改写:统计将改动的文件与处数
    md_files = _collect_md(root)
    hash_hits, prefix_hits = {}, {}
    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        n1 = len(HASH_LINK.findall(text))
        n2 = text.count("](/docs/") if shell_form else 0
        if n1:
            hash_hits[p] = n1
        if n2:
            prefix_hits[p] = n2

    # 4. 壳形态:外壳 sidebar 是用户内容,复制进 docs/(仅缺失时),一并参与链接改写
    sidebar_src = root / ".github/pages/_sidebar.md"
    if shell_form and sidebar_src.is_file() and not (root / "docs/_sidebar.md").is_file():
        plans.append(("~", "docs/_sidebar.md", "从 .github/pages/_sidebar.md 复制,改写 hash 链接及 /docs/ 前缀(原文保留)"))

    # 5. 下载页配置:壳形态 linkBase "/docs" 要清空(新形态 docs/ 即站点根)
    dl_cfg = root / ".github/scripts/download-page.json"
    link_base_note = None
    if dl_cfg.is_file():
        try:
            data = json.loads(dl_cfg.read_text(encoding="utf-8"))
            if (data.get("linkBase") or "").rstrip("/") == "/docs":
                link_base_note = 'linkBase "/docs" → ""(docs/ 现在是站点根)'
        except json.JSONDecodeError:
            warnings.append("download-page.json 不是纯 JSON(可能含注释),请人工核对 linkBase")

    plans += [
        ("+", "package.json / package-lock.json", "VitePress 依赖(模板锁定)"),
        ("+", VP_CONFIG_REL.as_posix(), "站点配置(托管)"),
        ("+", VP_SIDEBAR_REL.as_posix(), "由 _sidebar.md 生成(托管)"),
        ("+", "docs/public/.nojekyll", ""),
        ("+", ".github/workflows/docs.yml", "Node 22 构建 + Pages 部署"),
        ("~", ".docsite.json",
         f"engine=vitepress, engineVersion={new_cfg['engineVersion']}, version=2"),
        ("~", ".gitignore", "补 node_modules / dist / cache(缺才加)"),
    ]
    for p, n in hash_hits.items():
        plans.append(("~", str(p.relative_to(root).as_posix()), f"改写 docsify hash 链接 {n} 处"))
    for p, n in prefix_hits.items():
        plans.append(("~", str(p.relative_to(root).as_posix()), f"去掉链接 /docs/ 前缀 {n} 处"))
    # 正文、仓库配置也保留原件;失败后可以从备份恢复,不依赖 git 状态。
    for p in sorted(set(hash_hits) | set(prefix_hits) | {cfg_path} | ({dl_cfg} if link_base_note else set())):
        rel = p.relative_to(root).as_posix()
        backups.append((rel + ".docsite.bak", rel))
    if link_base_note:
        plans.append(("~", ".github/scripts/download-page.json", link_base_note))
    for rel in list(V2_MANAGED.values()) + [VP_CONFIG_REL, VP_SIDEBAR_REL] + [Path(p) for p in SYNCED.values()]:
        target = root / rel
        if target.is_file() and not is_managed(target):
            warnings.append(f"接管 {rel.as_posix()} 前将备份为 *.docsite.bak;请人工合并自定义 scripts/依赖等字段")
    for rel in SYNCED.values():
        plans.append(("+", rel, "下载页生成链路(托管)"))

    # 根目录 *.md 原来由 static.yml 发布,新形态不再自动发布——只提示,不移动
    root_md = sorted(p.name for p in root.glob("*.md"))
    if shell_form and root_md:
        warnings.append(f"根目录 {', '.join(root_md)} 不再随站点发布;如需保留请移入 docs/ 或改写链接")

    print(f"迁移计划:{root.resolve().name}"
          f"({'壳形态 .github/pages/' if shell_form else 'docs/ 形态'} → VitePress)")
    for mark, rel, note in plans:
        print(f"  {mark} {rel}" + (f"  ({note})" if note else ""))
    for bak, src in backups:
        print(f"  ! 备份 {src} → {bak}")
    for new, old in renames:
        print(f"  > 停用 {old} → {new}")
    for w in warnings:
        print(f"  ! {w}")
    if args.dry_run:
        print("\n--dry-run:未写盘。去掉 --dry-run 执行迁移。")
        return 0

    # ---- 执行 ----
    for bak_rel, src_rel in backups:
        src = root / src_rel
        if src.is_file():
            _backup_file(src)
            print(f"  ! 备份 {src_rel} → {bak_rel}")
    for new_rel, old_rel in renames:
        old = root / old_rel
        if old.is_file():
            _backup_file(old)
            old.unlink()  # 只停用旧 workflow;备份成功后才移除生效文件
            print(f"  > 停用 {old_rel} → {new_rel}")

    if shell_form and sidebar_src.is_file() and not (root / "docs/_sidebar.md").is_file():
        shutil.copy2(sidebar_src, root / "docs/_sidebar.md")
        print("  ~ docs/_sidebar.md(从外壳复制)")
        md_files = _collect_md(root)

    for p in md_files:
        text = p.read_text(encoding="utf-8", errors="ignore")
        new_text, n1 = _rewrite_hash_links(text)
        if shell_form:
            new_text, n2 = _strip_docs_prefix(new_text)
        else:
            n2 = 0
        if n1 or n2:
            write_file(p, new_text, overwrite=True)
            print(f"  ~ {p.relative_to(root).as_posix()}(hash {n1} 处 / 前缀 {n2} 处)")

    if link_base_note:
        data = json.loads(dl_cfg.read_text(encoding="utf-8"))
        data["linkBase"] = ""
        dl_cfg.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                          encoding="utf-8", newline="")
        print("  ~ .github/scripts/download-page.json(linkBase 清空)")

    cfg_path.write_text(json.dumps(new_cfg, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print("  ~ .docsite.json(engine/version: 2)")
    _write_v2_managed(new_cfg, root=root)

    print("""
迁移完成,接下来:
  1. npm install && python3 docsite.py build && python3 docsite.py preview   本地验收
  2. 核对 diff(链接改写、.docsite.bak、停用的 workflow)
  3. 构建与预览通过后,人工清理:旧壳文件(备份在 *.docsite.bak)与 .github/pages/ 残留
  4. 每仓库独立 PR,diff 可见可控;回滚 = git checkout""")
    return 0


def cmd_run_docs(args):
    """build/preview/dev:包装 npm run docs:*(渲染交给 VitePress CLI,Python 不做渲染)。"""
    if not is_vitepress("."):
        sys.exit("当前仓库不是 VitePress(v2)形态;Docsify 旧站点请先运行 migrate")
    if not Path("package.json").is_file():
        sys.exit("缺少 package.json;先运行 python3 docsite.py update 下发托管文件")
    npm = shutil.which("npm")
    if not npm:
        sys.exit("未检测到 npm。请先安装 Node.js 22+(https://nodejs.org/),"
                 "再运行 npm install 后重试。")
    if not Path("node_modules/vitepress").is_dir():
        print("本地尚未安装依赖,先执行 npm ci …")
        if subprocess.call([npm, "ci"]):
            sys.exit("npm ci 失败;请检查网络或手动运行 npm install")
    sys.exit(subprocess.call([npm, "run", f"docs:{args.cmd}"]))


def cmd_navcheck(args):
    """校验导航信息架构规约（确定性规则；主观的「分类好不好」不在检查范围）。

    规则表按引擎分两套（D-009 迁移期双轨，migrate 完成后 Docsify 表退役）：

    v2（VitePress，docs/.vitepress/config.mts 在场）error：
      COMBINED_LOCALES   根 sidebar 出现 /en/ 文档树（语言是站点维度，不是导航分类）
      EN_SIDEBAR_MISSING 有 docs/en/ 页面但缺 docs/en/_sidebar.md
      ANCHOR_LINK        sidebar 出现页内锚点（可用 navigation.allowSidebarAnchors 豁免）
      DUPLICATE_LINK     同一目标在同一 sidebar 出现多次
      BROKEN_SIDEBAR_LINK 侧边栏链接在 docs/ 下不存在（路由对照：/ ↔ README.md）
      SIDEBAR_STALE      sidebar.generated.mjs 与 _sidebar.md 再生成结果不一致
      NAVIGATION_SCHEMA  .docsite.json navigation 字段非法（白名单制）

    v1（Docsify，未迁移仓库，规则保持原样以兼容存量）error 额外有：
      GLOBAL_SIDEBAR_ALIAS / HEADING_INJECTION（docsify 外壳专属，v2 下无此文件）
      BROKEN_SIDEBAR_LINK 按发布路径判定（壳形态 .github/pages + 根 *.md + docs/）

    warning（两套共用）：SINGLE_PAGE_CATEGORY / NOT_ROOT_ABSOLUTE / EN_SIDEBAR_ZH_LINK
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
        branch = off_default_branch(root)
        if branch:
            print(f"➖ {root.name:<22} 本地在 {branch}，非默认分支，跳过（以 CI/远端为准）")
            continue
        zh = root / "docs/_sidebar.md"
        if not zh.is_file():
            zh = root / ".github/pages/_sidebar.md"
        if not zh.is_file():
            continue  # 无导航的仓库（如 docsite 自身）不参与
        checked += 1
        cfg, schema_problems = _nav_config(root)
        # 英文内容的前缀跟着发布布局走：壳形态在 /docs/en/，新形态在 /en/。
        en_prefix = "/docs/en/" if (root / ".github" / "pages" / "index.html").is_file() else "/en/"
        issues = []
        for problem in schema_problems:
            issues.append((root.name, "NAVIGATION_SCHEMA", problem, "error"))
        _navcheck_sidebar(root.name, zh, is_en=False, cfg=cfg, issues=issues, en_prefix=en_prefix)
        en = root / "docs/en/_sidebar.md"
        en_pages = [p for p in (root / "docs/en").glob("*.md")] if (root / "docs/en").is_dir() else []
        # 英文内容在根 README.en.md 的 CDN 壳仓（已声明 allowCombinedLocales）不要求 en sidebar
        if en_pages and not en.is_file() and not cfg["allowCombinedLocales"]:
            issues.append((f"{root.name}/en", "EN_SIDEBAR_MISSING",
                           "docs/en/ 有页面但没有 docs/en/_sidebar.md", "error"))
        elif en.is_file():
            _navcheck_sidebar(f"{root.name}/en", en, is_en=True, cfg=cfg, issues=issues,
                              en_prefix=en_prefix)

        if is_vitepress(root):
            _check_vp_targets(root.name, zh, root, issues)
            if en.is_file():
                _check_vp_targets(f"{root.name}/en", en, root, issues)
            _check_sidebar_consistency(root.name, root, issues)
        else:
            published = published_paths(root)
            _check_sidebar_targets(root.name, zh, root, issues, published)
            if en.is_file():
                _check_sidebar_targets(f"{root.name}/en", en, root, issues, published)

            # 明显旧结构：外壳配置检查（确定性）。外壳可能在 docs/，也可能在
            # .github/pages/（老仓库由 static.yml 拼接发布），两处都查。
            for shell in (root / "docs/index.html", root / ".github/pages/index.html"):
                if not shell.is_file():
                    continue
                stext = shell.read_text(encoding="utf-8", errors="ignore")
                # 匹配真实配置形态（键: 值），避免把文档/注释里的反例文字误报
                if re.search(r"/\.\*/_sidebar\.md\s*['\"]\s*:\s*['\"]/_sidebar\.md", stext):
                    issues.append((root.name, "GLOBAL_SIDEBAR_ALIAS",
                                   f"{shell.relative_to(root)} 配置了 '/.*/_sidebar.md' 通配 alias，"
                                   "会把 /en/ 页面静默改写回根侧边栏，破坏分语言导航", "error"))
                if re.search(r"subMaxLevel\s*:", stext):
                    issues.append((root.name, "HEADING_INJECTION",
                                   f"{shell.relative_to(root)} 配置了 subMaxLevel，"
                                   "当前页标题会被注入 sidebar 渲染", "warning"))

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
    # Windows 的传统控制台编码不能表示所有 emoji/状态符号;诊断不应因此崩溃。
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")
    if not TEMPLATE.exists():
        sys.exit(f"找不到模板目录 {TEMPLATE}")
    p = argparse.ArgumentParser(description="轻量级文档网站生成器(VitePress 引擎,Python 管工程)")
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

    m = sub.add_parser("migrate", help="把 docsite 托管的 Docsify 旧形态迁移到 VitePress")
    m.add_argument("path", nargs="?", default=".", help="目标仓库路径，默认当前目录")
    m.add_argument("--dry-run", action="store_true", help="只打印迁移计划，不写盘")
    m.set_defaults(func=cmd_migrate)

    for name, blurb in (("build", "构建站点（npm run docs:build）"),
                        ("preview", "本地预览构建产物（npm run docs:preview）"),
                        ("dev", "启动开发服务器（npm run docs:dev）")):
        d = sub.add_parser(name, help=blurb)
        d.set_defaults(func=cmd_run_docs, cmd=name)

    args = p.parse_args()
    sys.exit(args.func(args) or 0)


if __name__ == "__main__":
    main()
