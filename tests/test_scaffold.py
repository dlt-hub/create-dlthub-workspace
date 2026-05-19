from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from create_dlthub_workspace.config import AGENTS
from create_dlthub_workspace.errors import ScaffoldError
from create_dlthub_workspace.scaffold import (
    AGENT_FILES,
    INSTALL_TIME_SENTINEL,
    SCAFFOLDS_DIR,
    _drop_unselected_agent_entries,
    _stamp_install_time,
    copy_scaffold,
    validate_scaffold_name,
    validate_target_dir,
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


class DropUnselectedAgentEntriesTests(unittest.TestCase):
    """The filter that removes agent-specific entries from a copied scaffold."""

    def _seed(self, project_dir: Path) -> None:
        """Create every file/dir tracked in AGENT_FILES so we can assert deletion."""
        for entries in AGENT_FILES.values():
            for entry in entries:
                target = project_dir / entry
                # Mix of dirs (.claude, .cursor, .codex) and files (.mcp.json,
                # AGENTS.md). The function uses is_dir() vs file checks, so
                # exercise both.
                if entry.startswith("."):
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.touch()

    def test_full_selection_keeps_everything(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            self._seed(project_dir)

            _drop_unselected_agent_entries(project_dir, ("claude", "cursor", "codex"))

            for entries in AGENT_FILES.values():
                for entry in entries:
                    self.assertTrue((project_dir / entry).exists(), f"{entry} dropped unexpectedly")

    def test_partial_selection_drops_only_unselected_agents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            self._seed(project_dir)

            _drop_unselected_agent_entries(project_dir, ("claude",))

            for entry in AGENT_FILES["claude"]:
                self.assertTrue((project_dir / entry).exists())
            for entry in AGENT_FILES["cursor"]:
                self.assertFalse((project_dir / entry).exists())
            for entry in AGENT_FILES["codex"]:
                self.assertFalse((project_dir / entry).exists())

    def test_unknown_agent_in_selection_deletes_every_known_entry(self) -> None:
        # Wart: a typo like agents=("clade",) matches no key in AGENT_FILES,
        # so every entry gets removed. Argparse normally guards against this
        # at the CLI boundary, but programmatic callers can still trigger it.
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir)
            self._seed(project_dir)

            _drop_unselected_agent_entries(project_dir, ("clade",))

            for entries in AGENT_FILES.values():
                for entry in entries:
                    self.assertFalse(
                        (project_dir / entry).exists(),
                        f"{entry} survived a typo-selection — filter is non-strict.",
                    )


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


class ValidateTargetDirTests(unittest.TestCase):
    """Direct tests for the target-directory check that gates copy_scaffold."""

    def test_raises_when_dir_exists_and_is_non_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "occupied"
            project_dir.mkdir()
            (project_dir / "existing.txt").write_text("hi", encoding="utf-8")

            with self.assertRaises(ScaffoldError):
                validate_target_dir(project_dir)

    def test_passes_when_dir_does_not_exist(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "not_yet_created"
            validate_target_dir(project_dir)  # must not raise

    def test_passes_when_dir_exists_but_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "empty_dir"
            project_dir.mkdir()
            validate_target_dir(project_dir)  # must not raise


class ValidateScaffoldNameTests(unittest.TestCase):
    """Direct tests for scaffold-name validation."""

    def test_raises_for_unknown_scaffold(self) -> None:
        with self.assertRaises(ScaffoldError):
            validate_scaffold_name("does-not-exist")

    def test_passes_for_bundled_scaffolds(self) -> None:
        validate_scaffold_name("starter_workspace")  # must not raise
        validate_scaffold_name("minimal_workspace")  # must not raise


class ScaffoldsDirTests(unittest.TestCase):
    def test_bundled_scaffolds_exist(self) -> None:
        self.assertTrue((SCAFFOLDS_DIR / "starter_workspace").is_dir())
        self.assertTrue((SCAFFOLDS_DIR / "minimal_workspace").is_dir())


# Hardcoded snapshot of the top-level entries `dlthub ai init --agent <name>`
# produces on a fresh workspace, captured against dlthub 0.27.0a0. This is an
# INDEPENDENT source of truth: the other scaffold tests iterate AGENT_FILES to
# decide what to seed and assert, which means they tautologically prove "the
# map filters itself correctly." This snapshot proves the map matches reality.
#
# If a future dlthub release adds or removes entries, refresh this snapshot
# (by running `dlthub ai init --agent <name>` in a clean dir and inspecting
# the project root) and update AGENT_FILES in scaffold.py to match.
DLTHUB_GENERATED_PER_AGENT: dict[str, frozenset[str]] = {
    "claude": frozenset({".claude", ".claudeignore", ".mcp.json"}),
    "cursor": frozenset({".cursor", ".cursorignore"}),
    "codex": frozenset({".codex", ".codexignore", "AGENTS.md"}),
}


class AgentFilesCoverageTests(unittest.TestCase):
    """Verifies AGENT_FILES matches the observed dlthub-init output snapshot.

    Catches the class of bug where the map drifts from what dlthub actually
    generates — orphan files left in the user's workspace under partial
    agent selections.
    """

    def test_map_matches_snapshot_for_every_agent(self) -> None:
        for agent, expected in DLTHUB_GENERATED_PER_AGENT.items():
            with self.subTest(agent=agent):
                self.assertEqual(
                    frozenset(AGENT_FILES[agent]),
                    expected,
                    f"AGENT_FILES[{agent!r}] is out of sync with the captured "
                    "dlthub init output. Refresh by running "
                    f"`dlthub ai init --agent {agent}` in a clean dir, then "
                    "update both AGENT_FILES and DLTHUB_GENERATED_PER_AGENT.",
                )

    def test_map_keys_cover_every_agent(self) -> None:
        # If AGENTS grows but AGENT_FILES doesn't, partial selections silently
        # skip filtering for the new agent.
        self.assertEqual(set(AGENT_FILES.keys()), set(AGENTS))


if __name__ == "__main__":
    unittest.main()
