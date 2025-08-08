#!/usr/bin/env python3
"""
Zscaler DNS Firewall event generator
Generates synthetic Zscaler Internet Access DNS firewall logs
"""
import json
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Zscaler",
    "dataSource.name": "Zscaler DNS Firewall",
    "dataSource.category": "security",
}

# DNS query types
QUERY_TYPES = ["A", "AAAA", "MX", "NS", "PTR", "SOA", "TXT", "CNAME", "SRV"]

# Response codes
RESPONSE_CODES = ["NOERROR", "NXDOMAIN", "SERVFAIL", "REFUSED"]

# Actions
ACTIONS = ["ALLOWED", "BLOCKED", "REDIRECTED"]

# Policy IDs
POLICY_IDS = [
    "MALWARE-DOMAIN", "PHISHING-PROTECTION", "BOTNET-DETECTION",
    "DATA-LOSS-PREVENTION", "SECURITY-POLICY", "CONTENT-FILTER"
]

# Threat categories
THREAT_CATEGORIES = [
    "Malware", "Phishing", "Botnet", "Command & Control",
    "Suspicious", "Adult Content", "Gambling", "Social Media"
]

# Domains
DOMAINS = [
    "google.com", "microsoft.com", "amazon.com", "cloudflare.com",
    "github.com", "stackoverflow.com", "linkedin.com",
    "malicious.example", "phishing-site.org", "c2-server.net",
    "botnet.com", "suspicious-domain.com", "unknown.example"
]

# Users
USERS = [
    "alice@example.com", "bob@example.com", "charlie@example.com",
    "admin@example.com", "guest@example.com", "contractor@partner.com"
]

# Device IDs
DEVICE_IDS = [
    "LAPTOP-01", "LAPTOP-02", "LAPTOP-03", "DESKTOP-01", 
    "DESKTOP-02", "MOBILE-01", "MOBILE-02", "TABLET-01"
]

def generate_ip() -> str:
    """Generate source IP address"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def generate_answer_ip() -> str:
    """Generate DNS answer IP address"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def zscaler_dns_firewall_log() -> str:
    """Generate a single Zscaler DNS Firewall event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 1440))
    
    query = random.choice(DOMAINS)
    query_type = random.choice(QUERY_TYPES)
    response_code = random.choice(RESPONSE_CODES)
    user_name = random.choice(USERS)
    source_ip = generate_ip()
    device_id = random.choice(DEVICE_IDS)
    
    # Determine if this is a threat
    is_threat = any(threat in query for threat in ["malicious", "phishing", "c2-server", "botnet", "suspicious"])
    
    # Set action and other fields based on threat status
    if is_threat:
        action = "BLOCKED"
        policy_id = random.choice(POLICY_IDS)
        threat_category = random.choice(THREAT_CATEGORIES)
        answer = ""  # No answer for blocked queries
    else:
        action = "ALLOWED"
        policy_id = None
        threat_category = None
        if response_code == "NOERROR" and query_type == "A":
            answer = generate_answer_ip()
        elif response_code == "NOERROR" and query_type == "AAAA":
            answer = f"2001:db8::{random.randint(1, 65535):x}"
        else:
            answer = ""
    
    event = {
        "timestamp": event_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "userName": user_name,
        "sourceIp": source_ip,
        "deviceId": device_id,
        "query": query,
        "queryType": query_type,
        "responseCode": response_code,
        "answer": answer,
        "action": action,
        "bytes_sent": random.randint(50, 1000),
        "bytes_received": random.randint(50, 1000),
        "response_time_ms": random.randint(1, 500),
        **ATTR_FIELDS
    }
    
    # Add threat-related fields if applicable
    if is_threat:
        event["policyId"] = policy_id
        event["threatCategory"] = threat_category
        event["risk_score"] = random.randint(7, 10)
        event["blocked_reason"] = "Domain blocked by security policy"
    
    return json.dumps(event, separators=(',', ':'))

if __name__ == "__main__":
    # Generate sample events
    print("Sample Zscaler DNS Firewall Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(zscaler_dns_firewall_log())