#!/usr/bin/env python3
"""
Analyze consolidated_prospects.csv structure and data quality.
Task 1.3: Analyze consolidated_prospects.csv structure
"""

import pandas as pd
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
import json

# Add arco to path
sys.path.insert(0, str(Path(__file__).parent / "arco"))

from arco.models.prospect import Prospect

def analyze_csv_structure(csv_path: str = "arco/consolidated_prospects.csv") -> Dict[str, Any]:
    """Analyze CSV structure and data quality."""
    print("🔍 Analyzing consolidated_prospects.csv structure...")
    
    try:
        # Load CSV
        df = pd.read_csv(csv_path)
        print(f"✅ CSV loaded successfully: {len(df)} rows, {len(df.columns)} columns")
        
        # Basic statistics
        analysis = {
            "basic_stats": {
                "total_rows": len(df),
                "total_columns": len(df.columns),
                "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024
            },
            "columns": list(df.columns),
            "data_types": df.dtypes.to_dict(),
            "missing_data": {},
            "data_completeness": {},
            "field_mapping": {},
            "data_quality_issues": [],
            "sample_data": {}
        }
        
        # Analyze missing data
        print("\n📊 Analyzing data completeness...")
        for column in df.columns:
            missing_count = df[column].isnull().sum()
            missing_percentage = (missing_count / len(df)) * 100
            
            analysis["missing_data"][column] = {
                "missing_count": int(missing_count),
                "missing_percentage": round(missing_percentage, 2),
                "present_count": int(len(df) - missing_count)
            }
            
            # Calculate completeness score
            completeness = 100 - missing_percentage
            analysis["data_completeness"][column] = round(completeness, 2)
        
        # Map CSV fields to Prospect model
        print("\n🗺️ Mapping CSV fields to Prospect model...")
        field_mapping = map_csv_fields_to_prospect_model(df.columns)
        analysis["field_mapping"] = field_mapping
        
        # Identify data quality issues
        print("\n🔍 Identifying data quality issues...")
        quality_issues = identify_data_quality_issues(df)
        analysis["data_quality_issues"] = quality_issues
        
        # Sample data for each column
        print("\n📋 Collecting sample data...")
        for column in df.columns:
            non_null_values = df[column].dropna()
            if len(non_null_values) > 0:
                # Get up to 3 sample values
                samples = non_null_values.head(3).tolist()
                analysis["sample_data"][column] = samples
            else:
                analysis["sample_data"][column] = []
        
        return analysis
        
    except Exception as e:
        print(f"❌ Error analyzing CSV: {e}")
        return {}

def map_csv_fields_to_prospect_model(csv_columns: List[str]) -> Dict[str, Any]:
    """Map CSV columns to Prospect model fields."""
    
    # Define mapping from CSV columns to Prospect model fields
    field_mapping = {
        "direct_mappings": {
            # Direct 1:1 mappings
            "Company": "company_name",
            "Website": "website", 
            "Company Name for Emails": "company_name_alt",
            "# Employees": "employee_count",
            "Industry": "industry",
            "Company Country": "country",
            "Company State": "state",
            "Company City": "city",
            "Company Phone": "phone",
            "Technologies": "technologies_raw",
            "Annual Revenue": "revenue",
            "Founded Year": "founded_year",
            "Short Description": "description"
        },
        "complex_mappings": {
            # Fields that need processing
            "domain_extraction": {
                "source_fields": ["Website", "Company Linkedin Url"],
                "target_field": "domain",
                "processing": "extract_domain_from_url"
            },
            "contact_creation": {
                "source_fields": ["Account Owner"],
                "target_field": "contacts",
                "processing": "create_contact_from_email"
            },
            "address_combination": {
                "source_fields": ["Company Street", "Company City", "Company State", "Company Country", "Company Postal Code"],
                "target_field": "address",
                "processing": "combine_address_fields"
            },
            "technology_parsing": {
                "source_fields": ["Technologies"],
                "target_field": "technologies",
                "processing": "parse_technology_string"
            },
            "social_media": {
                "source_fields": ["Company Linkedin Url", "Facebook Url", "Twitter Url"],
                "target_field": "social_media",
                "processing": "collect_social_urls"
            }
        },
        "unused_fields": [
            # Fields that won't be mapped to Prospect model
            "Account Stage", "Lists", "Logo Url", "Subsidiary of",
            "Primary Intent Topic", "Primary Intent Score",
            "Secondary Intent Topic", "Secondary Intent Score",
            "Apollo Account Id", "SIC Codes", "Keywords",
            "Total Funding", "Latest Funding", "Latest Funding Amount",
            "Last Raised At", "Number of Retail Locations"
        ],
        "prospect_fields_coverage": {}
    }
    
    # Check which Prospect model fields can be populated
    prospect_fields = [
        "domain", "company_name", "website", "industry", "employee_count",
        "revenue", "country", "state", "city", "phone", "description",
        "founded_year", "technologies", "contacts", "address"
    ]
    
    for field in prospect_fields:
        coverage = "not_available"
        
        # Check direct mappings
        for csv_col, prospect_field in field_mapping["direct_mappings"].items():
            if prospect_field == field:
                coverage = f"direct_mapping:{csv_col}"
                break
        
        # Check complex mappings
        if coverage == "not_available":
            for mapping_name, mapping_info in field_mapping["complex_mappings"].items():
                if mapping_info["target_field"] == field:
                    coverage = f"complex_mapping:{mapping_name}"
                    break
        
        field_mapping["prospect_fields_coverage"][field] = coverage
    
    return field_mapping

def identify_data_quality_issues(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Identify data quality issues in the CSV."""
    issues = []
    
    # Check for completely empty columns
    for column in df.columns:
        if df[column].isnull().all():
            issues.append({
                "type": "empty_column",
                "column": column,
                "description": f"Column '{column}' is completely empty"
            })
    
    # Check for columns with very low data availability
    for column in df.columns:
        missing_percentage = (df[column].isnull().sum() / len(df)) * 100
        if missing_percentage > 80:
            issues.append({
                "type": "low_data_availability",
                "column": column,
                "missing_percentage": round(missing_percentage, 2),
                "description": f"Column '{column}' has {missing_percentage:.1f}% missing data"
            })
    
    # Check for inconsistent data formats
    
    # Website URL format issues
    if 'Website' in df.columns:
        website_issues = []
        websites = df['Website'].dropna()
        for idx, website in websites.items():
            if not str(website).startswith(('http://', 'https://')):
                website_issues.append(idx)
        
        if website_issues:
            issues.append({
                "type": "url_format_issue",
                "column": "Website",
                "affected_rows": len(website_issues),
                "description": f"{len(website_issues)} websites don't start with http:// or https://"
            })
    
    # Employee count data type issues
    if '# Employees' in df.columns:
        employee_data = df['# Employees'].dropna()
        non_numeric = []
        for idx, value in employee_data.items():
            try:
                int(value)
            except (ValueError, TypeError):
                non_numeric.append(idx)
        
        if non_numeric:
            issues.append({
                "type": "data_type_issue",
                "column": "# Employees",
                "affected_rows": len(non_numeric),
                "description": f"{len(non_numeric)} employee count values are not numeric"
            })
    
    # Revenue data issues
    if 'Annual Revenue' in df.columns:
        revenue_data = df['Annual Revenue'].dropna()
        non_numeric_revenue = []
        for idx, value in revenue_data.items():
            try:
                float(value)
            except (ValueError, TypeError):
                non_numeric_revenue.append(idx)
        
        if non_numeric_revenue:
            issues.append({
                "type": "data_type_issue",
                "column": "Annual Revenue",
                "affected_rows": len(non_numeric_revenue),
                "description": f"{len(non_numeric_revenue)} revenue values are not numeric"
            })
    
    # Check for duplicate companies
    if 'Company' in df.columns:
        duplicates = df['Company'].duplicated().sum()
        if duplicates > 0:
            issues.append({
                "type": "duplicate_data",
                "column": "Company",
                "duplicate_count": int(duplicates),
                "description": f"{duplicates} duplicate company names found"
            })
    
    return issues

def calculate_data_completeness_statistics(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall data completeness statistics."""
    
    completeness_scores = list(analysis["data_completeness"].values())
    
    stats = {
        "overall_completeness": round(sum(completeness_scores) / len(completeness_scores), 2),
        "best_fields": [],
        "worst_fields": [],
        "fields_above_80_percent": 0,
        "fields_above_50_percent": 0,
        "fields_below_20_percent": 0
    }
    
    # Sort fields by completeness
    sorted_fields = sorted(analysis["data_completeness"].items(), key=lambda x: x[1], reverse=True)
    
    stats["best_fields"] = sorted_fields[:5]  # Top 5
    stats["worst_fields"] = sorted_fields[-5:]  # Bottom 5
    
    # Count fields by completeness thresholds
    for field, completeness in analysis["data_completeness"].items():
        if completeness >= 80:
            stats["fields_above_80_percent"] += 1
        elif completeness >= 50:
            stats["fields_above_50_percent"] += 1
        elif completeness < 20:
            stats["fields_below_20_percent"] += 1
    
    return stats

def create_field_mapping_documentation(analysis: Dict[str, Any]) -> str:
    """Create field mapping documentation."""
    
    doc = """# CSV Field Mapping Documentation

## Overview
This document describes how fields from consolidated_prospects.csv map to the Prospect model.

## Direct Mappings
Fields that map directly from CSV to Prospect model:

"""
    
    field_mapping = analysis["field_mapping"]
    
    for csv_field, prospect_field in field_mapping["direct_mappings"].items():
        completeness = analysis["data_completeness"].get(csv_field, 0)
        doc += f"- **{csv_field}** → `{prospect_field}` (Completeness: {completeness}%)\n"
    
    doc += "\n## Complex Mappings\nFields that require processing:\n\n"
    
    for mapping_name, mapping_info in field_mapping["complex_mappings"].items():
        doc += f"### {mapping_name}\n"
        doc += f"- **Target Field**: `{mapping_info['target_field']}`\n"
        doc += f"- **Source Fields**: {', '.join(mapping_info['source_fields'])}\n"
        doc += f"- **Processing**: {mapping_info['processing']}\n\n"
    
    doc += "## Prospect Model Field Coverage\n\n"
    
    for field, coverage in field_mapping["prospect_fields_coverage"].items():
        if coverage.startswith("direct_mapping"):
            csv_field = coverage.split(":")[1]
            completeness = analysis["data_completeness"].get(csv_field, 0)
            doc += f"- `{field}`: ✅ Available via {csv_field} ({completeness}% complete)\n"
        elif coverage.startswith("complex_mapping"):
            mapping_name = coverage.split(":")[1]
            doc += f"- `{field}`: 🔄 Available via {mapping_name} processing\n"
        else:
            doc += f"- `{field}`: ❌ Not available in CSV\n"
    
    doc += f"\n## Unused CSV Fields\n\nThe following CSV fields will not be mapped to the Prospect model:\n\n"
    
    for field in field_mapping["unused_fields"]:
        doc += f"- {field}\n"
    
    return doc

def main():
    """Main analysis function."""
    print("🚀 Starting CSV Structure Analysis")
    print("=" * 50)
    
    # Analyze CSV structure
    analysis = analyze_csv_structure()
    
    if not analysis:
        print("❌ Analysis failed")
        return False
    
    # Calculate completeness statistics
    completeness_stats = calculate_data_completeness_statistics(analysis)
    analysis["completeness_statistics"] = completeness_stats
    
    # Print summary
    print("\n📊 Analysis Summary:")
    print(f"   Total Records: {analysis['basic_stats']['total_rows']}")
    print(f"   Total Fields: {analysis['basic_stats']['total_columns']}")
    print(f"   Overall Completeness: {completeness_stats['overall_completeness']}%")
    print(f"   High Quality Fields (>80%): {completeness_stats['fields_above_80_percent']}")
    print(f"   Medium Quality Fields (50-80%): {completeness_stats['fields_above_50_percent']}")
    print(f"   Low Quality Fields (<20%): {completeness_stats['fields_below_20_percent']}")
    print(f"   Data Quality Issues: {len(analysis['data_quality_issues'])}")
    
    # Show best and worst fields
    print(f"\n🏆 Best Fields (Completeness):")
    for field, completeness in completeness_stats["best_fields"]:
        print(f"   {field}: {completeness}%")
    
    print(f"\n⚠️ Worst Fields (Completeness):")
    for field, completeness in completeness_stats["worst_fields"]:
        print(f"   {field}: {completeness}%")
    
    # Show data quality issues
    if analysis["data_quality_issues"]:
        print(f"\n🔍 Data Quality Issues:")
        for issue in analysis["data_quality_issues"]:
            print(f"   {issue['type']}: {issue['description']}")
    
    # Save analysis results
    with open("csv_analysis_results.json", "w") as f:
        # Convert complex objects to JSON-serializable format
        json_analysis = convert_to_json_serializable(analysis)
        json.dump(json_analysis, f, indent=2, default=str)
    
    print(f"\n💾 Analysis results saved to csv_analysis_results.json")
    
    # Create field mapping documentation
    mapping_doc = create_field_mapping_documentation(analysis)
    with open("csv_field_mapping.md", "w", encoding='utf-8') as f:
        f.write(mapping_doc)
    
    print(f"📋 Field mapping documentation saved to csv_field_mapping.md")
    
    # Test prospect creation with sample data
    print(f"\n🧪 Testing Prospect creation with sample data...")
    test_prospect_creation()
    
    return True

def test_prospect_creation():
    """Test creating Prospect objects from CSV data."""
    try:
        df = pd.read_csv("arco/consolidated_prospects.csv")
        
        # Take first row as sample
        sample_row = df.iloc[0]
        
        print(f"Sample company: {sample_row.get('Company', 'Unknown')}")
        
        # Create basic prospect
        prospect = Prospect(
            domain=extract_domain_from_url(sample_row.get('Website', '')),
            company_name=sample_row.get('Company', ''),
            website=sample_row.get('Website', ''),
            industry=sample_row.get('Industry', ''),
            employee_count=safe_int_conversion(sample_row.get('# Employees')),
            revenue=safe_float_conversion(sample_row.get('Annual Revenue')),
            country=sample_row.get('Company Country', ''),
            description=sample_row.get('Short Description', '')
        )
        
        print(f"✅ Successfully created Prospect object:")
        print(f"   Domain: {prospect.domain}")
        print(f"   Company: {prospect.company_name}")
        print(f"   Industry: {prospect.industry}")
        print(f"   Employees: {prospect.employee_count}")
        print(f"   Country: {prospect.country}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Prospect: {e}")
        return False

def extract_domain_from_url(url: str) -> str:
    """Extract domain from URL."""
    if not url or pd.isna(url):
        return ""
    
    url = str(url).strip()
    if url.startswith(('http://', 'https://')):
        # Remove protocol
        url = url.split('://', 1)[1]
    
    # Remove www. prefix
    if url.startswith('www.'):
        url = url[4:]
    
    # Remove path and query parameters
    url = url.split('/')[0].split('?')[0]
    
    return url

def safe_int_conversion(value) -> Optional[int]:
    """Safely convert value to int."""
    if pd.isna(value):
        return None
    try:
        return int(float(value))  # Convert via float first to handle decimal strings
    except (ValueError, TypeError):
        return None

def safe_float_conversion(value) -> Optional[float]:
    """Safely convert value to float."""
    if pd.isna(value):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def convert_to_json_serializable(obj):
    """Convert complex objects to JSON-serializable format."""
    if isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    elif hasattr(obj, 'dtype'):  # pandas/numpy objects
        if pd.isna(obj):
            return None
        return obj.item() if hasattr(obj, 'item') else str(obj)
    elif isinstance(obj, (pd.Timestamp, pd.Timedelta)):
        return str(obj)
    else:
        return obj

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)