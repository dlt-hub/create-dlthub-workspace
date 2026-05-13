from __future__ import annotations

import io
import tarfile
import tempfile
import unittest
from pathlib import Path

from create_dlthub_workspace.errors import ScaffoldError
from create_dlthub_workspace.scaffold import extract_template_from_tarball


def make_tarball(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        for name, content in files.items():
            info = tarfile.TarInfo(name)
            info.size = len(content)
            tar.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


def make_symlink_tarball(name: str, target: str) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tar:
        info = tarfile.TarInfo(name)
        info.type = tarfile.SYMTYPE
        info.linkname = target
        tar.addfile(info)
    return buffer.getvalue()


class ScaffoldExtractionTests(unittest.TestCase):
    def test_extracts_template_contents_into_project_root(self) -> None:
        data = make_tarball(
            {
                "runtime-starter-pack-main/github_ingest_workspace/pyproject.toml": b"[project]\n",
                "runtime-starter-pack-main/other_template/ignore.txt": b"nope\n",
            }
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = Path(tmpdir) / "project"
            project_dir.mkdir()

            extract_template_from_tarball(data, project_dir, template_dir="github_ingest_workspace")

            self.assertEqual((project_dir / "pyproject.toml").read_bytes(), b"[project]\n")
            self.assertFalse((project_dir / "ignore.txt").exists())

    def test_raises_when_template_is_missing(self) -> None:
        data = make_tarball({"runtime-starter-pack-main/other/file.txt": b"hello\n"})

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ScaffoldError):
                extract_template_from_tarball(data, Path(tmpdir), template_dir="github_ingest_workspace")

    def test_rejects_links_in_template(self) -> None:
        data = make_symlink_tarball(
            "runtime-starter-pack-main/github_ingest_workspace/link",
            "/tmp/outside",
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ScaffoldError):
                extract_template_from_tarball(data, Path(tmpdir), template_dir="github_ingest_workspace")


if __name__ == "__main__":
    unittest.main()
