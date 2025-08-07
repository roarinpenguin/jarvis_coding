#!/usr/bin/env python3
"""
Akamai CDN access log event generator
"""
from __future__ import annotations
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Akamai",
    "dataSource.name": "Akamai CDN",
    "dataSource.category": "network",
    "metadata.product.vendor_name": "Akamai",
    "metadata.product.name": "Akamai CDN", 
    "metadata.version": "1.0.0",
    "class_uid": "4002",
    "class_name": "HTTP Activity",
    "category_uid": "4", 
    "category_name": "Network Activity",
    "activity_id": "1",
    "activity_name": "HTTP Request",
    "type_uid": "400201"
}

def akamai_cdn_log() -> Dict:
    """Generate Akamai CDN access log event"""
    
    # Generate realistic client IPs
    client_ips = [
        "198.51.100.40", "203.0.113.90", "192.0.2.100",
        "198.51.100.25", "203.0.113.55", "192.168.1.10"
    ]
    
    # Edge server IPs
    edge_ips = [
        "203.0.113.210", "203.0.113.211", "203.0.113.212", 
        "203.0.113.213", "203.0.113.214", "203.0.113.215"
    ]
    
    # Common hostnames
    hosts = [
        "www.example.com", "api.example.com", "cdn.example.com",
        "assets.example.com", "static.example.com", "media.example.com"
    ]
    
    # Common paths
    paths = [
        "/index.html", "/api/v1/data", "/images/logo.png",
        "/css/main.css", "/js/app.js", "/favicon.ico",
        "/api/v2/users", "/health", "/unknown", "/404"
    ]
    
    # HTTP methods
    methods = ["GET", "POST", "PUT", "HEAD", "OPTIONS"]
    
    # Status codes with weights
    status_codes = [200, 200, 200, 200, 301, 302, 404, 500, 502, 503]
    
    # Cache statuses
    cache_statuses = ["HIT", "MISS", "PASS", "STALE"]
    
    # Geographic locations
    locations = [
        ("US", "Seattle"), ("US", "Chicago"), ("US", "Boston"),
        ("US", "Los Angeles"), ("US", "New York"), ("CA", "Toronto"),
        ("UK", "London"), ("DE", "Berlin"), ("JP", "Tokyo")
    ]
    
    # Generate event data
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    stream_id = f"stream-{random.randint(100, 999)}"
    config_id = str(random.randint(10000, 99999))
    request_id = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=10))
    status_code = random.choice(status_codes)
    client_ip = random.choice(client_ips)
    host = random.choice(hosts)
    method = random.choice(methods)
    path = random.choice(paths)
    
    # Adjust path based on status code
    if status_code == 404:
        path = "/unknown" + str(random.randint(1, 999))
    
    bytes_sent = random.choice([512, 1024, 2048, 5120, 10240, 20480, 51200])
    cache_status = random.choice(cache_statuses)
    
    # Response time varies by cache status
    if cache_status == "HIT":
        response_time = random.randint(10, 50)
    elif cache_status == "MISS":
        response_time = random.randint(50, 150) 
    else:
        response_time = random.randint(30, 100)
        
    edge_ip = random.choice(edge_ips)
    country, city = random.choice(locations)
    
    # Create OCSF-compliant event
    event = {
        "timestamp": timestamp,
        "time": int(time.time() * 1000),
        "class_uid": 4002,
        "class_name": "HTTP Activity",
        "category_uid": 4,
        "category_name": "Network Activity", 
        "activity_id": 1,
        "activity_name": "HTTP Request",
        "type_uid": 400201,
        "severity_id": 1 if status_code < 400 else 2,
        "status_id": 1 if status_code < 400 else 2,
        
        "src_endpoint": {
            "ip": client_ip,
            "location": {
                "country": country,
                "city": city
            }
        },
        
        "dst_endpoint": {
            "ip": edge_ip
        },
        
        "http_request": {
            "hostname": host,
            "http_method": method,
            "url": {
                "path": path
            }
        },
        
        "http_response": {
            "code": status_code,
            "length": bytes_sent
        },
        
        "response_time": response_time,
        
        "enrichments": {
            "cache_status": cache_status,
            "stream_id": stream_id,
            "config_id": config_id
        },
        
        "metadata": {
            "correlation_uid": request_id,
            "log_name": stream_id,
            "version": "1.0.0",
            "product": {
                "vendor_name": "Akamai", 
                "name": "Akamai CDN"
            }
        },
        
        "observables": [
            {
                "name": "src_ip",
                "type": "IP Address", 
                "value": client_ip
            },
            {
                "name": "hostname",
                "type": "Hostname",
                "value": host
            }
        ],
        
        **ATTR_FIELDS
    }
    
    return event


if __name__ == "__main__":
    print(akamai_cdn_log())