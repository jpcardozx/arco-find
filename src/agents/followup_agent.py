"""
Follow-up Agent - ARCO V3
Manages automated follow-up sequences and response tracking
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional

from ..models.core_models import FollowupRecord, OutreachMessage

logger = logging.getLogger(__name__)


class FollowupAgent:
    """Follow-up automation and tracking"""
    
    def __init__(self):
        self.followup_intervals = [2, 5, 14]  # T+2, T+5, T+14 days
    
    def schedule_followups(self, outreach: OutreachMessage) -> List[FollowupRecord]:
        """Schedule follow-up sequence"""
        followups = []
        base_date = outreach.created_timestamp
        
        for i, interval in enumerate(self.followup_intervals):
            followup_date = base_date + timedelta(days=interval)
            followups.append(FollowupRecord(
                prospect_id=outreach.prospect_id,
                sent_at=base_date,
                responded=False,
                response_type=None,
                next_followup_date=followup_date,
                sequence_step=i + 1
            ))
        
        logger.info(f"📅 Scheduled {len(followups)} follow-ups for {outreach.prospect_id}")
        return followups
    
    def generate_followup_message(self, record: FollowupRecord, original: OutreachMessage) -> str:
        """Generate follow-up message"""
        templates = {
            1: "Quick follow-up on the {pain} analysis.\n\nAdded one more insight: {insight}\n\nStill offering the 24h audit (credited to sprint) if the timing works.\n\n{calendar}",
            2: "Last note on this — sharing a case study from {vertical}.\n\nSimilar issue ({pain}) → {result}\n\nIf Q4 performance is a priority, happy to run the audit.\nOtherwise, keeping this for reference.\n\n{case_study}",
            3: "Final check-in about the performance optimization opportunity.\n\nThe {pain} issue is still impacting conversions.\n\nHappy to help when timing improves.\n\n{contact}"
        }
        
        template = templates.get(record.sequence_step, templates[3])
        return template.format(
            pain=original.primary_pain_point,
            insight="Additional optimization insights",
            calendar="https://calendly.com/arco-audit",
            vertical=original.vertical_template.replace("_", " "),
            result="15% conversion improvement",
            case_study="https://case-studies.arco.dev",
            contact="alex@arco.dev"
        )