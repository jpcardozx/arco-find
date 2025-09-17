#!/usr/bin/env python3
"""
🔧 ARCO PRODUCTION SETUP
Install real APIs and dependencies for production engine
"""

import subprocess
import sys
import os
import json
from pathlib import Path

def run_command(command, description):
    """Run shell command with error handling"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {description} completed")
            return True
        else:
            print(f"   ❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ {description} error: {e}")
        return False

def check_node_npm():
    """Check if Node.js and npm are installed"""
    print("🔍 Checking Node.js and npm...")
    
    node_check = run_command("node --version", "Node.js version check")
    npm_check = run_command("npm --version", "npm version check")
    
    if not node_check or not npm_check:
        print("❌ Node.js/npm not found. Please install Node.js first:")
        print("   📥 Download: https://nodejs.org/")
        return False
    
    return True

def install_wappalyzer_cli():
    """Install Wappalyzer CLI globally"""
    print("\n📦 Installing Wappalyzer CLI...")
    
    success = run_command("npm install -g wappalyzer-cli", "Wappalyzer CLI installation")
    
    if success:
        run_command("wappalyzer --version", "Wappalyzer version verification")
    
    return success

def install_python_packages():
    """Install required Python packages"""
    print("\n🐍 Installing Python packages...")
    
    packages = [
        "facebook-business",      # Meta Ads API
        "google-cloud-bigquery",  # HTTP Archive access
        "httpx",                  # HTTP client
        "pyyaml",                 # Config files
        "asyncio",                # Async support
    ]
    
    for package in packages:
        success = run_command(f"pip install {package}", f"Installing {package}")
        if not success:
            print(f"   ⚠️ Failed to install {package}")

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "config",
        "data", 
        "logs",
        "output",
        "cache"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   ✅ Created: {directory}/")

def create_env_template():
    """Create .env template file"""
    print("\n🔐 Creating environment template...")
    
    env_content = """# ARCO PRODUCTION ENVIRONMENT VARIABLES
# Copy this to .env and fill in your real API credentials

# Meta Ads API
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
META_ADS_ACCESS_TOKEN=your_meta_ads_access_token

# Google Cloud (BigQuery)
GOOGLE_CLOUD_PROJECT_ID=your_google_cloud_project
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json

# Apollo API
APOLLO_API_KEY=your_apollo_api_key

# ZoomInfo API  
ZOOMINFO_USERNAME=your_zoominfo_username
ZOOMINFO_PASSWORD=your_zoominfo_password
ZOOMINFO_API_KEY=your_zoominfo_api_key

# Shopify Partner (Optional)
SHOPIFY_PARTNER_APP_ID=your_shopify_partner_app_id

# API Configuration
RATE_LIMIT_DELAY=2
CONFIDENCE_THRESHOLD=70
MIN_MONTHLY_WASTE=40
"""
    
    with open(".env.template", "w", encoding='utf-8') as f:
        f.write(env_content)
    
    print("   ✅ Created: .env.template")
    print("   📝 Copy to .env and add your real API credentials")

def verify_installation():
    """Verify all installations"""
    print("\n🔍 Verifying installation...")
    
    checks = [
        ("wappalyzer --version", "Wappalyzer CLI"),
        ("python -c 'import facebook_business'", "Facebook Business SDK"),
        ("python -c 'import google.cloud.bigquery'", "Google Cloud BigQuery"),
        ("python -c 'import httpx'", "HTTPX client"),
        ("python -c 'import yaml'", "PyYAML"),
    ]
    
    success_count = 0
    
    for command, description in checks:
        if run_command(command, f"Verifying {description}"):
            success_count += 1
    
    print(f"\n📊 Verification Results: {success_count}/{len(checks)} checks passed")
    
    if success_count == len(checks):
        print("✅ All dependencies installed successfully!")
        return True
    else:
        print("⚠️ Some dependencies failed. Check the errors above.")
        return False

def print_next_steps():
    """Print next steps for configuration"""
    print("\n🎯 NEXT STEPS:")
    print("=" * 50)
    print("1. 📝 Copy .env.template to .env")
    print("2. 🔐 Add your real API credentials to .env")
    print("3. 📊 Configure config/production.yml")
    print("4. 🗃️ Verify data/vendor_costs.yml")
    print("5. 🧪 Test: python arco_production_engine.py")
    print()
    print("📚 API Setup Guides:")
    print("   • Meta Ads: https://developers.facebook.com/docs/marketing-apis/")
    print("   • Google Cloud: https://cloud.google.com/bigquery/docs/quickstarts/")
    print("   • Apollo: https://apolloio.github.io/apollo-api-docs/")
    print("   • ZoomInfo: https://university.zoominfo.com/")
    print()
    print("⚠️ IMPORTANT: Use REAL APIs - no simulations in production!")

def main():
    """Main setup function"""
    print("🎯 ARCO PRODUCTION SETUP")
    print("=" * 60)
    print("🚫 Setting up REAL APIs (no simulations)")
    print("🔧 Installing production dependencies")
    print("=" * 60)
    
    # Check prerequisites
    if not check_node_npm():
        print("\n❌ Setup failed: Node.js/npm required")
        sys.exit(1)
    
    # Setup directories
    setup_directories()
    
    # Install dependencies
    wappalyzer_success = install_wappalyzer_cli()
    install_python_packages()
    
    # Create configuration templates
    create_env_template()
    
    # Verify installation
    verification_success = verify_installation()
    
    # Print results and next steps
    print("\n" + "=" * 60)
    if verification_success:
        print("✅ PRODUCTION SETUP COMPLETE!")
        print("🎯 Ready for real API integration")
    else:
        print("⚠️ SETUP INCOMPLETE")
        print("🔧 Fix the errors above and run again")
    
    print_next_steps()

if __name__ == "__main__":
    main()
