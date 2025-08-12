#!/usr/bin/env python3
"""
Validate Enterprise Attack Scenario Timestamps
==============================================
Test that all events are properly timestamped in chronological order
"""

import os
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'

from enterprise_attack_scenario import generate_enhanced_attack_scenario
from datetime import datetime, timezone
import json

def validate_enterprise_timestamps():
    """Validate that enterprise scenario has correct timestamp progression"""
    
    print("🔍 ENTERPRISE ATTACK SCENARIO TIMESTAMP VALIDATION")
    print("=" * 60)
    
    # Generate fresh scenario
    print("📝 Generating fresh attack scenario...")
    scenario = generate_enhanced_attack_scenario()
    events = scenario["events"]
    
    print(f"✅ Generated {len(events)} events")
    print(f"📊 Attack phases: {len(scenario['attack_phases'])}")
    print(f"🏢 Data sources: {len(scenario['data_sources'])}")
    
    # Analyze timestamps
    print(f"\n📅 TIMESTAMP ANALYSIS:")
    print("-" * 40)
    
    # Check wrapper timestamps
    wrapper_timestamps = []
    event_timestamps = []
    timestamp_issues = []
    
    for i, event in enumerate(events):
        wrapper_ts = event['timestamp']
        event_data = event['event']
        source = event['source']
        phase = event['phase']
        
        # Parse wrapper timestamp
        try:
            wrapper_dt = datetime.fromisoformat(wrapper_ts.replace('Z', '+00:00'))
            wrapper_timestamps.append((i, wrapper_dt, source, phase))
        except Exception as e:
            timestamp_issues.append(f"Event {i} ({source}): Invalid wrapper timestamp - {e}")
            continue
        
        # Check event data timestamps
        if isinstance(event_data, dict):
            # JSON event - check internal timestamps
            internal_ts = None
            
            # Check common timestamp fields
            for ts_field in ['timestamp', 'time', 'TimeCreated', '@timestamp']:
                if ts_field in event_data:
                    internal_ts = event_data[ts_field]
                    break
            
            if internal_ts:
                # Check if wrapper and internal timestamps match
                if internal_ts != wrapper_ts:
                    timestamp_issues.append(f"Event {i} ({source}): Wrapper ({wrapper_ts}) != Internal ({internal_ts})")
                else:
                    event_timestamps.append((i, internal_ts, source, phase, 'JSON'))
            else:
                timestamp_issues.append(f"Event {i} ({source}): JSON event missing internal timestamp")
        else:
            # Raw event - only wrapper timestamp available
            event_timestamps.append((i, wrapper_ts, source, phase, 'Raw'))
    
    # Check chronological order
    print(f"🕐 Chronological Order Check:")
    prev_dt = None
    order_issues = []
    
    for i, wrapper_dt, source, phase in wrapper_timestamps:
        if prev_dt and wrapper_dt < prev_dt:
            order_issues.append(f"Event {i} ({source}): Timestamp goes backward")
        prev_dt = wrapper_dt
    
    if order_issues:
        print("❌ CHRONOLOGICAL ORDER ISSUES:")
        for issue in order_issues[:10]:  # Show first 10
            print(f"   {issue}")
        if len(order_issues) > 10:
            print(f"   ... and {len(order_issues) - 10} more issues")
    else:
        print("✅ All events in chronological order")
    
    # Show timeline spread  
    if wrapper_timestamps:
        start_time = wrapper_timestamps[0][1]
        end_time = wrapper_timestamps[-1][1]
        duration = (end_time - start_time).total_seconds() / 60
        
        print(f"\n⏰ Timeline Spread:")
        print(f"   Start: {start_time.isoformat()}")
        print(f"   End:   {end_time.isoformat()}")
        print(f"   Duration: {duration:.1f} minutes")
    
    # Show sample events by phase
    print(f"\n📊 Sample Events by Phase:")
    phase_samples = {}
    for i, wrapper_dt, source, phase in wrapper_timestamps[:50]:  # First 50 events
        if phase not in phase_samples:
            phase_samples[phase] = []
        if len(phase_samples[phase]) < 3:  # Max 3 samples per phase
            phase_samples[phase].append((i, wrapper_dt, source))
    
    for phase, samples in phase_samples.items():
        print(f"   {phase.upper()}:")
        for i, dt, source in samples:
            print(f"     Event {i:3d} - {dt.strftime('%H:%M:%S')} - {source}")
    
    # Show data source breakdown
    print(f"\n🏢 Data Source Breakdown:")
    source_counts = {}
    json_sources = set()
    raw_sources = set() 
    
    for event in events:
        source = event['source']
        source_counts[source] = source_counts.get(source, 0) + 1
        
        if isinstance(event['event'], dict):
            json_sources.add(source)
        else:
            raw_sources.add(source)
    
    print(f"   JSON Sources ({len(json_sources)}): {', '.join(sorted(json_sources))}")
    print(f"   Raw Sources ({len(raw_sources)}): {', '.join(sorted(raw_sources))}")
    
    # Final validation summary
    print(f"\n🎯 VALIDATION SUMMARY:")
    print("-" * 30)
    total_issues = len(timestamp_issues) + len(order_issues)
    
    if total_issues == 0:
        print("✅ ALL VALIDATIONS PASSED")
        print(f"✅ {len(events)} events properly timestamped")
        print(f"✅ Chronological order maintained")
        print(f"✅ {duration:.1f} minute attack timeline") 
    else:
        print(f"❌ Found {total_issues} issues:")
        if timestamp_issues:
            print(f"   - {len(timestamp_issues)} timestamp issues")
        if order_issues:
            print(f"   - {len(order_issues)} chronological issues")
        
        print("\nFirst few issues:")
        all_issues = timestamp_issues + order_issues
        for issue in all_issues[:5]:
            print(f"   {issue}")
    
    return total_issues == 0

if __name__ == "__main__":
    validate_enterprise_timestamps()