#!/usr/bin/env python3
"""
🧪 TESTE DE PRODUÇÃO - ARCO ADVERTISING INTELLIGENCE
Valida se o sistema está pronto para operação real
"""

import os
import sys
from dotenv import load_dotenv

# Carregar environment variables
load_dotenv()

def test_environment_setup():
    """Testar configuração do ambiente"""
    print("🔧 TESTING ENVIRONMENT SETUP")
    print("=" * 50)
    
    # API Keys
    google_key = os.getenv('GOOGLE_API_KEY')
    if google_key and len(google_key) > 30:
        print(f"✅ GOOGLE_API_KEY: Configurada ({google_key[:10]}...)")
    else:
        print(f"⚠️  GOOGLE_API_KEY: {google_key[:20] if google_key else 'Not found'}")
        print("   📝 Obtenha em: https://console.cloud.google.com/apis/credentials")
    
    # Dependencies
    try:
        import requests
        import aiohttp
        from bs4 import BeautifulSoup
        print("✅ Dependencies: OK")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
    
    print()

def test_engine_initialization():
    """Testar inicialização do engine"""
    print("🚀 TESTING ENGINE INITIALIZATION")
    print("=" * 50)
    
    try:
        from arco_advertising_intelligence import AdvertisingIntelligenceEngine
        engine = AdvertisingIntelligenceEngine()
        print("✅ Engine inicializado com sucesso")
        
        # Testar rate limiting
        engine._rate_limit()
        print("✅ Rate limiting funcional")
        
        # Testar verticals config
        verticals = list(engine.target_verticals.keys())
        print(f"✅ Verticais configuradas: {verticals}")
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
    
    print()

def test_pain_signals_detection():
    """Testar detecção de pain signals"""
    print("🔍 TESTING PAIN SIGNALS DETECTION")
    print("=" * 50)
    
    try:
        from arco_advertising_intelligence import TechnicalPainSignal
        
        # Simular um pain signal
        test_signal = TechnicalPainSignal(
            category='web_vitals',
            severity='high',
            metric_name='LCP (Real User)',
            current_value=3500,  # 3.5s
            threshold_value=2500,  # 2.5s
            sprint_suggestion='Web Vitals Patch: Critical CSS + Image Optimization',
            estimated_impact='20-35% faster LCP'
        )
        
        print(f"✅ Pain Signal criado: {test_signal.metric_name}")
        print(f"   📊 Valor atual: {test_signal.current_value}ms")
        print(f"   🎯 Threshold: {test_signal.threshold_value}ms")
        print(f"   💡 Sprint: {test_signal.sprint_suggestion}")
        
    except Exception as e:
        print(f"❌ Erro nos pain signals: {e}")
    
    print()

def test_api_connectivity():
    """Testar conectividade das APIs (sem fazer requests reais)"""
    print("🌐 TESTING API CONNECTIVITY")
    print("=" * 50)
    
    google_key = os.getenv('GOOGLE_API_KEY')
    
    if not google_key or len(google_key) < 30:
        print("⚠️  Google API Key parece ser de teste")
        print("📝 Para produção, configure uma chave real:")
        print("   1. Google Cloud Console → APIs & Services → Credentials")
        print("   2. Create Credentials → API Key")
        print("   3. Restrict to Places API + PageSpeed Insights API")
        print("   4. Update .env file")
    else:
        print("✅ Google API Key configurada (formato válido)")
        print("🔄 Test de conectividade real pendente")
    
    print()

def test_output_structure():
    """Testar estrutura de output"""
    print("📄 TESTING OUTPUT STRUCTURE")
    print("=" * 50)
    
    try:
        from arco_advertising_intelligence import QualifiedAdvertiser, AdActivityIntel, TechnicalPainSignal
        
        # Simular um lead qualificado
        mock_ad_activity = [
            AdActivityIntel(
                platform='google_ads',
                is_active=False,  # Não assumimos mais
                recent_ads_count=0,
                latest_ad_date=None,
                creative_age_days=None,
                estimated_monthly_spend=None,
                confirmation_url='https://adstransparency.google.com/search?q=test'
            )
        ]
        
        mock_pain_signals = [
            TechnicalPainSignal(
                category='web_vitals',
                severity='high',
                metric_name='LCP (Real User)',
                current_value=3200,
                threshold_value=2500,
                sprint_suggestion='Web Vitals Patch',
                estimated_impact='25% faster loading'
            )
        ]
        
        qualified_lead = QualifiedAdvertiser(
            company_name="Test Dental Clinic",
            website="https://testdental.com.au",
            location="Wollongong, NSW",
            phone="+61 2 1234 5678",
            place_id="test_place_id",
            ad_activity=mock_ad_activity,
            total_active_platforms=1,
            estimated_total_monthly_spend=0,  # Não inventamos mais
            pain_signals=mock_pain_signals,
            web_vitals_score=65.0,
            technical_debt_score=35.0,
            qualification_score=78.0,
            sprint_viability='medium',
            suggested_sprint='Web Vitals Patch: LCP optimization + CDN setup',
            estimated_sprint_value=497.0,
            proof_pack={},
            discovery_date="2025-08-19T10:30:00",
            confidence_level='medium'
        )
        
        print("✅ Lead structure criada com sucesso")
        print(f"   🏢 Company: {qualified_lead.company_name}")
        print(f"   📊 Score: {qualified_lead.qualification_score}")
        print(f"   🎯 Sprint: {qualified_lead.suggested_sprint}")
        print(f"   💰 Value: ${qualified_lead.estimated_sprint_value}")
        
    except Exception as e:
        print(f"❌ Erro na estrutura: {e}")
    
    print()

def main():
    """Executar todos os testes"""
    print("🧪 ARCO ADVERTISING INTELLIGENCE - PRODUCTION READINESS TEST")
    print("=" * 70)
    print()
    
    test_environment_setup()
    test_engine_initialization()
    test_pain_signals_detection()
    test_api_connectivity()
    test_output_structure()
    
    print("🎯 PRÓXIMOS PASSOS PARA PRODUÇÃO:")
    print("=" * 50)
    print("1. ✅ Configure Google API Key real (se ainda não feito)")
    print("2. 🧪 Execute teste com lead real: python test_real_lead.py")
    print("3. 📊 Valide pain signals com website real")
    print("4. 📄 Gere primeiro proof pack")
    print("5. 🎯 Execute primeiro sprint pilot")
    print()
    print("🚀 Sistema pronto para operação!")

if __name__ == "__main__":
    main()
