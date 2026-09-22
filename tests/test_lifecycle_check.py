#!/usr/bin/env python3
"""Unit tests for docsite.py lifecyclecheck (hermetic: temp dirs, no git required)."""
import argparse
import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import docsite  # noqa: E402


VALID_ARCHIVE = """\
<!-- doc-lifecycle: archive -->
Doc-Type: phase-report
Status: complete
Effective: 2026-09-12
Expires: 2030-12-31
Superseded-By: docs/README.md
---

# Archived phase report
"""


class LifecycleCheckTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_check(self):
        args = argparse.Namespace(all=None, paths=[str(self.root)])
        with contextlib.redirect_stdout(io.StringIO()):
            return docsite.cmd_lifecyclecheck(args)

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def test_root_transient_doc_flagged(self):
        self.write("one-off-report.md", "# one-off\n")
        self.assertEqual(self.run_check(), 1)

    def test_canonical_root_doc_allowed(self):
        self.write("README.md", "# ok\n")
        self.assertEqual(self.run_check(), 0)

    def test_dated_doc_outside_archive_flagged(self):
        self.write("docs/phase-status-2026-09-12.md", "# snapshot\n")
        self.assertEqual(self.run_check(), 1)

    def test_archive_file_with_lifecycle_block_ok(self):
        self.write("README.md", "# ok\n")
        self.write("docs/archive/report.md", VALID_ARCHIVE)
        self.assertEqual(self.run_check(), 0)

    def test_archive_missing_lifecycle_block_flagged(self):
        self.write("README.md", "# ok\n")
        self.write("docs/archive/report.md", "# missing metadata\n")
        self.assertEqual(self.run_check(), 1)

    def test_expired_archive_flagged(self):
        self.write("README.md", "# ok\n")
        self.write("docs/archive/report.md",
                   VALID_ARCHIVE.replace("Expires: 2030-12-31", "Expires: 2020-01-01"))
        self.assertEqual(self.run_check(), 1)

    def test_archive_link_in_sidebar_flagged(self):
        self.write("README.md", "# ok\n")
        self.write("docs/archive/report.md", VALID_ARCHIVE)
        self.write("docs/_sidebar.md", "- [x](/archive/report.md)\n")
        self.assertEqual(self.run_check(), 1)


if __name__ == "__main__":
    unittest.main()
