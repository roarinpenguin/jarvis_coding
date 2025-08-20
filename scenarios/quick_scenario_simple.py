#!/usr/bin/env python3
"""
Quick Scenario Generator - Simplified version for testing
=========================================================

This script creates quick, focused attack scenarios using only verified working generators.
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

# Import shared components (with fallbacks)
try:
    from starfleet_characters import (
        get_random_user, get_user_by_department, get_compromised_user, 
        get_high_value_targets, STARFLEET_USERS, ORGANIZATION
    )
    starfleet_available = True
except ImportError:
    starfleet_available = False
    def get_compromised_user():
        return "jean.picard@starfleet.corp"
    def get_user_by_department(dept):
        return "worf.security@starfleet.corp"
    ORGANIZATION = {"name": "Starfleet Corporation", "domain": "starfleet.corp"}

# Import working generators only
try:
    from proofpoint import proofpoint_log, ATTR_FIELDS as PROOFPOINT_FIELDS
    proofpoint_available = True
except ImportError:
    proofpoint_available = False
    PROOFPOINT_FIELDS = {}

try:
    from crowdstrike_falcon import crowdstrike_log, ATTR_FIELDS as CROWDSTRIKE_FIELDS
    crowdstrike_available = True
except ImportError:
    crowdstrike_available = False
    CROWDSTRIKE_FIELDS = {}

try:
    from microsoft_azure_ad_signin import microsoft_azure_ad_signin_log, ATTR_FIELDS as AZURE_AD_FIELDS
    azure_ad_available = True
except ImportError:
    azure_ad_available = False
    AZURE_AD_FIELDS = {}

# Dummy generators for testing
def dummy_log(config=None):
    return {"message": "Test log event", "timestamp": datetime.now().isoformat(), "source": "dummy"}

class QuickScenarioGenerator:
    def __init__(self, retroactive_hours: int = 0):
        self.retroactive_hours = retroactive_hours
        self.compromised_user = get_compromised_user()
        
        # Simple test scenarios with available generators
        self.scenarios = {
            "simple_test": {
                "name": "🧪 Simple Test Scenario",
                "description": f"Basic test scenario targeting {self.compromised_user}",
                "duration_minutes": 10,
                "events": []
            }
        }
        
        # Add events based on available generators
        if proofpoint_available:
            self.scenarios["simple_test"]["events"].append({
                "platform": "email", "generator": proofpoint_log, "attrs": PROOFPOINT_FIELDS, 
                "count": 2, "malicious": True, "product": "proofpoint"
            })
        
        if crowdstrike_available:
            self.scenarios["simple_test"]["events"].append({
                "platform": "endpoint", "generator": crowdstrike_log, "attrs": CROWDSTRIKE_FIELDS, 
                "count": 2, "malicious": True, "product": "crowdstrike_falcon"
            })
        
        if azure_ad_available:
            self.scenarios["simple_test"]["events"].append({
                "platform": "identity", "generator": microsoft_azure_ad_signin_log, "attrs": AZURE_AD_FIELDS, 
                "count": 3, "malicious": True, "product": "microsoft_azure_ad_signin"
            })
        
        # Add dummy event if no real generators available
        if not self.scenarios["simple_test"]["events"]:
            self.scenarios["simple_test"]["events"].append({
                "platform": "test", "generator": dummy_log, "attrs": {}, 
                "count": 1, "malicious": False, "product": "dummy"
            })
    
    def list_scenarios(self):
        """List available scenarios"""
        print("🖖 STARFLEET SECURITY SCENARIOS (Simplified)")
        print("=" * 60)
        
        if starfleet_available:
            print(f"✅ Star Trek characters loaded from {ORGANIZATION['name']}")
        else:
            print("⚠️  Using fallback Star Trek characters")
        
        print(f"✅ Proofpoint: {'Available' if proofpoint_available else 'Not available'}")
        print(f"✅ CrowdStrike: {'Available' if crowdstrike_available else 'Not available'}")
        print(f"✅ Azure AD: {'Available' if azure_ad_available else 'Not available'}")
        print()
        
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
    
    def generate_scenario(self, scenario_key: str) -> List[Dict[str, Any]]:
        """Generate events for a specific scenario"""
        if scenario_key not in self.scenarios:
            raise ValueError(f"Unknown scenario: {scenario_key}. Available: {list(self.scenarios.keys())}")
        
        scenario = self.scenarios[scenario_key]
        print(f"🎬 Generating scenario: {scenario['name']}")
        print(f"📝 {scenario['description']}")
        print(f"🖖 Targeting: {ORGANIZATION['name']} ({ORGANIZATION['domain']})")
        
        all_events = []
        start_time = datetime.now(timezone.utc) - timedelta(minutes=10)  # Recent events
        print(f"⏰ Recent Events: Starting from {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        
        duration = timedelta(minutes=scenario['duration_minutes'])
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
                time_offset = duration * (event_index / max(total_events, 1))
                event_time = start_time + time_offset
                
                # Generate event
                try:
                    if malicious and generator != dummy_log:
                        # Try to pass malicious config
                        try:
                            event_data = generator({"malicious": True})
                        except:
                            event_data = generator()
                    else:
                        event_data = generator()
                except Exception as e:
                    print(f"     ⚠️ Generator failed: {e}, using dummy event")
                    event_data = dummy_log()
                
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
                    "attr_fields": attrs
                }
                
                all_events.append(scenario_event)
                event_index += 1
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x["timestamp"])
        
        print(f"✅ Generated {len(all_events)} events over {scenario['duration_minutes']} minutes")
        print(f"🎯 Primary target: {self.compromised_user}")
        return all_events

def main():
    """Main execution function"""
    print("🖖 STARFLEET QUICK SCENARIO GENERATOR (Simplified)")
    print("Generate focused attack scenarios for testing")
    print("=" * 70)
    
    generator = QuickScenarioGenerator()
    
    # Show available scenarios
    generator.list_scenarios()
    
    # Get user selection
    scenario_key = input("Enter scenario key (or press Enter for 'simple_test'): ").strip()
    if not scenario_key:
        scenario_key = "simple_test"
    
    if scenario_key not in generator.scenarios:
        print(f"❌ Invalid scenario: {scenario_key}")
        print(f"Available scenarios: {list(generator.scenarios.keys())}")
        return
    
    # Generate scenario
    try:
        events = generator.generate_scenario(scenario_key)
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
    
    print(f"\n✅ Starfleet scenario complete!")
    print(f"📊 Generated {len(events)} events for scenario: {generator.scenarios[scenario_key]['name']}")
    print(f"🎯 Primary target: {generator.compromised_user}")
    
    # Show sample event
    if events:
        print(f"\n📋 Sample event:")
        print(json.dumps(events[0], indent=2, default=str))

if __name__ == "__main__":
    main()