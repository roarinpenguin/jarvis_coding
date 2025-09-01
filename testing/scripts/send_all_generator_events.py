#!/usr/bin/env python3
"""
Send events from ALL generators to ensure complete coverage for validation
"""
import subprocess
import time
import os
import sys

# Set the HEC token
os.environ['S1_HEC_TOKEN'] = "1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7"

# Complete list of ALL available generators
ALL_GENERATORS = [
    # Cloud & Infrastructure
    "aws_cloudtrail", "aws_elasticloadbalancer", "aws_elb", "aws_guardduty",
    "aws_route53", "aws_vpc_dns", "aws_vpcflow", "aws_vpcflowlogs", "aws_waf",
    "google_cloud_dns", "google_workspace",
    
    # Network Security
    "akamai_cdn", "akamai_dns", "akamai_general", "akamai_sitedefender",
    "cisco_asa", "cisco_duo", "cisco_firewall_threat_defense", "cisco_fmc",
    "cisco_ios", "cisco_ironport", "cisco_isa3000", "cisco_ise", 
    "cisco_meraki", "cisco_meraki_flow", "cisco_networks", "cisco_umbrella",
    "cloudflare_general", "cloudflare_waf", "corelight_conn", "corelight_http", 
    "corelight_ssl", "corelight_tunnel", "extreme_networks", "f5_networks", 
    "f5_vpn", "fortinet_fortigate", "isc_bind", "isc_dhcp", "juniper_networks",
    "paloalto_firewall", "paloalto_prismasase", "ubiquiti_unifi",
    "zscaler", "zscaler_dns_firewall", "zscaler_firewall",
    
    # Endpoint & Identity
    "abnormal_security", "armis", "crowdstrike_falcon", "hypr_auth",
    "iis_w3c", "jamf_protect", "linux_auth",
    "microsoft_365_collaboration", "microsoft_365_defender", "microsoft_365_mgmt_api",
    "microsoft_azure_ad_signin", "microsoft_azuread", "microsoft_defender_email",
    "microsoft_windows_eventlog", "okta_authentication",
    "pingfederate", "pingone_mfa", "pingprotect", "rsa_adaptive",
    "sentinelone_endpoint", "sentinelone_identity",
    
    # Email Security
    "mimecast", "proofpoint",
    
    # Web Application Security
    "imperva_sonar", "imperva_waf", "incapsula",
    
    # Privileged Access
    "beyondtrust_passwordsafe", "beyondtrust_privilegemgmtwindows",
    "cyberark_conjur", "cyberark_pas", "hashicorp_vault", "securelink",
    
    # SIEM & Analytics
    "darktrace", "darktrace_darktrace", "extrahop", "manch_siem", "vectra_ai",
    
    # IT Management & Data Protection
    "axway_sftp", "cohesity_backup", "github_audit",
    "manageengine_adauditplus", "manageengine_general",
    "microsoft_azure_ad", "microsoft_eventhub_azure_signin",
    "microsoft_eventhub_defender_email", "microsoft_eventhub_defender_emailforcloud",
    "sap", "veeam_backup", "wiz_cloud",
    
    # DevOps & CI/CD
    "buildkite", "harness_ci", "teleport",
    
    # Network Access & VPN
    "apache_http", "netskope", "tailscale",
    
    # Additional generators
    "checkpoint", "fortimanager", "infoblox_ddi", "zscaler_private_access"
]

def send_events_from_generator(generator, count=3):
    """Send events from a single generator"""
    try:
        result = subprocess.run(
            [".venv/bin/python", "event_generators/shared/hec_sender.py", 
             "--product", generator, "--count", str(count)],
            capture_output=True,
            text=True,
            timeout=45
        )
        
        if result.returncode == 0 and 'Success' in result.stdout:
            return True, f"SUCCESS - {count} events sent"
        else:
            error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
            return False, f"FAILED - {error_msg[:100]}"
            
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT after 45 seconds"
    except Exception as e:
        return False, f"ERROR - {str(e)[:100]}"

def main():
    print("=" * 80)
    print("COMPREHENSIVE EVENT GENERATION")
    print("=" * 80)
    print(f"📤 Sending events from ALL {len(ALL_GENERATORS)} generators")
    print("🎯 Target: 3 events per generator for complete validation coverage")
    print()
    
    successful = []
    failed = []
    total_events_sent = 0
    
    for i, generator in enumerate(ALL_GENERATORS, 1):
        print(f"[{i:3d}/{len(ALL_GENERATORS)}] {generator:35s} ", end="", flush=True)
        
        success, message = send_events_from_generator(generator, count=3)
        
        if success:
            print(f"✅ {message}")
            successful.append(generator)
            total_events_sent += 3
        else:
            print(f"❌ {message}")
            failed.append((generator, message))
        
        # Small delay to avoid overwhelming the endpoint
        time.sleep(0.1)
    
    # Print summary
    print("\n" + "=" * 80)
    print("COMPREHENSIVE EVENT GENERATION SUMMARY")
    print("=" * 80)
    print(f"✅ Successful: {len(successful)}/{len(ALL_GENERATORS)} generators ({len(successful)/len(ALL_GENERATORS)*100:.1f}%)")
    print(f"❌ Failed: {len(failed)}/{len(ALL_GENERATORS)} generators ({len(failed)/len(ALL_GENERATORS)*100:.1f}%)")
    print(f"📤 Total Events Sent: {total_events_sent}")
    print()
    
    if successful:
        print(f"✅ SUCCESSFUL GENERATORS ({len(successful)}):")
        for i, gen in enumerate(successful, 1):
            if i % 4 == 0:
                print(f"  {gen}")
            else:
                print(f"  {gen:25s}", end="")
        print()
    
    if failed:
        print(f"\n❌ FAILED GENERATORS ({len(failed)}):")
        for gen, error in failed[:10]:  # Show first 10 failures
            print(f"  • {gen}: {error}")
        if len(failed) > 10:
            print(f"  ... and {len(failed)-10} more failures")
    
    print(f"\n🎯 Ready for validation! All generators with events can now be validated via SDL API.")
    print(f"💫 All events include Star Trek characters (jean.picard, jordy.laforge, etc.) with STARFLEET domain")
    print(f"⏰ All events generated from the last 10 minutes for recent timestamp validation")

if __name__ == "__main__":
    main()