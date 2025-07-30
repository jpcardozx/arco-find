#!/usr/bin/env python3
"""
🔧 GIT REPOSITORY CONSOLIDATION STRATEGY
Estratégia sênior para organizar branches e deploy consolidado
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

class GitConsolidationStrategy:
    """Estratégia profissional para consolidação Git"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def analyze_current_state(self):
        """Analisa estado atual do repositório"""
        print("🔍 ANÁLISE DO ESTADO ATUAL DO REPOSITÓRIO")
        print("=" * 60)
        
        # Status atual
        status = self._run_git_command(['status', '--porcelain'])
        print(f"📊 Arquivos modificados: {len(status.splitlines()) if status else 0}")
        
        # Branches locais e remotas
        branches = self._run_git_command(['branch', '-a'])
        print(f"🌿 Branches disponíveis:")
        for line in branches.splitlines():
            line = line.strip()
            if line.startswith('*'):
                print(f"   → {line} (ATUAL)")
            elif 'remotes/origin/copilot/' in line:
                print(f"   🤖 {line} (Copilot PR)")
            elif 'remotes/origin/' in line:
                print(f"   🌐 {line} (Remoto)")
            else:
                print(f"   📍 {line} (Local)")
        
        # Últimos commits
        log = self._run_git_command(['log', '--oneline', '-5'])
        print(f"\n📝 Últimos commits:")
        for line in log.splitlines():
            print(f"   {line}")
        
        return {
            'detached_head': 'HEAD detached' in branches,
            'has_changes': len(status.splitlines()) > 0 if status else False,
            'copilot_branches': [line for line in branches.splitlines() if 'copilot/' in line]
        }
    
    def create_consolidation_plan(self):
        """Cria plano de consolidação"""
        print(f"\n🎯 PLANO DE CONSOLIDAÇÃO SÊNIOR")
        print("=" * 60)
        
        plan = {
            'phase_1': 'Preparação e backup do trabalho atual',
            'phase_2': 'Análise dos PRs do Copilot para aproveitamento',
            'phase_3': 'Criação de branch de desenvolvimento estável',
            'phase_4': 'Consolidação das melhorias maduras',
            'phase_5': 'Deploy limpo para main com estrutura sólida',
            'phase_6': 'Limpeza de branches obsoletas'
        }
        
        for phase, description in plan.items():
            print(f"   {phase.upper()}: {description}")
        
        return plan
    
    def execute_consolidation(self):
        """Executa consolidação profissional"""
        print(f"\n🚀 EXECUTANDO CONSOLIDAÇÃO PROFISSIONAL")
        print("=" * 60)
        
        try:
            # FASE 1: Backup do trabalho atual
            print("\n📦 FASE 1: Backup do trabalho atual")
            self._backup_current_work()
            
            # FASE 2: Análise dos PRs do Copilot
            print("\n🤖 FASE 2: Análise dos PRs do Copilot")
            self._analyze_copilot_contributions()
            
            # FASE 3: Criar branch de desenvolvimento
            print("\n🌿 FASE 3: Criação de branch de desenvolvimento")
            self._create_development_branch()
            
            # FASE 4: Consolidar melhorias
            print("\n🔧 FASE 4: Consolidação de melhorias")
            self._consolidate_improvements()
            
            # FASE 5: Preparar para main
            print("\n🎯 FASE 5: Preparação para main")
            self._prepare_for_main()
            
            print(f"\n✅ CONSOLIDAÇÃO CONCLUÍDA COM SUCESSO!")
            self._show_next_steps()
            
        except Exception as e:
            print(f"\n❌ Erro na consolidação: {e}")
            self._show_recovery_steps()
    
    def _backup_current_work(self):
        """Faz backup do trabalho atual"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_branch = f"backup/consolidation_{timestamp}"
        
        # Adicionar mudanças não commitadas
        self._run_git_command(['add', '.'])
        
        # Criar commit de backup
        commit_msg = f"🛡️ Backup antes da consolidação - {timestamp}"
        self._run_git_command(['commit', '-m', commit_msg])
        
        # Criar branch de backup
        self._run_git_command(['checkout', '-b', backup_branch])
        
        print(f"   ✅ Backup criado: {backup_branch}")
        return backup_branch
    
    def _analyze_copilot_contributions(self):
        """Analisa contribuições dos PRs do Copilot"""
        copilot_branches = [
            'origin/copilot/fix-818f3225-89f4-415a-aa83-afa9a749581a',
            'origin/copilot/fix-fbbfd8de-1677-432a-804c-7db4b9b50308'
        ]
        
        valuable_contributions = []
        
        for branch in copilot_branches:
            try:
                # Analisar diferenças
                diff = self._run_git_command(['diff', 'origin/main', branch, '--name-only'])
                
                if diff:
                    files_changed = diff.splitlines()
                    print(f"   🔍 {branch}:")
                    print(f"      📁 Arquivos alterados: {len(files_changed)}")
                    
                    # Verificar se há melhorias valiosas
                    has_tests = any('test' in f for f in files_changed)
                    has_docs = any('doc' in f.lower() or 'readme' in f.lower() for f in files_changed)
                    has_config = any('config' in f or 'setup' in f for f in files_changed)
                    
                    if has_tests or has_docs or has_config:
                        valuable_contributions.append({
                            'branch': branch,
                            'files': files_changed,
                            'has_tests': has_tests,
                            'has_docs': has_docs,
                            'has_config': has_config
                        })
                        print(f"      ✅ Contribuição valiosa identificada")
                    else:
                        print(f"      ⚠️ Mudanças menores")
                
            except Exception as e:
                print(f"   ❌ Erro analisando {branch}: {e}")
        
        print(f"   📊 Contribuições valiosas: {len(valuable_contributions)}")
        return valuable_contributions
    
    def _create_development_branch(self):
        """Cria branch de desenvolvimento estável"""
        # Ir para main remoto mais recente
        self._run_git_command(['checkout', 'origin/main'])
        
        # Criar nova branch de desenvolvimento
        dev_branch = "development/consolidated-architecture"
        self._run_git_command(['checkout', '-b', dev_branch])
        
        print(f"   ✅ Branch de desenvolvimento criada: {dev_branch}")
        return dev_branch
    
    def _consolidate_improvements(self):
        """Consolida melhorias da branch de backup"""
        # Aplicar melhorias do backup seletivamente
        backup_branch = self._get_latest_backup_branch()
        
        if backup_branch:
            # Cherry-pick melhorias específicas
            try:
                # Aplicar apenas arquivos essenciais
                essential_files = [
                    'src/core/lead_qualification_engine.py',
                    'src/connectors/searchapi_connector.py',
                    'src/config/arco_config_manager.py',
                    'config/api_keys.py',
                    'scripts/',
                    'docs/',
                ]
                
                for file_pattern in essential_files:
                    try:
                        self._run_git_command(['checkout', backup_branch, '--', file_pattern])
                        print(f"   ✅ Aplicado: {file_pattern}")
                    except:
                        print(f"   ⚠️ Não encontrado: {file_pattern}")
                
                # Commit das consolidações
                self._run_git_command(['add', '.'])
                self._run_git_command(['commit', '-m', '🎯 Consolidate core improvements and architecture'])
                
            except Exception as e:
                print(f"   ⚠️ Erro na consolidação: {e}")
    
    def _prepare_for_main(self):
        """Prepara branch para merge em main"""
        # Verificar se tudo está commitado
        status = self._run_git_command(['status', '--porcelain'])
        
        if status:
            self._run_git_command(['add', '.'])
            self._run_git_command(['commit', '-m', '🔧 Final preparation for main branch'])
        
        # Push da branch de desenvolvimento
        dev_branch = "development/consolidated-architecture"
        self._run_git_command(['push', '-u', 'origin', dev_branch])
        
        print(f"   ✅ Branch preparada para merge em main")
        print(f"   🌐 Pushed: origin/{dev_branch}")
    
    def _get_latest_backup_branch(self):
        """Obtém a branch de backup mais recente"""
        branches = self._run_git_command(['branch', '--list', 'backup/*'])
        if branches:
            backup_branches = branches.splitlines()
            return backup_branches[-1].strip() if backup_branches else None
        return None
    
    def _run_git_command(self, args):
        """Executa comando git e retorna output"""
        try:
            result = subprocess.run(['git'] + args, 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=self.project_root)
            
            if result.returncode != 0:
                raise Exception(f"Git command failed: {result.stderr}")
            
            return result.stdout.strip()
        except Exception as e:
            print(f"   ❌ Git command error: {e}")
            raise
    
    def _show_next_steps(self):
        """Mostra próximos passos"""
        print(f"\n🎯 PRÓXIMOS PASSOS:")
        print("   1. Revisar branch: development/consolidated-architecture")
        print("   2. Criar Pull Request para main")
        print("   3. Merge após aprovação")
        print("   4. Limpar branches antigas")
        print(f"\n📋 COMANDOS RECOMENDADOS:")
        print("   git checkout development/consolidated-architecture")
        print("   git push origin development/consolidated-architecture")
        print("   # Criar PR no GitHub")
        print("   # Após merge: git checkout main && git pull")
    
    def _show_recovery_steps(self):
        """Mostra passos de recuperação em caso de erro"""
        print(f"\n🛡️ PASSOS DE RECUPERAÇÃO:")
        print("   1. git checkout <backup-branch>")
        print("   2. git checkout -b recovery/manual-fix")
        print("   3. Aplicar mudanças manualmente")
        print("   4. Executar testes de validação")

def main():
    """Executa estratégia de consolidação"""
    print("🎯 GIT CONSOLIDATION STRATEGY - SENIOR APPROACH")
    print("=" * 70)
    print(f"📅 Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    strategy = GitConsolidationStrategy()
    
    # Análise do estado atual
    current_state = strategy.analyze_current_state()
    
    # Plano de consolidação
    plan = strategy.create_consolidation_plan()
    
    # Confirmar execução
    print(f"\n❓ Deseja executar a consolidação? [y/N]: ", end="")
    response = input().lower().strip()
    
    if response == 'y':
        strategy.execute_consolidation()
    else:
        print("   ⚠️ Consolidação cancelada pelo usuário")
        print("   💡 Execute manualmente quando estiver pronto")

if __name__ == "__main__":
    main()
