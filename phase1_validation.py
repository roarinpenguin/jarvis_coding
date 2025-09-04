#!/usr/bin/env python3
"""Phase 1 Critical Fixes Validation Script

This script validates the Phase 1 critical fixes for generator-parser alignment.
It tests the specific fixes implemented:
1. AWS CloudTrail marketplace parser mapping
2. AWS GuardDuty marketplace parser mapping  
3. AWS ELB marketplace parser mapping
4. Okta authentication parser name fix
5. CrowdStrike Falcon parser name fix

Expected outcome: Improved success rate from 21% to 40%+
"""

import os
import subprocess
import sys
import time

# Set the HEC token for testing
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'

def test_generator(test_name, command):
    """Test a single generator and return success status"""
    print(f"🧪 Testing {test_name}...")
    try:
        # Ensure environment is passed to subprocess
        env = os.environ.copy()
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, env=env)
        if result.returncode == 0 and ('Success' in result.stdout or '"code": 0' in result.stdout):
            print(f"✅ {test_name}: SUCCESS")
            return True
        else:
            print(f"❌ {test_name}: FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            if result.stdout:
                print(f"   Output: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {test_name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {test_name}: ERROR - {e}")
        return False

def main():
    print("🚀 Phase 1 Critical Fixes Validation")
    print("=" * 50)
    
    # Phase 1 critical tests
    tests = [
        ("AWS CloudTrail Marketplace Parser", 
         "python3 event_generators/shared/hec_sender.py --marketplace-parser marketplace-awscloudtrail-latest --count 1"),
        ("AWS GuardDuty Marketplace Parser", 
         "python3 event_generators/shared/hec_sender.py --marketplace-parser marketplace-awsguardduty-latest --count 1"),
        ("AWS ELB Marketplace Parser", 
         "python3 event_generators/shared/hec_sender.py --marketplace-parser marketplace-awselasticloadbalancer-latest --count 1"),
        ("Okta Authentication Fixed Mapping", 
         "python3 event_generators/shared/hec_sender.py --product okta_authentication --count 1"),
        ("CrowdStrike Falcon Fixed Mapping", 
         "python3 event_generators/shared/hec_sender.py --product crowdstrike_falcon --count 1"),
    ]
    
    # Additional enterprise critical tests
    additional_tests = [
        ("Fortinet FortiGate Marketplace", 
         "python3 event_generators/shared/hec_sender.py --product fortinet_fortigate --count 1"),
        ("Zscaler Marketplace", 
         "python3 event_generators/shared/hec_sender.py --product zscaler --count 1"),
        ("AWS VPC Flow Logs Marketplace", 
         "python3 event_generators/shared/hec_sender.py --marketplace-parser marketplace-awsvpcflowlogs-latest --count 1"),
        ("Microsoft Azure AD", 
         "python3 event_generators/shared/hec_sender.py --product microsoft_azuread --count 1"),
        ("Microsoft 365 Collaboration", 
         "python3 event_generators/shared/hec_sender.py --product microsoft_365_collaboration --count 1"),
    ]
    
    print("\n📊 PHASE 1 CRITICAL FIXES:")
    phase1_passed = 0
    for test_name, command in tests:
        if test_generator(test_name, command):
            phase1_passed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    print(f"\n📊 Phase 1 Results: {phase1_passed}/{len(tests)} critical fixes working ({phase1_passed/len(tests)*100:.1f}%)")
    
    print("\n📊 ADDITIONAL ENTERPRISE TESTS:")
    additional_passed = 0
    for test_name, command in additional_tests:
        if test_generator(test_name, command):
            additional_passed += 1
        time.sleep(0.5)  # Brief pause between tests
    
    total_tests = len(tests) + len(additional_tests)
    total_passed = phase1_passed + additional_passed
    final_success_rate = total_passed / total_tests * 100
    
    print("\n" + "=" * 50)
    print("🎯 FINAL VALIDATION RESULTS")
    print("=" * 50)
    print(f"Phase 1 Critical Fixes: {phase1_passed}/{len(tests)} ({phase1_passed/len(tests)*100:.1f}%)")
    print(f"Additional Enterprise Tests: {additional_passed}/{len(additional_tests)} ({additional_passed/len(additional_tests)*100:.1f}%)")
    print(f"Overall Success Rate: {total_passed}/{total_tests} ({final_success_rate:.1f}%)")
    
    if final_success_rate >= 40:
        print("✅ SUCCESS: Target of 40%+ achieved!")
        print("🎉 Phase 1 critical fixes implementation successful!")
    else:
        print("⚠️  WARNING: Success rate below 40% target")
        print("🔧 Additional fixes may be needed")
    
    return final_success_rate >= 40

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)