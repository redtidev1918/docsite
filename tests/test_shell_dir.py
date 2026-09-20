#!/usr/bin/env python3
"""外壳目录识别：新仓库用 docs/，老仓库用 .github/pages/。

老形态（NekoTime / ludum / paranote / pixiv-token-getter / telepress）把 docsify 外壳
放在 .github/pages/，由 static.yml 与 docs/ 内容拼成 _site。update 以前只认 docs/，
会把托管外壳写到错的地方；这里钉住两种形态。
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
}


class ShellDirTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / ".docsite.json").write_text(json.dumps(CFG), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_docsite(self, *args):
        return subprocess.run([sys.executable, str(DOCSITE), *args],
                              cwd=self.root, capture_output=True, text=True)

    def make_shell_repo(self, wildcard_alias=False):
        shell = self.root / ".github" / "pages"
        shell.mkdir(parents=True)
        alias = (
            "      alias: {\n        '/.*/_sidebar.md': '/_sidebar.md'\n      },\n"
            if wildcard_alias else ""
        )
        (shell / "index.html").write_text(
            "<!doctype html>\n<script>\n  window.$docsify = {\n"
            "    loadSidebar: true,\n" + alias + "  };\n</script>\n",
            encoding="utf-8")
        (shell / "_sidebar.md").write_text("- start\n  - [home](/README.md)\n", encoding="utf-8")
        (self.root / "README.md").write_text("# root readme\n", encoding="utf-8")
        (self.root / "docs").mkdir()
        (self.root / "docs" / "README.md").write_text("# content\n", encoding="utf-8")
        return shell

    def test_update_writes_shell_dir_not_docs(self):
        shell = self.make_shell_repo()
        self.assertEqual(self.run_docsite("update").returncode, 0)
        self.assertIn("docsite: managed file", (shell / "index.html").read_text(encoding="utf-8"))
        self.assertTrue((shell / "assets" / "vendor" / "docsify.min.js").is_file())
        self.assertTrue((shell / ".nojekyll").is_file())
        self.assertFalse((self.root / "docs" / "index.html").exists())
        self.assertEqual((self.root / "docs" / "README.md").read_text(encoding="utf-8"), "# content\n")

    def test_update_still_uses_docs_for_new_layout(self):
        (self.root / "docs").mkdir()
        (self.root / "docs" / "index.html").write_text("<html></html>", encoding="utf-8")
        self.assertEqual(self.run_docsite("update").returncode, 0)
        self.assertIn("docsite: managed file",
                      (self.root / "docs" / "index.html").read_text(encoding="utf-8"))
        self.assertTrue((self.root / "docs" / "assets" / "vendor" / "docsify.min.js").is_file())
        self.assertFalse((self.root / ".github" / "pages").exists())

    def test_update_tolerates_config_without_site_fields(self):
        (self.root / ".docsite.json").write_text(
            json.dumps({"navigation": {"allowCombinedLocales": True}}), encoding="utf-8")
        self.make_shell_repo()
        self.assertEqual(self.run_docsite("update").returncode, 0)

    def test_navcheck_sees_shell_dir_alias(self):
        self.make_shell_repo(wildcard_alias=True)
        run = self.run_docsite("navcheck")
        self.assertEqual(run.returncode, 1)
        self.assertIn("GLOBAL_SIDEBAR_ALIAS", run.stdout)

    def test_navcheck_checks_sidebar_links_against_published_paths(self):
        shell = self.make_shell_repo()
        (self.root / "docs" / "en").mkdir()
        (self.root / "docs" / "en" / "README.md").write_text("# en\n", encoding="utf-8")
        # 壳形态的英文页在 /docs/en/：写成 /en/ 就是死链
        (self.root / "docs" / "en" / "_sidebar.md").write_text(
            "- Docs\n  - [Home](/en/README.md)\n", encoding="utf-8")
        run = self.run_docsite("navcheck")
        self.assertEqual(run.returncode, 1)
        self.assertIn("BROKEN_SIDEBAR_LINK", run.stdout)
        (self.root / "docs" / "en" / "_sidebar.md").write_text(
            "- Docs\n  - [Home](/docs/en/README.md)\n", encoding="utf-8")
        self.assertEqual(self.run_docsite("navcheck").returncode, 0)
        self.assertEqual(shell, self.root / ".github" / "pages")

    def test_language_category_is_not_a_content_category(self):
        self.make_shell_repo()
        (self.root / "docs" / "en").mkdir()
        (self.root / "docs" / "en" / "guide.md").write_text("# guide\n", encoding="utf-8")
        (self.root / "docs" / "guide.md").write_text("# 指南\n", encoding="utf-8")
        # 语言入口分类：只要一个页面，且整类标注（中文）后不再逐条报 EN_SIDEBAR_ZH_LINK
        (self.root / "docs" / "en" / "_sidebar.md").write_text(
            "- Docs\n  - [Guide](/docs/en/guide.md)\n\n- 中文\n  - [指南](/docs/guide.md)\n",
            encoding="utf-8")
        run = self.run_docsite("navcheck")
        self.assertEqual(run.returncode, 0)
        self.assertNotIn("「中文」", run.stdout)
        self.assertNotIn("EN_SIDEBAR_ZH_LINK", run.stdout)


if __name__ == "__main__":
    unittest.main()
