#!/usr/bin/env python3
"""
ARCO REFINED 2025 - Sistema Final Baseado em Revisão Crítica
Funis A + B aprovados, Funil C eliminado, Kill rules específicas

Execução: python arco_refined_main.py --niche dental --validate
"""

import asyncio
import argparse
import logging
import json
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.arco_refined_2025 import ARCORefined2025
from config.api_keys import APIConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/arco_refined.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("arco-refined")


class RefinedTracker:
    """Tracker refinado com kill rules específicas por funil"""
    
    def __init__(self):
        self.metrics = {
            "funnel_a": {
                "prospects_entered": 0,
                "leads_generated": 0, 
                "audits_sold": 0,
                "sprints_closed": 0,
                "upgrade_rate": 0.0,
                "cost_per_lead": 0.0,
                "kill_triggered": False,
                "kill_reason": None
            },
            "funnel_b": {
                "prospects_entered": 0,
                "emails_sent": 0,
                "videos_completed": 0,
                "responses": 0,
                "calls_booked": 0,
                "response_rate": 0.0,
                "cost_per_lead": 0.0,
                "kill_triggered": False,
                "kill_reason": None
            },
            "overall": {
                "total_prospects": 0,
                "total_revenue": 0,
                "total_cost": 0,
                "roi_multiple": 0.0,
                "break_even": False,
                "recommendation": ""
            }
        }
        
        # Kill rules refinadas
        self.kill_rules = {
            "funnel_a": {
                "min_upgrade_rate": 0.20,
                "min_lead_cvr": 0.12,
                "max_cpl": 25,
                "max_weeks_testing": 3
            },
            "funnel_b": {
                "min_response_rate": 0.06,
                "min_video_completion": 0.35,
                "max_cpl": 15,
                "max_weeks_testing": 2
            }
        }
    
    def update_funnel_a_metrics(self, prospects_entered: int, leads: int, audits: int, sprints: int, cpl: float):
        """Update Funil A metrics and check kill rules"""
        fa = self.metrics["funnel_a"]
        fa["prospects_entered"] = prospects_entered
        fa["leads_generated"] = leads
        fa["audits_sold"] = audits
        fa["sprints_closed"] = sprints
        fa["upgrade_rate"] = sprints / audits if audits > 0 else 0
        fa["cost_per_lead"] = cpl
        
        # Check kill rules
        if fa["upgrade_rate"] < self.kill_rules["funnel_a"]["min_upgrade_rate"]:
            fa["kill_triggered"] = True
            fa["kill_reason"] = f"Upgrade rate {fa['upgrade_rate']:.1%} < 20%"
        
        if cpl > self.kill_rules["funnel_a"]["max_cpl"]:
            fa["kill_triggered"] = True
            fa["kill_reason"] = f"CPL ${cpl} > $25"
        
        lead_cvr = leads / prospects_entered if prospects_entered > 0 else 0
        if lead_cvr < self.kill_rules["funnel_a"]["min_lead_cvr"]:
            fa["kill_triggered"] = True
            fa["kill_reason"] = f"Lead CVR {lead_cvr:.1%} < 12%"
    
    def update_funnel_b_metrics(self, prospects_entered: int, emails: int, videos: int, responses: int, calls: int, cpl: float):
        """Update Funil B metrics and check kill rules"""
        fb = self.metrics["funnel_b"]
        fb["prospects_entered"] = prospects_entered
        fb["emails_sent"] = emails
        fb["videos_completed"] = videos
        fb["responses"] = responses
        fb["calls_booked"] = calls
        fb["response_rate"] = responses / emails if emails > 0 else 0
        fb["cost_per_lead"] = cpl
        
        # Check kill rules
        if fb["response_rate"] < self.kill_rules["funnel_b"]["min_response_rate"]:
            fb["kill_triggered"] = True
            fb["kill_reason"] = f"Response rate {fb['response_rate']:.1%} < 6%"
        
        if cpl > self.kill_rules["funnel_b"]["max_cpl"]:
            fb["kill_triggered"] = True
            fb["kill_reason"] = f"CPL ${cpl} > $15"
        
        video_completion_rate = videos / emails if emails > 0 else 0
        if video_completion_rate < self.kill_rules["funnel_b"]["min_video_completion"]:
            fb["kill_triggered"] = True
            fb["kill_reason"] = f"Video completion {video_completion_rate:.1%} < 35%"
    
    def calculate_overall_performance(self, total_cost: float):
        """Calculate overall performance and ROI"""
        overall = self.metrics["overall"]
        
        # Revenue calculation
        sprints_revenue = self.metrics["funnel_a"]["sprints_closed"] * 750  # $750 per sprint
        calls_revenue = self.metrics["funnel_b"]["calls_booked"] * 500  # $500 estimated per call conversion
        
        overall["total_prospects"] = (self.metrics["funnel_a"]["prospects_entered"] + 
                                    self.metrics["funnel_b"]["prospects_entered"])
        overall["total_revenue"] = sprints_revenue + calls_revenue
        overall["total_cost"] = total_cost
        overall["roi_multiple"] = overall["total_revenue"] / total_cost if total_cost > 0 else 0
        overall["break_even"] = overall["total_revenue"] >= total_cost
        
        # Recommendation based on performance
        if overall["roi_multiple"] >= 3.0:
            overall["recommendation"] = "SCALE - ROI justifica investimento Brasilprev"
        elif overall["roi_multiple"] >= 1.0:
            overall["recommendation"] = "CONTINUE - Break-even atingido, otimizar"
        else:
            overall["recommendation"] = "STOP - ROI insuficiente, reavaliar estratégia"
    
    def get_kill_summary(self) -> Dict:
        """Get summary of kill rule triggers"""
        return {
            "funnel_a_killed": self.metrics["funnel_a"]["kill_triggered"],
            "funnel_a_reason": self.metrics["funnel_a"]["kill_reason"],
            "funnel_b_killed": self.metrics["funnel_b"]["kill_triggered"], 
            "funnel_b_reason": self.metrics["funnel_b"]["kill_reason"],
            "any_killed": (self.metrics["funnel_a"]["kill_triggered"] or 
                          self.metrics["funnel_b"]["kill_triggered"])
        }


async def execute_single_niche(niche: str, budget: int) -> Dict:
    """Execute strategy for single niche"""
    logger.info(f"🎯 Executando estratégia refinada para {niche}")
    
    tracker = RefinedTracker()
    
    try:
        async with ARCORefined2025() as engine:
            result = await engine.execute_niche_strategy(niche, weekly_budget=budget)
            
            if not result["success"]:
                return {"success": False, "error": result["error"]}
            
            perf = result["performance"]
            
            # Update tracker with results
            funnel_a = perf["funnel_a_performance"]
            funnel_b = perf["funnel_b_performance"]
            
            # Simulate detailed metrics for Funil A
            fa_leads = int(funnel_a["prospects_entered"] * funnel_a["conversion_rate"])
            fa_audits = int(fa_leads * 0.28)  # 28% lead→audit
            fa_sprints = int(fa_audits * funnel_a["upgrade_rate"])
            
            tracker.update_funnel_a_metrics(
                prospects_entered=funnel_a["prospects_entered"],
                leads=fa_leads,
                audits=fa_audits, 
                sprints=fa_sprints,
                cpl=funnel_a["cost_per_lead"]
            )
            
            # Simulate detailed metrics for Funil B
            fb_emails = funnel_b["prospects_entered"]
            fb_videos = int(fb_emails * 0.42)  # 42% video completion
            fb_responses = int(fb_emails * funnel_b["response_rate"])
            fb_calls = int(fb_responses * 0.32)  # 32% response→call
            
            tracker.update_funnel_b_metrics(
                prospects_entered=funnel_b["prospects_entered"],
                emails=fb_emails,
                videos=fb_videos,
                responses=fb_responses, 
                calls=fb_calls,
                cpl=funnel_b["cost_per_lead"]
            )
            
            # Calculate overall performance
            tracker.calculate_overall_performance(budget)
            
            return {
                "success": True,
                "niche": niche,
                "metrics": tracker.metrics,
                "kill_summary": tracker.get_kill_summary(),
                "prospects_discovered": result["prospects_discovered"]
            }
            
    except Exception as e:
        logger.error(f"❌ Erro executando {niche}: {str(e)}")
        return {"success": False, "error": str(e)}


async def execute_4_week_validation(budget: int = 800) -> Dict:
    """Execute 4-week validation across all niches"""
    logger.info("🎯 Iniciando Validação 4 Semanas - ARCO Refined 2025")
    
    niches = ["dental", "legal", "home_services", "real_estate"]
    weekly_budget = budget // 4
    
    overall_tracker = RefinedTracker()
    niche_results = {}
    
    try:
        for week, niche in enumerate(niches, 1):
            logger.info(f"\n📅 SEMANA {week}: {niche.upper()}")
            
            result = await execute_single_niche(niche, weekly_budget)
            niche_results[f"week_{week}_{niche}"] = result
            
            if result["success"]:
                # Accumulate metrics
                metrics = result["metrics"]
                
                overall_tracker.metrics["funnel_a"]["prospects_entered"] += metrics["funnel_a"]["prospects_entered"]
                overall_tracker.metrics["funnel_a"]["sprints_closed"] += metrics["funnel_a"]["sprints_closed"]
                
                overall_tracker.metrics["funnel_b"]["prospects_entered"] += metrics["funnel_b"]["prospects_entered"]
                overall_tracker.metrics["funnel_b"]["calls_booked"] += metrics["funnel_b"]["calls_booked"]
        
        # Calculate final metrics
        overall_tracker.calculate_overall_performance(budget)
        
        # Validation decision
        total_sprints = overall_tracker.metrics["funnel_a"]["sprints_closed"]
        total_calls = overall_tracker.metrics["funnel_b"]["calls_booked"]
        total_revenue = overall_tracker.metrics["overall"]["total_revenue"]
        roi_multiple = overall_tracker.metrics["overall"]["roi_multiple"]
        
        validation_decision = {
            "proceed_with_brasilprev": total_sprints >= 1,  # Minimum 1 sprint
            "total_sprints_closed": total_sprints,
            "total_calls_booked": total_calls,
            "total_revenue": total_revenue,
            "roi_multiple": roi_multiple,
            "break_even_achieved": overall_tracker.metrics["overall"]["break_even"],
            "recommendation": overall_tracker.metrics["overall"]["recommendation"]
        }
        
        return {
            "success": True,
            "validation_decision": validation_decision,
            "overall_metrics": overall_tracker.metrics,
            "niche_results": niche_results,
            "kill_summary": overall_tracker.get_kill_summary()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na validação 4 semanas: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="ARCO Refined 2025 - Sistema Final",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Teste nicho específico
  python arco_refined_main.py --niche dental --budget 200
  
  # Validação 4 semanas
  python arco_refined_main.py --validate --budget 800
  
  # Análise kill rules
  python arco_refined_main.py --analyze-kills
        """
    )
    
    parser.add_argument("--niche", choices=["dental", "legal", "home_services", "real_estate"],
                       help="Execute strategy for specific niche")
    parser.add_argument("--budget", type=int, default=200,
                       help="Budget in USD (default: 200)")
    parser.add_argument("--validate", action="store_true",
                       help="Run 4-week validation across all niches")
    parser.add_argument("--analyze-kills", action="store_true",
                       help="Analyze kill rule performance")
    
    args = parser.parse_args()
    
    # Validate API configuration
    try:
        APIConfig.validate_s_tier_config()
    except ValueError as e:
        logger.error(f"❌ API validation failed: {e}")
        return 1
    
    try:
        if args.niche:
            result = asyncio.run(execute_single_niche(args.niche, args.budget))
            
            if result["success"]:
                print(f"\n{'='*60}")
                print(f"RESULTADO {args.niche.upper()}")
                print(f"{'='*60}")
                
                metrics = result["metrics"]
                fa = metrics["funnel_a"]
                fb = metrics["funnel_b"] 
                overall = metrics["overall"]
                
                print(f"FUNIL A (Auditoria Express):")
                print(f"  Prospects: {fa['prospects_entered']}")
                print(f"  Sprints fechadas: {fa['sprints_closed']}")
                print(f"  Upgrade rate: {fa['upgrade_rate']:.1%}")
                print(f"  Status: {'❌ KILL' if fa['kill_triggered'] else '✅ CONTINUE'}")
                if fa['kill_triggered']:
                    print(f"  Razão: {fa['kill_reason']}")
                
                print(f"\nFUNIL B (Teardown 60s):")
                print(f"  Prospects: {fb['prospects_entered']}")
                print(f"  Calls agendadas: {fb['calls_booked']}")
                print(f"  Response rate: {fb['response_rate']:.1%}")
                print(f"  Status: {'❌ KILL' if fb['kill_triggered'] else '✅ CONTINUE'}")
                if fb['kill_triggered']:
                    print(f"  Razão: {fb['kill_reason']}")
                
                print(f"\nPERFORMANCE GERAL:")
                print(f"  ROI múltiplo: {overall['roi_multiple']:.1f}x")
                print(f"  Break-even: {'✅ SIM' if overall['break_even'] else '❌ NÃO'}")
                print(f"  Recomendação: {overall['recommendation']}")
                
            else:
                print(f"❌ Erro: {result['error']}")
                return 1
        
        elif args.validate:
            result = asyncio.run(execute_4_week_validation(args.budget))
            
            if result["success"]:
                print(f"\n{'='*80}")
                print("VALIDAÇÃO 4 SEMANAS - ARCO REFINED 2025")
                print(f"{'='*80}")
                
                decision = result["validation_decision"]
                overall = result["overall_metrics"]["overall"]
                
                print(f"RESULTADOS:")
                print(f"  Sprints fechadas: {decision['total_sprints_closed']}")
                print(f"  Calls agendadas: {decision['total_calls_booked']}")
                print(f"  Revenue total: ${decision['total_revenue']:,.0f}")
                print(f"  ROI múltiplo: {decision['roi_multiple']:.1f}x")
                print(f"  Break-even: {'✅ SIM' if decision['break_even_achieved'] else '❌ NÃO'}")
                
                print(f"\n🎯 DECISÃO BRASILPREV:")
                if decision['proceed_with_brasilprev']:
                    print(f"  ✅ PROCEDER - {decision['total_sprints_closed']} sprint(s) fechada(s)")
                    print(f"  Canal validado com risco controlado")
                else:
                    print(f"  ❌ NÃO PROCEDER - Nenhuma sprint fechada")
                    print(f"  Reavaliar estratégia antes de investimento")
                
                print(f"\n📊 RECOMENDAÇÃO: {decision['recommendation']}")
                
                # Kill summary
                kill_summary = result["kill_summary"]
                if kill_summary["any_killed"]:
                    print(f"\n🚨 KILL RULES ATIVADAS:")
                    if kill_summary["funnel_a_killed"]:
                        print(f"  ❌ Funil A: {kill_summary['funnel_a_reason']}")
                    if kill_summary["funnel_b_killed"]:
                        print(f"  ❌ Funil B: {kill_summary['funnel_b_reason']}")
                
            else:
                print(f"❌ Erro: {result['error']}")
                return 1
        
        elif args.analyze_kills:
            print("📊 ANÁLISE DE KILL RULES")
            print("="*40)
            print("Funil A (Auditoria Express):")
            print("  • Upgrade rate <20% por 3 semanas → KILL")
            print("  • LP CVR <12% após 2 iterações → KILL")
            print("  • CPL >$25 → PAUSE")
            print("\nFunil B (Teardown 60s):")
            print("  • Response rate <6% por 2 semanas → KILL")
            print("  • Video completion <35% → KILL")
            print("  • CPL >$15 → PAUSE")
            print("\nCondições de Scale:")
            print("  • Funil A: Upgrade >25% + CPL <$20 → SCALE 2x")
            print("  • Funil B: Response >10% + completion >40% → SCALE 2x")
        
        else:
            parser.print_help()
            return 1
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Operação cancelada pelo usuário")
        return 130
    except Exception as e:
        logger.error(f"❌ Erro inesperado: {str(e)}")
        return 1


if __name__ == "__main__":
    # Create required directories
    Path("logs").mkdir(exist_ok=True)
    Path("outputs/refined_2025").mkdir(parents=True, exist_ok=True)
    
    sys.exit(main())