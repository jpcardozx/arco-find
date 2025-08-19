#!/usr/bin/env python3
"""
🧪 TESTE RÁPIDO COM WEBSITE REAL
"""

from dotenv import load_dotenv
load_dotenv()

from arco_advertising_intelligence import AdvertisingIntelligenceEngine

def main():
    engine = AdvertisingIntelligenceEngine()
    
    # Website dental real de Wollongong  
    test_website = 'https://www.dentalcarewollongong.com.au'
    
    print(f'🔍 Testando: {test_website}')
    print('⏳ Analisando pain signals...')
    
    try:
        pain_signals, tech_score = engine.analyze_technical_pain_signals(test_website)
        
        print(f'\n📊 RESULTADOS:')
        print(f'   Technical Score: {tech_score:.1f}/100')
        print(f'   Pain Signals encontrados: {len(pain_signals)}')
        
        if pain_signals:
            print(f'\n🚨 PAIN SIGNALS DETECTADOS:')
            for i, signal in enumerate(pain_signals[:3], 1):
                print(f'   {i}. {signal.metric_name}')
                print(f'      📈 Valor: {signal.current_value} (threshold: {signal.threshold_value})')
                print(f'      🎯 Sprint: {signal.sprint_suggestion}')
                print(f'      🚨 Severidade: {signal.severity}')
                print()
        
        # Calcular qualification score
        engine._current_pain_signals = pain_signals
        score = engine._calculate_qualification_score(
            active_platforms=2,  # Simular 2 plataformas verificadas
            monthly_spend=0,
            high_severity_signals=len([s for s in pain_signals if s.severity == 'high']),
            technical_score=tech_score
        )
        
        print(f'🎯 QUALIFICATION SCORE: {score:.1f}/100')
        
        if score >= 70:
            print(f'✅ LEAD QUALIFICADO - Sprint viable!')
            print(f'💰 Estimated sprint value: $497 AUD')
        else:
            print(f'⚠️  Below qualification threshold')
        
        print(f'\n🚀 SISTEMA FUNCIONANDO COM DADOS REAIS!')
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
