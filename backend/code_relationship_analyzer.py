import ast
import os
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
}


def analyze_code_relationships(repository_path):
    """Analyze Python imports and identify relationships between files."""

    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {root}"
        )

    python_files = []

    for current_directory, directories, filenames in os.walk(root):
        directories[:] = sorted(
            directory
            for directory in directories
            if directory not in IGNORED_DIRECTORIES
        )

        current_path = Path(current_directory)

        for filename in filenames:
            if filename.endswith(".py"):
                python_files.append(current_path / filename)

    python_files.sort()

    # Build a map of module names to repository-relative file paths.
    module_to_file = {}

    for path in python_files:
        relative_path = path.relative_to(root)
        module_parts = list(relative_path.with_suffix("").parts)

        is_package_initializer = module_parts[-1] == "__init__"

        if is_package_initializer:
            module_parts.pop()

        if module_parts:
            module_name = ".".join(module_parts)
            module_to_file[module_name] = relative_path.as_posix()

            # Also support imports without the top-level folder name.
            module_to_file.setdefault(
                ".".join(module_parts[1:]),
                relative_path.as_posix(),
            )

            # Allow importing a module directly by its filename.
            if not is_package_initializer:
                module_to_file.setdefault(
                    module_parts[-1],
                    relative_path.as_posix(),
                )

    relationships = []
    warnings = []

    for path in python_files:
        relative_path = path.relative_to(root)
        source_file = relative_path.as_posix()

        try:
            source_code = path.read_text(encoding="utf-8")
            syntax_tree = ast.parse(
                source_code,
                filename=source_file,
            )

        except (OSError, UnicodeError, SyntaxError) as exc:
            warnings.append(
                f"Could not analyze {source_file}: {exc}"
            )
            continue

        imported_modules = set()

        for node in ast.walk(syntax_tree):

            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.level:
                    # Resolve relative imports from the current package.
                    package_parts = list(relative_path.parent.parts)

                    for _ in range(max(0, node.level - 1)):
                        if package_parts:
                            package_parts.pop()

                    if node.module:
                        package_parts.extend(node.module.split("."))

                    if package_parts:
                        imported_modules.add(".".join(package_parts))

                elif node.module:
                    imported_modules.add(node.module)

                # Also inspect names imported from a module.
                if node.module:
                    for alias in node.names:
                        if alias.name != "*":
                            imported_modules.add(
                                f"{node.module}.{alias.name}"
                            )

        for imported_module in sorted(imported_modules):
            target_file = module_to_file.get(imported_module)

            if target_file is None:
                target_file = module_to_file.get(
                    imported_module.rsplit(".", 1)[-1]
                )

            if target_file is None or target_file == source_file:
                continue

            relationships.append({
                "source_file": source_file,
                "target_file": target_file,
                "imported_module": imported_module,
                "relationship": "imports",
            })

    # Remove duplicate relationships.
    unique_relationships = {
        (
            item["source_file"],
            item["target_file"],
            item["imported_module"],
        ): item
        for item in relationships
    }

    relationships = [
        unique_relationships[key]
        for key in sorted(unique_relationships)
    ]

    imported_by_count = {}

    for relationship in relationships:
        target = relationship["target_file"]
        imported_by_count[target] = (
            imported_by_count.get(target, 0) + 1
        )

    return {
        "python_files_analyzed": len(python_files),
        "relationships_count": len(relationships),
        "relationships": relationships,
        "imported_by_count": imported_by_count,
        "warnings": warnings,
    }