#!/usr/bin/env python3
"""VitePress(v2 引擎)集成:sidebar 转换器、config 渲染、navcheck 新规则。

约定:用户永远只维护 _sidebar.md;sidebar.generated.mjs 是托管产物,
navcheck 校验它与再生成结果逐字一致。config.mts 的 token 处于 JS 字符串
上下文,渲染必须转义(D-005);base 由仓库名推导,不接受配置覆盖。
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DOCSITE = Path(__file__).resolve().parent.parent / "docsite.py"
sys.path.insert(0, str(DOCSITE.parent))
import docsite  # noqa: E402

CFG = {
    "repo": "owner/project",
    "name": "Project",
    "emoji": "P",
    "description": "Project docs.",
    "branch": "main",
    "themeKey": "project-theme",
}

ZH_SIDEBAR = """- 开始
  - [概览](/)
  - [快速开始](/QUICKSTART.md)
  - [外部](https://example.com/)
- 规范
  - [命名](/CONVENTIONS.md)
  - [导航](/NAVIGATION.md)
"""
EN_SIDEBAR = "- Docs\n  - [Home](/en/)\n  - [Quick Start](/en/QUICKSTART.md)\n"


class ConfigSafetyTestCase(unittest.TestCase):
    def test_extra_content_paths_are_quoted_and_optional(self):
        template = "paths:\n      - 'package-lock.json'@@CONTENT_PATHS@@\n"
        self.assertEqual(docsite.render(template, CFG), "paths:\n      - 'package-lock.json'\n")
        cfg = dict(CFG, contentPaths=['*.md', 'themes/**', '.github/scripts/*docs.mjs'])
        docsite.validate_config(cfg)
        rendered = docsite.render(template, cfg)
        for value in cfg['contentPaths']:
            self.assertIn('      - ' + json.dumps(value), rendered)

    def test_json_escaping_handles_both_quote_contexts(self):
        value = '"; throw new Error("injected"); //\n\t'
        rendered = docsite.render_config("'@@NAME@@' \"@@EMOJI@@\"", dict(CFG, name=value, emoji=value))
        self.assertIn('\\"', rendered)
        self.assertIn('\\n\\t', rendered)
        self.assertNotIn('\n', rendered)

    def test_rejects_schema_and_workflow_injection(self):
        for cfg in [dict(CFG, repo='owner/name\nextra'), dict(CFG, branch='main\n  - bad'),
                    dict(CFG, ignoreEverything=True), dict(CFG, name=42),
                    dict(CFG, navigation={'allowSidebarAnchors': 'yes'})]:
            with self.subTest(cfg=cfg), self.assertRaises(ValueError):
                docsite.with_defaults(cfg)


class LinkConversionTestCase(unittest.TestCase):
    def test_md_suffix_stripped(self):
        self.assertEqual(docsite._vp_link("/QUICKSTART.md"), "/QUICKSTART")
        self.assertEqual(docsite._vp_link("/en/download.md"), "/en/download")

    def test_home_and_external_unchanged(self):
        self.assertEqual(docsite._vp_link("/"), "/")
        self.assertEqual(docsite._vp_link("/en/"), "/en/")
        self.assertEqual(docsite._vp_link("https://example.com/"), "https://example.com/")
        self.assertEqual(docsite._vp_link(None), None)

    def test_anchor_preserved(self):
        self.assertEqual(docsite._vp_link("/CONVENTIONS.md#files"), "/CONVENTIONS#files")


class SidebarTreeTestCase(unittest.TestCase):
    def test_two_level_structure(self):
        items = docsite._sidebar_items(ZH_SIDEBAR)
        tree = docsite._vitepress_sidebar(items)
        self.assertEqual(tree[0]["text"], "开始")
        self.assertEqual(tree[0]["items"][0], {"text": "概览", "link": "/"})
        self.assertEqual(tree[0]["items"][1], {"text": "快速开始", "link": "/QUICKSTART"})
        # 外部链接原样保留
        self.assertEqual(tree[0]["items"][2]["link"], "https://example.com/")
        self.assertEqual(tree[1]["text"], "规范")
        self.assertEqual(tree[1]["items"][0]["link"], "/CONVENTIONS")

    def test_top_level_bare_link_becomes_leaf(self):
        tree = docsite._vitepress_sidebar([(0, "单独页", "/solo.md")])
        self.assertEqual(tree, [{"text": "单独页", "link": "/solo"}])

    def test_module_text_includes_both_locales_and_marker(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/_sidebar.md").write_text(ZH_SIDEBAR, encoding="utf-8")
            (root / "docs/en").mkdir()
            (root / "docs/en/_sidebar.md").write_text(EN_SIDEBAR, encoding="utf-8")
            text = docsite.sidebar_module_text(root)
            self.assertIn("docsite: managed file", text[:200])
            self.assertIn('"/":', text)
            self.assertIn('"/en/":', text)
            self.assertIn('"text": "开始"', text)
            self.assertIn('"link": "/en/QUICKSTART"', text)
            # 确定性:同样输入两次生成逐字一致(SIDEBAR_STALE 依赖这一点)
            self.assertEqual(text, docsite.sidebar_module_text(root))

    def test_module_without_en_sidebar_omits_en_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs").mkdir()
            (root / "docs/_sidebar.md").write_text(ZH_SIDEBAR, encoding="utf-8")
            self.assertNotIn('"/en/"', docsite.sidebar_module_text(root))


class RenderConfigTestCase(unittest.TestCase):
    TEMPLATE = "title: '@@NAME@@'; base: '@@BASE@@'; repo: '@@REPO@@'; desc: '@@DESCRIPTION@@'"

    def test_base_derived_from_repo(self):
        out = docsite.render_config(self.TEMPLATE, dict(CFG))
        self.assertIn("base: '/project/'", out)

    def test_github_io_repo_gets_root_base(self):
        cfg = dict(CFG, repo="owner/owner.github.io")
        self.assertIn("base: '/'", docsite.render_config(self.TEMPLATE, cfg))

    def test_js_single_quote_escaped(self):
        cfg = dict(CFG, name="D'Avatar \\ Viewer")
        out = docsite.render_config(self.TEMPLATE, cfg)
        self.assertIn("title: 'D\\'Avatar \\\\ Viewer'", out)

    def test_description_newline_escaped(self):
        cfg = dict(CFG, description="line1\nline2")
        self.assertIn("'line1\\nline2'", docsite.render_config(self.TEMPLATE, cfg))

    def test_real_template_renders_without_leftover_tokens(self):
        tpl = (DOCSITE.parent / "template/docs/.vitepress/config.mts").read_text(encoding="utf-8")
        self.assertNotIn("@@", docsite.render_config(tpl, CFG))


class NavcheckV2TestCase(unittest.TestCase):
    def test_retained_legacy_shell_does_not_change_v2_locale_prefix(self):
        shell = self.root / '.github/pages/index.html'
        shell.parent.mkdir(parents=True)
        shell.write_text('<!-- docsite: managed file -->', encoding='utf-8')
        docsite.write_sidebars(self.root)
        run = self.run_navcheck()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertNotIn('EN_SIDEBAR_ZH_LINK', run.stdout)

    """v2(VitePress)navcheck:BROKEN_SIDEBAR_LINK 按 docs/ 存在性;SIDEBAR_STALE 校一致性。"""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs/.vitepress").mkdir(parents=True)
        (self.root / "docs/.vitepress/config.mts").write_text("// docsite: managed file\n", encoding="utf-8")
        (self.root / "docs/en").mkdir(parents=True)
        (self.root / "docs/_sidebar.md").write_text(ZH_SIDEBAR, encoding="utf-8")
        (self.root / "docs/en/_sidebar.md").write_text(EN_SIDEBAR, encoding="utf-8")
        for rel in ("docs/README.md", "docs/QUICKSTART.md", "docs/CONVENTIONS.md", "docs/NAVIGATION.md",
                    "docs/en/README.md", "docs/en/QUICKSTART.md"):
            (self.root / rel).write_text("# page\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_navcheck(self):
        return subprocess.run([sys.executable, str(DOCSITE), "navcheck", str(self.root)],
                              capture_output=True, text=True)

    def test_green_when_consistent(self):
        docsite.write_sidebars(self.root)
        run = self.run_navcheck()
        self.assertEqual(run.returncode, 0, run.stdout)
        self.assertIn(self.root.name, run.stdout)

    def test_missing_generated_sidebar_is_stale(self):
        run = self.run_navcheck()
        self.assertEqual(run.returncode, 1)
        self.assertIn("SIDEBAR_STALE", run.stdout)

    def test_edited_generated_sidebar_is_stale(self):
        docsite.write_sidebars(self.root)
        gen = self.root / docsite.VP_SIDEBAR_REL
        gen.write_text(gen.read_text(encoding="utf-8").replace('"开始"', '"起航"'), encoding="utf-8")
        self.assertIn("SIDEBAR_STALE", self.run_navcheck().stdout)

    def test_broken_link_reports_against_docs_tree(self):
        docsite.write_sidebars(self.root)
        (self.root / "docs/_sidebar.md").write_text(
            ZH_SIDEBAR + "- 更多\n  - [不存在](/MISSING.md)\n", encoding="utf-8")
        docsite.write_sidebars(self.root)  # 重新生成后仍应报死链(文件不存在)
        run = self.run_navcheck()
        self.assertEqual(run.returncode, 1)
        self.assertIn("BROKEN_SIDEBAR_LINK", run.stdout)

    def test_legacy_alias_rule_not_applied_to_v2(self):
        # v2 仓库即使残留 docsify index.html 也不再执行 Docsify 外壳规则
        (self.root / "docs/index.html").write_text(
            "<script>alias: {'/.*/_sidebar.md': '/_sidebar.md'}</script>", encoding="utf-8")
        docsite.write_sidebars(self.root)
        run = self.run_navcheck()
        self.assertNotIn("GLOBAL_SIDEBAR_ALIAS", run.stdout)


if __name__ == "__main__":
    unittest.main()
