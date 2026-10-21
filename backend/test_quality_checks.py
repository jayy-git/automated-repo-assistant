import unittest
from quality_checks import check_repository


class TestQualityChecks(unittest.TestCase):

    def complete_repository(self):
        return {
            "repo_name": "demo-project",
            "files": [
                "README.md",
                "LICENSE",
                "CONTRIBUTING.md",
                "requirements.txt",
                ".gitignore"
            ],
            "readme_exists": True,
            "license_exists": True,
            "contributing_exists": True,
            "requirements_files": ["requirements.txt"]
        }

    def test_missing_required_files_report_expected_findings(self):
        repo_data = {
            "files": [],
            "readme_exists": False,
            "license_exists": False,
            "contributing_exists": False,
            "requirements_files": []
        }

        findings = check_repository(repo_data)
        finding_titles = [finding["title"] for finding in findings]

        self.assertIn("README file not found", finding_titles)
        self.assertIn("License file not found", finding_titles)
        self.assertIn("CONTRIBUTING guide not found", finding_titles)
        self.assertIn("Dependency file not found", finding_titles)
        self.assertIn(".gitignore file not found", finding_titles)

    def test_all_files_present(self):
        self.assertEqual(check_repository(self.complete_repository()), [])

    def test_every_finding_has_required_fields_and_valid_severity(self):
        repo_data = {
            "files": [],
            "readme_exists": False,
            "license_exists": False,
            "contributing_exists": False,
            "requirements_files": [],
            "readme_content": "Project overview without setup details."
        }
        required_fields = {
            "title",
            "severity",
            "category",
            "explanation",
            "suggestion"
        }
        allowed_severities = {"Critical", "High", "Medium", "Low", "Info"}

        for finding in check_repository(repo_data):
            self.assertTrue(required_fields.issubset(finding.keys()))
            self.assertIn(finding["severity"], allowed_severities)

    def test_incomplete_data(self):
        findings = check_repository({"files": []})

        self.assertIsInstance(findings, list)
        finding_titles = [finding["title"] for finding in findings]
        self.assertIn("README file not found", finding_titles)
        self.assertIn("License file not found", finding_titles)
        self.assertIn("CONTRIBUTING guide not found", finding_titles)
        self.assertIn("Dependency file not found", finding_titles)

    def test_non_dictionary_input_is_handled_safely(self):
        findings = check_repository(None)

        self.assertIsInstance(findings, list)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["title"], "Invalid repository data")

    def test_incorrectly_typed_files_field_is_reported_safely(self):
        findings = check_repository({"files": "README.md"})
        finding_titles = [finding["title"] for finding in findings]

        self.assertIn("Invalid repository file list", finding_titles)
        self.assertIn(".gitignore file not found", finding_titles)

    def test_gitignore_detection_accepts_windows_and_unix_paths(self):
        for gitignore_path in (r"config\.gitignore", "config/.gitignore"):
            with self.subTest(path=gitignore_path):
                repo_data = self.complete_repository()
                repo_data["files"] = [gitignore_path]

                finding_titles = [
                    finding["title"] for finding in check_repository(repo_data)
                ]

                self.assertNotIn(".gitignore file not found", finding_titles)

    def test_setup_check_is_skipped_when_readme_content_is_unavailable(self):
        repo_data = self.complete_repository()

        finding_titles = [
            finding["title"] for finding in check_repository(repo_data)
        ]

        self.assertNotIn("Setup instructions may be missing", finding_titles)

    def test_setup_finding_requires_supplied_readme_without_setup_instructions(self):
        repo_data = self.complete_repository()
        repo_data["readme_content"] = "This README describes the project."

        finding_titles = [
            finding["title"] for finding in check_repository(repo_data)
        ]

        self.assertIn("Setup instructions may be missing", finding_titles)

    def test_setup_finding_is_not_reported_when_readme_has_setup_instructions(self):
        repo_data = self.complete_repository()
        repo_data["readme_content"] = "## Installation\nRun the application."

        finding_titles = [
            finding["title"] for finding in check_repository(repo_data)
        ]

        self.assertNotIn("Setup instructions may be missing", finding_titles)


if __name__ == "__main__":
    unittest.main()