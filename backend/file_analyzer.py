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

IMPORTANT_FILES = {
    "main.py": "Possible Python backend entry point",
    "app.py": "Possible Python application entry point",
    "manage.py": "Django management entry point",
    "app.jsx": "Main React application component",
    "app.tsx": "Main React application component",
    "main.jsx": "Possible React entry point",
    "main.tsx": "Possible React entry point",
    "index.js": "Possible JavaScript entry point",
    "index.html": "HTML application entry point",
    "readme.md": "Project documentation",
    "requirements.txt": "Python dependencies",
    "package.json": "JavaScript dependencies and scripts",
    "dockerfile": "Container build instructions",
    "docker-compose.yml": "Docker service configuration",
    "docker-compose.yaml": "Docker service configuration",
    ".gitignore": "Files excluded from Git tracking",
}


def analyze_important_files(repository_path):
    """Find important files and describe their likely purpose."""

    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {root}"
        )

    important_files = []

    for path in root.rglob("*"):
        if not path.is_file():
            continue

        relative_path = path.relative_to(root)

        if any(
            part in IGNORED_DIRECTORIES
            for part in relative_path.parts
        ):
            continue

        filename = path.name.lower()

        # Skip SVG assets; they are not application entry points.
        if filename.endswith(".svg"):
            continue

        # Only process files in our important-files dictionary.
        if filename not in IMPORTANT_FILES:
            continue

        relative_file = relative_path.as_posix()
        parts = {part.lower() for part in relative_path.parts}

        purpose = IMPORTANT_FILES[filename]

        # Improve descriptions using the file's location.
        if filename == "main.py" and "backend" in parts:
            purpose = "Backend application entry point candidate"

        elif (
            filename in {"main.jsx", "main.tsx"}
            and "src" in parts
        ):
            purpose = "Frontend application entry point candidate"

        elif (
            filename in {"app.jsx", "app.tsx"}
            and "src" in parts
        ):
            purpose = "Main frontend application component"

        important_files.append({
            "file": relative_file,
            "purpose": purpose,
        })

    return sorted(
        important_files,
        key=lambda item: item["file"].lower(),
    )