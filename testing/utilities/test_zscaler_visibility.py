#!/usr/bin/env python3
"""
Test Zscaler Event Visibility
==============================
Send test Zscaler events with clear markers for validation
"""

import os
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'

from zscaler import zscaler_log
from hec_sender import send_one
from datetime import datetime, timezone
import time

def test_zscaler_events():
    """Send clearly marked Zscaler test events"""
    
    print("🔍 ZSCALER VISIBILITY TEST")
    print("=" * 60)
    
    # Generate 5 test events with unique markers
    for i in range(1, 6):
        event = zscaler_log()
        
        # Add unique search markers
        timestamp = datetime.now(timezone.utc).isoformat()
        event['datetime'] = timestamp
        event['timestamp'] = timestamp
        event['user'] = f"ZSCALER_TEST_USER_{i}"
        event['urlcategory'] = f"TEST_CATEGORY_{i}"
        event['action'] = "allowed" if i % 2 == 0 else "blocked"
        event['bytes_out'] = 10000000 * i  # Large uploads for exfiltration
        event['hostname'] = f"test-host-{i}.example.com"
        
        # Add threat indicators for some events
        if i > 3:
            event['threatname'] = f"TEST_THREAT_{i}"
            event['malware_category'] = "Test Malware"
            event['risk_score'] = 80 + i
        
        print(f"\n📤 Sending Zscaler test event {i}:")
        print(f"   User: {event['user']}")
        print(f"   Category: {event['urlcategory']}")
        print(f"   Action: {event['action']}")
        print(f"   Bytes: {event['bytes_out']}")
        
        # Send to HEC
        attr_fields = {
            "dataSource.vendor": "Zscaler",
            "dataSource.name": "Zscaler Internet Access",
            "dataSource.category": "security"
        }
        
        try:
            result = send_one(event, 'zscaler', attr_fields)
            print(f"   ✅ Sent successfully: {result}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)  # Space out events
    
    print("\n" + "=" * 60)
    print("✅ ZSCALER TEST COMPLETE")
    print("\n🔍 SEARCH QUERIES TO VALIDATE:")
    print('   sourcetype="marketplace-zscalerinternetaccess-latest"')
    print('   sourcetype="marketplace-zscalerinternetaccess-latest" user="ZSCALER_TEST_USER_*"')
    print('   sourcetype="marketplace-zscalerinternetaccess-latest" bytes_out>10000000')
    print('   sourcetype="marketplace-zscalerinternetaccess-latest" threatname="TEST_THREAT_*"')

if __name__ == "__main__":
    test_zscaler_events()