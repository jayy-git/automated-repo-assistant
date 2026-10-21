def check_repository(repo_data):
    findings = []

    if not isinstance(repo_data, dict):
        return [{
            "title": "Invalid repository data",
            "severity": "Medium",
            "category": "Input",
            "explanation": "Repository data must be provided as a dictionary.",
            "suggestion": "Provide repository data as a dictionary with the expected fields."
        }]

    raw_files = repo_data.get("files", [])
    if isinstance(raw_files, list):
        files = [name for name in raw_files if isinstance(name, str)]
        if len(files) != len(raw_files):
            findings.append({
                "title": "Invalid repository file list",
                "severity": "Medium",
                "category": "Input",
                "explanation": "The files field must contain only file path strings.",
                "suggestion": "Provide the files field as a list of file path strings."
            })
    else:
        files = []
        findings.append({
            "title": "Invalid repository file list",
            "severity": "Medium",
            "category": "Input",
            "explanation": "The files field must be a list of file path strings.",
            "suggestion": "Provide the files field as a list of file path strings."
        })

    requirements_files = repo_data.get("requirements_files", [])
    if not isinstance(requirements_files, list):
        findings.append({
            "title": "Invalid dependency file list",
            "severity": "Medium",
            "category": "Input",
            "explanation": "The requirements_files field must be a list.",
            "suggestion": "Provide requirements_files as a list of dependency file paths."
        })
        requirements_files = []

    # Check 1: README
    if not repo_data.get("readme_exists", False):
        findings.append({
            "title": "README file not found",
            "severity": "Medium",
            "category": "Documentation",
            "explanation": "Users may not understand what the project does or how to use it.",
            "suggestion": "Add a README.md explaining the project, setup, and usage."
        })

    # Check 2: License
    if not repo_data.get("license_exists", False):
        findings.append({
            "title": "License file not found",
            "severity": "Medium",
            "category": "Legal",
            "explanation": "Users may not know the terms under which they can use or modify the project.",
            "suggestion": "Consider adding an appropriate open-source license."
        })

    # Check 3: Contribution guide
    if not repo_data.get("contributing_exists", False):
        findings.append({
            "title": "CONTRIBUTING guide not found",
            "severity": "Low",
            "category": "Onboarding",
            "explanation": "New contributors may not know how to propose changes.",
            "suggestion": "Consider adding a CONTRIBUTING.md with setup and pull request instructions."
        })
    # Check 4: Dependency files
    if not requirements_files:
        findings.append({
            "title": "Dependency file not found",
            "severity": "Low",
            "category": "Setup",
            "explanation": "Users may not know which packages are needed to run the project.",
            "suggestion": "If this project uses external packages, add a requirements.txt or an appropriate dependency file."
        })

    # Check 5: Setup instructions
    readme_content = repo_data.get("readme_content")
    setup_terms = ("installation", "getting started", "setup", "how to run", "usage")
    has_setup = isinstance(readme_content, str) and any(
        term in readme_content.lower() for term in setup_terms
    )

    if isinstance(readme_content, str) and not has_setup:
        findings.append({
            "title": "Setup instructions may be missing",
            "severity": "Low",
            "category": "Onboarding",
            "explanation": "The provided README content does not appear to include setup instructions.",
            "suggestion": "Review the README and add installation and run instructions if they are missing."
        })

    # Check 6: Git ignore file
    has_gitignore = any(
        name.replace("\\", "/").rsplit("/", 1)[-1].lower() == ".gitignore"
        for name in files
    )

    if not has_gitignore:
        findings.append({
            "title": ".gitignore file not found",
            "severity": "Low",
            "category": "Configuration",
            "explanation": "Without a .gitignore file, developers may accidentally commit temporary files or local settings.",
            "suggestion": "Consider adding a .gitignore file for generated files and local-only files."
        })
    return findings