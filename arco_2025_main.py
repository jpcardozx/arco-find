#!/usr/bin/env python3
"""
ARCO 2025 - Sistema de Lead Generation Focado em Conversão Real
Baseado em benchmarks de mercado e evidências de performance

Execução: python arco_2025_main.py --funnel audit_express --budget 200
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

from src.lead_engine_2025 import LeadEngine2025
from src.outreach_templates_2025 import OutreachTemplates2025
from config.api_keys import APIConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/arco_2025.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("arco-2025")


class ARCO2025Tracker:
    """Tracking simples e efetivo baseado em métricas que importam"""
    
    def __init__(self, output_dir: str = "outputs/tracking"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.metrics = {
            "prospects_discovered": 0,
            "prospects_qualified": 0,
            "emails_sent": 0,
            "emails_opened": 0,
            "emails_replied": 0,
            "calls_booked": 0,
            "sprints_closed": 0,
            "revenue_generated": 0,
            "costs_incurred": 0,
            "kill_rules_triggered": [],
            "performance_vs_benchmarks": {}
        }
        
        # Benchmarks 2025 para comparação
        self.benchmarks_2025 = {
            "email_open_rate": 0.25,
            "email_response_rate": 0.09,
            "call_conversion_rate": 0.30,
            "cost_per_lead_max": 25,
            "landing_cvr_target": 0.12,
            "sprint_close_rate": 0.22
        }
    
    def track_discovery_phase(self, prospects_found: int, qualified: int, credits_used: int):
        """Track discovery phase metrics"""
        self.metrics["prospects_discovered"] = prospects_found
        self.metrics["prospects_qualified"] = qualified
        self.metrics["costs_incurred"] += credits_used * 0.10  # $0.10 per credit estimate
        
        qualification_rate = qualified / prospects_found if prospects_found > 0 else 0
        logger.info(f"📊 Discovery: {prospects_found} found → {qualified} qualified ({qualification_rate:.1%})")
    
    def track_outreach_phase(self, sent: int, opened: int, replied: int):
        """Track outreach performance"""
        self.metrics["emails_sent"] = sent
        self.metrics["emails_opened"] = opened
        self.metrics["emails_replied"] = replied
        
        open_rate = opened / sent if sent > 0 else 0
        response_rate = replied / sent if sent > 0 else 0
        
        # Check against benchmarks
        self.metrics["performance_vs_benchmarks"]["open_rate"] = {
            "actual": open_rate,
            "benchmark": self.benchmarks_2025["email_open_rate"],
            "status": "ABOVE" if open_rate > self.benchmarks_2025["email_open_rate"] else "BELOW"
        }
        
        self.metrics["performance_vs_benchmarks"]["response_rate"] = {
            "actual": response_rate,
            "benchmark": self.benchmarks_2025["email_response_rate"],
            "status": "ABOVE" if response_rate > self.benchmarks_2025["email_response_rate"] else "BELOW"
        }
        
        logger.info(f"📧 Outreach: {sent} sent → {opened} opened ({open_rate:.1%}) → {replied} replied ({response_rate:.1%})")
    
    def track_conversion_phase(self, calls_booked: int, sprints_closed: int, revenue: float):
        """Track conversion metrics"""
        self.metrics["calls_booked"] = calls_booked
        self.metrics["sprints_closed"] = sprints_closed
        self.metrics["revenue_generated"] = revenue
        
        call_conversion = calls_booked / self.metrics["emails_replied"] if self.metrics["emails_replied"] > 0 else 0
        sprint_close_rate = sprints_closed / calls_booked if calls_booked > 0 else 0
        
        self.metrics["performance_vs_benchmarks"]["call_conversion"] = {
            "actual": call_conversion,
            "benchmark": self.benchmarks_2025["call_conversion_rate"],
            "status": "ABOVE" if call_conversion > self.benchmarks_2025["call_conversion_rate"] else "BELOW"
        }
        
        logger.info(f"💰 Conversion: {calls_booked} calls → {sprints_closed} sprints (${revenue})")
    
    def check_kill_rules(self, cpl: float, cvr: float, days_running: int):
        """Check if kill rules should be triggered"""
        triggered = []
        
        if cpl > self.benchmarks_2025["cost_per_lead_max"]:
            triggered.append(f"CPL too high: ${cpl:.2f} > ${self.benchmarks_2025['cost_per_lead_max']}")
        
        if cvr < 0.05 and days_running >= 3:
            triggered.append(f"CVR too low: {cvr:.1%} < 5% after {days_running} days")
        
        if days_running >= 14 and self.metrics["sprints_closed"] == 0:
            triggered.append(f"No sprints closed after {days_running} days")
        
        self.metrics["kill_rules_triggered"].extend(triggered)
        
        if triggered:
            logger.warning(f"🚨 Kill Rules Triggered: {triggered}")
            return True
        return False
    
    def calculate_roi(self) -> Dict:
        """Calculate ROI and break-even analysis"""
        total_cost = self.metrics["costs_incurred"]
        total_revenue = self.metrics["revenue_generated"]
        
        roi = (total_revenue - total_cost) / total_cost if total_cost > 0 else 0
        break_even = total_revenue >= total_cost
        
        roi_analysis = {
            "total_revenue": total_revenue,
            "total_cost": total_cost,
            "roi_percentage": roi * 100,
            "roi_multiple": total_revenue / total_cost if total_cost > 0 else 0,
            "break_even_achieved": break_even,
            "recommendation": "PROCEED" if roi > 1.0 else "REASSESS"
        }
        
        logger.info(f"💹 ROI: {roi:.1%} ({roi_analysis['roi_multiple']:.1f}x) - {roi_analysis['recommendation']}")
        return roi_analysis
    
    def save_report(self, filename: str = None):
        """Save comprehensive tracking report"""
        if not filename:
            filename = f"arco_2025_report_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics,
            "benchmarks_2025": self.benchmarks_2025,
            "roi_analysis": self.calculate_roi(),
            "summary": {
                "prospects_to_qualified_rate": self.metrics["prospects_qualified"] / max(self.metrics["prospects_discovered"], 1),
                "email_funnel_rate": self.metrics["emails_replied"] / max(self.metrics["emails_sent"], 1),
                "call_to_close_rate": self.metrics["sprints_closed"] / max(self.metrics["calls_booked"], 1),
                "overall_conversion_rate": self.metrics["sprints_closed"] / max(self.metrics["prospects_discovered"], 1)
            }
        }
        
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"📄 Report saved: {filepath}")
        return filepath


async def run_funnel(funnel_type: str, budget: int, target_prospects: int) -> Dict:
    """Execute specific funnel with tracking"""
    tracker = ARCO2025Tracker()
    
    logger.info(f"🚀 Iniciando Funil {funnel_type.upper()} - Budget: ${budget}")
    
    try:
        async with LeadEngine2025(weekly_budget_usd=budget) as engine:
            
            if funnel_type == "audit_express":
                result = await engine.run_funnel_a_audit_express(target_prospects)
            elif funnel_type == "teardown_60s":
                result = await engine.run_funnel_b_teardown_60s(target_prospects)
            elif funnel_type == "landing_relampago":
                result = await engine.run_funnel_c_landing_relampago(target_prospects)
            else:
                raise ValueError(f"Funnel type '{funnel_type}' not recognized")
            
            if not result.success:
                logger.error(f"❌ Funnel failed: {result.error_message}")
                return {"success": False, "error": result.error_message}
            
            # Track metrics
            tracker.track_discovery_phase(
                prospects_found=result.prospects_generated,
                qualified=result.qualified_leads,
                credits_used=30  # Estimate
            )
            
            # Simulate outreach tracking (in real implementation, integrate with email service)
            estimated_sent = result.qualified_leads
            estimated_opened = int(estimated_sent * 0.25)  # 25% open rate
            estimated_replied = int(estimated_sent * result.conversion_rate)
            
            tracker.track_outreach_phase(estimated_sent, estimated_opened, estimated_replied)
            
            # Track conversions
            estimated_revenue = result.booked_calls * 750  # $750 per sprint
            tracker.track_conversion_phase(result.booked_calls, result.booked_calls, estimated_revenue)
            
            # Check kill rules
            cpl = result.cost_per_lead
            cvr = result.conversion_rate
            should_kill = tracker.check_kill_rules(cpl, cvr, 7)  # 7 days running
            
            # Generate report
            report_path = tracker.save_report()
            
            return {
                "success": True,
                "funnel_result": result,
                "tracking_metrics": tracker.metrics,
                "roi_analysis": tracker.calculate_roi(),
                "should_kill": should_kill,
                "report_path": str(report_path)
            }
            
    except Exception as e:
        logger.error(f"❌ Error executing funnel: {str(e)}")
        return {"success": False, "error": str(e)}


async def run_4_week_validation(budget: int = 200) -> Dict:
    """
    Execute 4-week validation with kill rules
    Objetivo: pelo menos 1 sprint fechada para validar
    """
    logger.info("🎯 Iniciando Validação 4 Semanas - Sistema ARCO 2025")
    
    tracker = ARCO2025Tracker()
    
    try:
        async with LeadEngine2025(weekly_budget_usd=budget) as engine:
            validation_result = await engine.run_4_week_validation()
            
            if not validation_result:
                return {"success": False, "error": "Validation failed"}
            
            summary = validation_result["validation_summary"]
            
            # Track final metrics
            total_prospects = sum(r.prospects_generated for r in validation_result["weekly_results"].values())
            total_qualified = sum(r.qualified_leads for r in validation_result["weekly_results"].values())
            total_calls = sum(r.booked_calls for r in validation_result["weekly_results"].values())
            
            tracker.track_discovery_phase(total_prospects, total_qualified, 400)  # 4 weeks estimate
            tracker.track_outreach_phase(total_qualified, int(total_qualified * 0.25), int(total_qualified * 0.09))
            tracker.track_conversion_phase(total_calls, summary["estimated_sprints_closed"], summary["estimated_revenue_usd"])
            
            # Final decision
            decision = {
                "proceed_with_brasilprev": summary["break_even_achieved"],
                "reason": f"ROI: {summary['roi_multiple']:.1f}x, Sprints: {summary['estimated_sprints_closed']}",
                "next_steps": "PROCEED WITH INVESTMENT" if summary["break_even_achieved"] else "REASSESS STRATEGY"
            }
            
            # Save comprehensive report
            report_path = tracker.save_report("arco_2025_4week_validation.json")
            
            logger.info(f"✅ Validação completa: {decision['next_steps']}")
            
            return {
                "success": True,
                "validation_summary": summary,
                "decision": decision,
                "tracking_metrics": tracker.metrics,
                "report_path": str(report_path)
            }
            
    except Exception as e:
        logger.error(f"❌ Error in 4-week validation: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="ARCO 2025 - Lead Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run specific funnel
  python arco_2025_main.py --funnel audit_express --budget 200 --prospects 25
  
  # Run 4-week validation
  python arco_2025_main.py --validate --budget 800
  
  # Test outreach templates
  python arco_2025_main.py --test-templates
        """
    )
    
    parser.add_argument("--funnel", choices=["audit_express", "teardown_60s", "landing_relampago"],
                       help="Execute specific funnel")
    parser.add_argument("--budget", type=int, default=200,
                       help="Weekly budget in USD (default: 200)")
    parser.add_argument("--prospects", type=int, default=25,
                       help="Target prospects (default: 25)")
    parser.add_argument("--validate", action="store_true",
                       help="Run 4-week validation")
    parser.add_argument("--test-templates", action="store_true",
                       help="Test outreach templates")
    
    args = parser.parse_args()
    
    # Validate API configuration
    try:
        APIConfig.validate_s_tier_config()
    except ValueError as e:
        logger.error(f"❌ API validation failed: {e}")
        return 1
    
    try:
        if args.funnel:
            result = asyncio.run(run_funnel(args.funnel, args.budget, args.prospects))
            
            if result["success"]:
                print("\n" + "="*60)
                print(f"RESULTADO FUNIL {args.funnel.upper()}")
                print("="*60)
                print(f"Prospects qualificados: {result['funnel_result'].qualified_leads}")
                print(f"Taxa de conversão: {result['funnel_result'].conversion_rate:.1%}")
                print(f"CPL: ${result['funnel_result'].cost_per_lead}")
                print(f"Calls agendadas: {result['funnel_result'].booked_calls}")
                print(f"ROI múltiplo: {result['roi_analysis']['roi_multiple']:.1f}x")
                print(f"Recomendação: {result['roi_analysis']['recommendation']}")
                
                if result["should_kill"]:
                    print("\n🚨 KILL RULES ATIVADAS - REVISAR ESTRATÉGIA")
                
                print(f"\n📄 Relatório completo: {result['report_path']}")
            else:
                print(f"❌ Erro: {result['error']}")
                return 1
        
        elif args.validate:
            result = asyncio.run(run_4_week_validation(args.budget))
            
            if result["success"]:
                print("\n" + "="*60)
                print("VALIDAÇÃO 4 SEMANAS - ARCO 2025")
                print("="*60)
                summary = result["validation_summary"]
                print(f"Prospects descobertos: {summary['total_prospects_generated']}")
                print(f"Calls agendadas: {summary['total_calls_booked']}")
                print(f"Sprints estimadas: {summary['estimated_sprints_closed']}")
                print(f"Receita estimada: ${summary['estimated_revenue_usd']}")
                print(f"ROI múltiplo: {summary['roi_multiple']:.1f}x")
                print(f"Break-even: {'✅ SIM' if summary['break_even_achieved'] else '❌ NÃO'}")
                print(f"\n🎯 DECISÃO: {result['decision']['next_steps']}")
                print(f"Razão: {result['decision']['reason']}")
                print(f"\n📄 Relatório completo: {result['report_path']}")
            else:
                print(f"❌ Erro: {result['error']}")
                return 1
        
        elif args.test_templates:
            templates = OutreachTemplates2025()
            
            # Test data
            prospect_data = {
                "company_name": "TechStart Solutions",
                "domain": "techstart.com",
                "contact_name": "Maria",
                "industry": "saas",
                "sender_name": "João"
            }
            
            teardown_insights = {
                "domain": "techstart.com",
                "performance_score": 58,
                "issue_1": "Performance mobile crítica",
                "issue_2": "CLS alto prejudicando UX",
                "issue_3": "Imagens não otimizadas"
            }
            
            # Generate sequences
            audit_seq = templates.generate_audit_express_sequence(prospect_data)
            teardown_seq = templates.generate_teardown_60s_sequence(prospect_data, teardown_insights)
            landing_seq = templates.generate_landing_relampago_sequence(prospect_data)
            
            print("TEMPLATES DE OUTREACH 2025")
            print("="*40)
            print(f"✅ Audit Express: {len(audit_seq)} emails gerados")
            print(f"✅ Teardown 60s: {len(teardown_seq)} emails gerados")
            print(f"✅ Landing Relâmpago: {len(landing_seq)} emails gerados")
            print("\nPrimeiros subject lines:")
            print(f"  • {audit_seq[0].subject}")
            print(f"  • {teardown_seq[0].subject}")
            print(f"  • {landing_seq[0].subject}")
        
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
    Path("outputs").mkdir(exist_ok=True)
    
    sys.exit(main())