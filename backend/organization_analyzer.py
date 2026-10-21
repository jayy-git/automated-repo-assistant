"""
organization_analyzer.py
========================
Repository Structure & Organization Analysis Engine for RepoGuide

Implements the 8 core organization analysis capabilities:
1. Directory analysis — maps repository folders, file hierarchy, depth, and file counts.
2. File classification — classifies source code, tests, documentation, configuration, and assets.
3. Project convention detection — identifies architectural conventions (Fullstack, Python, React, etc.).
4. Organisation issue detection — flags misplaced files, tests mixed with source, root clutter, missing elements.
5. Folder structure recommendations — proposes an optimal directory structure when justified.
6. Dependency and configuration review — analyzes dependency manifests, build configs, and identifies gaps.
7. Change planning — generates a concrete list of file moves, folder creations, and renames.
8. Organisation report — creates a comprehensive human-readable report with rationale.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


# =====================================================================
# 1. DIRECTORY ANALYSIS
# =====================================================================

def analyze_directories(files: List[str]) -> Dict[str, Any]:
    """
    Maps repository directories, folder hierarchy, file distribution, and depth.
    """
    directory_files: Dict[str, List[str]] = {"root": []}
    directory_depths: Dict[str, int] = {"root": 0}

    for file_path in files:
        normalized = file_path.replace("\\", "/").strip("/")
        parts = normalized.split("/")

        if len(parts) == 1:
            directory_files["root"].append(normalized)
        else:
            dir_name = "/".join(parts[:-1])
            directory_files.setdefault(dir_name, []).append(normalized)
            directory_depths[dir_name] = len(parts) - 1

    # Directory summary metrics
    dir_counts = {dir_name: len(flist) for dir_name, flist in directory_files.items()}
    max_depth = max(directory_depths.values()) if directory_depths else 0
    total_directories = len([d for d in directory_files.keys() if d != "root"])

    return {
        "total_directories": total_directories,
        "max_directory_depth": max_depth,
        "directory_counts": dir_counts,
        "directories": sorted(list(directory_files.keys())),
        "directory_files": directory_files,
    }


# =====================================================================
# 2. FILE CLASSIFICATION
# =====================================================================

SOURCE_EXTENSIONS = {
    ".py", ".pyw", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    ".java", ".c", ".cpp", ".cc", ".cxx", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".cs", ".swift", ".kt", ".scala"
}

DOCUMENTATION_EXTENSIONS = {
    ".md", ".rst", ".txt", ".adoc", ".pdf"
}

CONFIGURATION_EXTENSIONS = {
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".xml", ".properties"
}

ASSET_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
    ".css", ".scss", ".sass", ".less", ".html", ".woff", ".woff2", ".ttf"
}


def classify_files(files: List[str]) -> Dict[str, Any]:
    """
    Classifies all repository files into functional categories:
    source, tests, documentation, configuration, assets, and other.
    """
    classified: Dict[str, List[str]] = {
        "source": [],
        "tests": [],
        "documentation": [],
        "configuration": [],
        "assets": [],
        "other": []
    }

    for file_path in files:
        normalized = file_path.replace("\\", "/").strip("/")
        parts = [p.lower() for p in normalized.split("/")]
        filename = parts[-1]
        suffix = Path(filename).suffix.lower()

        # Check for tests first
        is_test = (
            filename.startswith("test_")
            or filename.endswith(("_test.py", ".test.js", ".test.jsx", ".test.ts", ".test.tsx", ".spec.js", ".spec.ts", ".spec.jsx", ".spec.tsx"))
            or "tests" in parts
            or "test" in parts
            or "__tests__" in parts
        )

        if is_test:
            classified["tests"].append(normalized)
        elif (
            filename in {"requirements.txt", "pipfile", "pipfile.lock", "gemfile", "cargo.toml", "go.mod", "procfile"}
            or filename.startswith("requirements")
            or suffix in CONFIGURATION_EXTENSIONS
            or filename.startswith((".env", ".git", ".eslint", ".prettier", ".editorconfig", "dockerfile"))
        ):
            classified["configuration"].append(normalized)
        elif suffix in DOCUMENTATION_EXTENSIONS or filename in {"readme", "license", "contributing", "notice", "authors", "changelog"}:
            classified["documentation"].append(normalized)
        elif suffix in SOURCE_EXTENSIONS:
            classified["source"].append(normalized)
        elif suffix in ASSET_EXTENSIONS:
            classified["assets"].append(normalized)
        else:
            classified["other"].append(normalized)

    counts = {category: len(flist) for category, flist in classified.items()}

    return {
        "categories": classified,
        "counts": counts,
        "total_files": len(files)
    }


# =====================================================================
# 3. PROJECT CONVENTION DETECTION
# =====================================================================

def detect_project_conventions(files: List[str], classified: Dict[str, List[str]]) -> Dict[str, Any]:
    """
    Recognises common project conventions and architectural structures:
    - Fullstack Split (e.g., frontend/ + backend/)
    - Python Standard Package (e.g., src/ or package folder + tests/ + pyproject.toml)
    - FastAPI / Flask Web API
    - React / Vite Single Page App
    - Monorepo structure
    - Flat / Script collection
    """
    normalized_files = [f.replace("\\", "/").lower() for f in files]
    top_level_folders = {f.split("/")[0] for f in normalized_files if "/" in f}

    detected_frameworks = []
    architecture_type = "Unknown"
    confidence = "Low"

    has_backend_dir = "backend" in top_level_folders or "server" in top_level_folders or "api" in top_level_folders
    has_frontend_dir = "frontend" in top_level_folders or "client" in top_level_folders or "ui" in top_level_folders

    if has_backend_dir and has_frontend_dir:
        architecture_type = "Full-Stack Application (Frontend / Backend Split)"
        confidence = "High"
    elif "src" in top_level_folders and any("pyproject.toml" in f or "setup.py" in f for f in normalized_files):
        architecture_type = "Standard Python Package (src layout)"
        confidence = "High"
    elif any("package.json" in f for f in normalized_files) and any("vite" in f or "react" in f for f in normalized_files):
        architecture_type = "Modern Frontend Application (Vite / React)"
        confidence = "High"
    elif any(f.endswith(".py") for f in normalized_files) and len(top_level_folders) == 0:
        architecture_type = "Flat Script Collection (No subdirectories)"
        confidence = "Medium"
    elif any(f.endswith(".py") for f in normalized_files):
        architecture_type = "Python Application"
        confidence = "Medium"
    elif any(f.endswith((".js", ".ts")) for f in normalized_files):
        architecture_type = "JavaScript / TypeScript Application"
        confidence = "Medium"

    # Specific Framework detection
    if any("fastapi" in f or "main.py" in f for f in normalized_files):
        detected_frameworks.append("FastAPI")
    if any("flask" in f or "app.py" in f for f in normalized_files):
        detected_frameworks.append("Flask")
    if any("vite.config" in f for f in normalized_files):
        detected_frameworks.append("Vite")
    if any("react" in f or f.endswith((".jsx", ".tsx")) for f in normalized_files):
        detected_frameworks.append("React")
    if any("dockerfile" in f or "docker-compose" in f for f in normalized_files):
        detected_frameworks.append("Docker")

    return {
        "architecture_type": architecture_type,
        "confidence": confidence,
        "detected_frameworks": sorted(list(set(detected_frameworks))),
        "top_level_folders": sorted(list(top_level_folders)),
    }


# =====================================================================
# 4. ORGANISATION ISSUE DETECTION
# =====================================================================

def detect_organization_issues(files: List[str], classified: Dict[str, List[str]], conventions: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Identifies potentially misplaced files, tests mixed with code, root clutter,
    and missing organizational elements.
    """
    issues: List[Dict[str, str]] = []
    normalized_files = [f.replace("\\", "/").strip("/") for f in files]
    files_lower = {f: f.lower() for f in normalized_files}

    # 1. Misplaced test files (tests living alongside source instead of in a tests/ directory)
    test_files = classified.get("tests", [])
    tests_not_in_test_dir = [
        f for f in test_files
        if not any(part in {"tests", "test", "__tests__"} for part in f.lower().split("/")[:-1])
    ]
    if tests_not_in_test_dir:
        issues.append({
            "severity": "Medium",
            "category": "Test Organization",
            "issue": f"{len(tests_not_in_test_dir)} test file(s) are mixed directly inside source directories instead of a dedicated 'tests/' folder.",
            "impact": "Mixes test code with production/source modules, complicating packaging, deployments, and automated testing.",
            "files": ", ".join(tests_not_in_test_dir[:4]) + ("..." if len(tests_not_in_test_dir) > 4 else "")
        })

    # 2. Root directory clutter (too many loose source files at the root)
    root_source_files = [
        f for f in classified.get("source", [])
        if "/" not in f
    ]
    if len(root_source_files) > 3:
        issues.append({
            "severity": "Low",
            "category": "Root Hygiene",
            "issue": f"Root directory contains {len(root_source_files)} loose source files.",
            "impact": "Clutters the repository entry point; makes it harder for contributors to find where the main logic lives.",
            "files": ", ".join(root_source_files[:4]) + ("..." if len(root_source_files) > 4 else "")
        })

    # 3. Missing tests directory
    has_test_dir = any(
        any(part in {"tests", "test", "__tests__"} for part in f.lower().split("/")[:-1])
        for f in normalized_files
    )
    if not has_test_dir and not test_files:
        issues.append({
            "severity": "High",
            "category": "Quality Infrastructure",
            "issue": "No test directory or automated test suite detected.",
            "impact": "Code cannot be automatically validated during pull requests or deployments.",
            "files": "tests/"
        })

    # 4. Missing Documentation / Docs folder
    has_readme = any("readme" in Path(f).name.lower() for f in normalized_files)
    if not has_readme:
        issues.append({
            "severity": "High",
            "category": "Documentation",
            "issue": "Missing README.md in root directory.",
            "impact": "New contributors and users have no guidance on how to run or install the project.",
            "files": "README.md"
        })

    # 5. Missing License
    has_license = any(Path(f).name.lower().startswith("license") or Path(f).name.lower().startswith("licence") for f in normalized_files)
    if not has_license:
        issues.append({
            "severity": "Medium",
            "category": "Legal",
            "issue": "Missing LICENSE file in root directory.",
            "impact": "Without an explicit open-source license, default copyright laws apply and others cannot legally use or contribute.",
            "files": "LICENSE"
        })

    # 6. Sensitive or local files committed
    sensitive_patterns = {".env", ".env.local", ".env.development", ".env.production", "id_rsa", "id_ed25519"}
    committed_sensitive = [
        f for f in normalized_files
        if Path(f).name.lower() in sensitive_patterns or f.lower().endswith((".pem", ".key"))
    ]
    if committed_sensitive:
        issues.append({
            "severity": "Critical",
            "category": "Security",
            "issue": f"Potential sensitive configuration or private key committed: {', '.join(committed_sensitive)}",
            "impact": "Secrets or credentials may leak to unauthorized parties or public history.",
            "files": ", ".join(committed_sensitive)
        })

    return issues


# =====================================================================
# 5. FOLDER STRUCTURE RECOMMENDATIONS
# =====================================================================

def recommend_folder_structure(conventions: Dict[str, Any], issues: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Proposes an optimized repository folder layout based on detected architecture
    and organizational gaps.
    """
    arch = conventions.get("architecture_type", "")

    if "Full-Stack" in arch:
        recommended_tree = """project-root/
├── .gitignore
├── LICENSE
├── README.md
├── backend/
│   ├── app/ or main.py      # Backend API application
│   ├── requirements.txt     # Python backend dependencies
│   └── tests/               # Dedicated backend tests
│       ├── __init__.py
│       └── test_api.py
└── frontend/
    ├── package.json         # Frontend dependencies and scripts
    ├── index.html           # SPA entry point
    └── src/
        ├── App.jsx
        └── components/      # Reusable UI components"""
        rationale = "Maintains a clean separation of concerns between client and server layers while isolating test suites into dedicated directories."

    elif "Python" in arch:
        recommended_tree = """project-root/
├── .gitignore
├── LICENSE
├── README.md
├── pyproject.toml           # Build system and dependency configuration
├── src/
│   └── package_name/        # Source code
│       ├── __init__.py
│       └── core.py
├── tests/                   # Isolated test suite
│   ├── __init__.py
│   └── test_core.py
└── docs/                    # Extended documentation"""
        rationale = "Adheres to PEP 517/518 and standard Python 'src' packaging conventions, preventing accidental imports of uninstalled local files during testing."

    else:
        recommended_tree = """project-root/
├── .gitignore
├── LICENSE
├── README.md
├── src/                     # All application source code
├── tests/                   # Automated tests
└── docs/                    # Setup & architecture guides"""
        rationale = "Consolidates logic into 'src/' and 'tests/', keeping the root directory clean and approachable."

    return {
        "recommended_layout": recommended_tree,
        "rationale": rationale,
        "target_architecture": arch
    }


# =====================================================================
# 6. DEPENDENCY AND CONFIGURATION REVIEW
# =====================================================================

def review_dependencies_and_config(files: List[str]) -> Dict[str, Any]:
    """
    Reviews project configuration, package managers, and dependency declarations.
    Identifies missing configuration elements.
    """
    normalized_files = [f.replace("\\", "/").lower() for f in files]

    found_configs = []
    found_dependencies = []
    missing_recommendations = []

    # Dependency manifests
    dep_manifests = {
        "requirements.txt": "Python pip dependencies",
        "pyproject.toml": "Python modern packaging & tooling config",
        "setup.py": "Python setuptools build file",
        "pipfile": "Pipenv dependency manifest",
        "package.json": "Node.js / JavaScript package manifest",
        "cargo.toml": "Rust Cargo manifest",
        "go.mod": "Go module definition"
    }

    for file_path in normalized_files:
        base = Path(file_path).name
        if base in dep_manifests:
            found_dependencies.append({
                "file": file_path,
                "type": dep_manifests[base]
            })

    # Tooling and infrastructure configurations
    tool_configs = {
        ".gitignore": "Git ignore patterns",
        "dockerfile": "Docker container build definition",
        "docker-compose.yml": "Docker multi-container orchestration",
        "docker-compose.yaml": "Docker multi-container orchestration",
        "eslint.config.js": "ESLint linter configuration",
        ".eslintrc.json": "ESLint configuration",
        ".prettierrc": "Prettier code formatting",
        "tsconfig.json": "TypeScript compiler options"
    }

    for file_path in normalized_files:
        base = Path(file_path).name
        if base in tool_configs:
            found_configs.append({
                "file": file_path,
                "purpose": tool_configs[base]
            })

    # Missing configuration checks
    has_python = any(f.endswith(".py") for f in normalized_files)
    has_python_dep = any("requirements" in f or "pyproject.toml" in f or "setup.py" in f for f in normalized_files)
    if has_python and not has_python_dep:
        missing_recommendations.append("Python source files detected, but no requirements.txt or pyproject.toml was found.")

    has_js = any(f.endswith((".js", ".jsx", ".ts", ".tsx")) for f in normalized_files)
    has_js_dep = any("package.json" in f for f in normalized_files)
    if has_js and not has_js_dep:
        missing_recommendations.append("JavaScript/TypeScript files detected, but no package.json was found.")

    has_gitignore = any(Path(f).name == ".gitignore" for f in normalized_files)
    if not has_gitignore:
        missing_recommendations.append("Missing .gitignore: generated files, virtual environments, and caches risk being committed.")

    return {
        "dependency_files": found_dependencies,
        "configuration_files": found_configs,
        "configuration_gaps": missing_recommendations
    }


# =====================================================================
# 7. CHANGE PLANNING
# =====================================================================

def plan_organization_changes(files: List[str], classified: Dict[str, List[str]], issues: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Generates a proposed list of concrete file and folder changes to resolve
    organizational issues.
    """
    plan: List[Dict[str, str]] = []
    normalized_files = [f.replace("\\", "/").strip("/") for f in files]

    # Plan 1: Move misplaced test files into dedicated tests/ folders
    for test_file in classified.get("tests", []):
        parts = test_file.split("/")
        if not any(part in {"tests", "test", "__tests__"} for part in parts[:-1]):
            # If inside backend/test_x.py -> backend/tests/test_x.py
            if len(parts) > 1:
                target_dir = "/".join(parts[:-1]) + "/tests"
                target_path = f"{target_dir}/{parts[-1]}"
            else:
                target_path = f"tests/{test_file}"

            plan.append({
                "action": "MOVE",
                "source": test_file,
                "destination": target_path,
                "rationale": "Isolate automated tests in a dedicated 'tests/' folder to separate test suites from production code."
            })

    # Plan 2: Missing standard project documents
    files_lower = {f.lower() for f in normalized_files}
    if not any("readme" in f for f in files_lower):
        plan.append({
            "action": "CREATE",
            "destination": "README.md",
            "rationale": "Provide project overview, prerequisite guide, and run instructions for new developers."
        })

    if not any("license" in f or "licence" in f for f in files_lower):
        plan.append({
            "action": "CREATE",
            "destination": "LICENSE",
            "rationale": "Specify open-source license terms (e.g., MIT, Apache 2.0) to clearly define reuse permissions."
        })

    if not any(".gitignore" in f for f in files_lower):
        plan.append({
            "action": "CREATE",
            "destination": ".gitignore",
            "rationale": "Prevent caching artifacts, virtual environments, and sensitive local secrets from polluting Git."
        })

    return plan


# =====================================================================
# 8. ORGANISATION REPORT
# =====================================================================

def generate_organization_report(org_data: Dict[str, Any]) -> str:
    """
    Generates a detailed human-readable Markdown organization report
    explaining recommendations and their rationale.
    """
    dirs = org_data["directory_analysis"]
    classified = org_data["file_classification"]
    conv = org_data["project_conventions"]
    issues = org_data["organization_issues"]
    recommendations = org_data["folder_recommendations"]
    deps = org_data["dependency_review"]
    plan = org_data["change_plan"]

    lines = [
        "# RepoGuide Repository Organization & Structure Report",
        "",
        "## 1. Executive Summary",
        f"- **Detected Architecture:** {conv.get('architecture_type', 'Unknown')} (Confidence: {conv.get('confidence', 'N/A')})",
        f"- **Total Files Analyzed:** {classified.get('total_files', 0)} files across {dirs.get('total_directories', 0)} directories (Max depth: {dirs.get('max_directory_depth', 0)}).",
        f"- **Identified Frameworks:** {', '.join(conv.get('detected_frameworks', [])) or 'None detected'}",
        f"- **Total Organizational Issues Found:** {len(issues)}",
        "",
        "## 2. File Classification Breakdown",
        f"- **Source Code:** {classified['counts'].get('source', 0)} files",
        f"- **Test Files:** {classified['counts'].get('tests', 0)} files",
        f"- **Documentation:** {classified['counts'].get('documentation', 0)} files",
        f"- **Configuration:** {classified['counts'].get('configuration', 0)} files",
        f"- **Assets & Styling:** {classified['counts'].get('assets', 0)} files",
        f"- **Other:** {classified['counts'].get('other', 0)} files",
        "",
        "## 3. Organizational Issues & Quality Gaps",
    ]

    if issues:
        for idx, item in enumerate(issues, start=1):
            lines.extend([
                f"### Issue {idx}: [{item.get('severity', 'Info')}] {item.get('issue')}",
                f"- **Category:** {item.get('category')}",
                f"- **Impact & Rationale:** {item.get('impact')}",
                f"- **Affected Items:** `{item.get('files')}`",
                ""
            ])
    else:
        lines.append("No critical organizational issues identified! The repository structure adheres to standard conventions.")
        lines.append("")

    lines.extend([
        "## 4. Recommended Folder Structure",
        recommendations.get("rationale", ""),
        "",
        "```",
        recommendations.get("recommended_layout", ""),
        "```",
        "",
        "## 5. Dependency & Tooling Review",
        "### Detected Dependency Manifests:",
    ])

    if deps.get("dependency_files"):
        for dep in deps["dependency_files"]:
            lines.append(f"- `{dep['file']}`: {dep['type']}")
    else:
        lines.append("- None detected.")

    lines.append("")
    lines.append("### Detected Configuration & Tooling:")
    if deps.get("configuration_files"):
        for cfg in deps["configuration_files"]:
            lines.append(f"- `{cfg['file']}`: {cfg['purpose']}")
    else:
        lines.append("- None detected.")

    if deps.get("configuration_gaps"):
        lines.append("")
        lines.append("### Configuration Gaps:")
        for gap in deps["configuration_gaps"]:
            lines.append(f"- ⚠️ {gap}")

    lines.extend([
        "",
        "## 6. Actionable Change Plan",
        "Proposed steps to optimize project organization:",
    ])

    if plan:
        for idx, step in enumerate(plan, start=1):
            if step["action"] == "MOVE":
                lines.append(f"{idx}. **MOVE**: `{step['source']}` ➔ `{step['destination']}`")
            else:
                lines.append(f"{idx}. **{step['action']}**: `{step['destination']}`")
            lines.append(f"   *Rationale:* {step['rationale']}")
    else:
        lines.append("No immediate file relocations required.")

    return "\n".join(lines)


# =====================================================================
# MAIN FACADE FUNCTION
# =====================================================================

def analyze_organization(files: List[str], repo_name: str = "") -> Dict[str, Any]:
    """
    Main orchestration function.
    Given a list of file paths, executes all 8 organization analysis capabilities
    and returns a normalized result dictionary.
    """
    dir_analysis = analyze_directories(files)
    file_classification = classify_files(files)
    conventions = detect_project_conventions(files, file_classification["categories"])
    issues = detect_organization_issues(files, file_classification["categories"], conventions)
    recommendations = recommend_folder_structure(conventions, issues)
    dep_review = review_dependencies_and_config(files)
    change_plan = plan_organization_changes(files, file_classification["categories"], issues)

    result = {
        "repo_name": repo_name,
        "directory_analysis": dir_analysis,
        "file_classification": file_classification,
        "project_conventions": conventions,
        "organization_issues": issues,
        "folder_recommendations": recommendations,
        "dependency_review": dep_review,
        "change_plan": change_plan,
    }

    # Generate the Markdown report and attach it
    result["organization_report"] = generate_organization_report(result)
    return result
