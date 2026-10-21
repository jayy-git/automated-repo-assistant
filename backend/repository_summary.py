from pathlib import Path

from repository_analyzer import scan_repository
from technology_detector import detect_technology_stack
from file_analyzer import analyze_important_files
from dependency_analyzer import analyze_dependencies
from code_relationship_analyzer import analyze_code_relationships



def generate_repository_summary(repository_path):
    """Generate a structured summary of a software repository."""

    root = Path(repository_path).resolve()

    # Collect information from our existing components.
    inventory = scan_repository(root)
    technologies = detect_technology_stack(root)
    important_files = analyze_important_files(root)
    dependencies = analyze_dependencies(root)
    code_relationships = analyze_code_relationships(root)
    

        # Build a simple overview of the repository structure.
    structure = {}

    for file in inventory["files"]:
        parts = Path(file).parts

        if len(parts) == 1:
            structure.setdefault("Root", []).append(file)
        else:
            folder = parts[0]
            structure.setdefault(folder, []).append(file)

    summary = {
    "repository_name": root.name,
    "repository_path": str(root),
    "total_files": inventory["total_files"],
    "technology_stack": technologies,
    "dependencies": dependencies,
    "important_files": important_files,
    "project_structure": structure,
    "code_relationships": code_relationships,
}

    return summary