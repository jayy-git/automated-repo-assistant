"""
test_repository_analyzer.py
===========================
Tests for Person A's repository_analyzer module:
- Online GitHub repository analysis (analyze_repository)
- Local directory scanning (scan_repository)
- Organization & Structure Analysis integration
"""

from pathlib import Path
from repository_analyzer import analyze_repository, scan_repository

def test_online_analyzer():
    print("Testing online analyze_repository...")
    url = "https://github.com/octocat/Hello-World"
    result = analyze_repository(url)
    print("Repo Name:", result["repo_name"])
    print("Default Branch:", result["default_branch"])
    print("Files found:", result["files"])
    print("README exists:", result["readme_exists"])
    print("Organization Analysis:", "Present" if result.get("organization") else "Missing")
    assert result["error"] is None
    assert result["readme_exists"] is True
    assert result.get("organization") is not None
    assert "file_classification" in result["organization"]
    print("[PASS] Online repository analyzer test passed!\n")

def test_local_scanner():
    print("Testing local scan_repository...")
    project_root = Path(__file__).resolve().parents[1]
    result = scan_repository(project_root)
    print("Repository:", result["repository_path"])
    print("Total files:", result["total_files"])
    print("Architecture Detected:", result["organization"]["project_conventions"]["architecture_type"])
    assert result["total_files"] > 0
    assert result.get("organization") is not None
    print("[PASS] Local scanner test passed!\n")

if __name__ == "__main__":
    test_online_analyzer()
    test_local_scanner()
