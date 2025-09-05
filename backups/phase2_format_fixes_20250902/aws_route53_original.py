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

# Common domains with Star Trek themed enterprise domains
DOMAINS = [
    "starfleet.corp",
    "www.starfleet.corp", 
    "api.starfleet.corp",
    "bridge.enterprise.starfleet.corp",
    "engineering.enterprise.starfleet.corp",
    "sickbay.enterprise.starfleet.corp",
    "google.com",
    "amazonaws.com",
    "microsoft.com",
    "cloudflare.com",
    "github.com",
    "stackoverflow.com",
    "romulan-spy.org",
    "borg-collective.net",
    "ferengi-trading.com"
]

# AWS edge locations
EDGE_LOCATIONS = [
    "IAD79-P3", "DFW50-P2", "LAX3-P1", "SEA19-P4", 
    "ORD52-P3", "ATL56-P2", "SFO53-P1", "MIA50-P3"
]

def generate_client_ip() -> str:
    """Generate client IP address"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def aws_route53_log(overrides: dict = None) -> str:
    """Generate a single AWS Route 53 DNS event log in syslog format"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 10))
    
    domain = random.choice(DOMAINS)
    query_type = random.choice(QUERY_TYPES)
    response_code = random.choice(RESPONSE_CODES)
    edge_location = random.choice(EDGE_LOCATIONS)
    
    timestamp = event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # Generate syslog format
    log = (f'{timestamp} Route53 queryName="{domain}" queryType="{query_type}" '
           f'clientIp="{generate_client_ip()}" edgeLocation="{edge_location}" '
           f'responseCode="{response_code}" resolverEndpointId="rslvr-endpt-{random.randint(1000, 9999)}"')
    
    # Apply overrides if provided (for scenario customization)
    if overrides:
        # For syslog format, we can override individual fields
        if "domain" in overrides:
            log = log.replace(f'queryName="{domain}"', f'queryName="{overrides["domain"]}"')
        if "query_type" in overrides:
            log = log.replace(f'queryType="{query_type}"', f'queryType="{overrides["query_type"]}"')
        if "response_code" in overrides:
            log = log.replace(f'responseCode="{response_code}"', f'responseCode="{overrides["response_code"]}"')
    
    return log

if __name__ == "__main__":
    # Generate sample events
    print("Sample AWS Route 53 DNS Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(aws_route53_log())