from pathlib import Path
from repository_analyzer import scan_repository

# Find the main project directory
project_root = Path(__file__).resolve().parents[1]

# Scan the project
result = scan_repository(project_root)

# Display the results
print("Repository:", result["repository_path"])
print("Total files:", result["total_files"])

print("\nFiles found:")

for file in result["files"]:
    print("-", file)