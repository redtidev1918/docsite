#!/usr/bin/env python3
"""build/preview/dev 命令:包装 npm run docs:*。

无 Node 环境时跳过真实调用并明示;非 v2 仓库、缺 package.json 给出清晰指引。
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

DOCSITE = Path(__file__).resolve().parent.parent / "docsite.py"
HAS_NPM = shutil.which("npm") is not None


@unittest.skipUnless(HAS_NPM, "本机无 npm,跳过 build 包装命令的真实调用")
class BuildWrapperTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "docs/.vitepress").mkdir(parents=True)
        (self.root / "docs/.vitepress/config.mts").write_text("// docsite: managed file\n", encoding="utf-8")
        # 轻量假工程:验证 CLI 接线,不跑完整 VitePress 构建(CI 与阶段 4 另行真构)
        (self.root / "package.json").write_text(
            json.dumps({"name": "docs", "private": True,
                        "scripts": {"docs:build": "node -e \"require('fs').writeFileSync('built.txt','ok')\""},
                        "devDependencies": {}}), encoding="utf-8")
        # 占位 node_modules/vitepress,避免包装命令抢先执行 npm ci
        (self.root / "node_modules/vitepress").mkdir(parents=True)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cmd(self, cmd):
        return subprocess.run([sys.executable, str(DOCSITE), cmd],
                              cwd=self.root, capture_output=True, text=True)

    def test_build_invokes_npm_script(self):
        run = self.run_cmd("build")
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual((self.root / "built.txt").read_text(encoding="utf-8"), "ok")

    def test_preview_and_dev_pass_through(self):
        # preview/dev 无对应假脚本时 npm 报错退出——只验证接线的退出码传导(非零)
        run = self.run_cmd("preview")
        self.assertNotEqual(run.returncode, 0)


class BuildGuardTestCase(unittest.TestCase):
    """无 npm / 非 v2 / 缺 package.json:清晰指引,不静默成功。"""

    def run_cmd(self, cmd, cwd):
        return subprocess.run([sys.executable, str(DOCSITE), cmd],
                              cwd=cwd, capture_output=True, text=True)

    def test_rejects_non_v2_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            run = self.run_cmd("build", tmp)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("migrate", run.stderr + run.stdout)

    @unittest.skipIf(HAS_NPM, "本机有 npm,该拒绝路径无法在本机验证")
    def test_rejects_without_npm(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "docs/.vitepress").mkdir(parents=True)
            (root / "docs/.vitepress/config.mts").write_text("// x\n", encoding="utf-8")
            (root / "package.json").write_text("{}", encoding="utf-8")
            run = self.run_cmd("build", tmp)
            self.assertNotEqual(run.returncode, 0)
            self.assertIn("Node.js 22+", run.stderr + run.stdout)


if __name__ == "__main__":
    unittest.main()
