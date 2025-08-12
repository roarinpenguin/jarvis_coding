#!/bin/bash
# Systematic Event Sender - Send substantial volumes to SentinelOne
# This script sends events in organized batches without validation

export S1_HEC_TOKEN=1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7

echo "🚀 SYSTEMATIC EVENT SENDER - SUBSTANTIAL VOLUME TO SENTINELONE"
echo "=================================================================="
echo "Start time: $(date)"
echo

# High-Priority Marketplace Parsers (Send 8-12 events each)
echo "🏪 PHASE 1: HIGH-PRIORITY MARKETPLACE PARSERS"
echo "----------------------------------------------"

echo "📤 AWS Marketplace Parsers:"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-awscloudtrail-latest --count 10 && echo "✅ AWS CloudTrail: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-awselasticloadbalancer-latest --count 8 && echo "✅ AWS ELB: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-awsguardduty-latest --count 6 && echo "✅ AWS GuardDuty: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-awsvpcflowlogs-latest --count 12 && echo "✅ AWS VPC Flow: 12 events sent"

echo "📤 Network Security Marketplace Parsers:"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-checkpointfirewall-latest --count 10 && echo "✅ Check Point Firewall: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-ciscofirewallthreatdefense-latest --count 8 && echo "✅ Cisco FTD: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-fortinetfortigate-latest --count 10 && echo "✅ FortiGate: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-paloaltonetworksfirewall-latest --count 8 && echo "✅ Palo Alto: 8 events sent"

echo "📤 Network Analysis Marketplace Parsers:"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-corelight-conn-latest --count 12 && echo "✅ Corelight Connections: 12 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-corelight-http-latest --count 10 && echo "✅ Corelight HTTP: 10 events sent"

echo "📤 Zero Trust Marketplace Parsers:"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-zscalerinternetaccess-latest --count 10 && echo "✅ Zscaler Internet Access: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --marketplace-parser marketplace-zscalerprivateaccess-latest --count 8 && echo "✅ Zscaler Private Access: 8 events sent"

echo
echo "📊 PHASE 2: HIGH-VOLUME COMMUNITY GENERATORS"
echo "---------------------------------------------"

echo "📤 Cloud & Infrastructure (40+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product aws_waf --count 8 && echo "✅ AWS WAF: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product aws_route53 --count 10 && echo "✅ AWS Route53: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product google_cloud_dns --count 6 && echo "✅ Google Cloud DNS: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product google_workspace --count 8 && echo "✅ Google Workspace: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product microsoft_azuread --count 10 && echo "✅ Microsoft Azure AD: 10 events sent"

echo "📤 Identity & Access Management (50+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product okta_authentication --count 12 && echo "✅ Okta: 12 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product pingfederate --count 8 && echo "✅ PingFederate: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cyberark_pas --count 6 && echo "✅ CyberArk PAS: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cyberark_conjur --count 6 && echo "✅ CyberArk Conjur: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product microsoft_365_defender --count 10 && echo "✅ Microsoft 365 Defender: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product microsoft_365_collaboration --count 8 && echo "✅ Microsoft 365 Collaboration: 8 events sent"

echo "📤 Network Security Community (60+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product cisco_asa --count 8 && echo "✅ Cisco ASA: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cisco_umbrella --count 10 && echo "✅ Cisco Umbrella: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cisco_fmc --count 8 && echo "✅ Cisco FMC: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cisco_ios --count 12 && echo "✅ Cisco IOS: 12 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cisco_duo --count 8 && echo "✅ Cisco Duo: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cisco_ironport --count 6 && echo "✅ Cisco IronPort: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product paloalto_prismasase --count 8 && echo "✅ Palo Alto Prisma SASE: 8 events sent"

echo "📤 Endpoint Security (40+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product sentinelone_endpoint --count 12 && echo "✅ SentinelOne Endpoint: 12 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product crowdstrike_falcon --count 10 && echo "✅ CrowdStrike Falcon: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product jamf_protect --count 8 && echo "✅ Jamf Protect: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product linux_auth --count 12 && echo "✅ Linux Auth: 12 events sent"

echo "📤 Email Security (30+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product abnormal_security --count 8 && echo "✅ Abnormal Security: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product mimecast --count 10 && echo "✅ Mimecast: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product proofpoint --count 8 && echo "✅ Proofpoint: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product microsoft_defender_email --count 6 && echo "✅ Microsoft Defender Email: 6 events sent"

echo "📤 Web Security (40+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product zscaler_firewall --count 8 && echo "✅ Zscaler Firewall: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product zscaler_dns_firewall --count 10 && echo "✅ Zscaler DNS Firewall: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product imperva_waf --count 8 && echo "✅ Imperva WAF: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product cloudflare_general --count 8 && echo "✅ Cloudflare General: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product incapsula --count 6 && echo "✅ Incapsula: 6 events sent"

echo
echo "📈 PHASE 3: ADDITIONAL HIGH-VALUE GENERATORS"
echo "--------------------------------------------"

echo "📤 SIEM & Analytics (30+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product darktrace --count 10 && echo "✅ Darktrace: 10 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product extrahop --count 8 && echo "✅ ExtraHop: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product vectra_ai --count 6 && echo "✅ Vectra AI: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product armis --count 6 && echo "✅ Armis: 6 events sent"

echo "📤 DevOps & CI/CD (20+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product buildkite --count 6 && echo "✅ Buildkite: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product harness_ci --count 6 && echo "✅ Harness CI: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product github_audit --count 8 && echo "✅ GitHub Audit: 8 events sent"

echo "📤 Additional Network & Infrastructure (40+ events):"
.venv/bin/python event_python_writer/hec_sender.py --product f5_networks --count 6 && echo "✅ F5 Networks: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product juniper_networks --count 6 && echo "✅ Juniper Networks: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product extreme_networks --count 6 && echo "✅ Extreme Networks: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product ubiquiti_unifi --count 6 && echo "✅ Ubiquiti UniFi: 6 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product netskope --count 8 && echo "✅ Netskope: 8 events sent"
.venv/bin/python event_python_writer/hec_sender.py --product tailscale --count 8 && echo "✅ Tailscale: 8 events sent"

echo
echo "✅ SYSTEMATIC EVENT SENDING COMPLETE"
echo "===================================="
echo "End time: $(date)"
echo
echo "📊 ESTIMATED EVENTS SENT:"
echo "  🏪 Marketplace Parsers: ~100 events across 12 parsers"
echo "  📊 Community Generators: ~400+ events across 50+ generators"
echo "  🎯 Total Estimated: ~500+ events from ~60 different products"
echo
echo "⏰ Events should appear in SentinelOne within 2-5 minutes"
echo "🔍 Look for events from timestamp: $(date -Iseconds)"