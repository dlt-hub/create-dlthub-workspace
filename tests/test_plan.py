"""Tests for build_plan — the decision tree that resolves CLI args + prompts
into a frozen WorkspacePlan.

Mocks every external dependency (find_uv, choose_scaffold, choose_agents,
confirm, validate_scaffold_target) so each test is fast and deterministic.
"""

from __future__ import annotations

import argparse
import unittest
from unittest.mock import MagicMock, patch

from create_dlthub_workspace.config import RECOMMENDED
from create_dlthub_workspace.errors import ScaffoldError, WorkspaceError
from create_dlthub_workspace.plan import WorkspaceStage, build_plan


def _make_args(**overrides: object) -> argparse.Namespace:
    """Mirror what argparse would produce; tests override individual fields."""
    defaults: dict[str, object] = {
        "project_dir": "/tmp/test_workspace",
        "scaffold": None,
        "agent": None,
        "yes": False,
        "verbose": False,
        "skip_uv_sync": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


class BuildPlanYesModeTests(unittest.TestCase):
    """`--yes` runs the recommended path with no prompts fired."""

    @patch("create_dlthub_workspace.plan.choose_agents")
    @patch("create_dlthub_workspace.plan.choose_scaffold")
    @patch("create_dlthub_workspace.plan.confirm")
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_uv_present_produces_full_recommended_plan(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        confirm: MagicMock,
        choose_scaffold: MagicMock,
        choose_agents: MagicMock,
    ) -> None:
        plan = build_plan(_make_args(yes=True))

        self.assertEqual(plan.stage, WorkspaceStage.FULL)
        self.assertEqual(plan.scaffold, RECOMMENDED.scaffold)
        self.assertEqual(plan.agents, RECOMMENDED.agents)
        self.assertFalse(plan.install_uv)
        self.assertEqual(plan.uv_executable, "/usr/local/bin/uv")
        confirm.assert_not_called()
        choose_scaffold.assert_not_called()
        choose_agents.assert_not_called()

    @patch("create_dlthub_workspace.plan.confirm")
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value=None)
    def test_uv_absent_marks_install_uv_without_prompting(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        confirm: MagicMock,
    ) -> None:
        plan = build_plan(_make_args(yes=True))

        self.assertEqual(plan.stage, WorkspaceStage.FULL)
        self.assertTrue(plan.install_uv)
        self.assertIsNone(plan.uv_executable)
        confirm.assert_not_called()

    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_skip_uv_sync_forces_through_uv_install_stage(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
    ) -> None:
        plan = build_plan(_make_args(yes=True, skip_uv_sync=True))

        self.assertEqual(plan.stage, WorkspaceStage.THROUGH_UV_INSTALL)
        # Agents are vendored into the scaffold, so the recommended set is
        # honored even when execution stops before uv sync.
        self.assertEqual(plan.agents, RECOMMENDED.agents)


class BuildPlanInteractiveTests(unittest.TestCase):
    """Interactive mode: prompts fire and shape the plan."""

    @patch(
        "create_dlthub_workspace.plan.choose_agents",
        return_value=["claude", "cursor"],
    )
    @patch(
        "create_dlthub_workspace.plan.choose_scaffold",
        return_value="starter_workspace",
    )
    @patch("create_dlthub_workspace.plan.confirm", return_value=True)
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_uv_present_sync_confirmed_runs_full(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        confirm: MagicMock,
        choose_scaffold: MagicMock,
        choose_agents: MagicMock,
    ) -> None:
        plan = build_plan(_make_args())

        self.assertEqual(plan.stage, WorkspaceStage.FULL)
        self.assertEqual(plan.scaffold, "starter_workspace")
        self.assertEqual(plan.agents, ("claude", "cursor"))
        choose_scaffold.assert_called_once()
        choose_agents.assert_called_once()
        # Only the uv-sync prompt fires when uv is already present.
        self.assertEqual(confirm.call_count, 1)

    @patch("create_dlthub_workspace.plan.choose_agents", return_value=["claude"])
    @patch(
        "create_dlthub_workspace.plan.choose_scaffold",
        return_value="starter_workspace",
    )
    @patch("create_dlthub_workspace.plan.confirm", return_value=False)
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value=None)
    def test_uv_install_declined_stops_at_scaffold_only(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        _confirm: MagicMock,
        _choose_scaffold: MagicMock,
        choose_agents: MagicMock,
    ) -> None:
        plan = build_plan(_make_args())

        self.assertEqual(plan.stage, WorkspaceStage.SCAFFOLD_ONLY)
        self.assertFalse(plan.install_uv)
        # Agents are asked before the uv prompts now, so a SCAFFOLD_ONLY plan
        # still carries the user's actual selection (vendored into the copy).
        self.assertEqual(plan.agents, ("claude",))
        choose_agents.assert_called_once()

    @patch("create_dlthub_workspace.plan.choose_agents", return_value=["claude", "codex"])
    @patch(
        "create_dlthub_workspace.plan.choose_scaffold",
        return_value="starter_workspace",
    )
    @patch("create_dlthub_workspace.plan.confirm")
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_sync_declined_stops_at_through_uv_install(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        confirm: MagicMock,
        _choose_scaffold: MagicMock,
        choose_agents: MagicMock,
    ) -> None:
        # Only the uv-sync prompt fires (uv was already present), so a single
        # `False` return is enough to drive the path.
        confirm.return_value = False

        plan = build_plan(_make_args())

        self.assertEqual(plan.stage, WorkspaceStage.THROUGH_UV_INSTALL)
        # Agents are asked before the uv-sync prompt, so the user's selection
        # is carried into the plan regardless of the sync decision.
        self.assertEqual(plan.agents, ("claude", "codex"))
        choose_agents.assert_called_once()

    @patch(
        "create_dlthub_workspace.plan.choose_agents",
        return_value=["claude"],
    )
    @patch(
        "create_dlthub_workspace.plan.choose_scaffold",
        return_value="starter_workspace",
    )
    @patch("create_dlthub_workspace.plan.confirm", return_value=True)
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value=None)
    def test_uv_install_accepted_then_sync_accepted_runs_full(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        confirm: MagicMock,
        _choose_scaffold: MagicMock,
        _choose_agents: MagicMock,
    ) -> None:
        plan = build_plan(_make_args())

        self.assertEqual(plan.stage, WorkspaceStage.FULL)
        self.assertTrue(plan.install_uv)
        # Two confirm prompts fire: install-uv? and run-uv-sync?
        self.assertEqual(confirm.call_count, 2)


class BuildPlanArgOverrideTests(unittest.TestCase):
    """Explicit CLI flags bypass the corresponding prompts."""

    @patch("create_dlthub_workspace.plan.choose_agents", return_value=["claude"])
    @patch("create_dlthub_workspace.plan.choose_scaffold")
    @patch("create_dlthub_workspace.plan.confirm", return_value=True)
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_scaffold_arg_skips_scaffold_prompt(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        _confirm: MagicMock,
        choose_scaffold: MagicMock,
        _choose_agents: MagicMock,
    ) -> None:
        plan = build_plan(_make_args(scaffold="minimal_workspace"))

        self.assertEqual(plan.scaffold, "minimal_workspace")
        choose_scaffold.assert_not_called()

    @patch("create_dlthub_workspace.plan.choose_agents")
    @patch("create_dlthub_workspace.plan.choose_scaffold", return_value="starter_workspace")
    @patch("create_dlthub_workspace.plan.confirm", return_value=True)
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_agent_arg_skips_agents_prompt(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        _confirm: MagicMock,
        _choose_scaffold: MagicMock,
        choose_agents: MagicMock,
    ) -> None:
        plan = build_plan(_make_args(agent=["claude", "codex"]))

        self.assertEqual(plan.agents, ("claude", "codex"))
        choose_agents.assert_not_called()


class BuildPlanFlagInteractionTests(unittest.TestCase):
    """Documents how flags interact with the prompt path.

    These tests pin down behaviors that have non-obvious side effects (silent
    drops, prompt short-circuits) so any change to flag handling shows up as
    a failing test instead of a silent UX regression.
    """

    @patch("create_dlthub_workspace.plan.choose_agents", return_value=["claude"])
    @patch("create_dlthub_workspace.plan.choose_scaffold", return_value="starter_workspace")
    @patch("create_dlthub_workspace.plan.confirm")
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_skip_uv_sync_short_circuits_the_sync_prompt(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        confirm: MagicMock,
        _choose_scaffold: MagicMock,
        _choose_agents: MagicMock,
    ) -> None:
        # Interactive mode, but --skip-uv-sync should win without asking.
        plan = build_plan(_make_args(skip_uv_sync=True))

        self.assertEqual(plan.stage, WorkspaceStage.THROUGH_UV_INSTALL)
        confirm.assert_not_called()

    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_explicit_agent_honored_even_when_stage_skips_uv_sync(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
    ) -> None:
        # Vendored AI workbenches don't need uv to be installed, so an explicit
        # --agent selection is preserved even when --skip-uv-sync truncates the
        # stage. Regression guard for the previously-silent input drop.
        plan = build_plan(_make_args(yes=True, agent=["claude"], skip_uv_sync=True))

        self.assertEqual(plan.stage, WorkspaceStage.THROUGH_UV_INSTALL)
        self.assertEqual(plan.agents, ("claude",))


class BuildPlanValidationTests(unittest.TestCase):
    """Failures and edge cases."""

    @patch("create_dlthub_workspace.plan.find_uv")
    @patch(
        "create_dlthub_workspace.plan.validate_scaffold_target",
        side_effect=ScaffoldError("Unknown scaffold 'x'"),
    )
    def test_scaffold_validation_fails_before_uv_detection(
        self,
        _validate: MagicMock,
        find_uv: MagicMock,
    ) -> None:
        with self.assertRaises(ScaffoldError):
            build_plan(_make_args(scaffold="starter_workspace", yes=True))

        # Validation short-circuits the rest of planning, including uv detection.
        find_uv.assert_not_called()

    @patch("create_dlthub_workspace.plan.choose_agents", return_value=[])
    @patch("create_dlthub_workspace.plan.choose_scaffold", return_value="starter_workspace")
    @patch("create_dlthub_workspace.plan.confirm", return_value=True)
    @patch("create_dlthub_workspace.plan.validate_scaffold_target")
    @patch("create_dlthub_workspace.plan.find_uv", return_value="/usr/local/bin/uv")
    def test_empty_agent_selection_raises_workspace_error(
        self,
        _find_uv: MagicMock,
        _validate: MagicMock,
        _confirm: MagicMock,
        _choose_scaffold: MagicMock,
        _choose_agents: MagicMock,
    ) -> None:
        with self.assertRaises(WorkspaceError):
            build_plan(_make_args())


if __name__ == "__main__":
    unittest.main()
