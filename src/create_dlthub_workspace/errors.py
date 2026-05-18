"""CLI-specific exceptions."""


class WorkspaceError(Exception):
    """Base exception for expected user-facing failures."""


class ScaffoldError(WorkspaceError):
    """Raised when the starter scaffold cannot be downloaded or extracted."""


class UvError(WorkspaceError):
    """Raised when uv detection, installation, or execution fails."""


class CommandError(WorkspaceError):
    """Raised when an external command fails."""
