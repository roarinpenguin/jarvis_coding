#!/usr/bin/env python3
"""
Comprehensive Validation Test for All Generator-Parser Alignment Fixes
Tests all Phase 1, 2, and 3 improvements to measure actual success rate
"""

import json
import subprocess
import sys
import os
from datetime import datetime
import importlib.util

# Add event_generators to path
sys.path.insert(0, '/Users/nathanial.smalley/projects/jarvis_coding')
sys.path.insert(0, '/Users/nathanial.smalley/projects/jarvis_coding/event_generators/shared')

def test_generator(generator_path, generator_name):
    """Test a single generator and return results"""
    try:
        # Import the generator module
        spec = importlib.util.spec_from_file_location(generator_name, generator_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the log generation function
        func_name = f"{generator_name.replace('_', '')}_log"
        if not hasattr(module, func_name):
            # Try alternate naming
            func_name = f"{generator_name}_log"
            if not hasattr(module, func_name):
                return {"status": "NO_FUNCTION", "error": f"No function {func_name} found"}
        
        # Generate a log
        log_func = getattr(module, func_name)
        log_data = log_func()
        
        # Validate output
        if isinstance(log_data, dict):
            # Check for Star Trek themes
            log_str = json.dumps(log_data) if isinstance(log_data, dict) else str(log_data)
            has_star_trek = any(name in log_str.lower() for name in 
                               ['picard', 'worf', 'data', 'laforge', 'crusher', 'riker', 'starfleet', 'enterprise'])
            
            return {
                "status": "SUCCESS",
                "format": "JSON" if isinstance(log_data, dict) else "OTHER",
                "field_count": len(log_data) if isinstance(log_data, dict) else 0,
                "has_star_trek": has_star_trek,
                "sample_fields": list(log_data.keys())[:5] if isinstance(log_data, dict) else []
            }
        elif isinstance(log_data, str):
            # Check if it's JSON string
            try:
                json_data = json.loads(log_data)
                return {
                    "status": "SUCCESS",
                    "format": "JSON_STRING",
                    "field_count": len(json_data) if isinstance(json_data, dict) else 0,
                    "has_star_trek": any(name in log_data.lower() for name in 
                                        ['picard', 'worf', 'data', 'laforge', 'crusher', 'riker', 'starfleet', 'enterprise']),
                    "sample_fields": list(json_data.keys())[:5] if isinstance(json_data, dict) else []
                }
            except:
                return {
                    "status": "SUCCESS",
                    "format": "SYSLOG" if ">" in log_data else "KEY_VALUE" if "=" in log_data else "OTHER",
                    "field_count": 0,
                    "has_star_trek": any(name in log_data.lower() for name in 
                                        ['picard', 'worf', 'data', 'laforge', 'crusher', 'riker', 'starfleet', 'enterprise']),
                    "output_sample": log_data[:200]
                }
        else:
            return {"status": "UNKNOWN_FORMAT", "type": str(type(log_data))}
            
    except Exception as e:
        return {"status": "ERROR", "error": str(e)}

def check_parser_mapping(generator_name):
    """Check if generator has proper parser mapping in hec_sender.py"""
    try:
        # Set dummy token to avoid import error
        os.environ['S1_HEC_TOKEN'] = 'dummy_token_for_testing'
        
        # Import hec_sender to check mappings
        spec = importlib.util.spec_from_file_location(
            "hec_sender", 
            "/Users/nathanial.smalley/projects/jarvis_coding/event_generators/shared/hec_sender.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if generator is in GENERATOR_MAP
        if hasattr(module, 'GENERATOR_MAP'):
            has_generator = generator_name in module.GENERATOR_MAP
        else:
            has_generator = False
            
        # Check if it has a sourcetype mapping
        if hasattr(module, 'SOURCETYPE_MAP'):
            has_parser = generator_name in module.SOURCETYPE_MAP
            parser_name = module.SOURCETYPE_MAP.get(generator_name, "")
        else:
            has_parser = False
            parser_name = ""
            
        # Check marketplace mappings
        if hasattr(module, 'MARKETPLACE_PARSERS'):
            is_marketplace = parser_name in module.MARKETPLACE_PARSERS.values()
        else:
            is_marketplace = False
            
        return {
            "has_generator": has_generator,
            "has_parser_mapping": has_parser,
            "parser_name": parser_name,
            "is_marketplace": is_marketplace
        }
    except Exception as e:
        return {
            "has_generator": False,
            "has_parser_mapping": False,
            "parser_name": "",
            "error": str(e)
        }

def main():
    print("=" * 80)
    print("COMPREHENSIVE VALIDATION TEST - ALL PHASES")
    print("=" * 80)
    print(f"Test run: {datetime.now()}\n")
    
    # Define all generators we've fixed across phases
    phase1_fixes = [
        ("identity_access", "okta_authentication"),
        ("endpoint_security", "crowdstrike_falcon"),
        ("endpoint_security", "sentinelone_endpoint"),
        ("network_security", "paloalto_firewall")
    ]
    
    phase2_fixes = [
        ("cloud_infrastructure", "aws_route53"),
        ("identity_access", "microsoft_365_collaboration"),
        ("identity_access", "microsoft_365_defender"),
        ("network_security", "cisco_duo"),
        ("network_security", "cisco_fmc")
    ]
    
    phase3_fixes = [
        ("cloud_infrastructure", "aws_cloudtrail"),
        ("cloud_infrastructure", "aws_guardduty"),
        ("cloud_infrastructure", "aws_vpcflowlogs"),
        ("network_security", "cisco_ironport"),
        ("cloud_infrastructure", "google_workspace"),
        ("web_security", "cloudflare_general"),
        ("email_security", "abnormal_security"),
        ("web_security", "zscaler_dns_firewall")
    ]
    
    all_results = {
        "phase1": {},
        "phase2": {},
        "phase3": {},
        "summary": {}
    }
    
    # Test Phase 1 - Name Mapping Fixes
    print("PHASE 1 - Name Mapping Fixes")
    print("-" * 40)
    phase1_success = 0
    for category, generator in phase1_fixes:
        mapping = check_parser_mapping(generator)
        status = "✅" if mapping["has_parser_mapping"] else "❌"
        print(f"{status} {generator}: Parser={mapping['parser_name'] or 'NONE'}")
        all_results["phase1"][generator] = mapping
        if mapping["has_parser_mapping"]:
            phase1_success += 1
    
    print(f"\nPhase 1 Result: {phase1_success}/{len(phase1_fixes)} mappings fixed")
    
    # Test Phase 2 - Format Conversions
    print("\nPHASE 2 - Format Conversions to JSON")
    print("-" * 40)
    phase2_success = 0
    for category, generator in phase2_fixes:
        path = f"/Users/nathanial.smalley/projects/jarvis_coding/event_generators/{category}/{generator}.py"
        if os.path.exists(path):
            result = test_generator(path, generator)
            is_json = result.get("format", "").startswith("JSON")
            status = "✅" if result["status"] == "SUCCESS" and is_json else "❌"
            print(f"{status} {generator}: Format={result.get('format', 'ERROR')}, Fields={result.get('field_count', 0)}")
            all_results["phase2"][generator] = result
            if result["status"] == "SUCCESS" and is_json:
                phase2_success += 1
        else:
            print(f"❌ {generator}: File not found")
            all_results["phase2"][generator] = {"status": "FILE_NOT_FOUND"}
    
    print(f"\nPhase 2 Result: {phase2_success}/{len(phase2_fixes)} converted to JSON")
    
    # Test Phase 3 - AWS Mappings + More Conversions
    print("\nPHASE 3 - AWS Marketplace + JSON Conversions")
    print("-" * 40)
    phase3_success = 0
    for category, generator in phase3_fixes:
        # Check mapping for AWS services
        if generator.startswith("aws_"):
            mapping = check_parser_mapping(generator)
            is_success = mapping["has_parser_mapping"] and mapping.get("is_marketplace", False)
            status = "✅" if is_success else "❌"
            print(f"{status} {generator}: Marketplace={mapping.get('is_marketplace', False)}, Parser={mapping['parser_name'] or 'NONE'}")
            all_results["phase3"][generator] = mapping
            if is_success:
                phase3_success += 1
        else:
            # Test generator format
            path = f"/Users/nathanial.smalley/projects/jarvis_coding/event_generators/{category}/{generator}.py"
            if os.path.exists(path):
                result = test_generator(path, generator)
                is_json = result.get("format", "").startswith("JSON")
                status = "✅" if result["status"] == "SUCCESS" and is_json else "❌"
                print(f"{status} {generator}: Format={result.get('format', 'ERROR')}, Fields={result.get('field_count', 0)}")
                all_results["phase3"][generator] = result
                if result["status"] == "SUCCESS" and is_json:
                    phase3_success += 1
            else:
                print(f"❌ {generator}: File not found")
                all_results["phase3"][generator] = {"status": "FILE_NOT_FOUND"}
    
    print(f"\nPhase 3 Result: {phase3_success}/{len(phase3_fixes)} fixes successful")
    
    # Calculate overall success
    total_fixes = len(phase1_fixes) + len(phase2_fixes) + len(phase3_fixes)
    total_success = phase1_success + phase2_success + phase3_success
    success_rate = (total_success / total_fixes * 100) if total_fixes > 0 else 0
    
    print("\n" + "=" * 80)
    print("COMPREHENSIVE VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Phase 1 (Name Mappings):     {phase1_success}/{len(phase1_fixes)} ✅")
    print(f"Phase 2 (Format Conversions): {phase2_success}/{len(phase2_fixes)} ✅")
    print(f"Phase 3 (AWS + Conversions):  {phase3_success}/{len(phase3_fixes)} ✅")
    print("-" * 40)
    print(f"TOTAL:                        {total_success}/{total_fixes} ✅")
    print(f"Overall Success Rate:         {success_rate:.1f}%")
    
    # Estimate parser success improvement
    baseline_success = 38.7  # Starting success rate
    expected_improvement = 31.3  # Expected total improvement
    actual_improvement = (success_rate / 100) * expected_improvement
    estimated_success = baseline_success + actual_improvement
    
    print("\n📊 ESTIMATED PARSER SUCCESS RATE:")
    print(f"Baseline:                     {baseline_success:.1f}%")
    print(f"Expected Improvement:         +{expected_improvement:.1f}%")
    print(f"Fix Success Rate:             {success_rate:.1f}%")
    print(f"Estimated Current Success:    {estimated_success:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 EXCELLENT! All phases validated successfully!")
    elif success_rate >= 70:
        print("\n✅ GOOD! Most fixes are working correctly.")
    else:
        print("\n⚠️  Some fixes need attention.")
    
    # Save detailed results
    all_results["summary"] = {
        "test_timestamp": datetime.now().isoformat(),
        "phase1_success": f"{phase1_success}/{len(phase1_fixes)}",
        "phase2_success": f"{phase2_success}/{len(phase2_fixes)}",
        "phase3_success": f"{phase3_success}/{len(phase3_fixes)}",
        "total_success": f"{total_success}/{total_fixes}",
        "success_rate": f"{success_rate:.1f}%",
        "estimated_parser_success": f"{estimated_success:.1f}%"
    }
    
    with open("comprehensive_validation_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print("\n📁 Detailed results saved to: comprehensive_validation_results.json")
    print("=" * 80)

if __name__ == "__main__":
    main()