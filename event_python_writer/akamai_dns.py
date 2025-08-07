#!/usr/bin/env python3
"""
Akamai DNS query log event generator
"""
from __future__ import annotations
import random
import time
from datetime import datetime, timezone
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Akamai",
    "dataSource.name": "Akamai DNS",
    "dataSource.category": "network", 
    "metadata.product.vendor_name": "Akamai",
    "metadata.product.name": "Akamai DNS",
    "metadata.version": "1.0.0",
    "class_uid": "4003",
    "class_name": "DNS Activity",
    "category_uid": "4",
    "category_name": "Network Activity",
    "activity_id": "1", 
    "activity_name": "DNS Query",
    "type_uid": "400301"
}

def akamai_dns_log() -> Dict:
    """Generate Akamai DNS query log event"""
    
    # Generate realistic client IPs
    client_ips = [
        "198.51.100.30", "203.0.113.60", "192.0.2.80",
        "198.51.100.45", "203.0.113.75", "192.168.1.15"
    ]
    
    # Resolver IPs
    resolver_ips = [
        "203.0.113.200", "203.0.113.201", "203.0.113.202",
        "8.8.8.8", "1.1.1.1", "9.9.9.9"
    ]
    
    # Common domains
    domains = [
        "www.example.com", "api.example.com", "mail.example.com",
        "cdn.example.com", "blog.example.com", "shop.example.com", 
        "nonexistent.example.com", "test.example.org", "app.example.net"
    ]
    
    # DNS record types
    record_types = ["A", "AAAA", "CNAME", "MX", "NS", "TXT", "SRV"]
    
    # DNS response codes with weights
    response_codes = [
        "NOERROR", "NOERROR", "NOERROR", "NOERROR", "NOERROR",
        "NXDOMAIN", "SERVFAIL", "FORMERR", "REFUSED"
    ]
    
    # Edge servers
    edge_servers = [
        "edge-ldn", "edge-sfo", "edge-nyc", "edge-fra", 
        "edge-nrt", "edge-syd", "edge-ams", "edge-mia"
    ]
    
    # Generate event data
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    stream_id = f"dns-{random.randint(100, 999)}"
    client_ip = random.choice(client_ips)
    resolver_ip = random.choice(resolver_ips)
    domain = random.choice(domains)
    record_type = random.choice(record_types)
    response_code = random.choice(response_codes)
    edge_server = random.choice(edge_servers)
    
    # Generate appropriate answer based on response code and record type
    answer = ""
    if response_code == "NOERROR":
        if record_type == "A":
            answer = f"192.0.2.{random.randint(1, 254)}"
        elif record_type == "AAAA":
            answer = f"2001:db8::{random.randint(1, 255):x}"
        elif record_type == "CNAME": 
            answer = f"alias.{domain}"
        elif record_type == "MX":
            answer = f"{random.randint(10, 50)} mail.{domain}"
        elif record_type == "TXT":
            answer = "v=spf1 include:_spf.example.com ~all"
        else:
            answer = f"ns1.{domain}"
    
    # TTL based on record type and response
    if response_code == "NOERROR":
        if record_type in ["A", "AAAA"]:
            ttl = random.choice([300, 600, 1800, 3600])
        elif record_type == "CNAME":
            ttl = random.choice([300, 600, 1800])
        else:
            ttl = random.choice([3600, 7200, 86400])
    else:
        ttl = 0
        
    # Response size
    bytes_size = random.choice([64, 96, 128, 192, 256, 384])
    
    # Create OCSF-compliant event  
    event = {
        "timestamp": timestamp,
        "time": int(time.time() * 1000),
        "class_uid": 4003,
        "class_name": "DNS Activity",
        "category_uid": 4,
        "category_name": "Network Activity",
        "activity_id": 1,
        "activity_name": "DNS Query", 
        "type_uid": 400301,
        "severity_id": 1 if response_code == "NOERROR" else 2,
        "status_id": 1 if response_code == "NOERROR" else 2,
        
        "src_endpoint": {
            "ip": client_ip
        },
        
        "dst_endpoint": {
            "ip": resolver_ip
        },
        
        "query": {
            "hostname": domain,
            "type": record_type
        },
        
        "response": {
            "code": response_code,
            "length": bytes_size
        },
        
        "answers": [
            {
                "address": answer,
                "ttl": ttl,
                "type": record_type
            }
        ] if answer else [],
        
        "enrichments": {
            "edge_server": edge_server,
            "stream_id": stream_id
        },
        
        "metadata": {
            "log_name": edge_server,
            "correlation_uid": stream_id,
            "version": "1.0.0",
            "product": {
                "vendor_name": "Akamai",
                "name": "Akamai DNS"
            }
        },
        
        "observables": [
            {
                "name": "query_hostname",
                "type": "Hostname", 
                "value": domain
            },
            {
                "name": "src_ip",
                "type": "IP Address",
                "value": client_ip
            }
        ],
        
        **ATTR_FIELDS
    }
    
    return event


if __name__ == "__main__":
    print(akamai_dns_log())