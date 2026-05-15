from __future__ import annotations

import unittest
from unittest.mock import patch

from create_dlthub_workspace.errors import UvError
from create_dlthub_workspace.uv import ensure_uv, run_uv_command, run_uv_sync


class UvTests(unittest.TestCase):
    @patch("create_dlthub_workspace.uv.find_uv", return_value="/usr/local/bin/uv")
    def test_ensure_uv_returns_existing_executable(self, _find_uv) -> None:
        self.assertEqual(
            ensure_uv(assume_yes=False, confirm_install=lambda _message: False),
            "/usr/local/bin/uv",
        )

    @patch("create_dlthub_workspace.uv.find_uv", return_value=None)
    def test_ensure_uv_requires_confirmation(self, _find_uv) -> None:
        with self.assertRaises(UvError):
            ensure_uv(assume_yes=False, confirm_install=lambda _message: False)

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
