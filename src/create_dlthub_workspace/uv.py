"""uv detection, installation, and execution helpers."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import urllib.request
from pathlib import Path

from .errors import UvError

UV_UNIX_INSTALLER = "https://astral.sh/uv/install.sh"
UV_WINDOWS_INSTALLER = "https://astral.sh/uv/install.ps1"


def find_uv() -> str | None:
    """Find uv on PATH or in the default standalone installer locations."""
    found = shutil.which("uv")
    if found:
        return found

    for candidate in _common_uv_paths():
        if candidate.exists():
            return str(candidate)
    return None


def ensure_uv(*, assume_yes: bool, confirm_install) -> str:
    """Return a uv executable, installing uv if the user approves."""
    uv = find_uv()
    if uv:
        return uv

    if not assume_yes and not confirm_install("uv is required but was not found. Install uv now?"):
        raise UvError("uv is required. Install uv and run this command again.")

    install_uv()
    uv = find_uv()
    if uv:
        return uv

    raise UvError("uv was installed, but it is not available on PATH yet. Open a new terminal and try again.")


def install_uv() -> None:
    """Install uv with Astral's official standalone installer."""
    system = platform.system().lower()
    if system == "windows":
        _run_windows_installer()
    else:
        _run_unix_installer()


def run_uv_sync(uv_executable: str, project_dir: Path) -> None:
    """Run `uv sync` in the generated workspace."""
    _run([uv_executable, "sync"], cwd=project_dir, isolated_project=True)


def run_uv_command(uv_executable: str, project_dir: Path, args: list[str]) -> None:
    """Run a uv command in the generated workspace."""
    _run([uv_executable, *args], cwd=project_dir, isolated_project=True)


def _run_unix_installer() -> None:
    try:
        with urllib.request.urlopen(UV_UNIX_INSTALLER, timeout=30) as response:
            script = response.read()
    except OSError as exc:
        raise UvError(f"Could not download uv installer: {exc}") from exc

    _run(["sh"], input_bytes=script)


def _run_windows_installer() -> None:
    powershell = shutil.which("powershell") or shutil.which("pwsh")
    if not powershell:
        raise UvError("PowerShell is required to install uv on Windows.")

    try:
        with urllib.request.urlopen(UV_WINDOWS_INSTALLER, timeout=30) as response:
            script = response.read()
    except OSError as exc:
        raise UvError(f"Could not download uv installer: {exc}") from exc

    _run([powershell, "-ExecutionPolicy", "ByPass", "-Command", "-"], input_bytes=script)


def _run(
    command: list[str],
    *,
    cwd: Path | None = None,
    input_bytes: bytes | None = None,
    isolated_project: bool = False,
) -> None:
    try:
        subprocess.run(
            command,
            cwd=cwd,
            env=_isolated_project_env() if isolated_project else None,
            input=input_bytes,
            check=True,
        )
    except FileNotFoundError as exc:
        raise UvError(f"Command not found: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        joined = " ".join(command)
        raise UvError(f"Command failed with exit code {exc.returncode}: {joined}") from exc


def _common_uv_paths() -> tuple[Path, ...]:
    home = Path.home()
    if os.name == "nt":
        return (
            home / ".local" / "bin" / "uv.exe",
            home / ".cargo" / "bin" / "uv.exe",
        )
    return (
        home / ".local" / "bin" / "uv",
        home / ".cargo" / "bin" / "uv",
    )


def _isolated_project_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("VIRTUAL_ENV", "CONDA_PREFIX", "PYTHONPATH"):
        env.pop(name, None)
    return env
