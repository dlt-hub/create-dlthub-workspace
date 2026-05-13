"""Download and extract the starter scaffold."""

from __future__ import annotations

import io
import shutil
import tarfile
import urllib.request
from pathlib import Path

from .config import DEFAULT_TEMPLATE_DIR, tarball_url
from .errors import ScaffoldError


def download_scaffold(
    project_dir: Path,
    *,
    template_ref: str,
    template_dir: str = DEFAULT_TEMPLATE_DIR,
) -> None:
    """Download the starter-pack tarball and extract one template directory."""
    if project_dir.exists() and any(project_dir.iterdir()):
        raise ScaffoldError(f"Target directory already exists and is not empty: {project_dir}")

    try:
        with urllib.request.urlopen(tarball_url(template_ref), timeout=30) as response:
            data = response.read()
    except OSError as exc:
        raise ScaffoldError(f"Could not download starter scaffold: {exc}") from exc

    project_dir.mkdir(parents=True, exist_ok=True)
    extract_template_from_tarball(data, project_dir, template_dir=template_dir)


def extract_template_from_tarball(
    data: bytes,
    project_dir: Path,
    *,
    template_dir: str = DEFAULT_TEMPLATE_DIR,
) -> None:
    """Extract only `template_dir` from a GitHub tarball into `project_dir`."""
    extracted_any = False
    project_root = project_dir.resolve()

    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            for member in tar.getmembers():
                relative_name = _template_relative_name(member.name, template_dir)
                if relative_name is None:
                    continue
                if member.issym() or member.islnk():
                    raise ScaffoldError(f"Refusing to extract link from scaffold: {member.name}")

                destination = (project_root / relative_name).resolve()
                if not _is_relative_to(destination, project_root):
                    raise ScaffoldError(f"Refusing to extract unsafe path: {member.name}")

                _extract_member(tar, member, destination)
                extracted_any = True
    except tarfile.TarError as exc:
        raise ScaffoldError(f"Could not extract starter scaffold: {exc}") from exc

    if not extracted_any:
        raise ScaffoldError(f"Template directory not found in starter scaffold: {template_dir}")


def _template_relative_name(member_name: str, template_dir: str) -> Path | None:
    parts = Path(member_name).parts
    if len(parts) < 2 or parts[1] != template_dir:
        return None
    relative_parts = parts[2:]
    if not relative_parts:
        return None
    return Path(*relative_parts)


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _extract_member(tar: tarfile.TarFile, member: tarfile.TarInfo, destination: Path) -> None:
    if member.isdir():
        destination.mkdir(parents=True, exist_ok=True)
        return

    if not member.isfile():
        raise ScaffoldError(f"Refusing to extract unsupported tar member: {member.name}")

    source = tar.extractfile(member)
    if source is None:
        raise ScaffoldError(f"Could not read file from scaffold: {member.name}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with source, destination.open("wb") as target:
        shutil.copyfileobj(source, target)
