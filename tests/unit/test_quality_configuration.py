import tomllib
import unittest
from pathlib import Path


class TestQAQualityConfiguration(unittest.TestCase):
    """QA: testa a configuração mínima de qualidade do projeto."""

    @classmethod
    def setUpClass(cls):
        """QA: carrega os arquivos de configuração e documentação.

        Pré-condição: os arquivos devem existir na raiz do projeto.
        Pós-condição: seus conteúdos ficam disponíveis para os testes.
        """
        project_root = Path(__file__).resolve().parents[2]
        cls.pyproject = tomllib.loads(
            (project_root / "pyproject.toml").read_text(encoding="utf-8")
        )
        cls.readme = (project_root / "README.md").read_text(encoding="utf-8")
        cls.makefile = (project_root / "Makefile").read_text(encoding="utf-8")

    def test_qa_declares_coverage_and_ruff_development_dependencies(self):
        """QA: dependências de desenvolvimento devem incluir coverage e ruff."""
        development_dependencies = self.pyproject["project"]["optional-dependencies"][
            "dev"
        ]

        self.assertTrue(
            any(
                dependency.startswith("coverage")
                for dependency in development_dependencies
            )
        )
        self.assertTrue(
            any(
                dependency.startswith("ruff") for dependency in development_dependencies
            )
        )

    def test_qa_requires_minimum_eighty_percent_coverage(self):
        """QA: relatório deve falhar quando a cobertura estiver abaixo de 80%."""
        coverage_report = self.pyproject["tool"]["coverage"]["report"]

        self.assertEqual(coverage_report["fail_under"], 80)

    def test_qa_configures_ruff_for_python_312(self):
        """QA: Ruff deve analisar o projeto usando Python 3.12."""
        ruff_configuration = self.pyproject["tool"]["ruff"]

        self.assertEqual(ruff_configuration["target-version"], "py312")

    def test_qa_makefile_exposes_quality_commands(self):
        """QA: Makefile deve oferecer testes, cobertura, lint e formatação."""
        for target in ("test:", "coverage:", "lint:", "format:", "quality:"):
            with self.subTest(target=target):
                self.assertIn(target, self.makefile)

    def test_qa_readme_documents_commands_and_traceability(self):
        """QA: README deve documentar uso e IDs obrigatórios nos testes."""
        expected_content = (
            "python -m unittest discover -s tests",
            "coverage run -m unittest discover -s tests",
            "coverage report --fail-under=80",
            "ruff check .",
            "ruff format .",
            "ID da estória",
        )

        for content in expected_content:
            with self.subTest(content=content):
                self.assertIn(content, self.readme)
