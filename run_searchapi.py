"""
ARCO SearchAPI - Script de Execução Rápida
=========================================

Script simplificado para executar as 3 camadas do SearchAPI
sem precisar configurar imports complexos.

Uso:
python run_searchapi.py
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path

def setup_environment():
    """Setup básico do ambiente"""
    
    # Criar diretórios necessários
    Path("data").mkdir(exist_ok=True)
    Path("logs").mkdir(exist_ok=True)
    Path("data/searchapi_results").mkdir(exist_ok=True)
    
    # Setup logging
    log_file = f"logs/searchapi_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    
    return logging.getLogger(__name__)

def get_api_key():
    """Obtém API key do SearchAPI"""
    
    # Tentar variável de ambiente primeiro
    api_key = os.getenv('SEARCHAPI_KEY')
    
    if not api_key:
        # Tentar config file
        try:
            config_path = Path("config/discovery_config.json")
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    api_key = config.get('searchapi_config', {}).get('api_key', '')
        except:
            pass
    
    if not api_key or api_key == '' or '${' in api_key:
        print("\n❌ SearchAPI key não encontrada!")
        print("\nConfigurações possíveis:")
        print("1. Definir variável de ambiente: export SEARCHAPI_KEY=sua_chave")
        print("2. Adicionar no arquivo .env: SEARCHAPI_KEY=sua_chave")
        print("3. Atualizar config/discovery_config.json")
        print("\nObtenha sua chave em: https://serpapi.com/")
        return None
    
    return api_key

def run_quick_demo():
    """Executa demo rápida das 3 camadas"""
    
    logger = setup_environment()
    logger.info("🚀 Iniciando demo do ARCO SearchAPI")
    
    # Verificar API key
    api_key = get_api_key()
    if not api_key:
        return False
    
    logger.info("✅ API key configurada")
    
    try:
        # Importar apenas o que precisamos (inline import para evitar erros)
        sys.path.append(str(Path(__file__).parent / "src" / "engines"))
        
        from searchapi_layer1_seed_generation import SearchAPILayer1SeedGeneration
        
        logger.info("📦 Módulos importados com sucesso")
        
        # === DEMO LAYER 1 ===
        logger.info("\n🌱 LAYER 1: Seed Generation")
        
        layer1 = SearchAPILayer1SeedGeneration(api_key)
        
        # Teste com 1 keyword, região AU
        logger.info("Buscando anunciantes para 'invisalign' na Austrália...")
        
        seeds = layer1.search_advertisers_by_keyword(
            keyword="invisalign",
            region="AU",
            num_advertisers=5,  # Limite baixo para demo
            num_domains=5
        )
        
        logger.info(f"✅ Layer 1: {seeds['total_advertisers']} advertisers, {seeds['total_domains']} domains encontrados")
        
        # Salvar resultado
        output_file = f"data/demo_layer1_{int(datetime.now().timestamp())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(seeds, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Resultados salvos em: {output_file}")
        
        # === DEMONSTRAÇÃO CONCEITUAL ===
        logger.info("\n📋 DEMONSTRAÇÃO CONCEITUAL das 3 camadas:")
        
        print("\n" + "="*60)
        print("ARCO SearchAPI - Pipeline de 3 Camadas")
        print("="*60)
        
        print(f"\n🌱 LAYER 1 - SEED GENERATION")
        print(f"   ✓ Keyword testada: 'invisalign'")
        print(f"   ✓ Região: Austrália (AU)")
        print(f"   ✓ Advertisers encontrados: {seeds['total_advertisers']}")
        print(f"   ✓ Domains únicos: {seeds['total_domains']}")
        
        if seeds['advertisers']:
            print(f"\n   📊 Amostra de advertisers:")
            for i, advertiser in enumerate(seeds['advertisers'][:3]):
                print(f"      {i+1}. {advertiser.get('name', 'N/A')} ({advertiser.get('advertiser_id', 'N/A')})")
        
        print(f"\n🔍 LAYER 2 - ADVERTISER CONSOLIDATION (Conceitual)")
        print(f"   • Consolidaria por domínio único")
        print(f"   • Filtraria por atividade recente (últimos 30 dias)")
        print(f"   • Aplicaria score de qualificação (3-80 ads)")
        print(f"   • Removeria marketplaces/franquias")
        print(f"   • Output esperado: ~30-50% dos advertisers qualificados")
        
        print(f"\n🎯 LAYER 3 - AD DETAILS ANALYSIS (Conceitual)")
        print(f"   • Extrairia detalhes dos criativos")
        print(f"   • Analisaria CTAs e sinais de CRO")
        print(f"   • Capturaria final_url das landing pages")
        print(f"   • Calcularia score ARCO final (0-100)")
        print(f"   • Output esperado: ~20-30% prontos para outreach")
        
        print(f"\n📈 PROJEÇÃO PARA ESTE CASO:")
        estimated_qualified = max(1, int(seeds['total_advertisers'] * 0.4))
        estimated_outreach = max(1, int(estimated_qualified * 0.3))
        
        print(f"   • Advertisers qualificados (Layer 2): ~{estimated_qualified}")
        print(f"   • Prontos para outreach (Layer 3): ~{estimated_outreach}")
        print(f"   • Potencial de conversão: {estimated_outreach} prospects ARCO")
        
        print(f"\n💰 OPORTUNIDADE ESTIMADA:")
        print(f"   • Vertical: Dental/Ortodontia")
        print(f"   • Ticket médio: 3-8k AUD (implantes/invisalign)")
        print(f"   • ROI potencial: Sprint ARCO se paga com +20% conv. rate")
        
        print(f"\n🔧 PRÓXIMOS PASSOS:")
        print(f"   1. Executar Layer 2 com advertisers encontrados")
        print(f"   2. Filtrar e qualificar por score ARCO")
        print(f"   3. Extrair landing pages e gerar outreach")
        print(f"   4. Implementar pipeline automatizado")
        
        print("="*60)
        
        logger.info("✅ Demo concluída com sucesso!")
        logger.info(f"📁 Confira os resultados em: {output_file}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Erro de importação: {e}")
        logger.error("Certifique-se de que está executando do diretório raiz do projeto")
        return False
        
    except Exception as e:
        logger.error(f"❌ Erro durante execução: {str(e)}")
        return False

def main():
    """Função principal"""
    
    print("🎯 ARCO SearchAPI - Demo das 3 Camadas")
    print("="*50)
    
    success = run_quick_demo()
    
    if success:
        print("\n🎉 Demo executada com sucesso!")
        print("\n📖 Para mais informações, consulte:")
        print("   • README_SEARCHAPI_LAYERS.md - Documentação completa")
        print("   • test_searchapi_layers.py - Testes avançados")
        print("   • src/engines/ - Código das 3 camadas")
        
        print("\n🚀 Para executar pipeline completo:")
        print("   python test_searchapi_layers.py --test full")
        
    else:
        print("\n❌ Demo falhou. Verifique configurações e tente novamente.")
        
    print("\n" + "="*50)

if __name__ == "__main__":
    main()
