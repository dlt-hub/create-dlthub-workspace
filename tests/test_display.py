"""Tests for display panels (next-steps + resume-steps + banner).

Uses `console.capture()` to grab rendered text so we can assert on
the content of rich panels.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from create_dlthub_workspace.config import VERSION
from create_dlthub_workspace.display import (
    console,
    print_banner,
    print_next_steps,
    print_resume_steps,
)


class PrintNextStepsTests(unittest.TestCase):
    def test_starter_scaffold_renders_and_includes_cd_hint(self) -> None:
        project_dir = Path("/tmp/my_workspace")
        with console.capture() as cap:
            print_next_steps(project_dir, scaffold="starter_workspace")
        output = cap.get()

        # str(path) so the assertion matches the platform's separator
        # (Windows renders backslashes, POSIX renders forward slashes).
        self.assertIn(str(project_dir), output)
        self.assertIn("uv run dlthub run load_breweries", output)

    def test_minimal_scaffold_renders_with_its_pipeline_command(self) -> None:
        with console.capture() as cap:
            print_next_steps(Path("/tmp/my_workspace"), scaffold="minimal_workspace")
        output = cap.get()

        self.assertIn("uv run dlthub run load_data", output)
        # Minimal scaffold has an instruction-only step with no command.
        self.assertIn("Edit pipeline.py", output)

    def test_unknown_scaffold_raises_key_error(self) -> None:
        with self.assertRaises(KeyError):
            print_next_steps(Path("/tmp/my_workspace"), scaffold="bogus")


class PrintResumeStepsTests(unittest.TestCase):
    def test_uv_not_installed_includes_install_command(self) -> None:
        with console.capture() as cap:
            print_resume_steps(Path("/tmp/my_workspace"), uv_installed=False)
        output = cap.get()

        self.assertIn("Install uv", output)
        self.assertIn("curl -LsSf https://astral.sh/uv/install.sh", output)
        self.assertIn("uv sync", output)

    def test_uv_installed_omits_install_command(self) -> None:
        with console.capture() as cap:
            print_resume_steps(Path("/tmp/my_workspace"), uv_installed=True)
        output = cap.get()

        self.assertNotIn("curl -LsSf", output)
        self.assertIn("uv sync", output)


class PrintBannerTests(unittest.TestCase):
    def test_renders_with_version_in_title(self) -> None:
        with console.capture() as cap:
            print_banner()
        output = cap.get()

        self.assertIn(f"v{VERSION}", output)


if __name__ == "__main__":
    unittest.main()
