from pathlib import Path
import re


def validate_documentation(repository_path):
    """Validate generated onboarding documentation against repository files."""

    root = Path(repository_path).resolve()

    if not root.exists():
        raise FileNotFoundError(
            f"Repository path does not exist: {root}"
        )

    if not root.is_dir():
        raise NotADirectoryError(
            f"Expected a directory: {root}"
        )

    onboarding_path = root / "ONBOARDING.md"

    results = {
        "valid": True,
        "checks_performed": 0,
        "issues": [],
        "warnings": [],
    }

    # Check 1: Ensure the onboarding document exists.
    results["checks_performed"] += 1

    if not onboarding_path.is_file():
        results["issues"].append({
            "check": "onboarding_exists",
            "message": "ONBOARDING.md was not found in the repository root.",
            "suggestion": "Generate the onboarding document before validating it.",
        })

        results["valid"] = False
        return results

    # Read the generated documentation.
    try:
        content = onboarding_path.read_text(encoding="utf-8")

    except (OSError, UnicodeError) as exc:
        results["issues"].append({
            "check": "onboarding_readable",
            "message": f"Could not read ONBOARDING.md: {exc}",
            "suggestion": "Check the file's encoding and read permissions.",
        })

        results["valid"] = False
        return results

    # Check 2: Ensure the document is not empty.
    results["checks_performed"] += 1

    if not content.strip():
        results["issues"].append({
            "check": "onboarding_not_empty",
            "message": "ONBOARDING.md is empty.",
            "suggestion": "Regenerate the onboarding document.",
        })

        results["valid"] = False
        return results

    # Check 3: Verify expected documentation sections.
    results["checks_performed"] += 1

    required_sections = [
        "Project Overview",
        "Technology Stack",
        "Important Files",
        "Project Structure",
        "Setup Guidance",
    ]

    missing_sections = [
        section
        for section in required_sections
        if not re.search(
            rf"^#+\s+.*{re.escape(section)}",
            content,
            re.IGNORECASE | re.MULTILINE,
        )
    ]

    if missing_sections:
        results["issues"].append({
            "check": "required_sections",
            "message": (
                "Missing documentation sections: "
                + ", ".join(missing_sections)
            ),
            "suggestion": "Regenerate the document with all required sections.",
        })

        results["valid"] = False

    # Check 4: Verify repository-relative Python file references.
    results["checks_performed"] += 1

    referenced_files = set(
        re.findall(
            r"`((?:backend|frontend)/[^`\r\n]+\.py)`",
            content,
        )
    )

    missing_files = []

    for relative_path in sorted(referenced_files):
        candidate = Path(relative_path)

        # Reject paths that attempt to escape the repository root.
        if candidate.is_absolute() or ".." in candidate.parts:
            missing_files.append(relative_path)
            continue

        full_path = (root / candidate).resolve()

        try:
            full_path.relative_to(root)
        except ValueError:
            missing_files.append(relative_path)
            continue

        if not full_path.is_file():
            missing_files.append(relative_path)

    if missing_files:
        results["issues"].append({
            "check": "referenced_files_exist",
            "message": (
                "Documentation references files that do not exist: "
                + ", ".join(missing_files)
            ),
            "suggestion": "Correct the file references or update the repository.",
        })

        results["valid"] = False

    # Check 5: Confirm that the code relationships section exists.
    results["checks_performed"] += 1

    if not re.search(
        r"^#+\s+.*Code Relationships",
        content,
        re.IGNORECASE | re.MULTILINE,
    ):
        results["warnings"].append(
            "The Code Relationships section is missing."
        )

    return results