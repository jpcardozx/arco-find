"""
ARCO FIND - Production System Validator
Comprehensive validation to eliminate all simulations and ensure production readiness
"""

import os
import re
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime
import logging

# Configure validation logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionValidator:
    """Comprehensive production readiness validator"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.critical_failures = []
        self.warnings = []
        self.validation_results = {}
        
        # Patterns that indicate simulation/fake data
        self.simulation_patterns = [
            r'import\s+random',
            r'import\s+faker',
            r'random\.',
            r'fake\.',
            r'mock\.',
            r'simulate_',
            r'simulation',
            r'#.*simulate',
            r'#.*fake',
            r'#.*mock',
            r'random\.randint',
            r'random\.uniform',
            r'random\.choice',
            r'\.fake\(',
            r'mock_',
            r'dummy_',
            r'test_data',
            r'artificial',
            r'synthetic'
        ]
        
        # Patterns for hardcoded secrets (security risk)
        self.secret_patterns = [
            r'api_key\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
            r'API_KEY\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
            r'secret\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
            r'password\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][A-Za-z0-9]{20,}["\']',
            r'AIzaSy[A-Za-z0-9_-]{33}',  # Google API key pattern
            r'sk-[A-Za-z0-9]{32,}',      # OpenAI API key pattern
        ]
        
        # Production-ready file patterns
        self.production_files = [
            'arco_find_production.py',
            'engines/bigquery_stier_pipeline.py',
            'data_sources/real_data_pipeline.py',
            'intelligence/real_intelligence_engine.py'
        ]
    
    async def validate_full_system(self) -> Dict[str, Any]:
        """Run comprehensive system validation"""
        
        logger.info("🔍 Starting comprehensive production validation...")
        
        # 1. Validate codebase for simulations
        simulation_check = await self._check_simulation_code()
        
        # 2. Validate security (no hardcoded secrets)
        security_check = await self._check_security_issues()
        
        # 3. Validate environment configuration
        environment_check = self._check_environment_config()
        
        # 4. Validate dependencies
        dependency_check = self._check_dependencies()
        
        # 5. Validate file structure
        structure_check = self._check_file_structure()
        
        # 6. Validate API endpoints
        api_check = await self._check_api_availability()
        
        # Compile results
        self.validation_results = {
            'validation_timestamp': datetime.now().isoformat(),
            'overall_status': 'PASS' if len(self.critical_failures) == 0 else 'FAIL',
            'critical_failures': self.critical_failures,
            'warnings': self.warnings,
            'checks': {
                'simulation_elimination': simulation_check,
                'security_hardening': security_check,
                'environment_config': environment_check,
                'dependency_validation': dependency_check,
                'structure_validation': structure_check,
                'api_availability': api_check
            },
            'production_readiness_score': self._calculate_readiness_score(),
            'recommendations': self._generate_recommendations()
        }
        
        return self.validation_results
    
    async def _check_simulation_code(self) -> Dict[str, Any]:
        """Check for any simulation or fake data code"""
        
        logger.info("Checking for simulation code...")
        
        simulation_violations = []
        files_checked = 0
        
        # Check all Python files
        for py_file in self.workspace_path.rglob("*.py"):
            if py_file.name.startswith('.') or '__pycache__' in str(py_file):
                continue
                
            files_checked += 1
            
            try:
                content = py_file.read_text(encoding='utf-8')
                
                for pattern in self.simulation_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        simulation_violations.append({
                            'file': str(py_file.relative_to(self.workspace_path)),
                            'line': line_num,
                            'pattern': pattern,
                            'match': match.group(),
                            'severity': 'CRITICAL'
                        })
                        
            except Exception as e:
                self.warnings.append(f"Could not read {py_file}: {e}")
        
        # Add critical failures for simulation code
        for violation in simulation_violations:
            self.critical_failures.append(
                f"🚨 SIMULATION CODE: {violation['file']}:{violation['line']} - {violation['match']}"
            )
        
        result = {
            'files_checked': files_checked,
            'violations_found': len(simulation_violations),
            'violations': simulation_violations,
            'status': 'PASS' if len(simulation_violations) == 0 else 'CRITICAL_FAIL'
        }
        
        if len(simulation_violations) == 0:
            logger.info("✅ Zero simulation code detected - PASS")
        else:
            logger.error(f"❌ {len(simulation_violations)} simulation violations found - CRITICAL FAIL")
        
        return result
    
    async def _check_security_issues(self) -> Dict[str, Any]:
        """Check for hardcoded secrets and security issues"""
        
        logger.info("Checking for security issues...")
        
        security_violations = []
        files_checked = 0
        
        # Check all files for hardcoded secrets
        for file_path in self.workspace_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in ['.py', '.json', '.txt', '.md']:
                if file_path.name.startswith('.') or '__pycache__' in str(file_path):
                    continue
                    
                files_checked += 1
                
                try:
                    content = file_path.read_text(encoding='utf-8')
                    
                    for pattern in self.secret_patterns:
                        matches = re.finditer(pattern, content, re.IGNORECASE)
                        for match in matches:
                            line_num = content[:match.start()].count('\n') + 1
                            # Mask the secret for logging
                            masked_match = match.group()[:10] + "***MASKED***"
                            security_violations.append({
                                'file': str(file_path.relative_to(self.workspace_path)),
                                'line': line_num,
                                'pattern': pattern,
                                'masked_content': masked_match,
                                'severity': 'CRITICAL'
                            })
                            
                except Exception as e:
                    self.warnings.append(f"Could not read {file_path}: {e}")
        
        # Add critical failures for security issues
        for violation in security_violations:
            self.critical_failures.append(
                f"🔐 SECURITY RISK: {violation['file']}:{violation['line']} - Hardcoded secret detected"
            )
        
        result = {
            'files_checked': files_checked,
            'violations_found': len(security_violations),
            'violations': security_violations,
            'status': 'PASS' if len(security_violations) == 0 else 'CRITICAL_FAIL'
        }
        
        if len(security_violations) == 0:
            logger.info("✅ No hardcoded secrets detected - PASS")
        else:
            logger.error(f"❌ {len(security_violations)} security violations found - CRITICAL FAIL")
        
        return result
    
    def _check_environment_config(self) -> Dict[str, Any]:
        """Check environment configuration"""
        
        logger.info("Checking environment configuration...")
        
        required_env_vars = [
            'GOOGLE_PAGESPEED_API_KEY',
            # 'GCP_PROJECT_ID',  # Optional for some workflows
            # 'SIMILARWEB_API_KEY'  # Optional
        ]
        
        missing_vars = []
        configured_vars = []
        
        for var in required_env_vars:
            if os.getenv(var):
                configured_vars.append(var)
            else:
                missing_vars.append(var)
        
        # Check for .env file
        env_file_exists = (self.workspace_path / '.env').exists()
        if env_file_exists:
            self.warnings.append("⚠️ .env file found - ensure it's not committed to version control")
        
        result = {
            'required_vars': required_env_vars,
            'configured_vars': configured_vars,
            'missing_vars': missing_vars,
            'env_file_exists': env_file_exists,
            'status': 'PASS' if len(missing_vars) == 0 else 'WARNING'
        }
        
        if missing_vars:
            for var in missing_vars:
                self.warnings.append(f"⚠️ Environment variable not set: {var}")
        
        return result
    
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check dependency configuration"""
        
        logger.info("Checking dependencies...")
        
        req_files = {
            'production': self.workspace_path / 'requirements_production.txt',
            'stier': self.workspace_path / 'requirements_stier.txt',
            'legacy': self.workspace_path / 'requirements.txt'
        }
        
        dependency_status = {}
        
        for name, req_file in req_files.items():
            if req_file.exists():
                try:
                    content = req_file.read_text()
                    
                    # Check for simulation libraries
                    forbidden_libs = ['faker', 'mock', 'random']
                    found_forbidden = []
                    
                    for lib in forbidden_libs:
                        if lib in content.lower():
                            found_forbidden.append(lib)
                    
                    dependency_status[name] = {
                        'exists': True,
                        'forbidden_libraries': found_forbidden,
                        'line_count': len(content.split('\n')),
                        'status': 'PASS' if len(found_forbidden) == 0 else 'FAIL'
                    }
                    
                    if found_forbidden:
                        self.critical_failures.append(
                            f"🚨 FORBIDDEN LIBRARIES in {req_file.name}: {', '.join(found_forbidden)}"
                        )
                    
                except Exception as e:
                    dependency_status[name] = {
                        'exists': True,
                        'error': str(e),
                        'status': 'ERROR'
                    }
            else:
                dependency_status[name] = {'exists': False, 'status': 'MISSING'}
        
        return {
            'dependency_files': dependency_status,
            'status': 'PASS' if all(
                dep.get('status') in ['PASS', 'MISSING'] for dep in dependency_status.values()
            ) else 'FAIL'
        }
    
    def _check_file_structure(self) -> Dict[str, Any]:
        """Check production file structure"""
        
        logger.info("Checking file structure...")
        
        file_status = {}
        
        for file_path in self.production_files:
            full_path = self.workspace_path / file_path
            
            if full_path.exists():
                try:
                    content = full_path.read_text()
                    file_status[file_path] = {
                        'exists': True,
                        'size_bytes': len(content),
                        'line_count': len(content.split('\n')),
                        'last_modified': datetime.fromtimestamp(full_path.stat().st_mtime).isoformat(),
                        'status': 'PASS'
                    }
                except Exception as e:
                    file_status[file_path] = {
                        'exists': True,
                        'error': str(e),
                        'status': 'ERROR'
                    }
            else:
                file_status[file_path] = {
                    'exists': False,
                    'status': 'MISSING'
                }
        
        return {
            'production_files': file_status,
            'status': 'PASS'  # File existence is not critical for all workflows
        }
    
    async def _check_api_availability(self) -> Dict[str, Any]:
        """Check API endpoint availability (basic connectivity)"""
        
        logger.info("Checking API availability...")
        
        api_endpoints = {
            'google_pagespeed': 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed',
            'bigquery_public': 'https://bigquery.googleapis.com',
        }
        
        api_status = {}
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                for api_name, endpoint in api_endpoints.items():
                    try:
                        # Simple connectivity test (without API key)
                        async with session.get(endpoint, timeout=5) as response:
                            api_status[api_name] = {
                                'endpoint': endpoint,
                                'reachable': True,
                                'status_code': response.status,
                                'status': 'REACHABLE'
                            }
                    except Exception as e:
                        api_status[api_name] = {
                            'endpoint': endpoint,
                            'reachable': False,
                            'error': str(e),
                            'status': 'UNREACHABLE'
                        }
                        self.warnings.append(f"⚠️ API unreachable: {api_name} - {e}")
                        
        except ImportError:
            api_status = {'error': 'aiohttp not available for connectivity testing'}
        
        return {
            'api_endpoints': api_status,
            'status': 'WARNING' if any(
                api.get('status') == 'UNREACHABLE' for api in api_status.values()
            ) else 'PASS'
        }
    
    def _calculate_readiness_score(self) -> float:
        """Calculate production readiness score (0-100)"""
        
        total_checks = 0
        passed_checks = 0
        
        for check_name, check_result in self.validation_results.get('checks', {}).items():
            total_checks += 1
            if check_result.get('status') in ['PASS', 'REACHABLE']:
                passed_checks += 1
            elif check_result.get('status') == 'WARNING':
                passed_checks += 0.5
        
        # Heavily penalize critical failures
        critical_penalty = min(50, len(self.critical_failures) * 25)
        
        base_score = (passed_checks / total_checks) * 100 if total_checks > 0 else 0
        final_score = max(0, base_score - critical_penalty)
        
        return round(final_score, 1)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations"""
        
        recommendations = []
        
        if self.critical_failures:
            recommendations.append("🚨 CRITICAL: Address all critical failures before production deployment")
        
        # Specific recommendations based on checks
        if any('SIMULATION' in failure for failure in self.critical_failures):
            recommendations.extend([
                "Remove all simulation, random, and mock code from production files",
                "Replace simulated data with real API calls",
                "Implement proper error handling for missing real data"
            ])
        
        if any('SECURITY' in failure for failure in self.critical_failures):
            recommendations.extend([
                "Move all API keys and secrets to environment variables",
                "Add .env to .gitignore to prevent secret exposure",
                "Consider using a secrets management service for production"
            ])
        
        if len(self.warnings) > 5:
            recommendations.append("Address warnings to improve system reliability")
        
        if not recommendations:
            recommendations.append("✅ System appears production-ready - proceed with deployment")
        
        return recommendations

async def main():
    """Run comprehensive production validation"""
    
    print("🔍 ARCO FIND - PRODUCTION VALIDATION")
    print("Comprehensive analysis for production readiness")
    print("=" * 60)
    
    # Initialize validator
    validator = ProductionValidator()
    
    # Run full validation
    results = await validator.validate_full_system()
    
    # Display results
    print(f"\n📊 VALIDATION RESULTS")
    print(f"Timestamp: {results['validation_timestamp']}")
    print(f"Overall Status: {results['overall_status']}")
    print(f"Production Readiness Score: {results['production_readiness_score']}/100")
    
    # Show critical failures
    if results['critical_failures']:
        print(f"\n🚨 CRITICAL FAILURES ({len(results['critical_failures'])}):")
        for failure in results['critical_failures']:
            print(f"   {failure}")
    
    # Show warnings
    if results['warnings']:
        print(f"\n⚠️ WARNINGS ({len(results['warnings'])}):")
        for warning in results['warnings'][:10]:  # Limit display
            print(f"   {warning}")
        if len(results['warnings']) > 10:
            print(f"   ... and {len(results['warnings']) - 10} more warnings")
    
    # Show check summaries
    print(f"\n📋 CHECK SUMMARIES:")
    for check_name, check_result in results['checks'].items():
        status = check_result.get('status', 'UNKNOWN')
        status_emoji = {
            'PASS': '✅',
            'FAIL': '❌',
            'CRITICAL_FAIL': '🚨',
            'WARNING': '⚠️',
            'REACHABLE': '🌐',
            'UNREACHABLE': '🔌'
        }.get(status, '❓')
        
        print(f"   {status_emoji} {check_name.replace('_', ' ').title()}: {status}")
    
    # Show recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in results['recommendations']:
        print(f"   📋 {rec}")
    
    # Save detailed results
    output_dir = Path("validation")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = output_dir / f"production_validation_{timestamp}.json"
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n📁 Detailed results saved: {results_file}")
    
    # Return appropriate exit code
    if results['overall_status'] == 'PASS':
        print(f"\n🎉 VALIDATION PASSED - System ready for production!")
        return 0
    else:
        print(f"\n❌ VALIDATION FAILED - Address critical issues before deployment")
        return 1

if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
