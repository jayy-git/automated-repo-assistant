import json
import re
import tomllib
from pathlib import Path


def analyze_dependencies(repository_path):
    """Extract declared dependencies from supported manifest files."""

    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {root}"
        )

    result = {
        "python": [],
        "javascript": [],
        "manifest_files": [],
        "warnings": [],
    }

    ignored_directories = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
    }

    def should_ignore(path):
        relative_path = path.relative_to(root)

        return any(
            part in ignored_directories
            for part in relative_path.parts[:-1]
        )

    # Analyze Python requirements files.
    for path in root.rglob("requirements.txt"):
        if should_ignore(path):
            continue

        result["manifest_files"].append(
            path.relative_to(root).as_posix()
        )

        try:
            for line in path.read_text(
                encoding="utf-8"
            ).splitlines():

                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.startswith(("-r ", "--requirement ")):
                    result["warnings"].append(
                        f"{path.name}: nested requirements files "
                        "are not expanded automatically."
                    )
                    continue

                if line.startswith(("-e ", "--editable ")):
                    result["warnings"].append(
                        f"{path.name}: editable dependency "
                        "requires manual inspection."
                    )
                    continue

                if line.startswith("-"):
                    result["warnings"].append(
                        f"{path.name}: unsupported requirement "
                        f"option: {line}"
                    )
                    continue

                match = re.match(
                    r"^([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)$",
                    line,
                )

                if match:
                    result["python"].append({
                        "name": match.group(1),
                        "version_specifier": match.group(2).strip(),
                        "source": path.relative_to(root).as_posix(),
                    })

        except (OSError, UnicodeError) as exc:
            result["warnings"].append(
                f"Could not read {path.name}: {exc}"
            )

    # Analyze JavaScript package.json files.
    for path in root.rglob("package.json"):
        if should_ignore(path):
            continue

        result["manifest_files"].append(
            path.relative_to(root).as_posix()
        )

        try:
            package_data = json.loads(
                path.read_text(encoding="utf-8")
            )

            for section in ("dependencies", "devDependencies"):
                dependencies = package_data.get(section, {})

                if not isinstance(dependencies, dict):
                    result["warnings"].append(
                        f"{path.name}: {section} must be an object."
                    )
                    continue

                for name, version in dependencies.items():
                    result["javascript"].append({
                        "name": name,
                        "version_specifier": version,
                        "dependency_type": section,
                        "source": path.relative_to(root).as_posix(),
                    })

        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            result["warnings"].append(
                f"Could not parse {path.name}: {exc}"
            )

    # Analyze pyproject.toml files.
    for path in root.rglob("pyproject.toml"):
        if should_ignore(path):
            continue

        result["manifest_files"].append(
            path.relative_to(root).as_posix()
        )

        try:
            project_data = tomllib.loads(
                path.read_text(encoding="utf-8")
            )

            project = project_data.get("project", {})
            dependencies = project.get("dependencies", [])

            for dependency in dependencies:
                match = re.match(
                    r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)\s*(.*)$",
                    dependency,
                )

                if match:
                    result["python"].append({
                        "name": match.group(1),
                        "version_specifier": match.group(2).strip(),
                        "source": path.relative_to(root).as_posix(),
                    })

        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            result["warnings"].append(
                f"Could not parse {path.name}: {exc}"
            )

    # Remove duplicate manifest paths while preserving order.
    result["manifest_files"] = list(
        dict.fromkeys(result["manifest_files"])
    )

    return result