#!/usr/bin/env python3
"""
🧪 TEST ENHANCED PIPELINE
========================
"""

import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from core.enhanced_complete_pipeline import EnhancedCompletePipeline

def main():
    """Test enhanced pipeline with fixes"""
    print("🧪 TESTING ENHANCED PIPELINE WITH CRITICAL FIXES")
    print("=" * 60)
    
    pipeline = EnhancedCompletePipeline()
    enhanced_leads = pipeline.run_enhanced_complete_pipeline(
        target_prospects=10,  # Smaller test
        min_monthly_waste=100
    )
    
    print(f"\n✅ Enhanced pipeline test complete: {len(enhanced_leads)} leads")

if __name__ == "__main__":
    main()
