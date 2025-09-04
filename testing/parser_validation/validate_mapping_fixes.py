#!/usr/bin/env python3
"""
Validate Generator-Parser Mapping Fixes
=======================================

This script validates that the critical mapping fixes have been applied correctly
and tests each fixed generator-parser pair.

Generated automatically by apply_generator_parser_fixes.py
"""

import sys
import os
import importlib
import json

# Add generator category paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
generator_root = os.path.join(current_dir, "event_generators")
for category in ['cloud_infrastructure', 'network_security', 'endpoint_security', 
                 'identity_access', 'email_security', 'web_security', 'infrastructure']:
    sys.path.insert(0, os.path.join(generator_root, category))

# Fixed mappings to test
FIXED_MAPPINGS = {
    "okta_authentication": "okta_ocsf_logs-latest",
    "crowdstrike_falcon": "crowdstrike_endpoint-latest",
    "sentinelone_endpoint": "singularityidentity_singularityidentity_logs-latest",
    "microsoft_azure_ad_signin": "microsoft_azure_ad_logs-latest",
    "paloalto_firewall": "paloalto_paloalto_logs-latest",
    "microsoft_defender_email": "microsoft_eventhub_defender_email_logs-latest"
}

def test_generator(generator_name: str) -> bool:
    """Test that a generator can be loaded and executed."""
    try:
        # Import the generator module
        module = importlib.import_module(generator_name)
        
        # Find the main generator function
        func_name = f"{generator_name}_log"
        if hasattr(module, func_name):
            generator_func = getattr(module, func_name)
            
            # Test execution
            event = generator_func()
            
            # Validate output
            if isinstance(event, (str, dict)):
                print(f"✅ {generator_name}: Generated {type(event).__name__} event")
                return True
            else:
                print(f"❌ {generator_name}: Invalid event type {type(event)}")
                return False
        else:
            print(f"❌ {generator_name}: Function {func_name} not found")
            return False
            
    except Exception as e:
        print(f"❌ {generator_name}: Import/execution error: {e}")
        return False

def validate_parser_exists(parser_name: str) -> bool:
    """Validate that a parser exists."""
    community_path = os.path.join(current_dir, "parsers", "community", parser_name)
    marketplace_path = os.path.join(current_dir, "parsers", "sentinelone", parser_name)
    
    exists = os.path.exists(community_path) or os.path.exists(marketplace_path)
    if exists:
        print(f"✅ Parser exists: {parser_name}")
    else:
        print(f"❌ Parser missing: {parser_name}")
    
    return exists

def main():
    """Run validation tests for all fixed mappings."""
    print("🔍 Validating Generator-Parser Mapping Fixes")
    print("=" * 50)
    
    total_tests = len(FIXED_MAPPINGS)
    passed_tests = 0
    
    for generator, parser in FIXED_MAPPINGS.items():
        print(f"\nTesting: {generator} → {parser}")
        print("-" * 40)
        
        generator_ok = test_generator(generator)
        parser_ok = validate_parser_exists(parser)
        
        if generator_ok and parser_ok:
            passed_tests += 1
            print(f"✅ PASS: {generator} → {parser}")
        else:
            print(f"❌ FAIL: {generator} → {parser}")
    
    print(f"\n📊 Results: {passed_tests}/{total_tests} mappings validated")
    print(f"Success rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 All critical mappings are working correctly!")
        return 0
    else:
        print(f"⚠️  {total_tests - passed_tests} mappings need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
