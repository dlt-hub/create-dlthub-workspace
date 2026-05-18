"""Regenerate bundled AI workbench files in every scaffold.

Run via `make generate-ai`. For each scaffold:

1. Copy the scaffold (minus runtime artifacts and existing AI files) to a
   throwaway tmp dir.
2. `uv sync` so `dlthub` is on PATH inside that workspace.
3. Run `dlthub ai init` for each AGENT and `dlthub ai toolkit install` for
   each TOOLKIT, pinning to `WORKBENCH_REF` from config.py.
4. Replace the AI-generated entries in the source scaffold with the freshly
   produced ones.

Commit the resulting diff alongside any `WORKBENCH_REF` bump.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

from create_dlthub_workspace.config import AGENTS, TOOLKITS, WORKBENCH_REF  # noqa: E402
from create_dlthub_workspace.scaffold import SCAFFOLDS_DIR  # noqa: E402

# Top-level entries (relative to the scaffold root) that `dlthub ai init` /
# `toolkit install` produce. These are wiped before regeneration and replaced
# with freshly generated copies. Anything not in this set is scaffold source
# code (pipelines, pyproject.toml, .dlt/config.toml, etc.) and is left alone.
AI_GENERATED_ENTRIES: tuple[str, ...] = (
    ".agents",
    ".claude",
    ".claudeignore",
    ".cursor",
    ".cursorignore",
    ".codex",
    "AGENTS.md",
    ".mcp.json",
    ".dlt/.toolkits",
)

_RUNTIME_DIRS = {".venv", ".pytest_cache", ".ruff_cache", ".mypy_cache", "__pycache__"}


def _ignore_runtime(src: str, names: list[str]) -> set[str]:
    """Skip dev-time artifacts when seeding the throwaway workspace."""
    skip: set[str] = set()
    src_basename = Path(src).name
    for name in names:
        if name in _RUNTIME_DIRS or name.endswith(".pyc"):
            skip.add(name)
        elif src_basename == ".dlt" and name in {"data", "state", ".var"}:
            skip.add(name)
    return skip


def _isolated_env() -> dict[str, str]:
    """Drop parent venv hints so uv resolves the workspace's own .venv."""
    env = os.environ.copy()
    for name in ("VIRTUAL_ENV", "CONDA_PREFIX", "PYTHONPATH"):
        env.pop(name, None)
    return env


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, env=_isolated_env(), check=True)


def _branch_args() -> list[str]:
    """Render --branch only when a ref is pinned; otherwise let dlthub use upstream default."""
    return ["--branch", WORKBENCH_REF] if WORKBENCH_REF else []


def regenerate(scaffold_dir: Path) -> None:
    print(f"\n=== {scaffold_dir.name} ===")
    with tempfile.TemporaryDirectory(prefix=f"gen-ai-{scaffold_dir.name}-") as tmp:
        work = Path(tmp) / "workspace"
        shutil.copytree(scaffold_dir, work, ignore=_ignore_runtime)

        # Start with a clean slate inside the throwaway copy.
        for entry in AI_GENERATED_ENTRIES:
            _remove(work / entry)

        print("  uv sync")
        _run(["uv", "sync"], cwd=work)

        ref_label = WORKBENCH_REF or "<upstream default>"

        for agent in AGENTS:
            print(f"  dlthub ai init --agent {agent}  (ref={ref_label})")
            _run(
                [
                    "uv",
                    "run",
                    "dlthub",
                    "--non-interactive",
                    "ai",
                    "init",
                    "--agent",
                    agent,
                    *_branch_args(),
                    "--overwrite",
                ],
                cwd=work,
            )

        for toolkit in TOOLKITS:
            print(f"  dlthub ai toolkit install {toolkit}  (ref={ref_label})")
            _run(
                [
                    "uv",
                    "run",
                    "dlthub",
                    "--non-interactive",
                    "ai",
                    "toolkit",
                    "install",
                    toolkit,
                    *_branch_args(),
                    "--overwrite",
                ],
                cwd=work,
            )

        # Swap the freshly generated AI entries into the source scaffold.
        for entry in AI_GENERATED_ENTRIES:
            target = scaffold_dir / entry
            _remove(target)
            source = work / entry
            if not source.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)

    print("  done")


def main() -> int:
    print(f"Regenerating AI workbench files (WORKBENCH_REF={WORKBENCH_REF})")
    for scaffold_dir in sorted(p for p in SCAFFOLDS_DIR.iterdir() if p.is_dir()):
        regenerate(scaffold_dir)
    print("\nAll scaffolds refreshed. Review with `git diff src/create_dlthub_workspace/scaffolds/`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
