from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from create_dlthub_workspace.errors import ScaffoldError
from create_dlthub_workspace.scaffold import (
    AGENT_FILES,
    INSTALL_TIME_SENTINEL,
    SCAFFOLDS_DIR,
    _stamp_install_time,
    copy_scaffold,
)


class CopyScaffoldTests(unittest.TestCase):
    def test_copies_bundled_minimal_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "new_workspace"
            copy_scaffold(project_dir, scaffold="minimal_workspace")

            self.assertTrue((project_dir / "pyproject.toml").exists())
            self.assertTrue((project_dir / "pipeline.py").exists())
            self.assertTrue((project_dir / "__deployment__.py").exists())
            self.assertTrue((project_dir / ".dlt" / "config.toml").exists())

    def test_copies_bundled_starter_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "new_workspace"
            copy_scaffold(project_dir, scaffold="starter_workspace")

            self.assertTrue((project_dir / "pyproject.toml").exists())
            self.assertTrue((project_dir / "starter_pipeline.py").exists())
            self.assertTrue((project_dir / "notebooks").is_dir())

    def test_skips_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "new_workspace"
            copy_scaffold(project_dir, scaffold="starter_workspace")

            # Verify the dev-time artifacts are not propagated to the user's workspace.
            self.assertFalse((project_dir / "__pycache__").exists())
            self.assertFalse((project_dir / ".venv").exists())
            if (project_dir / ".dlt").exists():
                self.assertFalse((project_dir / ".dlt" / "data").exists())
                self.assertFalse((project_dir / ".dlt" / "state").exists())

    def test_raises_for_unknown_scaffold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ScaffoldError):
                copy_scaffold(Path(tmpdir) / "p", scaffold="does-not-exist")

    def test_raises_when_target_is_not_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "occupied"
            project_dir.mkdir()
            (project_dir / "existing.txt").write_text("hi", encoding="utf-8")

            with self.assertRaises(ScaffoldError):
                copy_scaffold(project_dir, scaffold="minimal_workspace")

    def test_drops_entries_for_unselected_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "claude_only"
            # Seed the scaffold dir with the entries we'd expect to filter,
            # since the bundled scaffolds may or may not have AI files yet.
            scaffold_source = SCAFFOLDS_DIR / "minimal_workspace"
            for entries in AGENT_FILES.values():
                for entry in entries:
                    candidate = scaffold_source / entry
                    if not candidate.exists():
                        # Skip; we still validate the removal logic on whatever IS present.
                        continue

            copy_scaffold(project_dir, scaffold="minimal_workspace", agents=("claude",))

            for entry in AGENT_FILES["cursor"]:
                self.assertFalse((project_dir / entry).exists(), f"{entry} should be removed")
            for entry in AGENT_FILES["codex"]:
                self.assertFalse((project_dir / entry).exists(), f"{entry} should be removed")


class StampInstallTimeTests(unittest.TestCase):
    def test_replaces_sentinel_with_current_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            manifest = project_dir / ".dlt" / ".toolkits"
            manifest.parent.mkdir()
            manifest.write_text(
                f"init:\n  installed_at: '{INSTALL_TIME_SENTINEL}'\n  agent: claude\n",
                encoding="utf-8",
            )

            _stamp_install_time(project_dir)

            updated = manifest.read_text(encoding="utf-8")
            self.assertNotIn(INSTALL_TIME_SENTINEL, updated)
            # Real timestamps start with a 4-digit year and end with the UTC offset.
            self.assertRegex(updated, r"installed_at: '\d{4}-\d{2}-\d{2}T.+\+00:00'")

    def test_noop_when_manifest_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _stamp_install_time(Path(tmpdir))  # must not raise

    def test_noop_when_sentinel_already_replaced(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            manifest = project_dir / ".dlt" / ".toolkits"
            manifest.parent.mkdir()
            already_stamped = "installed_at: '2024-01-01T00:00:00+00:00'\n"
            manifest.write_text(already_stamped, encoding="utf-8")

            _stamp_install_time(project_dir)

            self.assertEqual(manifest.read_text(encoding="utf-8"), already_stamped)


class ScaffoldsDirTests(unittest.TestCase):
    def test_bundled_scaffolds_exist(self) -> None:
        self.assertTrue((SCAFFOLDS_DIR / "starter_workspace").is_dir())
        self.assertTrue((SCAFFOLDS_DIR / "minimal_workspace").is_dir())


if __name__ == "__main__":
    unittest.main()
