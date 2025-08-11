#!/usr/bin/env python3
"""
Check Point Next Generation Firewall Event Generator
Generates synthetic Check Point NGFW security events for testing
"""

import random
import time
import json
from datetime import datetime, timezone

# SentinelOne AI-SIEM specific field attributes
ATTR_FIELDS = {
    "vendor": "Check Point",
    "product": "Next Generation Firewall",
    "version": "1.0",
    "category": "network_security"
}

def check_point_ngfw_log():
    """Generate a synthetic Check Point NGFW log event."""
    
    # Check Point log format: timestamp hostname action=accept/drop src=IP dst=IP service=port proto=TCP/UDP
    timestamp = datetime.now().strftime("%d%b%Y %H:%M:%S")
    hostname = f"cp-gw-{random.randint(10,99)}"
    
    # Generate realistic Check Point fields
    actions = ["accept", "drop", "reject", "encrypt", "decrypt"]
    protocols = ["tcp", "udp", "icmp", "esp", "ah"]
    services = ["http", "https", "ssh", "smtp", "dns", "ftp"]
    
    src_ip = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
    dst_ip = f"203.0.113.{random.randint(1,254)}"
    action = random.choice(actions)
    protocol = random.choice(protocols)
    service = random.choice(services)
    
    # Build Check Point log message
    log_fields = [
        f"action={action}",
        f"src={src_ip}",
        f"dst={dst_ip}",
        f"service={service}",
        f"proto={protocol}",
        f"rule_name=Rule_{random.randint(1,100)}",
        f"rule_uid={{uuid-{random.randint(1000,9999)}}}",
        f"policy_name=Standard_Policy",
        f"layer_name=Network",
        f"bytes={random.randint(64, 65535)}",
        f"packets={random.randint(1, 1000)}"
    ]
    
    # Add conditional fields
    if action == "drop":
        log_fields.append(f"drop_reason=Rule_{random.randint(1,50)}")
    
    if protocol == "tcp":
        log_fields.extend([
            f"s_port={random.randint(1024, 65535)}",
            f"d_port={random.choice([80, 443, 22, 25, 993])}"
        ])
    
    log_message = "; ".join(log_fields)
    
    # Check Point syslog format
    raw_log = f"{timestamp} {hostname} {log_message}"
    
    return {
        "raw": raw_log,
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "vendor": "Check Point",
        "product": "Next Generation Firewall",
        "action": action,
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "protocol": protocol,
        "service": service,
        "hostname": hostname
    }

if __name__ == "__main__":
    # Generate and print sample events
    print("Check Point NGFW Log Examples:")
    print("=" * 50)
    
    for i in range(3):
        event = check_point_ngfw_log()
        print(f"\nEvent {i+1}:")
        print(f"Raw: {event['raw']}")
        print(f"Action: {event['action']}")
        print(f"Source: {event['src_ip']} → Destination: {event['dst_ip']}")