#!/usr/bin/env python3
"""
Test script for ARCO FIND Clean System
Tests only production-ready components without simulations
"""

import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_environment():
    """Test environment configuration"""
    print("[CONFIG] Testing environment configuration")
    
    # Check for required environment variables
    required_vars = ["GOOGLE_PAGESPEED_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"[WARNING] Missing environment variables: {', '.join(missing_vars)}")
        print("[INFO] System can run in demo mode without API keys")
        print("[INFO] To enable full functionality, copy .env.example to .env and configure")
        return True  # Demo mode compatibility
    else:
        print("[PASS] All required environment variables are set")
        return True

def test_imports():
    """Test that all clean system components can be imported"""
    print("\n[IMPORTS] Testing imports")
    
    try:
        # Test clean system import
        from arco_find_clean import (
            SecureConfig, 
            RealPageSpeedClient, 
            CleanLeadEngine
        )
        print("[PASS] Clean system components imported successfully")
        return True
    except ImportError as e:
        print(f"[FAIL] Import failed: {e}")
        return False

def test_clean_system_structure():
    """Test clean system structure and configuration"""
    print("\n[STRUCTURE] Testing clean system structure")
    
    try:
        from arco_find_clean import SecureConfig, RealPageSpeedClient, CleanLeadEngine
        
        # Test configuration
        config = SecureConfig()
        print("[PASS] SecureConfig instantiated")
        
        # Test client (without making actual API calls)
        client = RealPageSpeedClient()
        print("[PASS] RealPageSpeedClient instantiated")
        
        # Test engine
        engine = CleanLeadEngine()
        print("[PASS] CleanLeadEngine instantiated")
        
        return True
    except Exception as e:
        print(f"[FAIL] Structure test failed: {e}")
        return False

def test_dependencies():
    """Test that all required dependencies are available"""
    print("\n[DEPS] Testing dependencies")
    
    required_packages = [
        'aiohttp',
        'pandas',
        'openpyxl',
        'dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                from dotenv import load_dotenv
            else:
                __import__(package)
            print(f"[PASS] {package} available")
        except ImportError:
            print(f"[FAIL] {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n[ERROR] Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements_clean.txt")
        return False
    
    return True

async def test_api_client_structure():
    """Test API client structure without making real calls"""
    print("\n[API] Testing API client structure")
    
    try:
        from arco_find_clean import RealPageSpeedClient
        
        client = RealPageSpeedClient()
        
        # Check that client has required methods
        required_methods = ['analyze_performance']
        for method in required_methods:
            if not hasattr(client, method):
                print(f"[FAIL] Missing method: {method}")
                return False
            print(f"[PASS] Method {method} exists")
        
        # Test client initialization
        print("[PASS] API client structure is valid")
        return True
        
    except Exception as e:
        print(f"[FAIL] API client test failed: {e}")
        return False

def test_file_structure():
    """Test that required files exist"""
    print("\n[FILES] Testing file structure")
    
    required_files = [
        'arco_find_clean.py',
        'requirements_clean.txt',
        'demo_clean.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
            print(f"[FAIL] Missing file: {file}")
        else:
            print(f"[PASS] File exists: {file}")
    
    if missing_files:
        print(f"\n[ERROR] Missing files: {', '.join(missing_files)}")
        return False
    
    return True

async def run_comprehensive_test():
    """Run all tests"""
    print("ARCO FIND CLEAN SYSTEM - COMPREHENSIVE TEST")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("Clean System Structure", test_clean_system_structure),
        ("Environment", test_environment),
        ("API Client Structure", test_api_client_structure),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        if asyncio.iscoroutinefunction(test_func):
            result = await test_func()
        else:
            result = test_func()
        results[test_name] = result
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("SUCCESS: ALL TESTS PASSED - Clean system is ready!")
        return True
    else:
        print("ERROR: SOME TESTS FAILED - Please address issues above")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_comprehensive_test())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nWARNING: Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Test suite failed: {e}")
        sys.exit(1)
