"""
Módulo de validação para o projeto ARCO.

Este módulo fornece utilitários para validar a integridade do projeto,
incluindo verificação de estrutura de diretórios, importações e configurações.
"""

import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

logger = logging.getLogger(__name__)

class ProjectValidator:
    """
    Validador de projeto ARCO.
    
    Esta classe fornece métodos para validar a integridade do projeto ARCO,
    incluindo verificação de estrutura de diretórios, importações e configurações.
    """
    
    def __init__(self):
        """Inicializa o validador de projeto."""
        self.root_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
    
    def validate_project_structure(self) -> bool:
        """
        Valida a estrutura de diretórios do projeto.
        
        Returns:
            bool: True se a estrutura de diretórios for válida, False caso contrário.
        """
        required_dirs = [
            "arco",
            "arco/pipelines",
            "arco/engines",
            "arco/models",
            "arco/integrations",
            "arco/config",
            "arco/utils",
            "tests",
            "docs",
            "config",
            "archive"
        ]
        
        required_files = [
            "main.py",
            "requirements.txt",
            "setup.py",
            ".env.template",
            "README.md",
            "pytest.ini",
            "conftest.py"
        ]
        
        # Verificar diretórios
        for dir_path in required_dirs:
            full_path = self.root_dir / dir_path
            if full_path.is_dir():
                self.results["passed"].append(f"Directory {dir_path} exists")
            else:
                self.results["failed"].append(f"Directory {dir_path} does not exist")
        
        # Verificar arquivos
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if full_path.is_file():
                self.results["passed"].append(f"File {file_path} exists")
            else:
                self.results["failed"].append(f"File {file_path} does not exist")
        
        # Verificar profundidade de diretórios
        max_depth = 0
        for root, dirs, files in os.walk(self.root_dir / "arco"):
            depth = len(Path(root).relative_to(self.root_dir).parts)
            max_depth = max(max_depth, depth)
        
        if max_depth <= 3:
            self.results["passed"].append(f"Directory depth is {max_depth}, which is <= 3")
        else:
            self.results["failed"].append(f"Directory depth is {max_depth}, which is > 3")
        
        # Verificar convenções de pacotes Python
        python_packages = ["arco", "arco/pipelines", "arco/engines", "arco/models", 
                          "arco/integrations", "arco/config", "arco/utils"]
        
        for package in python_packages:
            init_file = self.root_dir / package / "__init__.py"
            if init_file.is_file():
                self.results["passed"].append(f"__init__.py exists in {package}")
            else:
                self.results["failed"].append(f"__init__.py missing in {package}")
        
        return len(self.results["failed"]) == 0
    
    def validate_imports(self) -> bool:
        """
        Valida as importações do projeto.
        
        Returns:
            bool: True se as importações forem válidas, False caso contrário.
        """
        # Adicionar o diretório raiz ao sys.path se não estiver lá
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))
        
        modules_to_check = [
            "arco",
            "arco.pipelines",
            "arco.engines",
            "arco.models",
            "arco.integrations",
            "arco.config",
            "arco.utils"
        ]
        
        for module_name in modules_to_check:
            try:
                importlib.import_module(module_name)
                self.results["passed"].append(f"Successfully imported {module_name}")
            except ImportError as e:
                self.results["failed"].append(f"Failed to import {module_name}: {e}")
        
        # Verificar importações específicas
        try:
            from arco.pipelines import StandardPipeline, AdvancedPipeline
            self.results["passed"].append("Successfully imported StandardPipeline and AdvancedPipeline")
        except ImportError as e:
            self.results["failed"].append(f"Failed to import StandardPipeline or AdvancedPipeline: {e}")
        
        return len([r for r in self.results["failed"] if r.startswith("Failed to import")]) == 0
    
    def validate_configuration(self) -> bool:
        """
        Valida as configurações do projeto.
        
        Returns:
            bool: True se as configurações forem válidas, False caso contrário.
        """
        # Verificar diretório de configuração
        config_dir = self.root_dir / "config"
        if not config_dir.is_dir():
            self.results["failed"].append("Configuration directory does not exist")
            return False
        
        # Verificar arquivos de configuração
        config_files = list(config_dir.glob("*.yml"))
        if not config_files:
            self.results["failed"].append("No configuration files found")
            return False
        
        self.results["passed"].append(f"Configuration directory contains {len(config_files)} files")
        
        # Verificar .env.template
        env_template = self.root_dir / ".env.template"
        if not env_template.is_file():
            self.results["failed"].append(".env.template does not exist")
        else:
            self.results["passed"].append(".env.template exists")
            
            # Verificar conteúdo do .env.template
            with open(env_template, "r", encoding="utf-8") as f:
                env_content = f.read().strip()
                if env_content:
                    self.results["passed"].append(".env.template has content")
                else:
                    self.results["warnings"].append(".env.template is empty")
        
        # Verificar requirements.txt
        requirements = self.root_dir / "requirements.txt"
        if not requirements.is_file():
            self.results["failed"].append("requirements.txt does not exist")
        else:
            self.results["passed"].append("requirements.txt exists")
            
            # Verificar conteúdo do requirements.txt
            with open(requirements, "r", encoding="utf-8") as f:
                req_content = f.read().strip()
                if req_content:
                    self.results["passed"].append("requirements.txt has content")
                else:
                    self.results["warnings"].append("requirements.txt is empty")
        
        return len([r for r in self.results["failed"] if r.startswith("Configuration")]) == 0
    
    def validate_documentation(self) -> bool:
        """
        Valida a documentação do projeto.
        
        Returns:
            bool: True se a documentação for válida, False caso contrário.
        """
        # Verificar diretório de documentação
        docs_dir = self.root_dir / "docs"
        if not docs_dir.is_dir():
            self.results["failed"].append("Documentation directory does not exist")
            return False
        
        # Verificar arquivos de documentação essenciais
        essential_docs = [
            "README.md",
            "docs/architecture.md",
            "docs/usage.md",
            "docs/installation.md",
            "docs/contributing.md",
            "docs/examples.md"
        ]
        
        for doc_file in essential_docs:
            doc_path = self.root_dir / doc_file
            if doc_path.is_file():
                self.results["passed"].append(f"Documentation file {doc_file} exists")
            else:
                self.results["failed"].append(f"Documentation file {doc_file} does not exist")
        
        # Verificar README.md
        readme = self.root_dir / "README.md"
        if readme.is_file():
            with open(readme, "r", encoding="utf-8") as f:
                readme_content = f.read().lower()
                if "structure" in readme_content or "directory" in readme_content or "organization" in readme_content:
                    self.results["passed"].append("README.md describes the project structure")
                else:
                    self.results["warnings"].append("README.md may not describe the project structure")
        
        return len([r for r in self.results["failed"] if r.startswith("Documentation")]) == 0
    
    def validate_tests(self) -> bool:
        """
        Valida os testes do projeto.
        
        Returns:
            bool: True se os testes forem válidos, False caso contrário.
        """
        # Verificar diretório de testes
        tests_dir = self.root_dir / "tests"
        if not tests_dir.is_dir():
            self.results["failed"].append("Tests directory does not exist")
            return False
        
        # Contar arquivos de teste
        test_files = []
        for root, _, files in os.walk(tests_dir):
            for file in files:
                if file.startswith("test_") and file.endswith(".py"):
                    test_files.append(os.path.join(root, file))
        
        if test_files:
            self.results["passed"].append(f"Tests directory contains {len(test_files)} test files")
        else:
            self.results["failed"].append("Tests directory is empty")
        
        # Verificar pytest.ini
        pytest_ini = self.root_dir / "pytest.ini"
        if pytest_ini.is_file():
            self.results["passed"].append("pytest.ini exists")
        else:
            self.results["failed"].append("pytest.ini does not exist")
        
        # Verificar conftest.py
        conftest = self.root_dir / "conftest.py"
        if conftest.is_file():
            self.results["passed"].append("conftest.py exists")
        else:
            self.results["failed"].append("conftest.py does not exist")
        
        return len([r for r in self.results["failed"] if r.startswith("Tests")]) == 0
    
    def validate_pipeline_functionality(self) -> bool:
        """
        Valida a funcionalidade dos pipelines.
        
        Returns:
            bool: True se os pipelines forem válidos, False caso contrário.
        """
        # Verificar arquivos de pipeline
        pipeline_files = [
            "arco/pipelines/standard_pipeline.py",
            "arco/pipelines/advanced_pipeline.py",
        ]
        
        for pipeline_file in pipeline_files:
            pipeline_path = self.root_dir / pipeline_file
            if pipeline_path.is_file():
                self.results["passed"].append(f"Pipeline file {pipeline_file} exists")
            else:
                self.results["failed"].append(f"Pipeline file {pipeline_file} does not exist")
        
        # Verificar diretório de integrações
        integrations_dir = self.root_dir / "arco/integrations"
        if integrations_dir.is_dir():
            integration_files = [f for f in os.listdir(integrations_dir) if f.endswith(".py")]
            if len(integration_files) > 1 or (len(integration_files) == 1 and integration_files[0] != "__init__.py"):
                self.results["passed"].append(f"Integration files exist: {', '.join(integration_files)}")
            else:
                self.results["warnings"].append("Few or no integration files found")
        else:
            self.results["failed"].append("Integrations directory does not exist")
        
        return len([r for r in self.results["failed"] if r.startswith("Pipeline")]) == 0
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Executa todas as validações e retorna os resultados.
        
        Returns:
            Dict[str, Any]: Resultados da validação.
        """
        self.validate_project_structure()
        self.validate_imports()
        self.validate_configuration()
        self.validate_documentation()
        self.validate_tests()
        self.validate_pipeline_functionality()
        
        return {
            "passed": len(self.results["passed"]),
            "failed": len(self.results["failed"]),
            "warnings": len(self.results["warnings"]),
            "details": self.results
        }
    
    def generate_report(self) -> str:
        """
        Gera um relatório de validação.
        
        Returns:
            str: Relatório de validação.
        """
        results = self.validate_all()
        
        report = []
        report.append("# ARCO Project Validation Report")
        report.append("")
        report.append("## Summary")
        report.append("")
        
        total_tests = results["passed"] + results["failed"]
        passed_percent = (results["passed"] / total_tests * 100) if total_tests > 0 else 0
        
        report.append(f"- **Total Tests:** {total_tests}")
        report.append(f"- **Passed:** {results['passed']} ({passed_percent:.1f}%)")
        report.append(f"- **Failed:** {results['failed']}")
        report.append(f"- **Warnings:** {results['warnings']}")
        report.append("")
        
        if results["failed"] > 0:
            report.append("## Failed Tests")
            report.append("")
            for failure in self.results["failed"]:
                report.append(f"- **{failure}**")
            report.append("")
        
        if results["warnings"] > 0:
            report.append("## Warnings")
            report.append("")
            for warning in self.results["warnings"]:
                report.append(f"- **{warning}**")
            report.append("")
        
        report.append("## Passed Tests")
        report.append("")
        for success in self.results["passed"]:
            report.append(f"- **{success}**")
        
        return "\n".join(report)


def validate_project() -> Dict[str, Any]:
    """
    Valida o projeto ARCO.
    
    Returns:
        Dict[str, Any]: Resultados da validação.
    """
    validator = ProjectValidator()
    return validator.validate_all()


def generate_validation_report() -> str:
    """
    Gera um relatório de validação do projeto ARCO.
    
    Returns:
        str: Relatório de validação.
    """
    validator = ProjectValidator()
    return validator.generate_report()


if __name__ == "__main__":
    report = generate_validation_report()
    print(report)
    
    # Salvar relatório em arquivo
    with open("validation_report.md", "w", encoding="utf-8") as f:
        f.write(report)