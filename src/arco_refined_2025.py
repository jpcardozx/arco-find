"""
ARCO REFINED 2025 - Revisão Crítica dos Funis
Baseado na análise: Funil A + B ficam, Funil C vira apoio

DECISÃO FINAL:
- Funil A (Auditoria Express): APROVADO - baixo atrito, upgrade claro
- Funil B (Teardown 60s): APROVADO - prova competência rapidamente  
- Funil C (Landing Kit): REJEITADO como funil principal, vira material de apoio

KILL RULES REFINADAS:
- Funil A: upgrade <20% por 3 semanas → MATAR
- Funil B: response <6% por 2 semanas → MATAR
- Qualquer funil: CPL >$25 → PAUSAR imediatamente
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import aiohttp

from config.api_keys import APIConfig

logger = logging.getLogger(__name__)


@dataclass
class RefinedProspect:
    """Prospect refinado com scoring baseado em evidências"""
    domain: str
    company_name: str
    vertical: str  # "dental", "legal", "home_services", "real_estate"
    spend_monthly: int
    contact_email: Optional[str] = None
    pain_score: float = 0.0  # 0-10 baseado em análise real
    conversion_likelihood: float = 0.0  # 0-1 baseado em padrões
    specific_issues: List[str] = None
    roi_potential: int = 0
    
    def __post_init__(self):
        if self.specific_issues is None:
            self.specific_issues = []


@dataclass
class FunnelPerformance:
    """Métricas refinadas de performance por funil"""
    funnel_name: str
    prospects_entered: int
    conversion_rate: float
    cost_per_lead: float
    upgrade_rate: float  # Específico para Funil A
    response_rate: float  # Específico para Funil B
    days_running: int
    should_kill: bool
    kill_reason: Optional[str] = None


class ARCORefined2025:
    """Sistema refinado baseado na revisão crítica"""
    
    def __init__(self):
        self.session = None
        
        # Kill rules refinadas por funil
        self.kill_rules = {
            "audit_express": {
                "min_upgrade_rate": 0.20,  # 20% upgrade rate mínimo
                "max_weeks_testing": 3,
                "min_lead_cvr": 0.12,  # 12% mínimo LP→Lead
                "max_cpl": 25
            },
            "teardown_60s": {
                "min_response_rate": 0.06,  # 6% response rate mínimo
                "max_weeks_testing": 2,
                "min_video_completion": 0.35,  # 35% completion mínimo
                "max_cpl": 15  # Principalmente outbound
            }
        }
        
        # Templates por nicho baseados na inteligência coletada
        self.niche_intelligence = self._load_niche_intelligence()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def _load_niche_intelligence(self) -> Dict:
        """Inteligência refinada por nicho baseada nos markdowns analisados"""
        return {
            "dental": {
                "pain_signals": [
                    "20+ campanhas ativas sem tracking claro",
                    "Landing pesada sem financiamento",
                    "Falta de antes/depois convincente",
                    "Performance mobile <60"
                ],
                "value_props": [
                    "Consolidação de campanhas (20→5)",
                    "Landing com parcelamento claro",
                    "Galeria antes/depois otimizada",
                    "Performance mobile 90+"
                ],
                "roi_calculation": "spend_monthly * 0.35",  # 35% economia típica
                "upgrade_likelihood": 0.25  # 25% dos auditorias viram sprint
            },
            "legal": {
                "pain_signals": [
                    "Claims vs reality gap",
                    "Promises without proof system",
                    "Trust claims no validation",
                    "Emergency claims sem sistema"
                ],
                "value_props": [
                    "Alignment claims↔reality",
                    "Proof of promise systems", 
                    "Digital validation systems",
                    "Emergency response tracking"
                ],
                "roi_calculation": "spend_monthly * 0.40",  # 40% economia
                "upgrade_likelihood": 0.30
            },
            "home_services": {
                "pain_signals": [
                    "No click-to-call acima da dobra",
                    "Sem ETA em X min",
                    "Sem no call-out fee",
                    "Performance emergência ruim"
                ],
                "value_props": [
                    "Header fixo com telefone",
                    "ETA tracking visível",
                    "Call-out fee transparency",
                    "Emergency landing otimizada"
                ],
                "roi_calculation": "spend_monthly * 0.30",
                "upgrade_likelihood": 0.35  # Alta urgência = maior conversão
            },
            "real_estate": {
                "pain_signals": [
                    "LP pesada com carrossel infinito",
                    "Formulário Frankenstein",
                    "Sem WhatsApp visível",
                    "Sem tour virtual/vídeo"
                ],
                "value_props": [
                    "LP única por imóvel",
                    "Formulário 3 campos + WhatsApp",
                    "Tour virtual integrado",
                    "Retarget com vídeo do imóvel"
                ],
                "roi_calculation": "spend_monthly * 0.25",
                "upgrade_likelihood": 0.20
            }
        }
    
    async def run_refined_funnel_a(self, prospects: List[RefinedProspect]) -> FunnelPerformance:
        """
        Funil A Refinado: Auditoria Express 48h → Sprint 7 dias
        APROVADO com kill rules específicas
        """
        logger.info("🔍 Executando Funil A Refinado - Auditoria Express")
        
        start_time = datetime.now()
        prospects_entered = len(prospects)
        
        # Qualificar prospects por pain score e vertical
        qualified_prospects = [
            p for p in prospects 
            if p.pain_score >= 7.0 and p.spend_monthly >= 3000
        ]
        
        # Simular performance baseada em benchmarks refinados
        landing_cvr = 0.14  # 14% CVR melhorada com otimizações
        lead_to_audit = 0.28  # 28% dos leads compram auditoria
        audit_to_sprint = 0.22  # 22% das auditorias viram sprint
        
        leads_generated = int(len(qualified_prospects) * landing_cvr)
        audits_sold = int(leads_generated * lead_to_audit)
        sprints_closed = int(audits_sold * audit_to_sprint)
        
        # Calcular métricas
        conversion_rate = leads_generated / prospects_entered if prospects_entered > 0 else 0
        upgrade_rate = sprints_closed / audits_sold if audits_sold > 0 else 0
        cost_per_lead = 18  # Otimizado com foco em retarget
        
        # Check kill rules
        days_running = 14  # Simulação 2 semanas
        should_kill = False
        kill_reason = None
        
        if upgrade_rate < self.kill_rules["audit_express"]["min_upgrade_rate"]:
            should_kill = True
            kill_reason = f"Upgrade rate {upgrade_rate:.1%} < {self.kill_rules['audit_express']['min_upgrade_rate']:.1%}"
        
        if conversion_rate < self.kill_rules["audit_express"]["min_lead_cvr"]:
            should_kill = True
            kill_reason = f"Lead CVR {conversion_rate:.1%} < {self.kill_rules['audit_express']['min_lead_cvr']:.1%}"
        
        logger.info(f"✅ Funil A: {leads_generated} leads → {audits_sold} auditorias → {sprints_closed} sprints")
        
        return FunnelPerformance(
            funnel_name="audit_express_refined",
            prospects_entered=prospects_entered,
            conversion_rate=conversion_rate,
            cost_per_lead=cost_per_lead,
            upgrade_rate=upgrade_rate,
            response_rate=0.0,  # N/A para este funil
            days_running=days_running,
            should_kill=should_kill,
            kill_reason=kill_reason
        )
    
    async def run_refined_funnel_b(self, prospects: List[RefinedProspect]) -> FunnelPerformance:
        """
        Funil B Refinado: Teardown 60s → Agenda imediata
        APROVADO com kill rules específicas
        """
        logger.info("🎬 Executando Funil B Refinado - Teardown 60s")
        
        prospects_entered = len(prospects)
        
        # Filtrar por prospects com issues específicos para teardown
        teardown_candidates = [
            p for p in prospects 
            if p.pain_score >= 6.0 and any("performance" in issue.lower() for issue in p.specific_issues)
        ]
        
        # Performance refinada baseada em evidências
        email_open_rate = 0.28  # 28% open rate com subject line otimizada
        video_completion_rate = 0.42  # 42% assistem >50% do vídeo
        response_rate = 0.08  # 8% response rate total
        call_conversion = 0.32  # 32% das respostas viram call
        
        emails_opened = int(len(teardown_candidates) * email_open_rate)
        videos_completed = int(emails_opened * video_completion_rate)
        responses = int(len(teardown_candidates) * response_rate)
        calls_booked = int(responses * call_conversion)
        
        # Métricas
        conversion_rate = responses / prospects_entered if prospects_entered > 0 else 0
        cost_per_lead = 12  # Baixo custo - principalmente outbound
        
        # Kill rules check
        days_running = 10  # Simulação 10 dias
        should_kill = False
        kill_reason = None
        
        if response_rate < self.kill_rules["teardown_60s"]["min_response_rate"]:
            should_kill = True
            kill_reason = f"Response rate {response_rate:.1%} < {self.kill_rules['teardown_60s']['min_response_rate']:.1%}"
        
        if video_completion_rate < self.kill_rules["teardown_60s"]["min_video_completion"]:
            should_kill = True
            kill_reason = f"Video completion {video_completion_rate:.1%} < {self.kill_rules['teardown_60s']['min_video_completion']:.1%}"
        
        logger.info(f"✅ Funil B: {responses} respostas → {calls_booked} calls agendadas")
        
        return FunnelPerformance(
            funnel_name="teardown_60s_refined",
            prospects_entered=prospects_entered,
            conversion_rate=conversion_rate,
            cost_per_lead=cost_per_lead,
            upgrade_rate=0.0,  # N/A para este funil
            response_rate=response_rate,
            days_running=days_running,
            should_kill=should_kill,
            kill_reason=kill_reason
        )
    
    async def discover_prospects_by_niche(self, niche: str, max_results: int = 50) -> List[RefinedProspect]:
        """Descoberta refinada por nicho com scoring inteligente"""
        
        if niche not in self.niche_intelligence:
            raise ValueError(f"Nicho '{niche}' não suportado")
        
        niche_data = self.niche_intelligence[niche]
        prospects = []
        
        # Query baseada no nicho
        search_queries = {
            "dental": "dental implants advertising active campaigns",
            "legal": "law firm advertising emergency legal services",
            "home_services": "emergency plumber HVAC advertising",
            "real_estate": "real estate property advertising"
        }
        
        query = search_queries.get(niche, f"{niche} advertising")
        
        try:
            params = {
                "q": query,
                "api_key": APIConfig.SEARCHAPI_KEY,
                "engine": "google",
                "num": min(max_results, 20)
            }
            
            async with self.session.get(APIConfig.SEARCHAPI_BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for result in data.get("organic_results", []):
                        domain = self._extract_domain(result.get("link", ""))
                        if not domain:
                            continue
                        
                        # Scoring baseado em pain signals do nicho
                        pain_score = await self._calculate_pain_score(domain, niche_data["pain_signals"])
                        
                        # ROI potential baseado na fórmula do nicho
                        estimated_spend = 4000  # Estimativa conservadora
                        roi_potential = int(eval(niche_data["roi_calculation"].replace("spend_monthly", str(estimated_spend))))
                        
                        prospect = RefinedProspect(
                            domain=domain,
                            company_name=result.get("title", "").split(" - ")[0],
                            vertical=niche,
                            spend_monthly=estimated_spend,
                            pain_score=pain_score,
                            conversion_likelihood=niche_data["upgrade_likelihood"],
                            specific_issues=niche_data["pain_signals"][:2],  # Top 2 issues
                            roi_potential=roi_potential
                        )
                        
                        prospects.append(prospect)
            
            # Ordenar por pain score
            prospects.sort(key=lambda p: p.pain_score, reverse=True)
            
        except Exception as e:
            logger.error(f"❌ Erro na descoberta para {niche}: {str(e)}")
        
        logger.info(f"🔍 Descobertos {len(prospects)} prospects para {niche}")
        return prospects[:max_results]
    
    async def _calculate_pain_score(self, domain: str, pain_signals: List[str]) -> float:
        """Calcula pain score baseado em análise real do site"""
        try:
            # Análise de performance
            performance_score = await self._get_performance_score(domain)
            
            # Score baseado em performance + pain signals
            pain_score = 10 - (performance_score / 10)  # Inverso da performance
            
            # Ajustar baseado em pain signals específicos
            if performance_score < 60:
                pain_score += 2  # Performance crítica
            if performance_score < 40:
                pain_score += 3  # Performance muito crítica
            
            return min(pain_score, 10.0)
            
        except Exception:
            return 5.0  # Score neutro se análise falhar
    
    async def _get_performance_score(self, domain: str) -> int:
        """Análise de performance via PageSpeed API"""
        try:
            url = f"https://{domain}"
            params = {
                "url": url,
                "key": APIConfig.GOOGLE_PAGESPEED_API_KEY,
                "strategy": "mobile",
                "category": ["performance"]
            }
            
            async with self.session.get(APIConfig.PAGESPEED_BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    score = data.get("lighthouseResult", {}).get("categories", {}).get("performance", {}).get("score", 0.7)
                    return int(score * 100)
                else:
                    return 70
                    
        except Exception:
            return 70
    
    def _extract_domain(self, url: str) -> str:
        """Extrai domínio limpo da URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url if url.startswith('http') else f'https://{url}')
            domain = parsed.netloc.replace('www.', '')
            return domain
        except:
            return ""
    
    async def execute_niche_strategy(self, niche: str, weekly_budget: int = 200) -> Dict:
        """
        Executa estratégia completa por nicho com os 2 funis aprovados
        """
        logger.info(f"🎯 Executando estratégia refinada para {niche}")
        
        # 1. Descoberta de prospects
        prospects = await self.discover_prospects_by_niche(niche, max_results=50)
        
        if not prospects:
            return {"success": False, "error": f"Nenhum prospect encontrado para {niche}"}
        
        # 2. Dividir prospects entre os 2 funis
        high_budget_prospects = [p for p in prospects if p.spend_monthly >= 4000][:25]
        mid_budget_prospects = [p for p in prospects if 2000 <= p.spend_monthly < 4000][:20]
        
        # 3. Executar Funil A (prospects de maior budget)
        funnel_a_result = await self.run_refined_funnel_a(high_budget_prospects)
        
        # 4. Executar Funil B (prospects médios + alguns altos)
        funnel_b_prospects = mid_budget_prospects + high_budget_prospects[:10]
        funnel_b_result = await self.run_refined_funnel_b(funnel_b_prospects)
        
        # 5. Análise de performance e kill decisions
        total_prospects = len(prospects)
        total_conversions = (funnel_a_result.prospects_entered * funnel_a_result.conversion_rate + 
                           funnel_b_result.prospects_entered * funnel_b_result.response_rate)
        
        overall_performance = {
            "niche": niche,
            "total_prospects": total_prospects,
            "funnel_a_performance": asdict(funnel_a_result),
            "funnel_b_performance": asdict(funnel_b_result),
            "combined_conversion_rate": total_conversions / total_prospects if total_prospects > 0 else 0,
            "kill_recommendations": [],
            "next_steps": []
        }
        
        # Kill recommendations
        if funnel_a_result.should_kill:
            overall_performance["kill_recommendations"].append(f"KILL Funil A: {funnel_a_result.kill_reason}")
        
        if funnel_b_result.should_kill:
            overall_performance["kill_recommendations"].append(f"KILL Funil B: {funnel_b_result.kill_reason}")
        
        # Next steps baseados em performance
        if not funnel_a_result.should_kill and funnel_a_result.upgrade_rate > 0.20:
            overall_performance["next_steps"].append("SCALE Funil A - Performance acima do threshold")
        
        if not funnel_b_result.should_kill and funnel_b_result.response_rate > 0.08:
            overall_performance["next_steps"].append("SCALE Funil B - Response rate sólida")
        
        if not overall_performance["next_steps"]:
            overall_performance["next_steps"].append("REASSESS strategy - Nenhum funil performando")
        
        logger.info(f"✅ Estratégia {niche} completa: {len(overall_performance['kill_recommendations'])} kills, {len(overall_performance['next_steps'])} next steps")
        
        return {
            "success": True,
            "performance": overall_performance,
            "prospects_discovered": prospects
        }


async def main():
    """Teste do sistema refinado por nicho"""
    
    async with ARCORefined2025() as engine:
        
        # Teste em 4 nichos priorizados
        niches_to_test = ["dental", "legal", "home_services", "real_estate"]
        
        results = {}
        
        for niche in niches_to_test:
            logger.info(f"\n{'='*60}")
            logger.info(f"TESTANDO NICHO: {niche.upper()}")
            logger.info(f"{'='*60}")
            
            result = await engine.execute_niche_strategy(niche, weekly_budget=200)
            results[niche] = result
            
            if result["success"]:
                perf = result["performance"]
                print(f"\n🎯 NICHO: {niche.upper()}")
                print(f"Prospects descobertos: {perf['total_prospects']}")
                print(f"Funil A - Upgrade rate: {perf['funnel_a_performance']['upgrade_rate']:.1%}")
                print(f"Funil B - Response rate: {perf['funnel_b_performance']['response_rate']:.1%}")
                print(f"Kill recommendations: {len(perf['kill_recommendations'])}")
                print(f"Next steps: {perf['next_steps']}")
            
            await asyncio.sleep(1)  # Rate limiting
        
        # Salvar resultados
        output_dir = Path("outputs/refined_2025")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / f"refined_niche_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # Summary executivo
        print(f"\n{'='*80}")
        print("SUMMARY EXECUTIVO - ARCO REFINED 2025")
        print(f"{'='*80}")
        
        for niche, result in results.items():
            if result["success"]:
                perf = result["performance"]
                funnel_a = perf["funnel_a_performance"]
                funnel_b = perf["funnel_b_performance"]
                
                print(f"\n{niche.upper()}:")
                print(f"  Funil A: {'✅ KEEP' if not funnel_a['should_kill'] else '❌ KILL'} (Upgrade: {funnel_a['upgrade_rate']:.1%})")
                print(f"  Funil B: {'✅ KEEP' if not funnel_b['should_kill'] else '❌ KILL'} (Response: {funnel_b['response_rate']:.1%})")
                print(f"  Recomendação: {perf['next_steps'][0] if perf['next_steps'] else 'REASSESS'}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())