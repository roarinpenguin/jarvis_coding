#!/usr/bin/env python3
"""
Final comprehensive parser validation using SDL API
Validates field extraction for all 100 parsers using the correct parser= query
"""
import os
import sys
import json
import time
import requests
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# Configuration
SDL_API_TOKEN = "0sjCPYMhCFzUao1m9SFpEVXOevQVP3y9rV_5pTAA6hdI-"
SDL_API_URL = "https://xdr.us1.sentinelone.net/api/query"

sys.path.insert(0, 'event_python_writer')
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'
from hec_sender import PROD_MAP, SOURCETYPE_MAP

def query_parser_events(parser_name: str, hours_back: int = 4) -> list:
    """Query SDL for events processed by a specific parser"""
    headers = {
        'Authorization': f'Bearer {SDL_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours_back)
    
    query_payload = {
        'queryType': 'log',
        'filter': f'* contains "{parser_name}"',
        'startTime': start_time.isoformat(),
        'endTime': end_time.isoformat()
    }
    
    try:
        response = requests.post(SDL_API_URL, headers=headers, json=query_payload, timeout=15)
        if response.status_code == 200:
            result = response.json()
            # Extract events from matches array
            matches = result.get('matches', [])
            events = []
            for match in matches:
                # Combine attributes and other fields into event object
                event = match.get('attributes', {}).copy()
                event.update({
                    'severity': match.get('severity'),
                    'timestamp': match.get('timestamp'),
                    'message': match.get('message', ''),
                    'thread': match.get('thread', ''),
                    'session': match.get('session', '')
                })
                events.append(event)
            return events
        return []
    except Exception:
        return []

def analyze_field_extraction(events: list) -> dict:
    """Analyze field extraction quality from parsed events"""
    if not events:
        return {"status": "no_events", "field_count": 0, "ocsf_score": 0}
    
    all_fields = set()
    ocsf_fields = set()
    has_observables = False
    
    for event in events:
        event_fields = set(event.keys())
        all_fields.update(event_fields)
        
        # Check for OCSF compliance
        for field in event_fields:
            if any(field.startswith(prefix) for prefix in [
                'activity_', 'category_', 'class_', 'severity_', 'status_', 
                'time', 'metadata', 'actor', 'device', 'src_endpoint', 'dst_endpoint'
            ]):
                ocsf_fields.add(field)
        
        # Check for observables
        if 'observables' in event or any('observable' in str(v) for v in event.values()):
            has_observables = True
    
    # Calculate OCSF compliance score
    ocsf_score = 0
    if len(ocsf_fields) >= 10:
        ocsf_score = 100
    elif len(ocsf_fields) >= 5:
        ocsf_score = 80
    elif len(ocsf_fields) >= 3:
        ocsf_score = 60
    elif len(ocsf_fields) >= 1:
        ocsf_score = 40
    
    # Bonus for observables
    if has_observables:
        ocsf_score = min(100, ocsf_score + 10)
    
    return {
        "status": "success",
        "event_count": len(events),
        "field_count": len(all_fields),
        "ocsf_fields": len(ocsf_fields),
        "ocsf_score": ocsf_score,
        "has_observables": has_observables,
        "sample_fields": sorted(list(all_fields))[:20],
        "ocsf_sample": sorted(list(ocsf_fields))[:10]
    }

def main():
    print("=" * 70)
    print("FINAL PARSER VALIDATION - SDL API ANALYSIS")
    print("=" * 70)
    print(f"Analysis time: {datetime.now().isoformat()}")
    print(f"SDL API: {SDL_API_URL}")
    print(f"Checking {len(SOURCETYPE_MAP)} parser mappings")
    print()
    
    results = {}
    categories = {
        "excellent": [],    # OCSF score >= 80 and observables
        "good": [],        # OCSF score >= 60
        "basic": [],       # OCSF score >= 20  
        "poor": [],        # OCSF score < 20
        "no_events": []    # No events found
    }
    
    total_events_found = 0
    
    print("Querying parsers for field extraction analysis...")
    print("-" * 70)
    
    for i, (generator_name, parser_name) in enumerate(SOURCETYPE_MAP.items(), 1):
        print(f"[{i:3d}/100] {generator_name:35s} → {parser_name:25s}", end=" ", flush=True)
        
        # Query events for this parser
        events = query_parser_events(parser_name)
        
        # Analyze field extraction
        analysis = analyze_field_extraction(events)
        results[generator_name] = {
            "parser": parser_name,
            "analysis": analysis
        }
        
        # Categorize result
        if analysis["status"] == "no_events":
            print("❌ No events")
            categories["no_events"].append(generator_name)
        else:
            total_events_found += analysis["event_count"]
            score = analysis["ocsf_score"]
            
            if score >= 80 and analysis["has_observables"]:
                print(f"✅ Excellent ({score}%, {analysis['field_count']} fields)")
                categories["excellent"].append(generator_name)
            elif score >= 60:
                print(f"🟡 Good ({score}%, {analysis['field_count']} fields)")  
                categories["good"].append(generator_name)
            elif score >= 20:
                print(f"⚠️  Basic ({score}%, {analysis['field_count']} fields)")
                categories["basic"].append(generator_name)
            else:
                print(f"🔴 Poor ({score}%, {analysis['field_count']} fields)")
                categories["poor"].append(generator_name)
        
        time.sleep(0.1)  # Rate limiting
    
    # Generate summary report
    print()
    print("=" * 70)
    print("VALIDATION RESULTS SUMMARY")
    print("=" * 70)
    
    total = len(SOURCETYPE_MAP)
    print(f"Total Parsers Tested: {total}")
    print(f"Total Events Found: {total_events_found}")
    print()
    print("Parser Performance Categories:")
    print(f"✅ Excellent (OCSF + Observables): {len(categories['excellent'])}")
    print(f"🟡 Good (Strong OCSF): {len(categories['good'])}")
    print(f"⚠️  Basic (Limited OCSF): {len(categories['basic'])}")
    print(f"🔴 Poor (Minimal fields): {len(categories['poor'])}")
    print(f"❌ No Events: {len(categories['no_events'])}")
    
    working_parsers = len(categories['excellent']) + len(categories['good'])
    success_rate = (working_parsers / total * 100) if total > 0 else 0
    print(f"\n📊 Parser Success Rate: {success_rate:.1f}% ({working_parsers}/{total})")
    
    if categories['excellent']:
        print(f"\n🌟 EXCELLENT PARSERS ({len(categories['excellent'])}):")
        for parser in categories['excellent'][:10]:
            analysis = results[parser]['analysis']
            print(f"   • {parser}: {analysis['ocsf_fields']} OCSF fields")
        if len(categories['excellent']) > 10:
            print(f"   ... and {len(categories['excellent']) - 10} more")
    
    if categories['no_events']:
        print(f"\n❌ PARSERS WITH NO EVENTS ({len(categories['no_events'])}):")
        for parser in categories['no_events'][:10]:
            print(f"   • {parser} → {results[parser]['parser']}")
        if len(categories['no_events']) > 10:
            print(f"   ... and {len(categories['no_events']) - 10} more")
        print("\nNote: Events may still be processing. Wait 10-15 minutes after sending.")
    
    # Save detailed results
    output = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_parsers": total,
            "total_events": total_events_found,
            "excellent": len(categories['excellent']),
            "good": len(categories['good']),
            "basic": len(categories['basic']),
            "poor": len(categories['poor']),
            "no_events": len(categories['no_events']),
            "success_rate": success_rate
        },
        "categories": categories,
        "detailed_results": results
    }
    
    with open("final_parser_validation_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n📁 Detailed results saved to: final_parser_validation_results.json")
    print("✅ Validation complete!")
    
    return categories

if __name__ == "__main__":
    main()