#!/usr/bin/env python3
"""
Enterprise Attack Scenario Sender
==================================

Sends the sophisticated enterprise attack scenario to SentinelOne AI-SIEM
with realistic timing and proper correlation opportunities.
"""

import os
import sys
import json
import time
import requests
from datetime import datetime, timezone
from typing import Dict, Any, List

# Import the scenario generator
from enterprise_attack_scenario import generate_enterprise_attack_scenario

# SentinelOne HEC Configuration
HEC_TOKEN = os.environ.get('S1_HEC_TOKEN', '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7')
HEC_URL = "https://usea1-purple.sentinelone.net:8088/services/collector"

def send_to_hec(event_data: Dict[str, Any], source: str) -> bool:
    """Send a single event to SentinelOne HEC"""
    
    # Create HEC payload
    hec_payload = {
        "time": int(datetime.now(timezone.utc).timestamp()),
        "source": source,
        "sourcetype": f"_json",
        "index": "main",
        "event": event_data
    }
    
    headers = {
        "Authorization": f"Splunk {HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            HEC_URL,
            headers=headers,
            data=json.dumps(hec_payload),
            timeout=30,
            verify=False
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ HEC Error: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request Error: {e}")
        return False

def send_scenario_with_timing(scenario: Dict[str, Any], compressed_timeline: bool = True):
    """Send scenario events with realistic timing"""
    
    events = scenario["events"]
    print(f"🚀 SENDING ENTERPRISE ATTACK SCENARIO")
    print(f"📊 Total Events: {len(events)}")
    print(f"🎯 Data Sources: {len(scenario['data_sources'])}")
    print(f"⏰ Timeline: {'Compressed (30 seconds)' if compressed_timeline else 'Realistic (12 hours)'}")
    print("=" * 80)
    
    success_count = 0
    failure_count = 0
    phase_events = {
        "Phase 1": 0, "Phase 2": 0, "Phase 3": 0,
        "Phase 4": 0, "Phase 5": 0, "Phase 6": 0
    }
    
    # Group events by phase for better visualization
    current_phase = "Phase 1"
    phase_counter = 1
    events_in_phase = 0
    
    for i, event_entry in enumerate(events, 1):
        source = event_entry["source"]
        event_data = event_entry["event"]
        timestamp = event_entry["timestamp"]
        
        # Determine phase based on event count (rough approximation)
        if i > len(events) * 0.83:  # Last 17% = Phase 6
            current_phase = "Phase 6"
        elif i > len(events) * 0.67:  # 67-83% = Phase 5
            current_phase = "Phase 5"
        elif i > len(events) * 0.50:  # 50-67% = Phase 4
            current_phase = "Phase 4"
        elif i > len(events) * 0.33:  # 33-50% = Phase 3
            current_phase = "Phase 3"
        elif i > len(events) * 0.17:  # 17-33% = Phase 2
            current_phase = "Phase 2"
        
        # Display phase progress
        if current_phase not in phase_events or phase_events[current_phase] == 0:
            print(f"\n🔥 {current_phase.upper()}: {'RECONNAISSANCE' if '1' in current_phase else 'INITIAL ACCESS' if '2' in current_phase else 'PERSISTENCE' if '3' in current_phase else 'LATERAL MOVEMENT' if '4' in current_phase else 'DATA EXFILTRATION' if '5' in current_phase else 'EVASION'}")
            print("-" * 60)
        
        phase_events[current_phase] += 1
        
        # Send event
        print(f"[{i:3d}/{len(events)}] {source:25s} → ", end="", flush=True)
        
        success = send_to_hec(event_data, source)
        if success:
            print("✅")
            success_count += 1
        else:
            print("❌")
            failure_count += 1
        
        # Timing control
        if compressed_timeline:
            # Fast delivery for demo (30 seconds total)
            time.sleep(0.5)  
        else:
            # Realistic timing (events spread over 12 hours)
            time.sleep(60)  # 1 minute between events
    
    # Final summary
    print("\n" + "=" * 80)
    print("🎯 ENTERPRISE ATTACK SCENARIO DELIVERY COMPLETE")
    print("=" * 80)
    print(f"✅ Events Sent Successfully: {success_count}")
    print(f"❌ Events Failed: {failure_count}")
    print(f"📈 Success Rate: {success_count/(success_count + failure_count)*100:.1f}%")
    
    print(f"\n📊 EVENTS BY ATTACK PHASE:")
    for phase, count in phase_events.items():
        if count > 0:
            print(f"   {phase}: {count} events")
    
    print(f"\n🔍 CORRELATION OPPORTUNITIES:")
    for opportunity in scenario["correlation_opportunities"]:
        print(f"   • {opportunity}")
    
    print(f"\n🏆 SentinelOne AI-SIEM should now show:")
    print(f"   • Cross-platform attack correlation")
    print(f"   • Multi-phase campaign timeline")
    print(f"   • Advanced threat hunting alerts")
    print(f"   • Infrastructure traversal mapping")
    print(f"   • Behavioral anomaly detection")

def main():
    """Main execution"""
    if len(sys.argv) > 1 and sys.argv[1] == '--realistic-timing':
        compressed = False
    else:
        compressed = True
    
    print("🏢 ENTERPRISE ATTACK SCENARIO - SentinelOne AI-SIEM Showcase")
    print("=" * 80)
    
    # Generate the scenario
    print("📝 Generating sophisticated multi-platform attack scenario...")
    scenario = generate_enterprise_attack_scenario()
    
    # Confirmation
    if compressed:
        print(f"\n⚡ COMPRESSED TIMELINE: Delivering {len(scenario['events'])} events in ~30 seconds")
        print("💡 Use --realistic-timing flag for 12-hour realistic delivery")
    else:
        print(f"\n🕐 REALISTIC TIMELINE: Delivering {len(scenario['events'])} events over 12 hours")
        print("⚠️  This will take a very long time - consider compressed mode for demos")
    
    response = input(f"\n🤔 Proceed with scenario delivery? [y/N]: ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Scenario delivery cancelled")
        return
    
    # Send the scenario
    send_scenario_with_timing(scenario, compressed_timeline=compressed)

if __name__ == "__main__":
    main()