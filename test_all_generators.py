#!/usr/bin/env python3
"""
Test all event generators by sending sample events to SentinelOne
"""
import subprocess
import time
import os

# Set the HEC token
os.environ['S1_HEC_TOKEN'] = "1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7"

# List of all available generators (100+ products)
GENERATORS = [
    # Cloud & Infrastructure
    "aws_cloudtrail", "aws_elasticloadbalancer", "aws_elb", "aws_guardduty",
    "aws_route53", "aws_vpc_dns", "aws_vpcflow", "aws_vpcflowlogs", "aws_waf",
    "google_cloud_dns", "google_workspace",
    
    # Network Security
    "akamai_cdn", "akamai_dns", "akamai_general", "akamai_sitedefender",
    "cisco_asa", "cisco_duo", "cisco_firewall_threat_defense", "cisco_fmc",
    "cisco_ios", "cisco_ironport", "cisco_isa3000", "cisco_ise", 
    "cisco_meraki", "cisco_meraki_flow", "cisco_networks", "cisco_umbrella",
    "cloudflare_general", "corelight_conn", "corelight_http", "corelight_ssl",
    "corelight_tunnel", "extreme_networks", "f5_networks", "f5_vpn",
    "fortinet_fortigate", "isc_bind", "isc_dhcp", "juniper_networks",
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
]

print(f"Testing {len(GENERATORS)} event generators with SentinelOne HEC endpoint...")
print("=" * 80)

# Track results
successful = []
failed = []

# Test each generator
for i, generator in enumerate(GENERATORS, 1):
    print(f"\n[{i}/{len(GENERATORS)}] Testing {generator}...")
    
    try:
        # Send 2 events from each generator
        result = subprocess.run(
            [".venv/bin/python", "event_generators/shared/hec_sender.py", 
             "--product", generator, "--count", "2"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"  ✓ {generator}: SUCCESS - 2 events sent")
            successful.append(generator)
        else:
            print(f"  ✗ {generator}: FAILED - {result.stderr[:100]}")
            failed.append((generator, result.stderr[:200]))
            
    except subprocess.TimeoutExpired:
        print(f"  ✗ {generator}: TIMEOUT")
        failed.append((generator, "Timeout after 30 seconds"))
    except Exception as e:
        print(f"  ✗ {generator}: ERROR - {str(e)[:100]}")
        failed.append((generator, str(e)[:200]))
    
    # Small delay between generators to avoid overwhelming the endpoint
    time.sleep(0.5)

# Print summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"✓ Successful: {len(successful)}/{len(GENERATORS)} generators")
print(f"✗ Failed: {len(failed)}/{len(GENERATORS)} generators")

if failed:
    print("\nFailed generators:")
    for gen, error in failed:
        print(f"  - {gen}: {error[:100]}")

print(f"\nTotal events sent: {len(successful) * 2} events")
print("All events should now be visible in SentinelOne with Star Trek characters and recent timestamps!")