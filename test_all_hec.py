#!/usr/bin/env python3
"""
Send 5 test events from ALL generators to HEC endpoint.
This script discovers all generators and sends sample events regardless of HEC sender mapping.
"""
import os
import sys
import json
import time
import random
import requests
import importlib
import glob
from datetime import datetime

# HEC Configuration
HEC_TOKEN = os.getenv("S1_HEC_TOKEN")
if not HEC_TOKEN:
    print("❌ Error: S1_HEC_TOKEN environment variable not set")
    print("Please run: export S1_HEC_TOKEN=your-token-here")
    sys.exit(1)

# Default HEC URLs (can be overridden with environment variables)
HEC_RAW_URL = os.getenv("S1_HEC_RAW_URL_BASE", "https://ingest.us1.sentinelone.net/services/collector/raw")
HEC_EVENT_URL = os.getenv("S1_HEC_EVENT_URL_BASE", "https://ingest.us1.sentinelone.net/services/collector/event")

HEADERS = {
    "Authorization": f"Bearer {HEC_TOKEN}",
    "Content-Type": "application/json"
}

def discover_generators():
    """Discover all generator files and their functions."""
    generators = {}
    exclude_files = [
        "hec_sender.py", "test_all_generators.py", "test_all_hec.py",
        "attack_scenario_orchestrator.py", "quick_scenario.py", 
        "scenario_hec_sender.py", "direct_sample.py"
    ]
    
    for file in glob.glob("*.py"):
        if file not in exclude_files and not file.startswith("_"):
            module_name = file[:-3]
            try:
                module = importlib.import_module(module_name)
                
                # Find the main log generation function
                log_func_name = None
                for attr_name in dir(module):
                    if attr_name.endswith("_log") and callable(getattr(module, attr_name)):
                        log_func_name = attr_name
                        break
                
                if log_func_name:
                    log_func = getattr(module, log_func_name)
                    attr_fields = getattr(module, 'ATTR_FIELDS', {})
                    
                    generators[module_name] = {
                        'function': log_func,
                        'attr_fields': attr_fields,
                        'module': module
                    }
                    
            except Exception as e:
                print(f"⚠️  Warning: Could not load {module_name}: {e}")
    
    return generators

def determine_hec_endpoint(output, attr_fields):
    """Determine whether to use raw or event endpoint based on output format."""
    # If it's JSON and has structured fields, use event endpoint
    if output.strip().startswith('{') and attr_fields:
        return HEC_EVENT_URL, True
    else:
        # For syslog, CSV, and other text formats, use raw endpoint
        return HEC_RAW_URL, False

def send_to_hec(output, attr_fields, generator_name, event_num):
    """Send a single event to appropriate HEC endpoint."""
    endpoint_url, is_event_endpoint = determine_hec_endpoint(output, attr_fields)
    
    try:
        if is_event_endpoint:
            # Event endpoint expects structured JSON
            try:
                event_data = json.loads(output)
            except:
                event_data = {"raw": output}
            
            payload = {
                "time": int(time.time()),
                "event": event_data,
                "fields": attr_fields
            }
        else:
            # Raw endpoint expects text with sourcetype
            sourcetype = f"generated_{generator_name}"
            payload = output
            endpoint_url += f"?sourcetype={sourcetype}"
            
            # Add fields as URL parameters if available
            if attr_fields:
                for key, value in attr_fields.items():
                    endpoint_url += f"&{key}={requests.utils.quote(str(value))}"
        
        # Send the request
        if is_event_endpoint:
            response = requests.post(endpoint_url, headers=HEADERS, json=payload, timeout=10)
        else:
            headers = HEADERS.copy()
            headers["Content-Type"] = "text/plain"
            response = requests.post(endpoint_url, headers=headers, data=payload, timeout=10)
        
        if response.status_code == 200:
            return True, "Success"
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Send 5 events from each generator to HEC."""
    print("🚀 HEC Test Suite - Sending 5 events from ALL generators")
    print("=" * 60)
    
    # Discover generators
    generators = discover_generators()
    print(f"📊 Found {len(generators)} generators")
    print(f"🎯 HEC Token: {HEC_TOKEN[:20]}...{HEC_TOKEN[-10:]}")
    print(f"🌐 Raw Endpoint: {HEC_RAW_URL}")
    print(f"🌐 Event Endpoint: {HEC_EVENT_URL}")
    print()
    
    # Statistics
    total_events = 0
    successful_events = 0
    failed_generators = []
    
    # Send events from each generator
    for generator_name in sorted(generators.keys()):
        generator_info = generators[generator_name]
        log_func = generator_info['function']
        attr_fields = generator_info['attr_fields']
        
        print(f"📡 Testing {generator_name}...")
        
        generator_success = 0
        generator_errors = []
        
        # Send 5 events from this generator
        for i in range(1, 6):
            try:
                # Generate event
                output = log_func()
                total_events += 1
                
                # Send to HEC
                success, message = send_to_hec(output, attr_fields, generator_name, i)
                
                if success:
                    successful_events += 1
                    generator_success += 1
                    print(f"  ✅ Event {i}/5: Sent ({len(output)} chars)")
                else:
                    generator_errors.append(f"Event {i}: {message}")
                    print(f"  ❌ Event {i}/5: {message}")
                
                # Small delay between events
                time.sleep(random.uniform(0.1, 0.3))
                
            except Exception as e:
                generator_errors.append(f"Event {i}: Generation error: {str(e)}")
                print(f"  ❌ Event {i}/5: Generation error: {str(e)}")
        
        # Generator summary
        if generator_success == 5:
            print(f"  🎉 {generator_name}: All 5 events sent successfully!")
        elif generator_success > 0:
            print(f"  ⚠️  {generator_name}: {generator_success}/5 events sent")
            failed_generators.append((generator_name, generator_errors))
        else:
            print(f"  💥 {generator_name}: All events failed")
            failed_generators.append((generator_name, generator_errors))
        
        print()
        
        # Delay between generators
        time.sleep(0.5)
    
    # Final summary
    print("=" * 60)
    print("📈 FINAL RESULTS")
    print("=" * 60)
    print(f"🧮 Total generators tested: {len(generators)}")
    print(f"📊 Total events attempted: {total_events}")
    print(f"✅ Successful events: {successful_events}")
    print(f"❌ Failed events: {total_events - successful_events}")
    print(f"📈 Success rate: {(successful_events/total_events*100):.1f}%")
    
    if failed_generators:
        print(f"\n⚠️  Generators with failures ({len(failed_generators)}):")
        for gen_name, errors in failed_generators:
            print(f"  • {gen_name}: {len(errors)} errors")
            for error in errors[:2]:  # Show first 2 errors
                print(f"    - {error}")
    else:
        print("\n🎉 All generators sent all events successfully!")
    
    print(f"\n⏰ Test completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()