#!/usr/bin/env python3
"""Unit tests for template/download-page.py (hermetic: payloads via --input-json)."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GEN = Path(__file__).resolve().parent.parent / "template" / "download-page.py"
REPO = "owner/project"


def make_payload(tag="v1.2.3", prerelease=False, assets=None, published="2026-09-15T10:00:00Z"):
    return {"tag_name": tag, "html_url": f"https://github.com/{REPO}/releases/tag/{tag}",
            "published_at": published, "prerelease": prerelease, "assets": assets or []}


def asset(name, size=1_048_576, url=None):
    return {"name": name, "size": size,
            "browser_download_url": url or f"https://github.com/{REPO}/releases/download/v1.2.3/{name}"}


TELPOST_ASSETS = [
    asset("telepost-1.2.3-linux-x64.tar.gz"), asset("telepost-linux-x64"),
    asset("telepost-1.2.3-windows-x64.zip"), asset("telepost-windows-x64.exe"),
    asset("telepost-1.2.3-macos-arm64.tar.gz"), asset("telepost-macos-arm64"),
    asset("app-release.apk", size=5242880), asset("SHA256SUMS", size=512),
    asset("RELEASE-METADATA.json", size=2048),
]


class GeneratorTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.payload = self.root / "release.json"

    def tearDown(self):
        self.tmp.cleanup()

    def write_payload(self, payload):
        self.payload.write_text(json.dumps(payload), encoding="utf-8")

    def write_config(self, cfg):
        p = self.root / "download-page.json"
        p.write_text(json.dumps(cfg), encoding="utf-8")
        return p

    def run_gen(self, *extra, config=None, force=False):
        args = [sys.executable, str(GEN), REPO, "--input-json", str(self.payload)]
        if force:
            args.append("--force")
        args += list(extra)
        if config:
            args += ["--config", str(config)]
        return subprocess.run(args, cwd=self.root, capture_output=True, text=True)

    def page(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    def test_explicit_tag_writes_both_languages_with_markers(self):
        self.write_payload(make_payload(assets=TELPOST_ASSETS))
        r = self.run_gen("--tag", "v1.2.3", config=self.write_config({}))
        self.assertEqual(r.returncode, 0, r.stderr)
        zh = self.page("docs/download.md")
        en = self.page("docs/en/download.md")
        self.assertIn("<!-- docsite-release-tag: v1.2.3 -->", zh)
        self.assertIn("<!-- docsite-release-repo: owner/project -->", zh)
        self.assertIn("## 最新版本：`v1.2.3`", zh)
        self.assertIn("## Latest version: `v1.2.3`", en)

    def test_asset_classification_and_checksum_row(self):
        self.write_payload(make_payload(assets=TELPOST_ASSETS))
        self.run_gen(config=self.write_config({}))
        zh = self.page("docs/download.md")
        for expected in ("Linux · x64", "Windows · x64", "macOS · arm64", "Android",
                         "SHA256SUMS", "RELEASE-METADATA.json"):
            self.assertIn(expected, zh)

    def test_no_assets_message(self):
        self.write_payload(make_payload(assets=[]))
        self.run_gen(config=self.write_config({}))
        self.assertIn("没有附带二进制资产", self.page("docs/download.md"))
        self.assertIn("ships no binary assets", self.page("docs/en/download.md"))

    def test_idempotent_render_same_tag(self):
        self.write_payload(make_payload(assets=TELPOST_ASSETS))
        self.run_gen(config=self.write_config({}))
        first_bytes = (self.root / "docs/download.md").read_bytes()
        self.run_gen(config=self.write_config({}))
        self.assertEqual(first_bytes, (self.root / "docs/download.md").read_bytes())

    def test_stale_write_refused_without_force(self):
        self.write_payload(make_payload(tag="v2.0.0", assets=[asset("a")]))
        self.run_gen(config=self.write_config({}))
        self.write_payload(make_payload(tag="v1.9.0", assets=[asset("a")]))
        r = self.run_gen(config=self.write_config({}))
        self.assertIn("refusing to downgrade", r.stderr)
        self.assertIn("v2.0.0", self.page("docs/download.md"))

    def test_prerelease_does_not_overwrite_stable_by_default(self):
        self.write_payload(make_payload(tag="v1.2.0", assets=[asset("a")]))
        self.run_gen(config=self.write_config({}))
        self.write_payload(make_payload(tag="v1.3.0-beta.1", prerelease=True, assets=[asset("b")]))
        r = self.run_gen(config=self.write_config({}))
        self.assertIn("refusing to overwrite stable page with prerelease", r.stderr)
        self.assertIn("v1.2.0", self.page("docs/download.md"))

    def test_prerelease_allowed_with_trackPrerelease(self):
        self.write_payload(make_payload(tag="v1.2.0", assets=[asset("a")]))
        self.run_gen(config=self.write_config({}))
        self.write_payload(make_payload(tag="v1.3.0-beta.1", prerelease=True, assets=[asset("b")]))
        r = self.run_gen(config=self.write_config({"trackPrerelease": True}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("v1.3.0-beta.1", self.page("docs/download.md"))

    def test_single_language_only(self):
        self.write_payload(make_payload(assets=TELPOST_ASSETS))
        r = self.run_gen("--language", "en", config=self.write_config({}))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.root / "docs/en/download.md").exists())
        self.assertFalse((self.root / "docs/download.md").exists())

    def test_custom_languages_and_paths(self):
        self.write_payload(make_payload(assets=TELPOST_ASSETS))
        cfg = {"languages": ["zh"], "outputs": {"zh": "downloads/current.md"}, "displayName": "CustomName"}
        self.run_gen(config=self.write_config(cfg))
        self.assertIn("下载 CustomName", self.page("downloads/current.md"))
        self.assertFalse((self.root / "docs").exists())

    def test_preview_only_in_first_language(self):
        self.write_payload(make_payload(assets=TELPOST_ASSETS))
        (self.root / "docs").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "download-preview.md").write_text("== CUSTOM PREVIEW ==", encoding="utf-8")
        self.run_gen(config=self.write_config({}))
        self.assertIn("== CUSTOM PREVIEW ==", self.page("docs/download.md"))
        self.assertNotIn("== CUSTOM PREVIEW ==", self.page("docs/en/download.md"))

    def test_check_ok(self):
        self.write_payload(make_payload(tag="v1.2.0", assets=[asset("a")]))
        self.run_gen(config=self.write_config({}))
        r = self.run_gen("--check", config=self.write_config({}))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("OK", r.stdout)

    def test_check_stale_detects_missing_and_old_tag(self):
        self.write_payload(make_payload(tag="v1.2.0", assets=[asset("a")]))
        r = self.run_gen("--check", config=self.write_config({}))
        self.assertEqual(r.returncode, 2)
        self.assertIn("MISSING", r.stdout)
        self.run_gen(config=self.write_config({}))
        self.write_payload(make_payload(tag="v1.9.0", assets=[asset("a")]))
        r = self.run_gen("--check", config=self.write_config({}))
        self.assertEqual(r.returncode, 2)
        self.assertIn("STALE", r.stdout)

    def test_drift_detected_when_marker_missing(self):
        (self.root / "docs").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "download.md").write_text("# hand written", encoding="utf-8")
        (self.root / "docs" / "en").mkdir(parents=True, exist_ok=True)
        (self.root / "docs" / "en" / "download.md").write_text("# hand written", encoding="utf-8")
        self.write_payload(make_payload(tag="v1.2.0", assets=[asset("a")]))
        r = self.run_gen("--check", config=self.write_config({}))
        self.assertEqual(r.returncode, 2)
        self.assertIn("DRIFT", r.stdout)


if __name__ == "__main__":
    unittest.main()
