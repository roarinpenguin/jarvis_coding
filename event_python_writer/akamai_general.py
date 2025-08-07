#!/usr/bin/env python3
"""
Akamai Security event generator
"""
from __future__ import annotations
import random
import time
from datetime import datetime, timezone
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Akamai",
    "dataSource.name": "Akamai Security",
    "dataSource.category": "security",
    "metadata.product.vendor_name": "Akamai",
    "metadata.product.name": "Akamai Security",
    "metadata.version": "1.0.0",
    "class_uid": "2001",
    "class_name": "Security Control",
    "category_uid": "2",
    "category_name": "Findings",
    "activity_id": "1",
    "activity_name": "Security Alert",
    "type_uid": "200101"
}

def akamai_general_log() -> Dict:
    """Generate Akamai Security event"""
    
    # Malicious IPs
    malicious_ips = [
        "198.51.100.24", "203.0.113.45", "192.0.2.100",
        "198.51.100.50", "203.0.113.75", "192.168.1.200"
    ]
    
    # Target hosts
    hosts = [
        "www.example.com", "api.example.com", "shop.example.com",
        "admin.example.com", "app.example.com", "login.example.com"
    ]
    
    # Attack paths
    attack_paths = [
        "/login", "/register", "/admin", "/api/v1/users",
        "/upload", "/search", "/contact", "/checkout"
    ]
    
    # Attack types and corresponding rule IDs
    attacks = [
        {"type": "SQL_Injection", "rule_ids": ["981176", "981318", "981242"], "severity": 4},
        {"type": "Cross_Site_Scripting", "rule_ids": ["941130", "941150", "941180"], "severity": 3},
        {"type": "Command_Injection", "rule_ids": ["932160", "932115"], "severity": 4},
        {"type": "Path_Traversal", "rule_ids": ["930100", "930110"], "severity": 3},
        {"type": "API_Scan", "rule_ids": ["100015", "100020"], "severity": 2}
    ]
    
    # Actions
    actions = ["blocked", "alert", "logged", "denied"]
    
    # HTTP methods
    methods = ["GET", "POST", "PUT", "DELETE", "HEAD"]
    
    # User agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
        "curl/7.88.0",
        "python-requests/2.28.1",
        "Nmap NSE",
        "sqlmap/1.6.12"
    ]
    
    # Generate event data
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    client_ip = random.choice(malicious_ips)
    host = random.choice(hosts)
    path = random.choice(attack_paths)
    attack = random.choice(attacks)
    rule_id = random.choice(attack["rule_ids"])
    action = random.choice(actions)
    method = random.choice(methods)
    user_agent = random.choice(user_agents)
    
    # Status code based on action
    if action in ["blocked", "denied"]:
        status_code = random.choice([403, 406, 451])
    else:
        status_code = random.choice([200, 302])
    
    # Generate attack-specific messages
    messages = {
        "SQL_Injection": [
            f"Attempted SQL injection in {path.split('/')[-1]} parameter detected and {action}",
            f"SQL injection attack blocked from {client_ip}",
            f"Malicious SQL pattern detected in request to {path}"
        ],
        "Cross_Site_Scripting": [
            f"Potential XSS pattern detected; request {action}",
            f"Cross-site scripting attempt {action}",
            f"XSS payload detected in {path}"
        ],
        "Command_Injection": [
            f"Command injection attempt {action}",
            f"OS command execution pattern detected",
            f"Shell command injection blocked"
        ],
        "Path_Traversal": [
            f"Directory traversal attempt {action}",
            f"Path traversal attack detected",
            f"File inclusion attempt blocked"
        ],
        "API_Scan": [
            f"Unusual API scanning behavior logged for further analysis",
            f"Automated scanning detected from {client_ip}",
            f"API enumeration attempt identified"
        ]
    }
    
    message = random.choice(messages[attack["type"]])
    
    # Create OCSF-compliant event
    event = {
        "timestamp": timestamp,
        "time": int(time.time() * 1000),
        "class_uid": 2001,
        "class_name": "Security Control",
        "category_uid": 2,
        "category_name": "Findings",
        "activity_id": 1,
        "activity_name": "Security Alert",
        "type_uid": 200101,
        "severity_id": attack["severity"],
        "status_id": 2 if action in ["blocked", "denied"] else 1,
        
        "src_endpoint": {
            "ip": client_ip
        },
        
        "http_request": {
            "hostname": host,
            "http_method": method,
            "url": {
                "path": path
            },
            "user_agent": user_agent
        },
        
        "http_response": {
            "code": status_code
        },
        
        "finding": {
            "type": attack["type"],
            "desc": message
        },
        
        "disposition": action,
        "message": message,
        
        "metadata": {
            "rule_uid": rule_id,
            "version": "1.0.0",
            "product": {
                "vendor_name": "Akamai",
                "name": "Akamai Security"
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
            },
            {
                "name": "attack_type",
                "type": "Other",
                "value": attack["type"]
            }
        ],
        
        **ATTR_FIELDS
    }
    
    return event


if __name__ == "__main__":
    print(akamai_general_log())