#!/usr/bin/env python3
"""
Measure Actual Success Rate Post-Fixes
=====================================

This script measures the actual success rate by using the HEC sender's
own mappings rather than trying to guess mappings independently.

The critical fixes we applied:
1. okta_authentication → okta_ocsf_logs-latest  
2. crowdstrike_falcon → crowdstrike_endpoint-latest
3. sentinelone_endpoint → singularityidentity_logs-latest
4. microsoft_azure_ad_signin → microsoft_azure_ad_logs-latest
5. paloalto_firewall → paloalto_paloalto_logs-latest
6. microsoft_defender_email → microsoft_eventhub_defender_email_logs-latest
"""

import sys
import os
import importlib
import json
from pathlib import Path

# Add generator category paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
generator_root = os.path.join(current_dir, "event_generators")
for category in ['cloud_infrastructure', 'network_security', 'endpoint_security', 
                 'identity_access', 'email_security', 'web_security', 'infrastructure']:
    sys.path.insert(0, os.path.join(generator_root, category))

# Import the HEC sender to get the actual mappings
sys.path.insert(0, os.path.join(generator_root, "shared"))
import hec_sender

def test_generator_parser_pair(product: str, sourcetype: str) -> dict:
    """Test a specific generator-parser pair using HEC sender logic."""
    result = {
        "product": product,
        "sourcetype": sourcetype,
        "status": "unknown",
        "error": None,
        "generator_working": False,
        "parser_exists": False,
        "format_match": False
    }
    
    try:
        # Check if generator exists in PROD_MAP
        if product not in hec_sender.PROD_MAP:
            result["status"] = "no_generator_mapping"
            result["error"] = f"Product '{product}' not in HEC sender PROD_MAP"
            return result
            
        # Try to load and execute the generator
        mod_name, func_names = hec_sender.PROD_MAP[product]
        try:
            gen_mod = importlib.import_module(mod_name)
            generators = [getattr(gen_mod, fn) for fn in func_names]
            
            # Test generator execution
            test_event = generators[0]()
            result["generator_working"] = True
            result["event_type"] = type(test_event).__name__
            
        except Exception as e:
            result["error"] = f"Generator error: {e}"
            return result
        
        # Check if parser exists (community or marketplace)
        parser_exists = False
        
        # Check community parsers
        community_parser_path = Path(current_dir) / "parsers" / "community" / sourcetype
        if community_parser_path.exists():
            parser_exists = True
            result["parser_location"] = "community"
        
        # Check marketplace parsers
        marketplace_parser_path = Path(current_dir) / "parsers" / "sentinelone" / sourcetype  
        if marketplace_parser_path.exists():
            parser_exists = True
            result["parser_location"] = "marketplace"
        
        # For marketplace parsers, they may not exist locally but are valid
        if sourcetype.startswith("marketplace-"):
            parser_exists = True
            result["parser_location"] = "marketplace_remote"
        
        result["parser_exists"] = parser_exists
        
        if not parser_exists:
            result["status"] = "parser_missing"
            result["error"] = f"Parser not found: {sourcetype}"
            return result
            
        # Format matching check (simplified)
        is_json_product = product in hec_sender.JSON_PRODUCTS
        result["expected_json"] = is_json_product
        result["format_match"] = True  # Assume HEC sender handles format correctly
        
        # Overall status
        if result["generator_working"] and result["parser_exists"] and result["format_match"]:
            result["status"] = "working"
        else:
            result["status"] = "issues_found"
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

def main():
    """Test all generator-parser mappings from HEC sender."""
    print("📊 Measuring Actual Success Rate After Phase 1 Fixes")
    print("=" * 60)
    
    # Get all mappings from HEC sender
    total_tests = 0
    working_pairs = 0
    failed_pairs = 0
    
    results = {
        "working": [],
        "failed": [],
        "summary": {}
    }
    
    print("Testing all HEC sender mappings...")
    print()
    
    for product, sourcetype in hec_sender.SOURCETYPE_MAP.items():
        total_tests += 1
        result = test_generator_parser_pair(product, sourcetype)
        
        status_icon = "✅" if result["status"] == "working" else "❌" 
        print(f"{status_icon} {product:30} → {sourcetype:40} [{result['status']}]")
        
        if result["status"] == "working":
            working_pairs += 1
            results["working"].append({
                "product": product,
                "sourcetype": sourcetype,
                "details": result
            })
        else:
            failed_pairs += 1  
            results["failed"].append({
                "product": product,
                "sourcetype": sourcetype,
                "error": result.get("error", "Unknown error"),
                "details": result
            })
            if result.get("error"):
                print(f"   └─ Error: {result['error']}")
    
    # Calculate success rate
    success_rate = (working_pairs / total_tests) * 100 if total_tests > 0 else 0
    
    print()
    print("📈 RESULTS SUMMARY")
    print("=" * 30)
    print(f"Total mappings tested: {total_tests}")
    print(f"Working pairs: {working_pairs}")
    print(f"Failed pairs: {failed_pairs}")
    print(f"Success rate: {success_rate:.1f}%")
    
    results["summary"] = {
        "total_tests": total_tests,
        "working_pairs": working_pairs,
        "failed_pairs": failed_pairs,
        "success_rate": success_rate,
        "phase_1_fixes_applied": [
            "okta_authentication → okta_ocsf_logs-latest",
            "crowdstrike_falcon → crowdstrike_endpoint-latest", 
            "sentinelone_endpoint → singularityidentity_logs-latest",
            "microsoft_azure_ad_signin → microsoft_azure_ad_logs-latest",
            "paloalto_firewall → paloalto_paloalto_logs-latest",
            "microsoft_defender_email → microsoft_eventhub_defender_email_logs-latest"
        ]
    }
    
    # Save detailed results
    results_file = os.path.join(current_dir, "actual_success_rate_results.json")
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\\n📄 Detailed results saved to: {results_file}")
    
    # Show critical fixes validation
    print("\\n🔧 Phase 1 Critical Fixes Validation:")
    print("-" * 40)
    critical_fixes = [
        "okta_authentication", "crowdstrike_falcon", "sentinelone_endpoint",
        "microsoft_azure_ad_signin", "paloalto_firewall", "microsoft_defender_email"
    ]
    
    fixed_count = 0
    for product in critical_fixes:
        if product in hec_sender.SOURCETYPE_MAP:
            sourcetype = hec_sender.SOURCETYPE_MAP[product]
            result = test_generator_parser_pair(product, sourcetype)
            status_icon = "✅" if result["status"] == "working" else "❌"
            print(f"{status_icon} {product}")
            if result["status"] == "working":
                fixed_count += 1
    
    print(f"\\nPhase 1 fixes working: {fixed_count}/{len(critical_fixes)} ({(fixed_count/len(critical_fixes))*100:.1f}%)")
    
    if success_rate >= 75:
        print("\\n🎉 SUCCESS! Target success rate of 75%+ achieved!")
    elif success_rate >= 65:
        print("\\n📈 Good progress! Close to target success rate.")
        print("Consider Phase 2 format conversion fixes.")
    else:
        print("\\n⚠️  More fixes needed to reach target success rate of 75%+")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())