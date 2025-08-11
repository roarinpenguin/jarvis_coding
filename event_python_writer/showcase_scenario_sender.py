#!/usr/bin/env python3
"""
Showcase Attack Scenario Sender
===============================

Sends the enterprise showcase attack scenario to SentinelOne AI-SIEM
for demonstration of advanced multi-platform correlation capabilities.
"""

import os
import json
import sys
import requests
import time
from datetime import datetime, timezone
from showcase_attack_scenario import generate_showcase_attack_scenario

# Configuration
HEC_TOKEN = os.environ.get('S1_HEC_TOKEN', '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7')
HEC_URL = "https://usea1-purple.sentinelone.net:8088/services/collector"

def send_to_hec(event_data, source):
    """Send event to SentinelOne HEC"""
    hec_payload = {
        "time": int(datetime.now(timezone.utc).timestamp()),
        "source": source,
        "sourcetype": "_json",
        "index": "main", 
        "event": event_data
    }
    
    headers = {
        "Authorization": f"Splunk {HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(HEC_URL, headers=headers, 
                               data=json.dumps(hec_payload), 
                               timeout=30, verify=False)
        return response.status_code == 200
    except:
        return False

def send_showcase_scenario():
    """Send the showcase attack scenario"""
    print("🚀 ENTERPRISE SHOWCASE ATTACK SCENARIO SENDER")
    print("=" * 80)
    
    # Generate scenario
    print("📝 Generating enterprise attack scenario...")
    scenario = generate_showcase_attack_scenario()
    
    events = scenario["events"]
    print(f"\n🎯 SENDING {len(events)} EVENTS TO SENTINELONE AI-SIEM")
    print(f"📊 Demonstrating correlation across {len(scenario['data_sources'])} data sources")
    print(f"🔥 {len(scenario['attack_phases'])} attack phases")
    print("=" * 80)
    
    # Phase tracking
    phase_counts = {}
    success_count = 0
    
    # Send events
    for i, event_entry in enumerate(events, 1):
        source = event_entry["source"]
        phase = event_entry["phase"]
        event_data = event_entry["event"]
        
        # Track phases
        if phase not in phase_counts:
            phase_counts[phase] = 0
        phase_counts[phase] += 1
        
        # Display progress
        print(f"[{i:2d}/{len(events)}] {source:25s} ({phase:15s}) → ", end="", flush=True)
        
        # Send event
        success = send_to_hec(event_data, source)
        if success:
            print("✅")
            success_count += 1
        else:
            print("❌") 
        
        # Brief pause for realistic timing
        time.sleep(0.3)
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 SHOWCASE SCENARIO DELIVERY COMPLETE")
    print("=" * 80)
    print(f"✅ Events Delivered: {success_count}/{len(events)}")
    print(f"📈 Success Rate: {success_count/len(events)*100:.1f}%")
    
    print(f"\n📊 EVENTS BY ATTACK PHASE:")
    for phase, count in phase_counts.items():
        print(f"   {phase.replace('_', ' ').title():20s}: {count:2d} events")
    
    print(f"\n🏆 SENTINELONE AI-SIEM CORRELATION DEMONSTRATION:")
    for opportunity in scenario["correlation_opportunities"]:
        print(f"   {opportunity}")
    
    print(f"\n🎯 Expected SentinelOne AI-SIEM Analytics:")
    print(f"   • Multi-platform attack timeline reconstruction")
    print(f"   • Cross-source user behavior analysis")
    print(f"   • Infrastructure traversal path mapping") 
    print(f"   • Advanced threat hunting alerts")
    print(f"   • Behavioral anomaly detection")
    print(f"   • Attack technique correlation (MITRE ATT&CK)")

if __name__ == "__main__":
    send_showcase_scenario()