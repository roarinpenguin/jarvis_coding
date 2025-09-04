#!/usr/bin/env python3
"""
Phase 2 Format Conversion Fixes Verification Script

This script verifies that all 5 Phase 2 generators have been successfully
converted to JSON format for improved parser compatibility.

Expected improvement: +10-15% success rate (from 47.2% to 57%+)
"""

import json
import sys
import traceback
from pathlib import Path

# Phase 2 target generators and their expected format
PHASE2_GENERATORS = [
    {
        "name": "AWS Route 53",
        "path": "event_generators/cloud_infrastructure/aws_route53.py",
        "function": "aws_route53_log",
        "original_format": "syslog",
        "target_format": "JSON"
    },
    {
        "name": "Microsoft 365 Collaboration", 
        "path": "event_generators/identity_access/microsoft_365_collaboration.py",
        "function": "microsoft_365_collaboration_log",
        "original_format": "key-value",
        "target_format": "JSON"
    },
    {
        "name": "Microsoft 365 Defender",
        "path": "event_generators/identity_access/microsoft_365_defender.py", 
        "function": "microsoft_365_defender_log",
        "original_format": "key-value",
        "target_format": "JSON"
    },
    {
        "name": "Cisco Duo",
        "path": "event_generators/network_security/cisco_duo.py",
        "function": "cisco_duo_log", 
        "original_format": "key-value",
        "target_format": "JSON"
    },
    {
        "name": "Cisco FMC",
        "path": "event_generators/network_security/cisco_fmc.py",
        "function": "cisco_fmc_log",
        "original_format": "syslog", 
        "target_format": "JSON"
    }
]

def verify_generator(generator_info):
    """Verify a single generator produces valid JSON output"""
    print(f"\n🔍 Testing {generator_info['name']}...")
    
    try:
        # Import the module dynamically
        module_path = generator_info['path'].replace('/', '.').replace('.py', '')
        module = __import__(module_path, fromlist=[generator_info['function']])
        
        # Get the generator function
        generator_function = getattr(module, generator_info['function'])
        
        # Generate an event
        event = generator_function()
        
        # Check if it returns a dictionary (JSON-compatible)
        if not isinstance(event, dict):
            print(f"   ❌ FAILED: Function returns {type(event).__name__}, expected dict")
            return False
            
        # Check if it's JSON serializable
        try:
            json_str = json.dumps(event)
            # Parse it back to ensure it's valid JSON
            parsed = json.loads(json_str)
            print(f"   ✅ PASSED: Valid JSON output with {len(event)} fields")
            
            # Check for Star Trek theme integration
            star_trek_indicators = []
            json_str_lower = json_str.lower()
            
            if any(theme in json_str_lower for theme in ['starfleet', 'enterprise', 'picard', 'riker', 'worf', 'data']):
                star_trek_indicators.append("Star Trek themes")
            if any(field in json_str_lower for field in ['timestamp', 'time']):
                star_trek_indicators.append("Proper timestamps")
            if 'datasource' in json_str_lower or 'metadata' in json_str_lower:
                star_trek_indicators.append("SentinelOne attributes")
                
            if star_trek_indicators:
                print(f"   🖖 Includes: {', '.join(star_trek_indicators)}")
                
            return True
            
        except (TypeError, ValueError) as e:
            print(f"   ❌ FAILED: Not JSON serializable - {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: Failed to test generator - {e}")
        traceback.print_exc()
        return False

def main():
    """Main verification function"""
    print("=" * 60)
    print("Phase 2 Format Conversion Fixes Verification")
    print("=" * 60)
    print(f"Testing {len(PHASE2_GENERATORS)} generators for JSON format compatibility...")
    
    results = []
    
    for generator in PHASE2_GENERATORS:
        success = verify_generator(generator)
        results.append({
            'name': generator['name'],
            'success': success,
            'original_format': generator['original_format'],
            'target_format': generator['target_format']
        })
    
    # Summary
    print("\n" + "=" * 60)
    print("PHASE 2 VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"{status} | {result['name']:<25} | {result['original_format']:<10} → {result['target_format']}")
    
    print(f"\n📊 Results: {passed}/{total} generators successfully converted to JSON")
    
    if passed == total:
        print("\n🎉 SUCCESS: All Phase 2 format conversions completed successfully!")
        print("📈 Expected improvement: +10-15% success rate")
        print("🎯 Projected total success rate: 57%+")
        return True
    else:
        print(f"\n⚠️  INCOMPLETE: {total - passed} generators still need conversion")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)