#!/usr/bin/env python3
"""
Quick Scenario Generator - Generate and send small attack scenarios for testing
==============================================================================

This script creates quick, focused attack scenarios for testing and demonstrations.
Perfect for validating parser configurations and testing SIEM detection rules.
"""

import json
import random
import sys
import os
from datetime import datetime, timezone, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import generators
from proofpoint import proofpoint_log
from crowdstrike_falcon import crowdstrike_log
from darktrace import darktrace_log
from microsoft_azure_ad_signin import microsoft_azure_ad_signin_log
from netskope import netskope_log
from hec_sender import send_one

# Import attr fields
from proofpoint import ATTR_FIELDS as PROOFPOINT_FIELDS
from crowdstrike_falcon import ATTR_FIELDS as CROWDSTRIKE_FIELDS
from darktrace import ATTR_FIELDS as DARKTRACE_FIELDS
from microsoft_azure_ad_signin import ATTR_FIELDS as AZURE_AD_FIELDS
from netskope import ATTR_FIELDS as NETSKOPE_FIELDS

class QuickScenarioGenerator:
    def __init__(self, retroactive_hours: int = 0):
        self.retroactive_hours = retroactive_hours
        self.scenarios = {
            "phishing_attack": {
                "name": "Phishing Attack with Compromise",
                "description": "Email phishing leading to successful compromise and lateral movement",
                "duration_minutes": 30,
                "events": [
                    {"platform": "email", "generator": proofpoint_log, "attrs": PROOFPOINT_FIELDS, "count": 3, "malicious": True},
                    {"platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, "count": 2, "malicious": True},
                    {"platform": "endpoint", "generator": crowdstrike_log, "attrs": CROWDSTRIKE_FIELDS, "count": 2, "malicious": True},
                    {"platform": "network", "generator": darktrace_log, "attrs": DARKTRACE_FIELDS, "count": 1, "malicious": True}
                ]
            },
            "insider_threat": {
                "name": "Insider Threat - Data Exfiltration",
                "description": "Privileged user accessing and exfiltrating sensitive data",
                "duration_minutes": 60,
                "events": [
                    {"platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, "count": 1, "malicious": False},
                    {"platform": "cloud", "generator": netskope_log, "attrs": NETSKOPE_FIELDS, "count": 3, "malicious": True},
                    {"platform": "network", "generator": darktrace_log, "attrs": DARKTRACE_FIELDS, "count": 2, "malicious": True}
                ]
            },
            "malware_outbreak": {
                "name": "Malware Outbreak",
                "description": "Malware infection spreading across multiple endpoints",
                "duration_minutes": 45,
                "events": [
                    {"platform": "email", "generator": proofpoint_log, "attrs": PROOFPOINT_FIELDS, "count": 2, "malicious": True},
                    {"platform": "endpoint", "generator": crowdstrike_log, "attrs": CROWDSTRIKE_FIELDS, "count": 5, "malicious": True},
                    {"platform": "network", "generator": darktrace_log, "attrs": DARKTRACE_FIELDS, "count": 3, "malicious": True}
                ]
            },
            "credential_stuffing": {
                "name": "Credential Stuffing Attack",
                "description": "Automated credential stuffing attack against user accounts",
                "duration_minutes": 20,
                "events": [
                    {"platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, "count": 10, "malicious": True},
                    {"platform": "network", "generator": darktrace_log, "attrs": DARKTRACE_FIELDS, "count": 2, "malicious": True}
                ]
            },
            "data_breach": {
                "name": "Multi-Stage Data Breach",
                "description": "Complete attack chain from initial access to data exfiltration",
                "duration_minutes": 120,
                "events": [
                    {"platform": "email", "generator": proofpoint_log, "attrs": PROOFPOINT_FIELDS, "count": 2, "malicious": True},
                    {"platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, "count": 3, "malicious": True},
                    {"platform": "endpoint", "generator": crowdstrike_log, "attrs": CROWDSTRIKE_FIELDS, "count": 4, "malicious": True},
                    {"platform": "cloud", "generator": netskope_log, "attrs": NETSKOPE_FIELDS, "count": 3, "malicious": True},
                    {"platform": "network", "generator": darktrace_log, "attrs": DARKTRACE_FIELDS, "count": 3, "malicious": True}
                ]
            }
        }
    
    def list_scenarios(self):
        """List available quick scenarios"""
        print("📋 Available Quick Scenarios:")
        print("=" * 50)
        for key, scenario in self.scenarios.items():
            total_events = sum(event["count"] for event in scenario["events"])
            print(f"🎯 {key}")
            print(f"   Name: {scenario['name']}")
            print(f"   Description: {scenario['description']}")
            print(f"   Duration: {scenario['duration_minutes']} minutes")
            print(f"   Total Events: {total_events}")
            print()
    
    def generate_scenario(self, scenario_key: str) -> list:
        """Generate events for a specific scenario"""
        if scenario_key not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_key}")
        
        scenario = self.scenarios[scenario_key]
        print(f"🎬 Generating scenario: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        
        all_events = []
        # Calculate start time - if retroactive, start in the past
        if self.retroactive_hours > 0:
            start_time = datetime.now(timezone.utc) - timedelta(hours=self.retroactive_hours)
            print(f"⏰ Retroactive Mode: Events from {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} to {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
        else:
            start_time = datetime.now(timezone.utc)
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
            
            print(f"   🔧 Generating {count} {platform} events...")
            
            for i in range(count):
                # Calculate event time (spread across duration)
                time_offset = duration * (event_index / total_events)
                event_time = start_time + time_offset
                
                # Generate event with malicious context if needed
                if malicious:
                    event_data = self._generate_malicious_event(generator, platform)
                else:
                    event_data = generator()
                
                # Create scenario event
                scenario_event = {
                    "timestamp": event_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    "scenario": scenario_key,
                    "platform": platform,
                    "event_index": event_index,
                    "malicious": malicious,
                    "raw_event": event_data,
                    "attr_fields": attrs
                }
                
                all_events.append(scenario_event)
                event_index += 1
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x["timestamp"])
        
        print(f"✅ Generated {len(all_events)} events over {scenario['duration_minutes']} minutes")
        return all_events
    
    def _generate_malicious_event(self, generator, platform: str):
        """Generate a malicious event based on platform"""
        malicious_configs = {
            "email": {
                "threatType": "phish",
                "subject": "Urgent: Account verification required",
                "sender": "security@phishing-site.com"
            },
            "identity": {
                "resultType": "50126",  # Failed login
                "ipAddress": "185.220.101.42",  # Suspicious IP
                "riskLevelAggregated": "high"
            },
            "endpoint": {
                "event_simpleName": "ProcessRollup2",
                "name": "Malware Detected",
                "Severity": 10,
                "ThreatFamily": "Emotet"
            },
            "network": {
                "model": {
                    "name": "Anomalous Connection / Data Sent to Rare Domain",
                    "description": "Device sending data to suspicious domain"
                },
                "score": 0.85,
                "externalDomain": "malicious-c2.com"
            },
            "cloud": {
                "event_type": "download",
                "action": "allow",
                "file_name": "sensitive_customer_data.xlsx",
                "breach_score": 95
            }
        }
        
        config = malicious_configs.get(platform, {})
        return generator(config)
    
    def send_to_hec(self, events: list, send_immediately: bool = True):
        """Send scenario events to HEC"""
        print(f"🚀 Sending {len(events)} events to HEC...")
        
        success_count = 0
        for i, event in enumerate(events):
            try:
                # Map platform to product for hec_sender
                platform_to_product = {
                    "email": "proofpoint",
                    "identity": "microsoft_azure_ad_signin", 
                    "endpoint": "crowdstrike_falcon",
                    "network": "darktrace",
                    "cloud": "netskope"
                }
                
                product = platform_to_product.get(event["platform"], "proofpoint")
                raw_event = event["raw_event"]
                
                # Enhanced attributes with scenario context
                attrs = {
                    **event["attr_fields"],
                    "scenario.name": event["scenario"],
                    "scenario.platform": event["platform"],
                    "scenario.malicious": str(event["malicious"]),
                    "scenario.event_index": str(event["event_index"])
                }
                
                # Send event
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
        return success_count

def main():
    """Main execution function"""
    print("⚡ QUICK SCENARIO GENERATOR")
    print("Generate focused attack scenarios for testing")
    print("=" * 50)
    
    # Ask about retroactive mode
    retroactive = input("Generate retroactive scenario? (y/N): ").lower().startswith('y')
    if retroactive:
        retroactive_hours = int(input("How many hours in the past should the scenario start? (default 2): ") or "2")
    else:
        retroactive_hours = 0
    
    generator = QuickScenarioGenerator(retroactive_hours=retroactive_hours)
    
    # Show available scenarios
    generator.list_scenarios()
    
    # Get user selection
    scenario_key = input("Enter scenario key: ").strip()
    if scenario_key not in generator.scenarios:
        print(f"❌ Invalid scenario: {scenario_key}")
        return
    
    # Generate scenario
    try:
        events = generator.generate_scenario(scenario_key)
    except Exception as e:
        print(f"❌ Error generating scenario: {e}")
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
            generator.send_to_hec(events, send_immediately=True)
        except Exception as e:
            print(f"❌ Error sending to HEC: {e}")
            print("💡 Make sure S1_HEC_TOKEN environment variable is set")
    
    print(f"\n✅ Quick scenario complete!")
    print(f"📊 Generated {len(events)} events for scenario: {generator.scenarios[scenario_key]['name']}")

if __name__ == "__main__":
    main()