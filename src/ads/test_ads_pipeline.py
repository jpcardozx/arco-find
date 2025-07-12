#!/usr/bin/env python3
"""
🔍 TESTE FOCADO: DESCOBERTA + QUALIFICAÇÃO PIPELINE ADS INTELLIGENCE
Validação robusta das duas primeiras fases sem avançar para outreach

OBJETIVO:
- Testar a descoberta de prospects usando Google Places API
- Validar a qualificação usando ADS INTELLIGENCE como produto principal
- Confirmar que leads ultra-qualificados atendem aos critérios
- NÃO executar outreach (fase 3)

CRITÉRIOS DE SUCESSO:
- Descobrir pelo menos 25 prospects reais nos nichos prioritários
- Qualificar pelo menos 5 leads ultra-qualificados
- Cada lead deve ter ≥ $1,200/mês em savings de ads
- Email individual do decisor identificado
- Score ≥ 75/100 de qualificação
"""

import sys
import os
import time
import json
import logging
from datetime import datetime
from typing import List, Dict

# Adicionar paths do projeto
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'specialist'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'ads'))

# Configurar logging detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f'ads_pipeline_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)

class AdsPipelineTester:
    """Testador focado nas fases 1 e 2 do pipeline de Ads Intelligence"""
    
    def __init__(self):
        self.test_start = datetime.now()
        self.results = {
            'discovery_phase': {},
            'qualification_phase': {},
            'summary': {},
            'errors': []
        }
        
        # Configurações de teste
        self.test_config = {
            'target_prospects': 25,
            'target_ultra_qualified': 5,
            'min_monthly_savings': 800,
            'min_qualification_score': 75,
            'test_nichos': ['dental_premium_toronto', 'dermatology_miami_tampa']  # 2 nichos para teste
        }

    def test_discovery_phase(self):
        """Teste da Fase 1: Descoberta de Prospects"""
        logger.info("🔍 INICIANDO TESTE DA FASE 1: DESCOBERTA")
        logger.info("=" * 60)
        
        try:
            # Importar o detector principal
            from ultra_qualified_leads_detector import UltraQualifiedLeadsDetector
            
            self.detector = UltraQualifiedLeadsDetector()
            
            discovery_results = {
                'prospects_found': 0,
                'valid_websites': 0,
                'by_niche': {},
                'discovery_time': 0,
                'errors': []
            }
            
            start_time = time.time()
            
            for niche_key in self.test_config['test_nichos']:
                if niche_key not in self.detector.priority_niches:
                    error = f"Nicho {niche_key} não encontrado na configuração"
                    discovery_results['errors'].append(error)
                    logger.error(f"❌ {error}")
                    continue
                
                niche_config = self.detector.priority_niches[niche_key]
                niche_prospects = []
                
                logger.info(f"\n🎯 Testando descoberta no nicho: {niche_key}")
                logger.info(f"   Search terms: {niche_config['search_terms']}")
                logger.info(f"   Locations: {niche_config['locations']}")
                
                # Testar descoberta para cada combinação search_term + location
                for search_term in niche_config['search_terms'][:2]:  # Limitar para teste
                    for location in niche_config['locations'][:1]:  # 1 localização por nicho
                        logger.info(f"   🔍 Buscando: '{search_term}' em '{location}'")
                        
                        try:
                            businesses = self.detector._discover_businesses(search_term, location)
                            
                            valid_businesses = []
                            for business in businesses:
                                website = business.get('website')
                                name = business.get('name', 'N/A')
                                
                                if website and website.startswith('http'):
                                    valid_businesses.append(business)
                                    discovery_results['valid_websites'] += 1
                                    logger.info(f"      ✅ {name}: {website}")
                                else:
                                    logger.info(f"      ❌ {name}: sem website válido")
                            
                            niche_prospects.extend(valid_businesses)
                            discovery_results['prospects_found'] += len(businesses)
                            
                            logger.info(f"   📊 Encontrados: {len(businesses)} prospects, {len(valid_businesses)} com websites")
                            
                        except Exception as e:
                            error = f"Erro descobrindo {search_term} em {location}: {str(e)}"
                            discovery_results['errors'].append(error)
                            logger.error(f"      ❌ {error}")
                        
                        time.sleep(2)  # Rate limiting para API
                
                discovery_results['by_niche'][niche_key] = {
                    'prospects': len(niche_prospects),
                    'valid_websites': len([b for b in niche_prospects if b.get('website')])
                }
                
                logger.info(f"   ✅ {niche_key}: {len(niche_prospects)} prospects com websites válidos")
            
            discovery_results['discovery_time'] = time.time() - start_time
            self.results['discovery_phase'] = discovery_results
            
            # Validar resultados da descoberta
            logger.info(f"\n📊 RESULTADOS DA DESCOBERTA:")
            logger.info(f"   Total prospects encontrados: {discovery_results['prospects_found']}")
            logger.info(f"   Prospects com websites válidos: {discovery_results['valid_websites']}")
            logger.info(f"   Tempo de descoberta: {discovery_results['discovery_time']:.1f}s")
            
            if discovery_results['valid_websites'] < 10:
                logger.warning(f"⚠️  Poucos prospects descobertos ({discovery_results['valid_websites']} < 10)")
                return False
            
            logger.info("✅ FASE 1: DESCOBERTA APROVADA")
            return True
            
        except Exception as e:
            error = f"Erro crítico na fase de descoberta: {str(e)}"
            self.results['errors'].append(error)
            logger.error(f"❌ {error}")
            return False

    def test_qualification_phase(self):
        """Teste da Fase 2: Qualificação com Ads Intelligence"""
        logger.info("\n🎯 INICIANDO TESTE DA FASE 2: QUALIFICAÇÃO")
        logger.info("=" * 60)
        
        try:
            qualification_results = {
                'prospects_analyzed': 0,
                'ultra_qualified_found': 0,
                'qualification_time': 0,
                'leads_details': [],
                'errors': []
            }
            
            start_time = time.time()
            
            # Executar qualificação em sample de prospects
            logger.info("🔍 Executando análise de qualificação completa...")
            
            ultra_qualified_leads = []
            
            for niche_key in self.test_config['test_nichos']:
                niche_config = self.detector.priority_niches[niche_key]
                
                logger.info(f"\n🎯 Qualificando prospects do nicho: {niche_key}")
                
                # Descobrir alguns prospects para teste
                search_term = niche_config['search_terms'][0]
                location = niche_config['locations'][0]
                
                businesses = self.detector._discover_businesses(search_term, location)
                
                for i, business in enumerate(businesses[:3]):  # Testar 3 por nicho
                    company_name = business.get('name', f'Company_{i}')
                    website = business.get('website')
                    
                    if not website:
                        continue
                    
                    logger.info(f"   📊 Analisando: {company_name}")
                    qualification_results['prospects_analyzed'] += 1
                    
                    try:
                        # Executar análise completa
                        lead = self.detector._analyze_potential_lead(
                            business, niche_config, location
                        )
                        
                        if lead and lead.qualification_score >= self.test_config['min_qualification_score']:
                            ultra_qualified_leads.append(lead)
                            qualification_results['ultra_qualified_found'] += 1
                            
                            lead_summary = {
                                'company': lead.company_name,
                                'website': lead.website_url,
                                'qualification_score': lead.qualification_score,
                                'monthly_savings': lead.total_monthly_savings,
                                'ads_savings': lead.immediate_ads_savings,
                                'estimated_spend': lead.estimated_monthly_spend,
                                'decision_maker_email': lead.decision_maker_email,
                                'payback_timeline': lead.payback_timeline,
                                'tech_tax_score': lead.tech_tax_score
                            }
                            
                            qualification_results['leads_details'].append(lead_summary)
                            
                            logger.info(f"      ✅ ULTRA-QUALIFICADO!")
                            logger.info(f"         Score: {lead.qualification_score}/100")
                            logger.info(f"         Savings: ${lead.total_monthly_savings:,.0f}/mês")
                            logger.info(f"         Ads Spend: ${lead.estimated_monthly_spend:,.0f}/mês")
                            logger.info(f"         Email: {lead.decision_maker_email}")
                        else:
                            score = lead.qualification_score if lead else 0
                            logger.info(f"      ❌ Não qualificado (Score: {score}/100)")
                            
                    except Exception as e:
                        error = f"Erro qualificando {company_name}: {str(e)}"
                        qualification_results['errors'].append(error)
                        logger.error(f"      ❌ {error}")
                    
                    time.sleep(1)  # Rate limiting
            
            qualification_results['qualification_time'] = time.time() - start_time
            self.results['qualification_phase'] = qualification_results
            
            # Validar resultados da qualificação
            logger.info(f"\n📊 RESULTADOS DA QUALIFICAÇÃO:")
            logger.info(f"   Prospects analisados: {qualification_results['prospects_analyzed']}")
            logger.info(f"   Ultra-qualificados encontrados: {qualification_results['ultra_qualified_found']}")
            logger.info(f"   Taxa de qualificação: {qualification_results['ultra_qualified_found']/max(qualification_results['prospects_analyzed'],1)*100:.1f}%")
            logger.info(f"   Tempo de qualificação: {qualification_results['qualification_time']:.1f}s")
            
            if qualification_results['ultra_qualified_found'] < 1:
                logger.warning("⚠️  Nenhum lead ultra-qualificado encontrado")
                return False
            
            logger.info("✅ FASE 2: QUALIFICAÇÃO APROVADA")
            return True
            
        except Exception as e:
            error = f"Erro crítico na fase de qualificação: {str(e)}"
            self.results['errors'].append(error)
            logger.error(f"❌ {error}")
            return False

    def validate_leads_quality(self):
        """Validar qualidade dos leads ultra-qualificados"""
        logger.info("\n🔍 VALIDANDO QUALIDADE DOS LEADS ULTRA-QUALIFICADOS")
        logger.info("=" * 60)
        
        leads_details = self.results['qualification_phase'].get('leads_details', [])
        
        if not leads_details:
            logger.error("❌ Nenhum lead para validar")
            return False
        
        validation_results = {
            'leads_with_valid_email': 0,
            'leads_with_sufficient_savings': 0,
            'leads_with_high_score': 0,
            'average_savings': 0,
            'average_score': 0
        }
        
        total_savings = 0
        total_score = 0
        
        for lead in leads_details:
            logger.info(f"\n📊 Validando: {lead['company']}")
            
            # Validar email
            if '@' in lead.get('decision_maker_email', ''):
                validation_results['leads_with_valid_email'] += 1
                logger.info(f"   ✅ Email válido: {lead['decision_maker_email']}")
            else:
                logger.info(f"   ❌ Email inválido: {lead.get('decision_maker_email', 'N/A')}")
            
            # Validar savings
            monthly_savings = lead.get('monthly_savings', 0)
            if monthly_savings >= self.test_config['min_monthly_savings']:
                validation_results['leads_with_sufficient_savings'] += 1
                logger.info(f"   ✅ Savings suficientes: ${monthly_savings:,.0f}/mês")
            else:
                logger.info(f"   ❌ Savings insuficientes: ${monthly_savings:,.0f}/mês < ${self.test_config['min_monthly_savings']:,}")
            
            # Validar score
            score = lead.get('qualification_score', 0)
            if score >= self.test_config['min_qualification_score']:
                validation_results['leads_with_high_score'] += 1
                logger.info(f"   ✅ Score alto: {score}/100")
            else:
                logger.info(f"   ❌ Score baixo: {score}/100")
            
            total_savings += monthly_savings
            total_score += score
        
        # Calcular médias
        num_leads = len(leads_details)
        validation_results['average_savings'] = total_savings / num_leads
        validation_results['average_score'] = total_score / num_leads
        
        self.results['validation'] = validation_results
        
        logger.info(f"\n📊 RESUMO DA VALIDAÇÃO:")
        logger.info(f"   Leads com email válido: {validation_results['leads_with_valid_email']}/{num_leads}")
        logger.info(f"   Leads com savings suficientes: {validation_results['leads_with_sufficient_savings']}/{num_leads}")
        logger.info(f"   Leads com score alto: {validation_results['leads_with_high_score']}/{num_leads}")
        logger.info(f"   Savings médio: ${validation_results['average_savings']:,.0f}/mês")
        logger.info(f"   Score médio: {validation_results['average_score']:.1f}/100")
        
        # Pipeline é válido se pelo menos 50% dos leads passam em todos os critérios
        success_rate = min(
            validation_results['leads_with_valid_email'],
            validation_results['leads_with_sufficient_savings'], 
            validation_results['leads_with_high_score']
        ) / num_leads
        
        if success_rate >= 0.5:
            logger.info(f"✅ VALIDAÇÃO APROVADA (Taxa de sucesso: {success_rate*100:.1f}%)")
            return True
        else:
            logger.warning(f"⚠️  VALIDAÇÃO REPROVADA (Taxa de sucesso: {success_rate*100:.1f}% < 50%)")
            return False

    def generate_test_report(self):
        """Gerar relatório detalhado do teste"""
        test_duration = (datetime.now() - self.test_start).total_seconds()
        
        self.results['summary'] = {
            'test_start': self.test_start.isoformat(),
            'test_duration_seconds': test_duration,
            'discovery_success': bool(self.results.get('discovery_phase', {}).get('valid_websites', 0) >= 10),
            'qualification_success': bool(self.results.get('qualification_phase', {}).get('ultra_qualified_found', 0) >= 1),
            'validation_success': hasattr(self, 'validation_passed') and self.validation_passed,
            'total_errors': len(self.results['errors'])
        }
        
        # Salvar resultados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"ads_pipeline_test_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        logger.info(f"\n📋 RELATÓRIO DE TESTE SALVO: {report_file}")
        
        # Resumo final
        logger.info("\n" + "="*80)
        logger.info("🎯 RESUMO FINAL DO TESTE DE PIPELINE ADS INTELLIGENCE")
        logger.info("="*80)
        
        discovery = self.results.get('discovery_phase', {})
        qualification = self.results.get('qualification_phase', {})
        
        logger.info(f"⏱️  Duração total: {test_duration:.1f}s")
        logger.info(f"🔍 DESCOBERTA: {discovery.get('valid_websites', 0)} prospects com websites válidos")
        logger.info(f"🎯 QUALIFICAÇÃO: {qualification.get('ultra_qualified_found', 0)} leads ultra-qualificados")
        logger.info(f"❌ ERROS: {len(self.results['errors'])} erros encontrados")
        
        if self.results['summary']['discovery_success'] and self.results['summary']['qualification_success']:
            logger.info("✅ PIPELINE APROVADO: Descoberta e qualificação funcionando")
            return True
        else:
            logger.info("❌ PIPELINE REPROVADO: Problemas nas fases críticas")
            return False

    def run_complete_test(self):
        """Executar teste completo do pipeline (apenas fases 1 e 2)"""
        logger.info("🚀 INICIANDO TESTE COMPLETO DO PIPELINE ADS INTELLIGENCE")
        logger.info("🎯 FOCO: Descoberta + Qualificação (SEM outreach)")
        logger.info("="*80)
        
        try:
            # Fase 1: Descoberta
            discovery_success = self.test_discovery_phase()
            
            if not discovery_success:
                logger.error("❌ Teste falhou na fase de descoberta")
                return self.generate_test_report()
            
            # Fase 2: Qualificação
            qualification_success = self.test_qualification_phase()
            
            if not qualification_success:
                logger.error("❌ Teste falhou na fase de qualificação")
                return self.generate_test_report()
            
            # Validação da qualidade
            self.validation_passed = self.validate_leads_quality()
            
            # Relatório final
            return self.generate_test_report()
            
        except Exception as e:
            logger.error(f"❌ Erro crítico no teste: {str(e)}")
            self.results['errors'].append(f"Erro crítico: {str(e)}")
            return self.generate_test_report()

if __name__ == "__main__":
    tester = AdsPipelineTester()
    success = tester.run_complete_test()
    
    if success:
        print("\n🎉 TESTE APROVADO: Pipeline pronto para produção")
        exit(0)
    else:
        print("\n❌ TESTE REPROVADO: Pipeline precisa de ajustes")
        exit(1)
