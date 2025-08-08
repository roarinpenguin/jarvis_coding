#!/usr/bin/env python3
"""
AWS Route 53 event generator
Generates synthetic AWS Route 53 DNS query logs in syslog format
"""
import random
from datetime import datetime, timezone, timedelta

# SentinelOne AI-SIEM specific field attributes
ATTR_FIELDS = {
    "dataSource.vendor": "AWS",
    "dataSource.name": "AWS Route 53",
    "dataSource.category": "network"
}

# DNS query types
QUERY_TYPES = ["A", "AAAA", "MX", "NS", "PTR", "SOA", "TXT", "CNAME", "SRV"]

# Response codes
RESPONSE_CODES = [
    "NOERROR",
    "NXDOMAIN", 
    "SERVFAIL",
    "REFUSED",
    "TIMEOUT"
]

# Common domains
DOMAINS = [
    "example.com",
    "www.example.com",
    "api.example.com",
    "google.com",
    "amazonaws.com",
    "microsoft.com",
    "cloudflare.com",
    "github.com",
    "stackoverflow.com",
    "nonexistent.example",
    "malicious.example",
    "phishing-site.org"
]

# AWS edge locations
EDGE_LOCATIONS = [
    "IAD79-P3", "DFW50-P2", "LAX3-P1", "SEA19-P4", 
    "ORD52-P3", "ATL56-P2", "SFO53-P1", "MIA50-P3"
]

def generate_client_ip() -> str:
    """Generate client IP address"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def aws_route53_log() -> str:
    """Generate a single AWS Route 53 DNS event log in syslog format"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 1440))
    
    domain = random.choice(DOMAINS)
    query_type = random.choice(QUERY_TYPES)
    response_code = random.choice(RESPONSE_CODES)
    edge_location = random.choice(EDGE_LOCATIONS)
    
    timestamp = event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Generate syslog format
    log = (f'{timestamp} Route53 queryName="{domain}" queryType="{query_type}" '
           f'clientIp="{generate_client_ip()}" edgeLocation="{edge_location}" '
           f'responseCode="{response_code}" resolverEndpointId="rslvr-endpt-{random.randint(1000, 9999)}"')
    
    return log

if __name__ == "__main__":
    # Generate sample events
    print("Sample AWS Route 53 DNS Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(aws_route53_log())