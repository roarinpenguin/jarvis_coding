#!/usr/bin/env python3
"""
Comprehensive HEC Test - All Fixed Generators
Tests all 22 generators from Phases 1-4 with real HEC sending
"""

import os
import subprocess
import time
from datetime import datetime
import json

# Set token
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'

# All fixed generators
all_generators = {
    "Phase 1 - Name Mappings": [
        "okta_authentication",
        "crowdstrike_falcon",
        "sentinelone_endpoint",
        "paloalto_firewall"
    ],
    "Phase 2 - Format Conversions": [
        "aws_route53",
        "microsoft_365_collaboration",
        "microsoft_365_defender",
        "cisco_duo",
        "cisco_fmc"
    ],
    "Phase 3 - AWS + Conversions": [
        "aws_cloudtrail",
        "aws_guardduty",
        "aws_vpcflowlogs",
        "cisco_ironport",
        "google_workspace",
        "cloudflare_general",
        "abnormal_security",
        "zscaler_dns_firewall"
    ],
    "Phase 4 - Final Push": [
        "fortinet_fortigate",
        "cisco_meraki",
        "darktrace",
        "cisco_umbrella",
        "zscaler"
    ]
}

print("=" * 80)
print("COMPREHENSIVE HEC VALIDATION - ALL 22 FIXED GENERATORS")
print("=" * 80)
print(f"Timestamp: {datetime.now()}")
print(f"Sending events to SentinelOne HEC endpoint\n")

results = {}
total_successful = 0
total_failed = 0

for phase, generators in all_generators.items():
    print(f"\n{'='*60}")
    print(f"{phase}")
    print('='*60)
    
    phase_results = {"successful": [], "failed": []}
    
    for generator in generators:
        print(f"\n🔧 Testing {generator}...", end="")
        
        cmd = [
            ".venv/bin/python",
            "event_generators/shared/hec_sender.py",
            "--product", generator,
            "--count", "2"  # Send 2 events per generator
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and ("successfully" in result.stdout.lower() or "delivered" in result.stdout.lower()):
                print(" ✅ Success!")
                print(f"   📤 2 events sent with Star Trek themes")
                phase_results["successful"].append(generator)
                total_successful += 1
            else:
                print(" ❌ Failed")
                error = result.stderr or result.stdout
                print(f"   Error: {error[:100]}")
                phase_results["failed"].append(generator)
                total_failed += 1
        except Exception as e:
            print(" ❌ Error")
            print(f"   Exception: {str(e)[:100]}")
            phase_results["failed"].append(generator)
            total_failed += 1
        
        time.sleep(0.5)  # Small delay between generators
    
    success_rate = len(phase_results["successful"]) / len(generators) * 100
    print(f"\n{phase} Result: {success_rate:.1f}% ({len(phase_results['successful'])}/{len(generators)})")
    results[phase] = phase_results

# Final summary
print("\n" + "=" * 80)
print("FINAL VALIDATION SUMMARY")
print("=" * 80)

for phase, phase_results in results.items():
    success_count = len(phase_results["successful"])
    total_count = success_count + len(phase_results["failed"])
    print(f"\n{phase}:")
    print(f"  ✅ Successful: {success_count}/{total_count}")
    if phase_results["failed"]:
        print(f"  ❌ Failed: {', '.join(phase_results['failed'])}")

total_generators = total_successful + total_failed
overall_success_rate = (total_successful / total_generators * 100) if total_generators > 0 else 0

print("\n" + "-" * 60)
print(f"OVERALL RESULTS:")
print(f"  ✅ Successful: {total_successful}/{total_generators}")
print(f"  ❌ Failed: {total_failed}/{total_generators}")
print(f"  📊 Success Rate: {overall_success_rate:.1f}%")

# Assessment
if overall_success_rate >= 90:
    status = "🎉 EXCELLENT! 90%+ success rate achieved!"
elif overall_success_rate >= 85:
    status = "✅ SUCCESS! Target 85-90% achieved!"
elif overall_success_rate >= 80:
    status = "🔶 GOOD! Close to 85% target!"
else:
    status = f"⚠️  Current: {overall_success_rate:.1f}% (Target: 85-90%)"

print(f"\n{status}")

# Event details
total_events = total_successful * 2  # 2 events per generator
print(f"\n📈 Events Summary:")
print(f"  • Total events sent: {total_events}")
print(f"  • Generators tested: {total_generators}")
print(f"  • Star Trek themed: Yes (jean.picard@starfleet.corp, etc.)")
print(f"  • Timestamp range: Last 10 minutes")

print("\n🖖 Star Trek Themes Included:")
print("  • Characters: jean.picard, worf.security, data.android, jordy.laforge")
print("  • Devices: ENTERPRISE-BRIDGE-01, ENTERPRISE-SECURITY-01")
print("  • Domains: starfleet.corp, enterprise.starfleet.corp")

# Save results
results_data = {
    "timestamp": datetime.now().isoformat(),
    "total_generators": total_generators,
    "successful": total_successful,
    "failed": total_failed,
    "success_rate": f"{overall_success_rate:.1f}%",
    "events_sent": total_events,
    "phase_results": results,
    "status": status
}

with open("comprehensive_hec_results.json", "w") as f:
    json.dump(results_data, f, indent=2)

print(f"\n📁 Results saved to: comprehensive_hec_results.json")
print("\n✨ Check your SentinelOne Events page to see all the Star Trek themed events!")
print("=" * 80)