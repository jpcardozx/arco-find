#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ARCO API Integration Engine - Validação com APIs Gratuitas
Integra múltiplas APIs gratuitas para validar problemas identificados
"""

import requests
import json
import time
from datetime import datetime
from urllib.parse import urlparse
import subprocess

class APIValidationEngine:
    """Engine que integra APIs gratuitas para validar problemas técnicos"""
    
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.domain = urlparse(target_url).netloc
        self.validation_results = {}
        
    def run_api_validations(self) -> dict:
        """Executa validações usando APIs gratuitas"""
        
        print("🔍 ARCO API VALIDATION ENGINE")
        print(f"Target: {self.target_url}")
        print("=" * 60)
        
        results = {
            'target_url': self.target_url,
            'validation_date': datetime.now().isoformat(),
            'api_validations': {},
            'consolidated_issues': [],
            'validation_summary': {}
        }
        
        # 1. PageSpeed Insights API (Google)
        print("\n📊 1. GOOGLE PAGESPEED INSIGHTS VALIDATION")
        pagespeed_data = self._validate_with_pagespeed()
        results['api_validations']['pagespeed_insights'] = pagespeed_data
        
        # 2. SSL Labs API
        print("\n🔒 2. SSL LABS VALIDATION") 
        ssl_data = self._validate_with_ssl_labs()
        results['api_validations']['ssl_labs'] = ssl_data
        
        # 3. Lighthouse Performance (via PageSpeed)
        print("\n🏆 3. LIGHTHOUSE METRICS VALIDATION")
        lighthouse_data = self._extract_lighthouse_metrics(pagespeed_data)
        results['api_validations']['lighthouse'] = lighthouse_data
        
        # 4. DNS/Network Analysis
        print("\n🌐 4. DNS & NETWORK VALIDATION")
        network_data = self._validate_network_performance()
        results['api_validations']['network'] = network_data
        
        # 5. Consolidate issues with API evidence
        results['consolidated_issues'] = self._consolidate_api_issues(results['api_validations'])
        
        # 6. Validation summary
        results['validation_summary'] = self._create_validation_summary(results)
        
        return results
    
    def _validate_with_pagespeed(self) -> dict:
        """Valida performance usando Google PageSpeed Insights API"""
        
        pagespeed_data = {
            'api_used': 'Google PageSpeed Insights',
            'status': 'error',
            'core_web_vitals': {},
            'performance_score': 0,
            'opportunities': [],
            'diagnostics': []
        }
        
        try:
            # API Key não necessária para uso básico
            api_url = f"https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                'url': self.target_url,
                'strategy': 'mobile',  # mobile first
                'category': 'performance',
                'locale': 'pt_BR'
            }
            
            print("  📡 Calling Google PageSpeed API...")
            response = requests.get(api_url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract performance score
                lighthouse_result = data.get('lighthouseResult', {})
                categories = lighthouse_result.get('categories', {})
                performance = categories.get('performance', {})
                
                pagespeed_data['status'] = 'success'
                pagespeed_data['performance_score'] = int(performance.get('score', 0) * 100)
                
                # Extract Core Web Vitals
                audits = lighthouse_result.get('audits', {})
                
                # First Contentful Paint
                fcp = audits.get('first-contentful-paint', {})
                pagespeed_data['core_web_vitals']['first_contentful_paint'] = {
                    'value': fcp.get('numericValue', 0) / 1000,  # Convert to seconds
                    'score': fcp.get('score', 0)
                }
                
                # Largest Contentful Paint  
                lcp = audits.get('largest-contentful-paint', {})
                pagespeed_data['core_web_vitals']['largest_contentful_paint'] = {
                    'value': lcp.get('numericValue', 0) / 1000,
                    'score': lcp.get('score', 0)
                }
                
                # Cumulative Layout Shift
                cls = audits.get('cumulative-layout-shift', {})
                pagespeed_data['core_web_vitals']['cumulative_layout_shift'] = {
                    'value': cls.get('numericValue', 0),
                    'score': cls.get('score', 0)
                }
                
                # Speed Index
                si = audits.get('speed-index', {})
                pagespeed_data['core_web_vitals']['speed_index'] = {
                    'value': si.get('numericValue', 0) / 1000,
                    'score': si.get('score', 0)
                }
                
                # Extract opportunities (top 5)
                opportunities = lighthouse_result.get('audits', {})
                opportunity_list = []
                
                key_opportunities = [
                    'unused-css-rules',
                    'uses-webp-images', 
                    'efficient-animated-content',
                    'offscreen-images',
                    'unminified-css',
                    'unminified-javascript',
                    'uses-text-compression'
                ]
                
                for opp_key in key_opportunities:
                    if opp_key in opportunities:
                        opp = opportunities[opp_key]
                        if opp.get('score', 1) < 0.9:  # Issues with score < 0.9
                            opportunity_list.append({
                                'id': opp_key,
                                'title': opp.get('title', ''),
                                'description': opp.get('description', ''),
                                'potential_savings': opp.get('numericValue', 0),
                                'score': opp.get('score', 0)
                            })
                
                pagespeed_data['opportunities'] = opportunity_list[:5]  # Top 5
                
                print(f"  ✅ PageSpeed Score: {pagespeed_data['performance_score']}/100")
                print(f"  📊 Core Web Vitals extracted: {len(pagespeed_data['core_web_vitals'])} metrics")
                print(f"  🎯 Opportunities found: {len(pagespeed_data['opportunities'])}")
                
            else:
                pagespeed_data['error'] = f"API call failed: {response.status_code}"
                print(f"  ❌ PageSpeed API failed: {response.status_code}")
                
        except Exception as e:
            pagespeed_data['error'] = str(e)
            print(f"  ❌ PageSpeed validation error: {e}")
        
        return pagespeed_data
    
    def _validate_with_ssl_labs(self) -> dict:
        """Valida SSL usando SSL Labs API"""
        
        ssl_data = {
            'api_used': 'Qualys SSL Labs',
            'status': 'error',
            'grade': '',
            'issues': [],
            'certificate_info': {}
        }
        
        try:
            # SSL Labs API - free but has rate limits
            api_url = "https://api.ssllabs.com/api/v3/analyze"
            params = {
                'host': self.domain,
                'publish': 'off',
                'startNew': 'off',
                'all': 'done'
            }
            
            print(f"  📡 Calling SSL Labs API for {self.domain}...")
            
            # First call to start analysis
            response = requests.get(api_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status', '')
                
                if status == 'READY':
                    # Analysis complete
                    endpoints = data.get('endpoints', [])
                    if endpoints:
                        endpoint = endpoints[0]  # Take first endpoint
                        
                        ssl_data['status'] = 'success'
                        ssl_data['grade'] = endpoint.get('grade', 'Unknown')
                        
                        # Certificate details
                        cert_info = endpoint.get('details', {}).get('cert', {})
                        ssl_data['certificate_info'] = {
                            'subject': cert_info.get('subject', ''),
                            'issuer': cert_info.get('issuerLabel', ''),
                            'valid_from': cert_info.get('notBefore', 0),
                            'valid_to': cert_info.get('notAfter', 0)
                        }
                        
                        # Check for common issues
                        grade = ssl_data['grade']
                        if grade in ['C', 'D', 'F']:
                            ssl_data['issues'].append(f"SSL Grade {grade} - security issues detected")
                        
                        print(f"  ✅ SSL Grade: {ssl_data['grade']}")
                        
                elif status in ['DNS', 'IN_PROGRESS']:
                    ssl_data['status'] = 'in_progress'
                    ssl_data['message'] = 'SSL analysis in progress, try again later'
                    print("  ⏳ SSL analysis in progress...")
                    
                else:
                    ssl_data['status'] = 'error'
                    ssl_data['error'] = f"SSL Labs status: {status}"
                    print(f"  ⚠️ SSL Labs status: {status}")
                    
            else:
                ssl_data['error'] = f"SSL Labs API error: {response.status_code}"
                print(f"  ❌ SSL Labs API failed: {response.status_code}")
                
        except Exception as e:
            ssl_data['error'] = str(e)
            print(f"  ❌ SSL validation error: {e}")
        
        return ssl_data
    
    def _extract_lighthouse_metrics(self, pagespeed_data: dict) -> dict:
        """Extrai métricas específicas do Lighthouse"""
        
        lighthouse = {
            'performance_breakdown': {},
            'accessibility_score': 0,
            'best_practices_score': 0,
            'seo_score': 0,
            'critical_issues': []
        }
        
        if pagespeed_data.get('status') == 'success':
            # Performance score already extracted
            lighthouse['performance_score'] = pagespeed_data.get('performance_score', 0)
            
            # Core Web Vitals analysis
            cwv = pagespeed_data.get('core_web_vitals', {})
            
            # Identify critical issues based on Google thresholds
            lcp_value = cwv.get('largest_contentful_paint', {}).get('value', 0)
            if lcp_value > 2.5:  # Google's "needs improvement" threshold
                lighthouse['critical_issues'].append({
                    'metric': 'Largest Contentful Paint',
                    'value': f"{lcp_value:.2f}s",
                    'threshold': '2.5s',
                    'status': 'needs_improvement',
                    'impact': 'Users may perceive the page as slow to load'
                })
            
            fcp_value = cwv.get('first_contentful_paint', {}).get('value', 0)
            if fcp_value > 1.8:
                lighthouse['critical_issues'].append({
                    'metric': 'First Contentful Paint',
                    'value': f"{fcp_value:.2f}s", 
                    'threshold': '1.8s',
                    'status': 'needs_improvement',
                    'impact': 'Page appears to load slowly to users'
                })
            
            cls_value = cwv.get('cumulative_layout_shift', {}).get('value', 0)
            if cls_value > 0.1:
                lighthouse['critical_issues'].append({
                    'metric': 'Cumulative Layout Shift',
                    'value': f"{cls_value:.3f}",
                    'threshold': '0.1',
                    'status': 'needs_improvement', 
                    'impact': 'Page elements shift unexpectedly during load'
                })
            
            print(f"  📊 Lighthouse critical issues: {len(lighthouse['critical_issues'])}")
            
        return lighthouse
    
    def _validate_network_performance(self) -> dict:
        """Valida performance de rede usando ferramentas básicas"""
        
        network = {
            'dns_resolution': {},
            'connection_time': {},
            'response_analysis': {}
        }
        
        try:
            # DNS resolution time
            import socket
            start_time = time.time()
            socket.gethostbyname(self.domain)
            dns_time = time.time() - start_time
            
            network['dns_resolution'] = {
                'time_seconds': round(dns_time, 3),
                'status': 'fast' if dns_time < 0.1 else 'slow' if dns_time > 0.5 else 'acceptable'
            }
            
            # HTTP response analysis
            start_time = time.time()
            response = requests.get(self.target_url, timeout=10)
            total_time = time.time() - start_time
            
            network['response_analysis'] = {
                'total_time_seconds': round(total_time, 3),
                'status_code': response.status_code,
                'headers_size': len(str(response.headers)),
                'content_size': len(response.content),
                'compression': 'gzip' in response.headers.get('content-encoding', ''),
                'cache_control': response.headers.get('cache-control', 'none')
            }
            
            print(f"  ✅ DNS resolution: {dns_time:.3f}s")
            print(f"  ✅ Total response time: {total_time:.3f}s")
            
        except Exception as e:
            network['error'] = str(e)
            print(f"  ❌ Network validation error: {e}")
        
        return network
    
    def _consolidate_api_issues(self, api_results: dict) -> list:
        """Consolida issues validados por APIs com evidências específicas"""
        
        consolidated = []
        
        # PageSpeed Issues
        pagespeed = api_results.get('pagespeed_insights', {})
        if pagespeed.get('status') == 'success':
            score = pagespeed.get('performance_score', 0)
            
            if score < 50:
                consolidated.append({
                    'category': 'Performance',
                    'severity': 'critical',
                    'issue': f"Performance Score Crítico: {score}/100",
                    'api_evidence': 'Google PageSpeed Insights',
                    'api_data': {'score': score, 'source': 'Google Official API'},
                    'impact': 'Site lento prejudica conversão e SEO',
                    'cost_estimate': 'R$ 3.000-8.000/mês em vendas perdidas'
                })
            elif score < 70:
                consolidated.append({
                    'category': 'Performance', 
                    'severity': 'high',
                    'issue': f"Performance Score Baixo: {score}/100",
                    'api_evidence': 'Google PageSpeed Insights',
                    'api_data': {'score': score, 'source': 'Google Official API'},
                    'impact': 'Performance abaixo da média afeta UX',
                    'cost_estimate': 'R$ 1.500-4.000/mês em performance perdida'
                })
            
            # Core Web Vitals issues
            cwv = pagespeed.get('core_web_vitals', {})
            lcp = cwv.get('largest_contentful_paint', {})
            if lcp.get('value', 0) > 2.5:
                consolidated.append({
                    'category': 'Core Web Vitals',
                    'severity': 'high',
                    'issue': f"LCP muito alto: {lcp.get('value', 0):.2f}s",
                    'api_evidence': 'Google PageSpeed Insights - Official Core Web Vitals',
                    'api_data': {'lcp_seconds': lcp.get('value', 0), 'threshold': 2.5},
                    'impact': 'Google penaliza sites com LCP > 2.5s no ranking',
                    'cost_estimate': 'R$ 2.000-5.000/mês em tráfego orgânico perdido'
                })
            
            # Opportunities from API
            opportunities = pagespeed.get('opportunities', [])
            for opp in opportunities[:3]:  # Top 3 opportunities
                if opp.get('potential_savings', 0) > 1000:  # >1s savings
                    savings_s = opp.get('potential_savings', 0) / 1000
                    consolidated.append({
                        'category': 'Performance Optimization',
                        'severity': 'medium',
                        'issue': f"{opp.get('title', '')}: {savings_s:.1f}s savings potential",
                        'api_evidence': 'Google PageSpeed Insights - Optimization Opportunities',
                        'api_data': {'savings_ms': opp.get('potential_savings', 0), 'score': opp.get('score', 0)},
                        'impact': opp.get('description', ''),
                        'cost_estimate': 'R$ 500-1.500/mês em performance perdida'
                    })
        
        # SSL Issues
        ssl = api_results.get('ssl_labs', {})
        if ssl.get('status') == 'success':
            grade = ssl.get('grade', '')
            if grade in ['C', 'D', 'F']:
                consolidated.append({
                    'category': 'Security',
                    'severity': 'critical',
                    'issue': f"SSL Grade Ruim: {grade}",
                    'api_evidence': 'Qualys SSL Labs - Industry Standard',
                    'api_data': {'ssl_grade': grade, 'issues': ssl.get('issues', [])},
                    'impact': 'SSL fraco prejudica confiança e SEO',
                    'cost_estimate': 'Risco de perda de confiança e vendas'
                })
        
        # Lighthouse Issues
        lighthouse = api_results.get('lighthouse', {})
        critical_issues = lighthouse.get('critical_issues', [])
        for issue in critical_issues:
            consolidated.append({
                'category': 'User Experience',
                'severity': 'high',
                'issue': f"{issue.get('metric', '')}: {issue.get('value', '')} (threshold: {issue.get('threshold', '')})",
                'api_evidence': 'Google Lighthouse - Official UX Metrics',
                'api_data': issue,
                'impact': issue.get('impact', ''),
                'cost_estimate': 'R$ 1.000-3.000/mês em UX prejudicada'
            })
        
        print(f"📊 Consolidated {len(consolidated)} API-validated issues")
        
        return consolidated
    
    def _create_validation_summary(self, results: dict) -> dict:
        """Cria resumo das validações com APIs"""
        
        api_validations = results.get('api_validations', {})
        consolidated_issues = results.get('consolidated_issues', [])
        
        summary = {
            'apis_used': len(api_validations),
            'successful_validations': sum(1 for api in api_validations.values() if api.get('status') == 'success'),
            'total_validated_issues': len(consolidated_issues),
            'issues_by_severity': {
                'critical': len([i for i in consolidated_issues if i.get('severity') == 'critical']),
                'high': len([i for i in consolidated_issues if i.get('severity') == 'high']),
                'medium': len([i for i in consolidated_issues if i.get('severity') == 'medium'])
            },
            'api_credibility': {
                'google_pagespeed': api_validations.get('pagespeed_insights', {}).get('status') == 'success',
                'ssl_labs': api_validations.get('ssl_labs', {}).get('status') == 'success',
                'lighthouse_metrics': len(api_validations.get('lighthouse', {}).get('critical_issues', [])) > 0
            }
        }
        
        return summary

def main():
    """Executa validações com APIs para OJambu"""
    
    print("🚀 ARCO API VALIDATION ENGINE")
    print("Validating technical issues with authoritative APIs")
    print("=" * 60)
    
    validator = APIValidationEngine("https://ojambubags.com.br/")
    
    # Run API validations
    validation_results = validator.run_api_validations()
    
    # Export results
    output_file = f"results/ojambu_api_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(validation_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 API Validation Results: {output_file}")
    
    # Summary
    summary = validation_results['validation_summary']
    print(f"\n📊 VALIDATION SUMMARY:")
    print(f"• APIs Used: {summary['apis_used']}")
    print(f"• Successful Validations: {summary['successful_validations']}")
    print(f"• Total Validated Issues: {summary['total_validated_issues']}")
    print(f"• Critical Issues: {summary['issues_by_severity']['critical']}")
    print(f"• High Priority Issues: {summary['issues_by_severity']['high']}")
    
    print(f"\n✅ API VALIDATION COMPLETE")

if __name__ == "__main__":
    main()
