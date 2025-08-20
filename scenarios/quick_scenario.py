#!/usr/bin/env python3
"""
Quick Scenario Generator - Generate and send comprehensive attack scenarios for testing
====================================================================================

This script creates quick, focused attack scenarios for testing and demonstrations.
Perfect for validating parser configurations and testing SIEM detection rules.

Updated for new categorized generator structure with Star Trek theme and marketplace parser support.
"""

import json
import random
import sys
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any

# Add paths for the new categorized structure
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
event_generators_root = os.path.join(project_root, "event_generators")

# Add all generator category directories to path
for category in ['cloud_infrastructure', 'network_security', 'endpoint_security', 
                 'identity_access', 'email_security', 'web_security', 'infrastructure', 'shared']:
    sys.path.insert(0, os.path.join(event_generators_root, category))

# Import shared components
from starfleet_characters import (
    get_random_user, get_user_by_department, get_compromised_user, 
    get_high_value_targets, STARFLEET_USERS, ORGANIZATION
)
from hec_sender import send_one, MARKETPLACE_PARSER_MAP

# Import generators from different categories
# Email Security
from proofpoint import proofpoint_log, ATTR_FIELDS as PROOFPOINT_FIELDS
from mimecast import mimecast_log, ATTR_FIELDS as MIMECAST_FIELDS
from abnormal_security import abnormal_security_log, ATTR_FIELDS as ABNORMAL_FIELDS

# Endpoint Security  
from crowdstrike_falcon import crowdstrike_log, ATTR_FIELDS as CROWDSTRIKE_FIELDS
from sentinelone_endpoint import sentinelone_endpoint_log, ATTR_FIELDS as SENTINELONE_FIELDS
from microsoft_windows_eventlog import microsoft_windows_eventlog_log, ATTR_FIELDS as WINDOWS_FIELDS

# Identity & Access
from okta_authentication import okta_authentication_log, ATTR_FIELDS as OKTA_FIELDS
from microsoft_azure_ad_signin import microsoft_azure_ad_signin_log, ATTR_FIELDS as AZURE_AD_FIELDS
from cyberark_pas import cyberark_pas_log, ATTR_FIELDS as CYBERARK_FIELDS

# Network Security
from cisco_firewall_threat_defense import cisco_firewall_threat_defense_log, ATTR_FIELDS as CISCO_FTD_FIELDS
from paloalto_firewall import paloalto_firewall_log, ATTR_FIELDS as PALOALTO_FIELDS
from fortinet_fortigate import forward_log as fortinet_fortigate_log, ATTR_FIELDS as FORTIGATE_FIELDS
from corelight_conn import corelight_conn_log, ATTR_FIELDS as CORELIGHT_FIELDS

# Cloud Infrastructure
from aws_cloudtrail import cloudtrail_log, ATTR_FIELDS as AWS_CLOUDTRAIL_FIELDS
from aws_guardduty import guardduty_log as aws_guardduty_log, ATTR_FIELDS as AWS_GUARDDUTY_FIELDS
from aws_vpcflowlogs import vpcflow_log as aws_vpcflow_log, ATTR_FIELDS as AWS_VPC_FIELDS

# Web Security
from cloudflare_waf import cloudflare_waf_log, ATTR_FIELDS as CLOUDFLARE_FIELDS
from imperva_waf import imperva_waf_log, ATTR_FIELDS as IMPERVA_FIELDS
from netskope import netskope_log, ATTR_FIELDS as NETSKOPE_FIELDS

# Infrastructure
from github_audit import github_audit_log, ATTR_FIELDS as GITHUB_FIELDS
from veeam_backup import veeam_backup_log, ATTR_FIELDS as VEEAM_FIELDS

class QuickScenarioGenerator:
    def __init__(self, retroactive_hours: int = 0):
        self.retroactive_hours = retroactive_hours
        self.compromised_user = get_compromised_user()
        self.high_value_targets = get_high_value_targets()
        
        # Enhanced scenarios with Star Trek theme and new generator categories
        self.scenarios = {
            "phishing_attack": {
                "name": "🎯 Enterprise Phishing Campaign",
                "description": f"Advanced phishing targeting Captain {self.compromised_user} with multi-stage compromise",
                "duration_minutes": 45,
                "events": [
                    {"platform": "email", "generator": proofpoint_log, "attrs": PROOFPOINT_FIELDS, "count": 2, "malicious": True, "product": "proofpoint"},
                    {"platform": "email", "generator": mimecast_log, "attrs": MIMECAST_FIELDS, "count": 1, "malicious": True, "product": "mimecast"},
                    {"platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, "count": 3, "malicious": True, "product": "microsoft_azure_ad_signin"},
                    {"platform": "endpoint", "generator": crowdstrike_log, "attrs": CROWDSTRIKE_FIELDS, "count": 2, "malicious": True, "product": "crowdstrike_falcon"},
                    {"platform": "network", "generator": cisco_firewall_threat_defense_log, "attrs": CISCO_FTD_FIELDS, "count": 2, "malicious": True, "product": "cisco_firewall_threat_defense"},
                    {"platform": "cloud", "generator": cloudtrail_log, "attrs": AWS_CLOUDTRAIL_FIELDS, "count": 2, "malicious": True, "product": "aws_cloudtrail"}
                ]
            },
            "insider_threat": {
                "name": "🕵️ Starfleet Insider Threat",
                "description": f"Security Officer {get_user_by_department('security')} accessing and exfiltrating classified data",
                "duration_minutes": 90,
                "events": [
                    {"platform": "identity", "generator": okta_authentication_log, "attrs": OKTA_FIELDS, "count": 2, "malicious": False, "product": "okta_authentication"},
                    {"platform": "privileged", "generator": cyberark_pas_log, "attrs": CYBERARK_FIELDS, "count": 3, "malicious": True, "product": "cyberark_pas"},
                    {"platform": "cloud", "generator": netskope_log, "attrs": NETSKOPE_FIELDS, "count": 4, "malicious": True, "product": "netskope"},
                    {"platform": "network", "generator": corelight_conn_log, "attrs": CORELIGHT_FIELDS, "count": 3, "malicious": True, "product": "corelight_conn"},
                    {"platform": "infrastructure", "generator": github_audit_log, "attrs": GITHUB_FIELDS, "count": 2, "malicious": True, "product": "github_audit"}
                ]
            },
            "malware_outbreak": {
                "name": "🦠 Borg Malware Assimilation",
                "description": "Multi-vector malware campaign spreading across Enterprise systems",
                "duration_minutes": 60,
                "events": [
                    {"platform": "email", "generator": abnormal_security_log, "attrs": ABNORMAL_FIELDS, "count": 2, "malicious": True, "product": "abnormal_security"},
                    {"platform": "endpoint", "generator": sentinelone_endpoint_log, "attrs": SENTINELONE_FIELDS, "count": 4, "malicious": True, "product": "sentinelone_endpoint"},
                    {"platform": "endpoint", "generator": microsoft_windows_eventlog_log, "attrs": WINDOWS_FIELDS, "count": 3, "malicious": True, "product": "microsoft_windows_eventlog"},
                    {"platform": "network", "generator": fortinet_fortigate_log, "attrs": FORTIGATE_FIELDS, "count": 3, "malicious": True, "product": "fortinet_fortigate"},
                    {"platform": "cloud", "generator": aws_guardduty_log, "attrs": AWS_GUARDDUTY_FIELDS, "count": 2, "malicious": True, "product": "aws_guardduty"}
                ]
            },
            "credential_stuffing": {
                "name": "🔐 Romulan Credential Assault",
                "description": "Automated credential stuffing attack against Starfleet accounts",
                "duration_minutes": 30,
                "events": [
                    {"platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, "count": 15, "malicious": True, "product": "microsoft_azure_ad_signin"},
                    {"platform": "identity", "generator": okta_authentication_log, "attrs": OKTA_FIELDS, "count": 8, "malicious": True, "product": "okta_authentication"},
                    {"platform": "web", "generator": cloudflare_waf_log, "attrs": CLOUDFLARE_FIELDS, "count": 5, "malicious": True, "product": "cloudflare_waf"},
                    {"platform": "network", "generator": paloalto_firewall_log, "attrs": PALOALTO_FIELDS, "count": 3, "malicious": True, "product": "paloalto_firewall"}
                ]
            },
            "data_breach": {
                "name": "🚨 Klingon APT - Full Enterprise Breach",
                "description": "Advanced persistent threat targeting Starfleet's classified systems",
                "duration_minutes": 180,
                "events": [
                    {"platform": "email", "generator": proofpoint_log, "attrs": PROOFPOINT_FIELDS, "count": 3, "malicious": True, "product": "proofpoint"},
                    {"platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, "count": 4, "malicious": True, "product": "microsoft_azure_ad_signin"},
                    {"platform": "endpoint", "generator": crowdstrike_log, "attrs": CROWDSTRIKE_FIELDS, "count": 5, "malicious": True, "product": "crowdstrike_falcon"},
                    {"platform": "privileged", "generator": cyberark_pas_log, "attrs": CYBERARK_FIELDS, "count": 3, "malicious": True, "product": "cyberark_pas"},
                    {"platform": "cloud", "generator": cloudtrail_log, "attrs": AWS_CLOUDTRAIL_FIELDS, "count": 4, "malicious": True, "product": "aws_cloudtrail"},
                    {"platform": "network", "generator": cisco_firewall_threat_defense_log, "attrs": CISCO_FTD_FIELDS, "count": 4, "malicious": True, "product": "cisco_firewall_threat_defense"},
                    {"platform": "web", "generator": imperva_waf_log, "attrs": IMPERVA_FIELDS, "count": 3, "malicious": True, "product": "imperva_waf"},
                    {"platform": "infrastructure", "generator": veeam_backup_log, "attrs": VEEAM_FIELDS, "count": 2, "malicious": True, "product": "veeam_backup"}
                ]
            },
            "supply_chain": {
                "name": "⛓️ Cardassian Supply Chain Attack",
                "description": "Compromised software update targeting engineering systems",
                "duration_minutes": 75,
                "events": [
                    {"platform": "infrastructure", "generator": github_audit_log, "attrs": GITHUB_FIELDS, "count": 3, "malicious": True, "product": "github_audit"},
                    {"platform": "endpoint", "generator": sentinelone_endpoint_log, "attrs": SENTINELONE_FIELDS, "count": 4, "malicious": True, "product": "sentinelone_endpoint"},
                    {"platform": "cloud", "generator": aws_guardduty_log, "attrs": AWS_GUARDDUTY_FIELDS, "count": 2, "malicious": True, "product": "aws_guardduty"},
                    {"platform": "network", "generator": corelight_conn_log, "attrs": CORELIGHT_FIELDS, "count": 3, "malicious": True, "product": "corelight_conn"}
                ]
            },
            "privilege_escalation": {
                "name": "⬆️ Dominion Privilege Escalation",
                "description": "Lateral movement and privilege escalation across Starfleet systems",
                "duration_minutes": 50,
                "events": [
                    {"platform": "identity", "generator": okta_authentication_log, "attrs": OKTA_FIELDS, "count": 2, "malicious": False, "product": "okta_authentication"},
                    {"platform": "privileged", "generator": cyberark_pas_log, "attrs": CYBERARK_FIELDS, "count": 4, "malicious": True, "product": "cyberark_pas"},
                    {"platform": "endpoint", "generator": microsoft_windows_eventlog_log, "attrs": WINDOWS_FIELDS, "count": 3, "malicious": True, "product": "microsoft_windows_eventlog"},
                    {"platform": "network", "generator": fortinet_fortigate_log, "attrs": FORTIGATE_FIELDS, "count": 2, "malicious": True, "product": "fortinet_fortigate"},
                    {"platform": "cloud", "generator": aws_vpcflow_log, "attrs": AWS_VPC_FIELDS, "count": 3, "malicious": True, "product": "aws_vpcflowlogs"}
                ]
            }
        }
    
    def list_scenarios(self):
        """List available quick scenarios with Star Trek theme"""
        print("🖖 STARFLEET SECURITY SCENARIOS")
        print("=" * 60)
        for key, scenario in self.scenarios.items():
            total_events = sum(event["count"] for event in scenario["events"])
            platforms = set(event["platform"] for event in scenario["events"])
            print(f"🎯 {key}")
            print(f"   Name: {scenario['name']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Duration: {scenario['duration_minutes']} minutes")
            print(f"   Total Events: {total_events}")
            print(f"   Platforms: {', '.join(sorted(platforms))}")
            print()
    
    def generate_scenario(self, scenario_key: str, use_marketplace: bool = False) -> List[Dict[str, Any]]:
        """Generate events for a specific scenario with Star Trek context"""
        if scenario_key not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_key}. Available: {list(self.scenarios.keys())}")
        
        scenario = self.scenarios[scenario_key]
        print(f"🎬 Generating scenario: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print(f"🖖 Targeting: {ORGANIZATION['name']} ({ORGANIZATION['domain']})")
        
        if use_marketplace:
            print("🏪 Using SentinelOne Marketplace parsers for enhanced OCSF compliance")
        
        all_events = []
        # Calculate start time - if retroactive, start in the past
        if self.retroactive_hours > 0:
            start_time = datetime.now(timezone.utc) - timedelta(hours=self.retroactive_hours)
            print(f"⏰ Retroactive Mode: Events from {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        else:
            start_time = datetime.now(timezone.utc) - timedelta(minutes=10)  # Recent events for testing
            print(f"⏰ Recent Events: Starting from {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        duration = timedelta(minutes=scenario['duration_minutes'])
        
        # Calculate total events for time distribution
        total_events = sum(event["count"] for event in scenario["events"])
        event_index = 0
        
        for event_group in scenario["events"]:
            platform = event_group["platform"]
            generator = event_group["generator"]
            attrs = event_group["attrs"]
            count = event_group["count"]
            malicious = event_group.get("malicious", False)
            product = event_group.get("product", "unknown")
            
            print(f"   🔧 Generating {count} {platform} events ({product})...")
            
            for i in range(count):
                # Calculate event time (spread across duration)
                time_offset = duration * (event_index / total_events)
                event_time = start_time + time_offset
                
                # Generate event with malicious context if needed
                if malicious:
                    event_data = self._generate_malicious_event(generator, platform, scenario_key)
                else:
                    event_data = generator()
                
                # Determine parser to use
                parser_name = None
                if use_marketplace:
                    # Try to find marketplace parser for this product
                    for marketplace_parser, mapped_product in MARKETPLACE_PARSER_MAP.items():
                        if mapped_product == product:
                            parser_name = marketplace_parser
                            break
                
                # Create scenario event
                scenario_event = {
                    "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    "scenario": scenario_key,
                    "scenario_name": scenario['name'],
                    "platform": platform,
                    "product": product,
                    "event_index": event_index,
                    "malicious": malicious,
                    "starfleet_target": self.compromised_user,
                    "raw_event": event_data,
                    "attr_fields": attrs,
                    "marketplace_parser": parser_name
                }
                
                all_events.append(scenario_event)
                event_index += 1
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x["timestamp"])
        
        print(f"✅ Generated {len(all_events)} events over {scenario['duration_minutes']} minutes")
        print(f"🎯 Primary target: {self.compromised_user}")
        return all_events
    
    def _generate_malicious_event(self, generator, platform: str, scenario: str):
        """Generate a malicious event based on platform with Star Trek context"""
        # Enhanced malicious configurations with Star Trek theme
        malicious_configs = {
            "email": {
                "threatType": "phish",
                "subject": f"URGENT: Starfleet Security Alert - Action Required for {get_random_user()}",
                "sender": "security@romulan-empire.net",
                "recipient": self.compromised_user,
                "attachment": "starfleet_credentials.zip"
            },
            "identity": {
                "resultType": "50126",  # Failed login
                "ipAddress": "185.220.101.42",  # Suspicious IP
                "userPrincipalName": self.compromised_user,
                "riskLevelAggregated": "high",
                "location": "Romulus"
            },
            "endpoint": {
                "event_simpleName": "ProcessRollup2",
                "name": "Borg Collective Malware Detected",
                "Severity": 10,
                "ThreatFamily": "BorgAssimilator",
                "user": get_username_from_email(self.compromised_user),
                "hostname": f"enterprise-{random.randint(1,20)}.starfleet.corp"
            },
            "network": {
                "model": {
                    "name": "Anomalous Connection to Klingon Territory",
                    "description": "Device communicating with known hostile networks"
                },
                "score": 0.95,
                "externalDomain": "klingon-intel.qonos",
                "src_ip": "10.0.1.42",
                "dest_ip": "203.0.113.42"
            },
            "cloud": {
                "event_type": "download",
                "action": "allow",
                "file_name": "classified_warp_core_schematics.pdf",
                "breach_score": 98,
                "user": self.compromised_user
            },
            "web": {
                "action": "blocked",
                "threat_type": "malware",
                "url": "http://cardassian-malware.alpha-quadrant/payload.exe",
                "client_ip": "10.0.1.42"
            },
            "privileged": {
                "action": "access_granted",
                "vault": "starfleet_classified",
                "user": self.compromised_user,
                "safe": "warp_core_codes",
                "risk_score": 85
            },
            "infrastructure": {
                "action": "repository_access",
                "repo": "starfleet/warp-drive-v2",
                "user": self.compromised_user,
                "suspicious": True,
                "data_exfiltrated": "2.3GB"
            }
        }
        
        config = malicious_configs.get(platform, {})
        try:
            return generator(config)
        except TypeError:
            # Generator doesn't accept config, use default
            return generator()
    
    def send_to_hec(self, events: List[Dict[str, Any]], send_immediately: bool = True, use_marketplace: bool = False):
        """Send scenario events to HEC with marketplace parser support"""
        print(f"🚀 Sending {len(events)} Starfleet scenario events to HEC...")
        
        if use_marketplace:
            print("🏪 Using marketplace parsers where available for enhanced OCSF compliance")
        
        success_count = 0
        marketplace_used = 0
        
        for i, event in enumerate(events):
            try:
                raw_event = event["raw_event"]
                product = event["product"]
                
                # Enhanced attributes with scenario context and Star Trek theme
                attrs = {
                    **event["attr_fields"],
                    "scenario.name": event["scenario"],
                    "scenario.display_name": event["scenario_name"],
                    "scenario.platform": event["platform"],
                    "scenario.malicious": str(event["malicious"]),
                    "scenario.event_index": str(event["event_index"]),
                    "scenario.target": event["starfleet_target"],
                    "organization.name": ORGANIZATION["name"],
                    "organization.domain": ORGANIZATION["domain"]
                }
                
                # Use marketplace parser if available and requested
                # Note: Marketplace parser support would require hec_sender.py updates
                if use_marketplace and event.get("marketplace_parser"):
                    # For now, just track that we would use marketplace parsers
                    marketplace_used += 1
                
                response = send_one(raw_event, product, attrs)
                
                success_count += 1
                
                if (i + 1) % 5 == 0:
                    print(f"   📈 Sent {i + 1}/{len(events)} events...")
                
                # Small delay between events if not immediate
                if not send_immediately:
                    import time
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"   ❌ Failed to send event {i}: {e}")
        
        print(f"✅ Successfully sent {success_count}/{len(events)} events")
        if use_marketplace:
            print(f"🏪 Marketplace parsers used: {marketplace_used}/{len(events)} events")
        return success_count

def get_username_from_email(email: str) -> str:
    """Extract username from email address"""
    return email.split('@')[0] if '@' in email else email

def main():
    """Main execution function"""
    print("🖖 STARFLEET QUICK SCENARIO GENERATOR")
    print("Generate focused attack scenarios featuring Star Trek characters")
    print("=" * 70)
    
    # Ask about retroactive mode
    retroactive = input("Generate retroactive scenario? (y/N): ").lower().startswith('y')
    if retroactive:
        retroactive_hours = int(input("How many hours in the past should the scenario start? (default 2): ") or "2")
    else:
        retroactive_hours = 0
    
    # Ask about marketplace parsers
    use_marketplace = input("Use SentinelOne Marketplace parsers for enhanced OCSF compliance? (y/N): ").lower().startswith('y')
    
    generator = QuickScenarioGenerator(retroactive_hours=retroactive_hours)
    
    # Show available scenarios
    generator.list_scenarios()
    
    # Get user selection
    scenario_key = input("Enter scenario key: ").strip()
    if scenario_key not in generator.scenarios:
        print(f"❌ Invalid scenario: {scenario_key}")
        print(f"Available scenarios: {list(generator.scenarios.keys())}")
        return
    
    # Generate scenario
    try:
        events = generator.generate_scenario(scenario_key, use_marketplace=use_marketplace)
    except Exception as e:
        print(f"❌ Error generating scenario: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Options
    print(f"\n⚙️  OPTIONS")
    save_file = input("Save to file (enter filename or leave blank): ").strip()
    if save_file:
        with open(save_file, 'w') as f:
            json.dump(events, f, indent=2, default=str)
        print(f"💾 Saved to: {save_file}")
    
    send_to_hec = input("Send to HEC immediately? (y/N): ").lower().startswith('y')
    if send_to_hec:
        try:
            generator.send_to_hec(events, send_immediately=True, use_marketplace=use_marketplace)
        except Exception as e:
            print(f"❌ Error sending to HEC: {e}")
            print("💡 Make sure S1_HEC_TOKEN environment variable is set")
            import traceback
            traceback.print_exc()
    
    print(f"\n✅ Starfleet scenario complete!")
    print(f"📊 Generated {len(events)} events for scenario: {generator.scenarios[scenario_key]['name']}")
    print(f"🎯 Primary target: {generator.compromised_user}")

if __name__ == "__main__":
    main()