import pytest

from src.core.arco_engine import ARCOEngine
from src.connectors.google_pagespeed_api import GooglePageSpeedAPI


class DummyPageSpeedAPI:
    def get_page_speed_score(self, url: str, strategy: str = "mobile"):
        return {"score": 90}


def test_analyze_saas_costs(monkeypatch):
    monkeypatch.setattr(GooglePageSpeedAPI, "__init__", lambda self: None)
    monkeypatch.setattr(GooglePageSpeedAPI, "get_page_speed_score", lambda self, url, strategy="mobile": {"score": 90})
    engine = ARCOEngine()
    result = engine.analyze_saas_costs({'name': 'TestCo', 'saas_spend': 1000, 'employee_count': 20})
    assert result['category'] == 'SaaS Cost Optimization'
    assert 'potential_monthly_savings' in result
    assert result['potential_monthly_savings'] > 0
    assert len(result['recommendations']) > 0


def test_generate_optimization_insights(monkeypatch):
    monkeypatch.setattr(GooglePageSpeedAPI, "__init__", lambda self: None)
    monkeypatch.setattr(GooglePageSpeedAPI, "get_page_speed_score", lambda self, url, strategy="mobile": {"score": 90})
    engine = ARCOEngine()

    monkeypatch.setattr(
        engine,
        'analyze_website_performance',
        lambda url: {
            'category': 'Website Performance Improvement',
            'performance_score': 80,
            'details': 'ok',
            'business_impact': {'priority': 'medium'}
        }
    )

    insights = engine.generate_optimization_insights(
        'TestCo', 'https://example.com', saas_spend=1000, employee_count=20, industry='tech'
    )
    assert insights['company'] == 'TestCo'
    assert insights['industry'] == 'tech'
    assert len(insights['insights']) >= 2
    assert 'business_impact' in insights
    assert 'executive_summary' in insights
    
    # Check SaaS insight structure
    saas_insight = insights['insights'][0]
    assert saas_insight['category'] == 'SaaS Cost Optimization'
    assert 'potential_monthly_savings' in saas_insight
