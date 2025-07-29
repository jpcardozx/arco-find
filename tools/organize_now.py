"""
ORGANIZADOR AUTOMÁTICO DO PROJETO ARCO
=====================================
Move arquivos para estrutura hierárquica correta
"""

import os
import shutil
from pathlib import Path

class ARCOProjectOrganizer:
    """Organizador automático do projeto"""
    
    def __init__(self, workspace_path: str):
        self.workspace = Path(workspace_path)
        
        # Estrutura hierárquica correta
        self.structure = {
            'core/': [
                'ARCO_SMB_AGENCY_INTELLIGENCE_SYSTEM.py',
                'arco_v2_final_optimized.py',
                'arco_constants.py',
                'error_handler.py'
            ],
            'engines/': [
                'arco_intermediate_lead_finder_v2_CRITICAL_FIX.py',
                'arco_intermediate_lead_finder_v2.py',
                'arco_intermediate_lead_finder_v2_OPTIMIZED.py',
                'arco_intermediate_lead_finder_v2_REFACTORED.py'
            ],
            'deprecated/': [
                'arco_engine.py',
                'arco_executive_*.py',
                'arco_hybrid_*.py',
                'arco_pain_signal_*.py',
                'arco_smart_lead_*.py',
                'meta_ads_*.py'
            ],
            'tests/': [
                'test_*.py',
                'validate_*.py',
                'debug_*.py',
                'quick_*.py'
            ],
            'reports/': [
                '*.md',
                'RELATORIO_*.md',
                'ANALISE_*.md',
                'SUMARIO_*.md',
                'ROOT_CAUSE_*.md'
            ],
            'exports/': [
                '*.json'
            ],
            'tools/': [
                'organize_project.py',
                'pipeline_optimizer.py',
                'project_cleaner_final.py',
                'system_auditor_v3.py'
            ]
        }
    
    def organize_project(self):
        """Organizar projeto automaticamente"""
        print("🔧 ORGANIZANDO PROJETO ARCO")
        print("=" * 40)
        
        # 1. Criar diretórios
        self._create_directories()
        
        # 2. Mover arquivos
        self._move_files()
        
        # 3. Limpar raiz
        self._clean_root()
        
        print("✅ PROJETO ORGANIZADO!")
    
    def _create_directories(self):
        """Criar estrutura de diretórios"""
        for directory in self.structure.keys():
            dir_path = self.workspace / directory
            dir_path.mkdir(exist_ok=True)
            print(f"📁 Criado: {directory}")
    
    def _move_files(self):
        """Mover arquivos para diretórios corretos"""
        
        # Mapear arquivos existentes
        existing_files = list(self.workspace.glob('*.py'))
        existing_files.extend(list(self.workspace.glob('*.md')))
        existing_files.extend(list(self.workspace.glob('*.json')))
        
        for file_path in existing_files:
            if file_path.is_file():
                target_dir = self._get_target_directory(file_path.name)
                if target_dir:
                    target_path = self.workspace / target_dir / file_path.name
                    
                    try:
                        if not target_path.exists():
                            shutil.move(str(file_path), str(target_path))
                            print(f"📦 Movido: {file_path.name} -> {target_dir}")
                        else:
                            print(f"⚠️ Já existe: {file_path.name} em {target_dir}")
                    except Exception as e:
                        print(f"❌ Erro movendo {file_path.name}: {e}")
    
    def _get_target_directory(self, filename: str) -> str:
        """Determinar diretório de destino"""
        
        # Core files
        if filename in self.structure['core/']:
            return 'core'
        
        # Engine files
        if any(pattern in filename for pattern in ['intermediate_lead', 'lead_finder']):
            return 'engines'
        
        # Deprecated patterns
        deprecated_patterns = ['arco_executive', 'arco_hybrid', 'arco_pain', 'arco_smart', 'meta_ads_engine']
        if any(pattern in filename for pattern in deprecated_patterns):
            return 'deprecated'
        
        # Test files
        if filename.startswith(('test_', 'validate_', 'debug_', 'quick_')):
            return 'tests'
        
        # Report files
        if filename.endswith('.md') and any(prefix in filename for prefix in ['RELATORIO', 'ANALISE', 'SUMARIO', 'ROOT_CAUSE']):
            return 'reports'
        
        # Export files
        if filename.endswith('.json') and ('intelligence' in filename.lower() or 'leads' in filename.lower()):
            return 'exports'
        
        # Tool files
        tool_patterns = ['organize_project', 'pipeline_optimizer', 'project_cleaner', 'system_auditor']
        if any(pattern in filename for pattern in tool_patterns):
            return 'tools'
        
        return None
    
    def _clean_root(self):
        """Limpar arquivos desnecessários da raiz"""
        
        # Arquivos temporários para remover
        temp_patterns = ['*.pyc', '__pycache__', '*.tmp', '*.bak']
        
        for pattern in temp_patterns:
            for file_path in self.workspace.glob(pattern):
                try:
                    if file_path.is_file():
                        file_path.unlink()
                        print(f"🗑️ Removido: {file_path.name}")
                    elif file_path.is_dir():
                        shutil.rmtree(file_path)
                        print(f"🗑️ Removido: {file_path.name}/")
                except Exception as e:
                    print(f"❌ Erro removendo {file_path}: {e}")

def main():
    """Execução principal"""
    workspace_path = r"c:\Users\João Pedro Cardozo\OneDrive\Área de Trabalho\arco\arco-find"
    
    organizer = ARCOProjectOrganizer(workspace_path)
    organizer.organize_project()
    
    print("\n📋 ESTRUTURA FINAL:")
    print("📁 core/ - Arquivos principais do sistema")
    print("📁 engines/ - Engines de busca e processamento")
    print("📁 deprecated/ - Arquivos obsoletos")
    print("📁 tests/ - Testes e validações")
    print("📁 reports/ - Relatórios e documentação")
    print("📁 exports/ - Dados exportados")
    print("📁 tools/ - Ferramentas de manutenção")
    print("\n🎯 RAIZ LIMPA E ORGANIZADA!")

if __name__ == "__main__":
    main()
