from pathlib import Path

from repository_analyzer import scan_repository
from technology_detector import detect_technology_stack
from file_analyzer import analyze_important_files


def generate_repository_summary(repository_path):
    """Generate a structured summary of a software repository."""

    root = Path(repository_path).resolve()

    # Collect information from our existing components.
    inventory = scan_repository(root)
    technologies = detect_technology_stack(root)
    important_files = analyze_important_files(root)

        # Build a simple overview of the repository structure.
    structure = {}

    for file in inventory["files"]:
        parts = Path(file).parts

        if len(parts) == 1:
            structure.setdefault("Root", []).append(file)
        else:
            folder = parts[0]
            structure.setdefault(folder, []).append(file)

    # Build the summary.
    summary = {
        "repository_name": "RepoGuide",
        "repository_path": str(root),
        "total_files": inventory["total_files"],
        "technology_stack": technologies,
        "important_files": important_files,
        "project_structure": structure,
    }

    return summary