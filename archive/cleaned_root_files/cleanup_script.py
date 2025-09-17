
import os
import shutil

# Create the archive directory if it doesn't exist
archive_dir = "archive/cleaned_root_files"
os.makedirs(archive_dir, exist_ok=True)

files_to_move = [
    # Scripts
    "analyze_csv_structure.py", "analyze_prospects_marketing.py", "analyze_prospects.py",
    "analyze_top_prospects_deep.py", "analyze_top_prospects_optimized.py", "analyze_top_prospects.py",
    "cleanup_script.py", "cleanup_temp_debug.py", "consolidate_prospects.py",
    "critical_refactoring_analysis.py", "delete_pipelines.py", "final_validation.py",
    "fix_leak_detection_logic.py", "move_core_files.ps1", "move_legacy_files.ps1",
    "real_data_sources_analysis.py", "run_complete_workflow.py", "run_marketing_analysis_enhanced.py",
    "run_marketing_analysis.py", "run_sample_analysis.py", "senior_engineer_feedback.py",
    "setup_marketing_analysis.py", "temp_create_dir.py", "validation_script.py",

    # Results and Reports
    "api_quota_info.json", "apollo_analysis_results.json", "csv_analysis_results.json",
    "deep_analysis_results_20250718_193834.json", "enhanced_leak_analysis.csv",
    "marketing_analysis_working.csv", "priority_leads_campaign.json", "sample_analysis_summary.csv",
    "sample_analysis.json", "top_10_leads_analysis_20250718_185156.json",
    "top_10_leads_analysis_20250718_193834.json", "top_10_leads_executive_report_20250718_185156.md",
    "top_10_leads_executive_report_20250718_193834.md", "top_10_leads_summary_20250718_185156.csv",
    "validation_report.json", "validation_report.md",

    # Root test files
    "test_api_configurations.py", "test_engines_functionality.py", "test_engines_validation.py",
    "test_enhanced_csv_adapter.py", "test_enhanced_leak_engine.py", "test_enhanced.py",
    "test_marketing_integration.py", "test_outreach_generation.py", "test_performance_impact_leak.py",
    "test_priority_engine.py", "test_prospects.py", "test_real_apis.py", "test_real_prospects.py",
    "test_refactored_leak_engine.py"
]

for f in files_to_move:
    if os.path.exists(f):
        try:
            shutil.move(f, os.path.join(archive_dir, os.path.basename(f)))
            print(f"Moved {f} to {archive_dir}")
        except Exception as e:
            print(f"Error moving {f}: {e}")

print("Cleanup script finished.")
