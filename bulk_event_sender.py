#!/usr/bin/env python3
"""
Bulk Event Sender - Sends substantial volumes of events to SentinelOne
Sends 5-10 events per generator to ensure good data volume for analysis
"""
import subprocess
import sys
import os
import json
import time
from datetime import datetime

# Set HEC token
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'

# High-priority generators for substantial event volumes
HIGH_PRIORITY_COMMUNITY = [
    "fortinet_fortigate", "zscaler", "aws_cloudtrail", "aws_vpcflowlogs", "aws_guardduty",
    "microsoft_azuread", "okta_authentication", "cisco_asa", "cisco_umbrella", 
    "crowdstrike_falcon", "cyberark_pas", "darktrace", "netskope", "mimecast",
    "corelight_conn", "corelight_http", "corelight_ssl", "sentinelone_endpoint",
    "cisco_fmc", "cisco_ios", "paloalto_firewall", "aws_waf", "cisco_ironport",
    "microsoft_365_defender", "pingfederate", "zscaler_dns_firewall", "cisco_duo",
    "checkpoint", "cisco_firewall_threat_defense", "zscaler_private_access"
]

# Key marketplace parsers for enhanced OCSF testing
KEY_MARKETPLACE_PARSERS = [
    "marketplace-awscloudtrail-latest",
    "marketplace-awselasticloadbalancer-latest", 
    "marketplace-checkpointfirewall-latest",
    "marketplace-ciscofirewallthreatdefense-latest",
    "marketplace-corelight-conn-latest",
    "marketplace-corelight-http-latest",
    "marketplace-fortinetfortigate-latest",
    "marketplace-paloaltonetworksfirewall-latest",
    "marketplace-zscalerinternetaccess-latest",
    "marketplace-zscalerprivateaccess-latest"
]

def send_bulk_events(product, count=5, is_marketplace=False):
    """Send bulk events for a product"""
    try:
        if is_marketplace:
            cmd = ['.venv/bin/python', 'event_python_writer/hec_sender.py', 
                   '--marketplace-parser', product, '--count', str(count)]
            product_type = "MARKETPLACE"
        else:
            cmd = ['.venv/bin/python', 'event_python_writer/hec_sender.py', 
                   '--product', product, '--count', str(count)]
            product_type = "COMMUNITY"
        
        print(f"📤 Sending {count} events from {product_type} {product}...", end=" ", flush=True)
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60,
                              cwd='/Users/nathanial.smalley/projects/jarvis_coding')
        
        if result.returncode == 0:
            # Count successful responses
            success_count = result.stdout.count("'code': 0")
            if success_count > 0:
                print(f"✅ {success_count} events sent successfully")
                return success_count, 0
            else:
                print(f"❌ No successful responses")
                return 0, count
        else:
            error_msg = result.stderr.strip()[:100] if result.stderr else "Unknown error"
            print(f"❌ Failed: {error_msg}")
            return 0, count
            
    except subprocess.TimeoutExpired:
        print(f"❌ Timeout after 60 seconds")
        return 0, count
    except Exception as e:
        print(f"❌ Error: {str(e)[:100]}")
        return 0, count

def main():
    print("=" * 80)
    print("🚀 BULK EVENT SENDER - SUBSTANTIAL VOLUME TO SENTINELONE")
    print("=" * 80)
    print(f"Start time: {datetime.now().isoformat()}")
    print(f"Target: ~{len(HIGH_PRIORITY_COMMUNITY) * 5 + len(KEY_MARKETPLACE_PARSERS) * 5} total events")
    print()
    
    total_sent = 0
    total_failed = 0
    
    # Send substantial volumes from high-priority community generators
    print(f"📊 SENDING BULK EVENTS FROM {len(HIGH_PRIORITY_COMMUNITY)} HIGH-PRIORITY COMMUNITY GENERATORS")
    print("-" * 80)
    
    for i, product in enumerate(HIGH_PRIORITY_COMMUNITY, 1):
        # Send 5-8 events per generator for good volume
        event_count = 5 if i <= 15 else 8 if i <= 25 else 5
        
        print(f"[{i:2d}/{len(HIGH_PRIORITY_COMMUNITY)}] ", end="")
        sent, failed = send_bulk_events(product, event_count)
        total_sent += sent
        total_failed += failed
        
        # Brief delay to avoid overwhelming HEC
        time.sleep(0.5)
    
    print(f"\n🏪 SENDING BULK EVENTS FROM {len(KEY_MARKETPLACE_PARSERS)} KEY MARKETPLACE PARSERS")
    print("-" * 80)
    
    for i, parser in enumerate(KEY_MARKETPLACE_PARSERS, 1):
        # Send 5-7 events per marketplace parser
        event_count = 7 if 'cisco' in parser or 'aws' in parser else 5
        
        print(f"[{i:2d}/{len(KEY_MARKETPLACE_PARSERS)}] ", end="")
        sent, failed = send_bulk_events(parser, event_count, is_marketplace=True)
        total_sent += sent
        total_failed += failed
        
        # Brief delay to avoid overwhelming HEC
        time.sleep(0.5)
    
    # Send additional events from remaining community generators
    remaining_generators = [
        "abnormal_security", "armis", "buildkite", "extrahop", "google_workspace",
        "imperva_waf", "juniper_networks", "linux_auth", "microsoft_365_collaboration",
        "proofpoint", "tailscale", "vectra_ai", "wiz_cloud", "jamf_protect",
        "hashicorp_vault", "iis_w3c", "rsa_adaptive", "veeam_backup"
    ]
    
    print(f"\n📈 SENDING ADDITIONAL EVENTS FROM {len(remaining_generators)} MORE GENERATORS")
    print("-" * 80)
    
    for i, product in enumerate(remaining_generators, 1):
        print(f"[{i:2d}/{len(remaining_generators)}] ", end="")
        sent, failed = send_bulk_events(product, 3)  # 3 events each
        total_sent += sent
        total_failed += failed
        time.sleep(0.3)
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 BULK SENDING COMPLETE")
    print("=" * 80)
    
    total_attempted = total_sent + total_failed
    success_rate = (total_sent / total_attempted * 100) if total_attempted > 0 else 0
    
    print(f"📤 Total Events Attempted: {total_attempted}")
    print(f"✅ Total Events Sent Successfully: {total_sent}")
    print(f"❌ Total Failed: {total_failed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    
    print(f"\n🔍 EXPECTED IN SENTINELONE:")
    print(f"   • High-Priority Community: {len(HIGH_PRIORITY_COMMUNITY)} generators × 5-8 events")
    print(f"   • Marketplace Parsers: {len(KEY_MARKETPLACE_PARSERS)} parsers × 5-7 events")  
    print(f"   • Additional Community: {len(remaining_generators)} generators × 3 events")
    print(f"   • **Total Expected: ~{total_sent} events across ~{len(HIGH_PRIORITY_COMMUNITY) + len(KEY_MARKETPLACE_PARSERS) + len(remaining_generators)} different products**")
    
    print(f"\n⏰ Events should appear in SentinelOne within 2-5 minutes")
    print(f"🔍 Look for events from timestamp: {datetime.now().isoformat()}")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_attempted": total_attempted,
        "total_sent": total_sent,
        "total_failed": total_failed,
        "success_rate": success_rate,
        "generators_tested": len(HIGH_PRIORITY_COMMUNITY) + len(KEY_MARKETPLACE_PARSERS) + len(remaining_generators)
    }
    
    with open('bulk_event_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📁 Results saved to: bulk_event_results.json")
    print("✅ Bulk event sending complete!")

if __name__ == "__main__":
    main()