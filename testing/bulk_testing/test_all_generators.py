#!/usr/bin/env python3
"""
Comprehensive test of all generators (community + marketplace)
Tests each generator by sending 1 event to HEC and reports success/failure
"""
import subprocess
import sys
import os
import json
from datetime import datetime

# Set HEC token
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'

# Community generators (from the error message above)
COMMUNITY_PRODUCTS = [
    "fortinet_fortigate", "zscaler", "aws_cloudtrail", "aws_vpcflowlogs", "aws_guardduty",
    "microsoft_azuread", "okta_authentication", "cisco_asa", "cisco_umbrella", "cisco_meraki",
    "crowdstrike_falcon", "cyberark_pas", "darktrace", "proofpoint", "microsoft_365_mgmt_api",
    "netskope", "mimecast", "microsoft_azure_ad_signin", "microsoft_defender_email",
    "beyondtrust_passwordsafe", "hashicorp_vault", "corelight_conn", "corelight_http",
    "corelight_ssl", "corelight_tunnel", "vectra_ai", "tailscale", "extrahop", "armis",
    "sentinelone_endpoint", "sentinelone_identity", "apache_http", "abnormal_security",
    "buildkite", "teleport", "cisco_ise", "google_workspace", "aws_vpc_dns", "cisco_networks",
    "cloudflare_general", "cloudflare_waf", "extreme_networks", "f5_networks", "google_cloud_dns",
    "imperva_waf", "juniper_networks", "ubiquiti_unifi", "zscaler_firewall", "cisco_fmc",
    "cisco_ios", "cisco_isa3000", "incapsula", "manageengine_general", "manch_siem",
    "microsoft_windows_eventlog", "paloalto_prismasase", "sap", "securelink", "aws_waf",
    "aws_route53", "cisco_ironport", "cyberark_conjur", "iis_w3c", "linux_auth",
    "microsoft_365_collaboration", "microsoft_365_defender", "pingfederate", "zscaler_dns_firewall",
    "akamai_cdn", "akamai_dns", "akamai_general", "akamai_sitedefender", "axway_sftp",
    "cisco_duo", "cohesity_backup", "f5_vpn", "github_audit", "harness_ci", "hypr_auth",
    "imperva_sonar", "isc_bind", "isc_dhcp", "jamf_protect", "pingone_mfa", "pingprotect",
    "rsa_adaptive", "veeam_backup", "wiz_cloud", "aws_elasticloadbalancer",
    "beyondtrust_privilegemgmt_windows", "cisco_firewall_threat_defense", "cisco_meraki_flow",
    "manageengine_adauditplus", "microsoft_azure_ad", "microsoft_eventhub_azure_signin",
    "microsoft_eventhub_defender_email", "microsoft_eventhub_defender_emailforcloud",
    "checkpoint", "fortimanager", "infoblox_ddi", "paloalto_firewall", "zscaler_private_access"
]

# Get marketplace parsers
def get_marketplace_parsers():
    """Get list of marketplace parsers from hec_sender.py"""
    try:
        result = subprocess.run([
            '.venv/bin/python', 'event_python_writer/hec_sender.py', 
            '--marketplace-parser', 'invalid-parser'
        ], capture_output=True, text=True, cwd='/Users/nathanial.smalley/projects/jarvis_coding')
        
        # Extract parser list from error message
        output = result.stderr
        if 'Available marketplace parsers:' in output:
            lines = output.split('\n')
            parsers = []
            capture = False
            for line in lines:
                if 'Available marketplace parsers:' in line:
                    capture = True
                    continue
                if capture and line.strip().startswith('marketplace-'):
                    parsers.append(line.strip())
                elif capture and line.strip() == '':
                    break
            return parsers
        return []
    except Exception as e:
        print(f"Error getting marketplace parsers: {e}")
        return []

def test_generator(product, is_marketplace=False, count=2):
    """Test a single generator with small event volume"""
    try:
        if is_marketplace:
            cmd = ['.venv/bin/python', 'event_python_writer/hec_sender.py', 
                   '--marketplace-parser', product, '--count', str(count)]
        else:
            cmd = ['.venv/bin/python', 'event_python_writer/hec_sender.py', 
                   '--product', product, '--count', str(count)]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30,
                              cwd='/Users/nathanial.smalley/projects/jarvis_coding')
        
        if result.returncode == 0 and 'Success' in result.stdout:
            return True, "SUCCESS"
        else:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            return False, error_msg[:100]
            
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    except Exception as e:
        return False, f"ERROR: {str(e)[:100]}"

def main():
    print("=" * 80)
    print("COMPREHENSIVE GENERATOR TEST")
    print("=" * 80)
    print(f"Test started: {datetime.now().isoformat()}")
    print(f"📤 SENDING SUBSTANTIAL EVENT VOLUMES (2 events per generator)")
    print()
    
    # Results tracking
    community_results = {"success": 0, "failed": 0, "failures": [], "events_sent": 0}
    marketplace_results = {"success": 0, "failed": 0, "failures": [], "events_sent": 0}
    
    # Test community generators
    print(f"🔍 TESTING {len(COMMUNITY_PRODUCTS)} COMMUNITY GENERATORS")
    print("-" * 80)
    
    for i, product in enumerate(COMMUNITY_PRODUCTS, 1):
        # Send 5-8 events per generator for substantial volume
        event_count = 2 if i <= 20 else 2 if i <= 50 else 2
        print(f"[{i:3d}/{len(COMMUNITY_PRODUCTS)}] {product:40s} ({event_count} events)", end=" ", flush=True)
        success, message = test_generator(product, count=event_count)
        
        if success:
            print(f"✅ SUCCESS ({success} events)")
            community_results["success"] += 1
            community_results["events_sent"] += event_count
        else:
            print(f"❌ FAILED: {message}")
            community_results["failed"] += 1
            community_results["failures"].append((product, message))
    
    # Test marketplace parsers
    print(f"\n🏪 TESTING MARKETPLACE PARSERS")
    print("-" * 80)
    
    marketplace_parsers = get_marketplace_parsers()
    if not marketplace_parsers:
        # Fallback to known key marketplace parsers
        marketplace_parsers = [
            "marketplace-awscloudtrail-latest",
            "marketplace-awselasticloadbalancer-latest", 
            "marketplace-checkpointfirewall-latest",
            "marketplace-ciscofirewallthreatdefense-latest",
            "marketplace-corelight-conn-latest",
            "marketplace-fortinetfortigate-latest",
            "marketplace-paloaltonetworksfirewall-latest",
            "marketplace-zscalerinternetaccess-latest",
            "marketplace-zscalerprivateaccess-latest"
        ]
    
    for i, parser in enumerate(marketplace_parsers, 1):
        # Send 6-10 events per marketplace parser for substantial volume
        event_count = 10 if 'aws' in parser or 'cisco' in parser else 8 if 'corelight' in parser else 6
        print(f"[{i:3d}/{len(marketplace_parsers)}] {parser:45s} ({event_count} events)", end=" ", flush=True)
        success, message = test_generator(parser, is_marketplace=True, count=event_count)
        
        if success:
            print(f"✅ SUCCESS ({success} events)")
            marketplace_results["success"] += 1
            marketplace_results["events_sent"] += event_count
        else:
            print(f"❌ FAILED: {message}")
            marketplace_results["failed"] += 1
            marketplace_results["failures"].append((parser, message))
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    total_community = len(COMMUNITY_PRODUCTS)
    total_marketplace = len(marketplace_parsers)
    
    print(f"📊 COMMUNITY GENERATORS:")
    print(f"   Total: {total_community}")
    print(f"   ✅ Success: {community_results['success']}")
    print(f"   ❌ Failed: {community_results['failed']}")
    print(f"   📤 Events Sent: {community_results['events_sent']}")
    print(f"   📈 Success Rate: {community_results['success']/total_community*100:.1f}%")
    
    print(f"\n🏪 MARKETPLACE PARSERS:")
    print(f"   Total: {total_marketplace}")
    print(f"   ✅ Success: {marketplace_results['success']}")
    print(f"   ❌ Failed: {marketplace_results['failed']}")
    print(f"   📤 Events Sent: {marketplace_results['events_sent']}")
    print(f"   📈 Success Rate: {marketplace_results['success']/total_marketplace*100:.1f}%")
    
    overall_success = community_results['success'] + marketplace_results['success']
    overall_total = total_community + total_marketplace
    total_events_sent = community_results['events_sent'] + marketplace_results['events_sent']
    
    print(f"\n🎯 OVERALL:")
    print(f"   Total Generators: {overall_total}")
    print(f"   ✅ Total Success: {overall_success}")
    print(f"   ❌ Total Failed: {community_results['failed'] + marketplace_results['failed']}")
    print(f"   📤 **TOTAL EVENTS SENT: {total_events_sent}**")
    print(f"   📈 Overall Success Rate: {overall_success/overall_total*100:.1f}%")
    
    # Show failures if any
    if community_results["failures"]:
        print(f"\n❌ COMMUNITY FAILURES ({len(community_results['failures'])}):")
        for product, error in community_results["failures"][:10]:
            print(f"   • {product}: {error}")
        if len(community_results["failures"]) > 10:
            print(f"   ... and {len(community_results['failures'])-10} more")
    
    if marketplace_results["failures"]:
        print(f"\n❌ MARKETPLACE FAILURES ({len(marketplace_results['failures'])}):")
        for parser, error in marketplace_results["failures"][:10]:
            print(f"   • {parser}: {error}")
        if len(marketplace_results["failures"]) > 10:
            print(f"   ... and {len(marketplace_results['failures'])-10} more")
    
    # Save detailed results
    results = {
        "timestamp": datetime.now().isoformat(),
        "community": {
            "total": total_community,
            "success": community_results["success"],
            "failed": community_results["failed"],
            "success_rate": community_results["success"]/total_community*100,
            "failures": community_results["failures"]
        },
        "marketplace": {
            "total": total_marketplace,
            "success": marketplace_results["success"], 
            "failed": marketplace_results["failed"],
            "success_rate": marketplace_results["success"]/total_marketplace*100 if total_marketplace > 0 else 0,
            "failures": marketplace_results["failures"]
        },
        "overall": {
            "total": overall_total,
            "success": overall_success,
            "failed": community_results["failed"] + marketplace_results["failed"],
            "success_rate": overall_success/overall_total*100
        }
    }
    
    with open('comprehensive_generator_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: comprehensive_generator_test_results.json")
    print(f"✅ Comprehensive test complete!")
    
    return results

if __name__ == "__main__":
    main()