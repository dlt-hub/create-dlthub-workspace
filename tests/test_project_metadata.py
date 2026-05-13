from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from create_dlthub_workspace.project_metadata import apply_workspace_name, normalize_project_name


class ProjectMetadataTests(unittest.TestCase):
    def test_normalize_project_name(self) -> None:
        self.assertEqual(normalize_project_name("My Workspace"), "my-workspace")
        self.assertEqual(normalize_project_name("github_ingest_workspace"), "github-ingest-workspace")
        self.assertEqual(normalize_project_name("___"), "dlthub-workspace")

    def test_apply_workspace_name_rewrites_project_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            pyproject = project_dir / "pyproject.toml"
            pyproject.write_text(
                '[project]\nname = "github-ingest-workspace"\nversion = "0.1.0"\n',
                encoding="utf-8",
            )

            package_name = apply_workspace_name(project_dir, "My Workspace")

            self.assertEqual(package_name, "my-workspace")
            self.assertIn('name = "my-workspace"', pyproject.read_text(encoding="utf-8"))

    def test_apply_workspace_name_inserts_missing_project_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            pyproject = project_dir / "pyproject.toml"
            pyproject.write_text('[project]\nversion = "0.1.0"\n', encoding="utf-8")

            apply_workspace_name(project_dir, "New Workspace")

            self.assertIn('name = "new-workspace"', pyproject.read_text(encoding="utf-8"))

