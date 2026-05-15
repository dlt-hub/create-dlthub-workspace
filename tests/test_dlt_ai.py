from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from create_dlthub_workspace.config import TOOLKITS
from create_dlthub_workspace.dlt_ai import initialize_agent, install_all_toolkits, install_toolkit


class DltAiTests(unittest.TestCase):
    @patch("create_dlthub_workspace.dlt_ai.run_uv_command")
    def test_initialize_agent_runs_dlt_ai_init_for_selected_agent(self, run_uv_command) -> None:
        project_dir = Path("/tmp/workspace")

        initialize_agent("/usr/local/bin/uv", project_dir, "claude")

        run_uv_command.assert_called_once_with(
            "/usr/local/bin/uv",
            project_dir,
            ["run", "dlthub", "ai", "init", "--agent", "claude"],
        )

    @patch("create_dlthub_workspace.dlt_ai.run_uv_command")
    def test_install_toolkit_runs_dlt_ai_toolkit_install(self, run_uv_command) -> None:
        project_dir = Path("/tmp/workspace")

        install_toolkit("/usr/local/bin/uv", project_dir, "data-exploration")

        run_uv_command.assert_called_once_with(
            "/usr/local/bin/uv",
            project_dir,
            ["run", "dlthub", "ai", "toolkit", "data-exploration", "install"],
        )

    @patch("create_dlthub_workspace.dlt_ai.install_toolkit")
    def test_install_all_toolkits_installs_every_configured_toolkit(self, install_toolkit_mock) -> None:
        project_dir = Path("/tmp/workspace")

        install_all_toolkits("/usr/local/bin/uv", project_dir)

        self.assertEqual(install_toolkit_mock.call_count, len(TOOLKITS))
        install_toolkit_mock.assert_any_call("/usr/local/bin/uv", project_dir, TOOLKITS[0])
