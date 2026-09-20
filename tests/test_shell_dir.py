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


if __name__ == "__main__":
    unittest.main()
