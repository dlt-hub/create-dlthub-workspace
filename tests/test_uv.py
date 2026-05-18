from __future__ import annotations

import unittest
from unittest.mock import patch

from create_dlthub_workspace.uv import run_uv_command, run_uv_sync


class UvTests(unittest.TestCase):
    @patch.dict(
        "os.environ",
        {
            "VIRTUAL_ENV": "/parent/.venv",
            "CONDA_PREFIX": "/parent/conda",
            "PYTHONPATH": "src",
            "UV_CACHE_DIR": "/tmp/uv-cache",
        },
    )
    @patch("subprocess.run")
    def test_run_uv_sync_drops_parent_python_environment(self, subprocess_run) -> None:
        run_uv_sync("/usr/local/bin/uv", project_dir="/tmp/workspace")

        env = subprocess_run.call_args.kwargs["env"]
        self.assertNotIn("VIRTUAL_ENV", env)
        self.assertNotIn("CONDA_PREFIX", env)
        self.assertNotIn("PYTHONPATH", env)
        self.assertEqual(env["UV_CACHE_DIR"], "/tmp/uv-cache")

    @patch("subprocess.run")
    def test_run_uv_command_executes_in_project_directory(self, subprocess_run) -> None:
        run_uv_command("/usr/local/bin/uv", project_dir="/tmp/workspace", args=["run", "dlthub", "--version"])

        subprocess_run.assert_called_once()
        self.assertEqual(subprocess_run.call_args.args[0], ["/usr/local/bin/uv", "run", "dlthub", "--version"])
        self.assertEqual(subprocess_run.call_args.kwargs["cwd"], "/tmp/workspace")


if __name__ == "__main__":
    unittest.main()
