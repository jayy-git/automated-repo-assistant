from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

IGNORED_FILES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    "ONBOARDING.md",
}

IGNORED_SUFFIXES = {
    ".pyc",
    ".pyo",
}


def scan_repository(repository_path):
    """Scan a repository and return a safe file inventory."""

    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {root}"
        )

    files = []

    for current_directory, directories, filenames in __import__(
        "os"
    ).walk(root):
        current_path = Path(current_directory)

        # Do not descend into ignored directories.
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        )

        for filename in filenames:
            path = current_path / filename

            if filename in IGNORED_FILES:
                continue

            if filename.endswith(tuple(IGNORED_SUFFIXES)):
                continue

            # Exclude environment variants and private keys.
            if filename.startswith(".env."):
                continue

            if path.suffix.lower() in {".pem", ".key"}:
                continue

            relative_path = path.relative_to(root)
            files.append(relative_path.as_posix())

    files.sort()

    return {
        "repository_path": str(root),
        "total_files": len(files),
        "files": files,
    }