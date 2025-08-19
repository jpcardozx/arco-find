#!/usr/bin/env python3
"""
🧪 TESTE REAL LEAD - ARCO ADVERTISING INTELLIGENCE  
Teste com website real para validar detecção de pain signals
"""

import os
import sys
from dotenv import load_dotenv

# Carregar environment variables
load_dotenv()

def test_real_website_analysis():
    """Testar análise de website real"""
    print("🔍 TESTING REAL WEBSITE ANALYSIS")
    print("=" * 50)
    
    try:
        from arco_advertising_intelligence import AdvertisingIntelligenceEngine
        engine = AdvertisingIntelligenceEngine()
        
        # Website de teste real (escolher um que provavelmente tem pain signals)
        test_website = "https://dentistryonline.com.au"  # Dental site australiano
        
        print(f"🌐 Analisando: {test_website}")
        print("⏳ Detectando pain signals...")
        
        # Analisar pain signals
        pain_signals, technical_score = engine.analyze_technical_pain_signals(test_website)
        
        print(f"\n📊 RESULTADOS:")
        print(f"   Technical Score: {technical_score:.1f}/100")
        print(f"   Pain Signals encontrados: {len(pain_signals)}")
        
        if pain_signals:
            print(f"\n🔧 PAIN SIGNALS DETECTADOS:")
            for i, signal in enumerate(pain_signals[:5], 1):  # Top 5
                print(f"   {i}. {signal.metric_name}")
                print(f"      📈 Valor: {signal.current_value} (threshold: {signal.threshold_value})")
                print(f"      🎯 Sprint: {signal.sprint_suggestion}")
                print(f"      🚨 Severidade: {signal.severity}")
                print()
        
        # Verificar se há signals críticos para sprint
        high_severity = [s for s in pain_signals if s.severity == 'high']
        web_vitals_issues = [s for s in pain_signals if s.category == 'web_vitals']
        
        print(f"🎯 QUALIFICATION ANALYSIS:")
        print(f"   High severity issues: {len(high_severity)}")
        print(f"   Web Vitals issues: {len(web_vitals_issues)}")
        
        if high_severity and web_vitals_issues:
            print(f"   ✅ SPRINT VIABLE - Pain signals detectados")
            print(f"   💰 Estimated sprint value: $497 AUD")
        else:
            print(f"   ⚠️  LIMITED SPRINT POTENTIAL - Poucos pain signals")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
        print(f"💡 Dica: Verifique se tem conexão com internet")
        return False

def test_ad_verification_links():
    """Testar geração de links de verificação"""
    print("\n🔗 TESTING AD VERIFICATION LINKS")
    print("=" * 50)
    
    try:
        from arco_advertising_intelligence import AdvertisingIntelligenceEngine
        engine = AdvertisingIntelligenceEngine()
        
        test_company = "Sydney Dental Clinic"
        test_domain = "sydneydental.com.au"
        
        print(f"🏢 Company: {test_company}")
        print(f"🌐 Domain: {test_domain}")
        
        # Gerar links de verificação
        google_ads = engine._check_google_ads_transparency(test_company)
        meta_ads = engine._check_meta_ad_library(test_company)
        tiktok_ads = engine._check_tiktok_creative_center(test_company)
        
        print(f"\n🔍 VERIFICATION LINKS GERADOS:")
        print(f"   Google ATC: {google_ads.confirmation_url}")
        print(f"   Meta Library: {meta_ads.confirmation_url}")
        print(f"   TikTok Center: {tiktok_ads.confirmation_url}")
        
        print(f"\n✅ Links gerados com sucesso!")
        print(f"💡 Para produção: abrir links e verificar anúncios ativos manualmente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na geração de links: {e}")
        return False

def test_qualification_scoring():
    """Testar sistema de scoring"""
    print("\n📊 TESTING QUALIFICATION SCORING")
    print("=" * 50)
    
    try:
        from arco_advertising_intelligence import AdvertisingIntelligenceEngine, TechnicalPainSignal
        engine = AdvertisingIntelligenceEngine()
        
        # Simular pain signals realistas
        mock_pain_signals = [
            TechnicalPainSignal(
                category='web_vitals',
                severity='high',
                metric_name='LCP (Real User)',
                current_value=3200,  # 3.2s > 2.5s threshold
                threshold_value=2500,
                sprint_suggestion='Web Vitals Patch: Critical CSS + Image Optimization',
                estimated_impact='25% faster LCP'
            ),
            TechnicalPainSignal(
                category='tracking',
                severity='high',
                metric_name='WhatsApp Links Without UTM',
                current_value=2,
                threshold_value=0,
                sprint_suggestion='Tracking Sane: WhatsApp UTM + Click Attribution',
                estimated_impact='Clear WhatsApp conversion tracking'
            ),
            TechnicalPainSignal(
                category='forms',
                severity='medium',
                metric_name='Form Validation Missing',
                current_value=0,
                threshold_value=1,
                sprint_suggestion='Leadflow Rescue: Form Validation + UX Optimization',
                estimated_impact='25-40% reduction in form abandonment'
            )
        ]
        
        # Simular pain signals context
        engine._current_pain_signals = mock_pain_signals
        
        # Testar scoring com diferentes cenários
        scenarios = [
            {"platforms": 2, "name": "High (2+ platforms + field data)"},
            {"platforms": 1, "name": "Medium (1 platform + some issues)"},
            {"platforms": 0, "name": "Low (no verification links)"}
        ]
        
        print("🎯 SCORING SCENARIOS:")
        for scenario in scenarios:
            score = engine._calculate_qualification_score(
                active_platforms=scenario["platforms"],
                monthly_spend=0,  # Não usamos mais
                high_severity_signals=2,
                technical_score=65.0
            )
            
            viability = 'HIGH' if score >= 85 else 'MEDIUM' if score >= 70 else 'LOW'
            status = '✅ QUALIFICA' if score >= 70 else '❌ NÃO QUALIFICA'
            
            print(f"   {scenario['name']}: {score:.1f}/100 - {viability} - {status}")
        
        print(f"\n📋 SCORING BREAKDOWN:")
        print(f"   40pts: Ad verification (2+ platforms = 40, 1 = 25)")
        print(f"   35pts: Web Vitals field data (LCP >2.5s, INP >400ms)")
        print(f"   15pts: Attribution issues (GA4, Pixel, WhatsApp UTM)")
        print(f"   10pts: Life signals (reviews, phone, website)")
        print(f"   Threshold: ≥70pts para qualificar")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no scoring: {e}")
        return False

def main():
    """Executar testes com dados reais"""
    print("🧪 ARCO REAL LEAD TESTING")
    print("=" * 70)
    
    google_key = os.getenv('GOOGLE_API_KEY')
    if not google_key or google_key == 'test_key':
        print("⚠️  AVISO: Usando API key de teste")
        print("📝 Para testes reais, configure Google API Key válida")
        print("=" * 50)
    
    # Executar testes
    results = []
    results.append(test_real_website_analysis())
    results.append(test_ad_verification_links())
    results.append(test_qualification_scoring())
    
    # Resumo final
    print("=" * 70)
    print("📊 RESUMO DOS TESTES:")
    
    test_names = [
        "Website Analysis",
        "Ad Verification Links", 
        "Qualification Scoring"
    ]
    
    for i, (name, result) in enumerate(zip(test_names, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {i+1}. {name}: {status}")
    
    passed = sum(results)
    total = len(results)
    
    print(f"\n🎯 RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🚀 SISTEMA PRONTO PARA PRODUÇÃO!")
        print("\n📋 PRÓXIMOS PASSOS:")
        print("   1. Configure Google API Key real")
        print("   2. Teste com lead australiano real")
        print("   3. Gere primeiro proof pack")
        print("   4. Execute sprint pilot")
    else:
        print("🔧 AJUSTES NECESSÁRIOS antes da produção")

if __name__ == "__main__":
    main()
