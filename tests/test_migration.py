#!/usr/bin/env python3
"""migrate 命令:旧 Docsify 形态 → VitePress(v2)。

钉住的安全契约:--dry-run 不写盘;受管文件先备份;用户 Markdown 永不删除;
`#/` hash 链接与壳形态 `/docs/` 前缀被改写;.docsite.json 升级 engine/version: 2;
旧 static.yml 停用为 .docsite.bak(新旧 Pages workflow 不得同时生效)。
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DOCSITE = Path(__file__).resolve().parent.parent / "docsite.py"
CFG = {
    "repo": "owner/project",
    "name": "Project",
    "emoji": "P",
    "description": "Project docs.",
    "branch": "main",
    "themeKey": "project-theme",
    "version": 1,
}


def make_old_shell_repo(root: Path):
    """壳形态老仓库:.github/pages 外壳 + static.yml + docs/ 内容(带 #/ 链接与 /docs/ 前缀)。"""
    (root / "README.md").write_text("# root\n", encoding="utf-8")
    shell = root / ".github/pages"
    shell.mkdir(parents=True)
    (shell / "index.html").write_text(
        "<!-- docsite: managed file -->\n<script>window.$docsify={loadSidebar:true}</script>\n",
        encoding="utf-8")
    (shell / "_sidebar.md").write_text(
        "- Docs\n  - [Home](/docs/README.md)\n  - [Guide](/docs/guide.md)\n", encoding="utf-8")
    vendor = shell / "assets/vendor"
    vendor.mkdir(parents=True)
    (vendor / "docsify.min.js").write_text("// docsify", encoding="utf-8")
    wf = root / ".github/workflows"
    wf.mkdir(parents=True)
    (wf / "static.yml").write_text(
        "name: pages\non: [push]\njobs:\n  build:\n    steps:\n"
        "      - run: cp -R .github/pages _site\n      - run: cp -R docs _site/docs\n"
        "      - uses: actions/deploy-pages@v5\n", encoding="utf-8")
    docs = root / "docs"
    docs.mkdir()
    (docs / "README.md").write_text("# home\n[guide](#/guide.md) and [home](#/)\n", encoding="utf-8")
    (docs / "guide.md").write_text("# guide\n", encoding="utf-8")
    (docs / "en").mkdir()
    (docs / "en/README.md").write_text("# en home\n", encoding="utf-8")
    (root / ".docsite.json").write_text(json.dumps(CFG), encoding="utf-8")


class MigrateDryRunTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_old_shell_repo(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def snapshot(self):
        return sorted(str(p.relative_to(self.root)) for p in self.root.rglob("*") if p.is_file())

    def run_migrate(self, *extra):
        return subprocess.run([sys.executable, str(DOCSITE), "migrate", str(self.root), *extra],
                              capture_output=True, text=True)

    def test_dry_run_writes_nothing(self):
        before = self.snapshot()
        run = self.run_migrate("--dry-run")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(before, self.snapshot())
        self.assertIn("迁移计划", run.stdout)

    def test_dry_run_lists_plans_backups_and_warnings(self):
        run = self.run_migrate("--dry-run")
        self.assertIn("package.json / package-lock.json", run.stdout)
        self.assertIn("engine=vitepress", run.stdout)
        self.assertIn("备份 .github/pages/index.html", run.stdout)
        self.assertIn("停用 .github/workflows/static.yml", run.stdout)
        self.assertIn("hash 链接", run.stdout)
        self.assertIn("/docs/ 前缀", run.stdout)
        self.assertIn("不再随站点发布", run.stdout)  # 根目录 *.md 提示

    def test_refuses_without_managed_shell(self):
        # 手写 docsify(无托管标记)不迁
        (self.root / ".github/pages/index.html").write_text("<html>hand-made</html>", encoding="utf-8")
        run = self.run_migrate()
        self.assertNotEqual(run.returncode, 0)
        self.assertIn("托管标记", run.stderr + run.stdout)

    def test_refuses_when_already_v2(self):
        (self.root / "docs/.vitepress").mkdir(parents=True)
        (self.root / "docs/.vitepress/config.mts").write_text("// docsite: managed file\n", encoding="utf-8")
        self.assertNotEqual(self.run_migrate().returncode, 0)

    def test_reports_extra_static_sources(self):
        workflow = self.root / ".github/workflows/static.yml"
        with workflow.open("a", encoding="utf-8") as stream:
            stream.write("      - run: cp -R themes _site/themes\n")
        run = self.run_migrate("--dry-run")
        self.assertIn("它还把 themes 拷进站点", run.stdout)


class MigrateExecuteTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        make_old_shell_repo(self.root)
        run = subprocess.run(
            [sys.executable, str(DOCSITE), "migrate", str(self.root)],
            capture_output=True, text=True)
        self.migrate_out = run.stdout
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def tearDown(self):
        self.tmp.cleanup()

    def test_v2_structure_written(self):
        for rel in ("package.json", "package-lock.json", "docs/.vitepress/config.mts",
                    "docs/.vitepress/sidebar.generated.mjs", "docs/public/.nojekyll",
                    ".github/workflows/docs.yml"):
            self.assertTrue((self.root / rel).is_file(), rel)
        self.assertIn("node-version: 22", (self.root / ".github/workflows/docs.yml").read_text(encoding="utf-8"))

    def test_backups_created_and_static_yml_disabled(self):
        self.assertTrue((self.root / ".github/pages/index.html.docsite.bak").is_file())
        self.assertTrue((self.root / ".github/pages/assets/vendor/docsify.min.js.docsite.bak").is_file())
        self.assertTrue((self.root / ".github/workflows/static.yml.docsite.bak").is_file())
        self.assertFalse((self.root / ".github/workflows/static.yml").exists())

    def test_shell_sidebar_copied_with_prefix_stripped(self):
        sidebar = (self.root / "docs/_sidebar.md").read_text(encoding="utf-8")
        self.assertIn("[Home](/README.md)", sidebar)
        self.assertIn("[Guide](/guide.md)", sidebar)
        # 原外壳 sidebar 保留(用户内容不删)
        self.assertTrue((self.root / ".github/pages/_sidebar.md").is_file())

    def test_hash_links_rewritten_in_content(self):
        text = (self.root / "docs/README.md").read_text(encoding="utf-8")
        self.assertIn("[guide](/guide.md)", text)
        self.assertIn("[home](/)", text)
        self.assertNotIn("](#/", text)
        backup = (self.root / "docs/README.md.docsite.bak").read_text(encoding="utf-8")
        self.assertIn("](#/guide.md)", backup)

    def test_config_upgraded_to_v2(self):
        cfg = json.loads((self.root / ".docsite.json").read_text(encoding="utf-8"))
        self.assertEqual(cfg["engine"], "vitepress")
        self.assertEqual(cfg["version"], 2)
        self.assertEqual(cfg["repo"], "owner/project")  # 原字段保留
        self.assertTrue(cfg["engineVersion"][0].isdigit())

    def test_generated_sidebar_matches_rewritten_source(self):
        import docsite as ds
        gen = self.root / ds.VP_SIDEBAR_REL
        self.assertEqual(gen.read_text(encoding="utf-8"), ds.sidebar_module_text(self.root))

    def test_user_content_untouched_outside_rewrites(self):
        # guide.md 没有旧式链接,应保持原样
        self.assertEqual((self.root / "docs/guide.md").read_text(encoding="utf-8"), "# guide\n")


class MigrateNewFormTestCase(unittest.TestCase):
    """docs/index.html 新形态老仓库:无壳、无 /docs/ 前缀,只做备份 + 结构写入 + hash 改写。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        docs = self.root / "docs"
        docs.mkdir()
        (docs / "index.html").write_text("<!-- docsite: managed file -->\n", encoding="utf-8")
        (docs / "_sidebar.md").write_text("- 开始\n  - [概览](/)\n  - [指南](/guide.md)\n", encoding="utf-8")
        (docs / "README.md").write_text("# home\n[link](#/guide.md)\n", encoding="utf-8")
        (docs / "guide.md").write_text("# guide\n", encoding="utf-8")
        (self.root / ".docsite.json").write_text(json.dumps(CFG), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_migrate_new_form(self):
        run = subprocess.run([sys.executable, str(DOCSITE), "migrate", str(self.root)],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertTrue((self.root / "docs/index.html.docsite.bak").is_file())
        self.assertIn("[link](/guide.md)", (self.root / "docs/README.md").read_text(encoding="utf-8"))
        # 旧壳 index.html 仍在场(清理是构建验证后的人工步骤),VitePress 不受它影响
        self.assertTrue((self.root / "docs/index.html").is_file())


class LinkBaseResetTestCase(unittest.TestCase):
    """壳形态的 download-page.json linkBase=/docs 迁移后必须清空(docs/ 成为站点根)。"""

    def test_link_base_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_old_shell_repo(root)
            dl = root / ".github/scripts/download-page.json"
            dl.parent.mkdir(parents=True)
            dl.write_text(json.dumps({"outputs": {"zh": "docs/download.md"}, "linkBase": "/docs"}),
                          encoding="utf-8")
            run = subprocess.run([sys.executable, str(DOCSITE), "migrate", str(root)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            data = json.loads(dl.read_text(encoding="utf-8"))
            self.assertEqual(data["linkBase"], "")
            self.assertEqual(data["outputs"]["zh"], "docs/download.md")


class UpdateV2TestCase(unittest.TestCase):
    """v2 仓库的 update:刷新托管文件,永不触碰用户 Markdown。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        docs = self.root / "docs/.vitepress"
        docs.mkdir(parents=True)
        (self.root / "docs/.vitepress/config.mts").write_text("// docsite: managed file\n", encoding="utf-8")
        (self.root / "docs/_sidebar.md").write_text("- 开始\n  - [概览](/)\n", encoding="utf-8")
        (self.root / "docs/README.md").write_text("# 我的内容\n", encoding="utf-8")
        (self.root / ".docsite.json").write_text(
            json.dumps(dict(CFG, engine="vitepress", engineVersion="1.6.4", version=2)),
            encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_update_refreshes_managed_keeps_content(self):
        run = subprocess.run([sys.executable, str(DOCSITE), "update"],
                             cwd=self.root, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertIn("VitePress(v2)", run.stdout)
        # 用户内容不动
        self.assertEqual((self.root / "docs/README.md").read_text(encoding="utf-8"), "# 我的内容\n")
        self.assertEqual((self.root / "docs/_sidebar.md").read_text(encoding="utf-8"),
                         "- 开始\n  - [概览](/)\n")
        # 托管文件就位且 config 无 token 残留
        cfg_text = (self.root / "docs/.vitepress/config.mts").read_text(encoding="utf-8")
        self.assertNotIn("@@", cfg_text)
        self.assertIn("base: '/project/'", cfg_text)
        self.assertIn("'P Project'", cfg_text)  # emoji + name
        # .gitignore 补齐
        gi = (self.root / ".gitignore").read_text(encoding="utf-8")
        for entry in ("node_modules/", "docs/.vitepress/dist/", "docs/.vitepress/cache/"):
            self.assertIn(entry, gi)
        # package.json 逐字节等于模板(含托管标记)
        import docsite as ds
        self.assertEqual((self.root / "package.json").read_text(encoding="utf-8"),
                         (ds.TEMPLATE / "package.json").read_text(encoding="utf-8"))

    def test_init_rejects_when_config_exists(self):
        run = subprocess.run(
            [sys.executable, str(DOCSITE), "init", "--repo", "a/b"],
            cwd=self.root, capture_output=True, text=True)
        self.assertNotEqual(run.returncode, 0)


class InitV2TestCase(unittest.TestCase):
    def test_migration_preserves_custom_package_and_existing_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_old_shell_repo(root)
            (root / "package.json").write_text('{"scripts":{"app":"node app.js"}}', encoding="utf-8")
            (root / "package.json.docsite.bak").write_text("original backup", encoding="utf-8")
            run = subprocess.run([sys.executable, str(DOCSITE), "migrate", str(root)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertEqual((root / "package.json.docsite.bak").read_text(), "original backup")
            self.assertIn('"app"', (root / "package.json.1.docsite.bak").read_text())

    def test_init_creates_v2_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run = subprocess.run(
                [sys.executable, str(DOCSITE), "init", "--repo", "owner/pixivflow",
                 "--name", "PixivFlow", "--emoji", "🎨"],
                cwd=root, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            cfg = json.loads((root / ".docsite.json").read_text(encoding="utf-8"))
            self.assertEqual(cfg["engine"], "vitepress")
            self.assertEqual(cfg["version"], 2)
            # 内容骨架 + 托管结构
            for rel in ("docs/README.md", "docs/_sidebar.md", "docs/en/README.md",
                        "docs/.vitepress/config.mts", "docs/.vitepress/sidebar.generated.mjs",
                        "package.json", ".github/workflows/docs.yml"):
                self.assertTrue((root / rel).is_file(), rel)
            cfg_text = (root / "docs/.vitepress/config.mts").read_text(encoding="utf-8")
            self.assertIn("base: '/pixivflow/'", cfg_text)
            self.assertIn("'🎨 PixivFlow'", cfg_text)
            # 不再创建 Docsify 外壳
            self.assertFalse((root / "docs/index.html").exists())
            self.assertFalse((root / "docs/assets").exists())


if __name__ == "__main__":
    unittest.main()
