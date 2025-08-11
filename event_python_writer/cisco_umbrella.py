#!/usr/bin/env python3
"""
Cisco Umbrella synthetic log generator
"""
import requests
import json
import csv, io, random, time, uuid

ATTR_FIELDS = {
    "dataSource.vendor": "Cisco",
    "dataSource.name": "Cisco Umbrella",
    "dataSource.category": "security",
    "LogType": "proxylogs",
}

def _ts():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

def umbrella_proxy_log():
    row = [
        _ts(), "Finance‑Dept", "10.0.1.55", "8.8.8.8", "93.184.216.34", "text/html",
        random.choice(["Allowed", "Blocked"]),
        "http://example.com/pdf", "http://ref.example.com",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        str(random.choice([200, 302, 403])), str(random.randint(200, 2000)),
        str(random.randint(500, 50000)), str(random.randint(100, 48000)),
        uuid.uuid4().hex,
        random.choice(["Malware", "Phishing", "None"]),
        str(random.randint(0, 3)), str(random.randint(0, 2)),
        random.choice(["Malicious", "Clean"]),
        "" if random.random() < 0.8 else "Eicar-Test-File",
        str(random.randint(0, 100)),
        "Roaming Computer",
        "" if random.random() < 0.7 else "Malware",
        "ACME‑Laptop42;Finance", "Roaming Computer;Group",
        random.choice(["GET", "POST"]), random.choice(["Clean", "Violation"]),
        "" if random.random() < 0.85 else "CertError",
        "download.exe",
        str(random.randint(1000, 9999)), str(random.randint(100000, 999999)),
        "123;456",
    ]
    buf = io.StringIO()
    csv.writer(buf, quoting=csv.QUOTE_ALL).writerow(row)
    return buf.getvalue().strip()

def umbrella_dns_log():
    row = [
        _ts(), "ACME‑Laptop42", "ACME‑Laptop42;Finance", "10.0.1.55", "8.8.8.8",
        random.choice(["Allowed", "Blocked"]),
        random.choice(["A", "AAAA", "CNAME", "TXT"]),
        random.choice(["NOERROR", "NXDOMAIN"]),
        random.choice(["example.com", "malware.test"]),
        random.choice(["Malware", "Phishing;Malware", "None"]),
        "Roaming Computer", "Roaming Computer;Group",
        "" if random.random() < 0.8 else "Malware",
    ]
    buf = io.StringIO()
    csv.writer(buf, quoting=csv.QUOTE_ALL).writerow(row)
    return buf.getvalue().strip()

def umbrella_audit_log():
    row = [
        str(uuid.uuid4()), _ts(),
        f"user{random.randint(1000,9999)}@example.com",
        random.choice(["alice", "bob", "charlie"]),
        random.choice(["LOGIN", "POLICY_UPDATE"]),
        random.choice(["SUCCESS", "FAILURE"]),
        f"203.0.113.{random.randint(1,254)}",
        "{}", "{}"
    ]
    buf = io.StringIO()
    csv.writer(buf, quoting=csv.QUOTE_ALL).writerow(row)
    return buf.getvalue().strip()

def cisco_umbrella_log():
    """
    Main function for JSON format compatible with parse=gron parser.
    
    Generates Cisco Umbrella DNS security events that represent:
    - DNS query logs from enterprise endpoints
    - Security policy enforcement (allowed/blocked domains)
    - Threat detection for malware, phishing, and C2 domains
    - Identity-based policy application
    
    Event Fields:
    - timestamp: When the DNS query occurred
    - identity: Device/computer making the DNS request
    - identity_types: Additional identity context (department, groups)
    - internal_ip: Internal IP of the requesting device
    - external_ip: External DNS resolver IP
    - action: Security disposition (Allowed/Blocked)
    - query_type: DNS record type (A, AAAA, CNAME, TXT)
    - response_code: DNS response (NOERROR, NXDOMAIN)
    - domain: The domain being queried
    - categories: Security categorization (Malware, Phishing, None)
    - policy_identity: Applied security policy
    - policy_identity_type: Policy context
    - blocked_categories: Categories that triggered blocking
    
    Use Cases:
    - Detecting DNS tunneling attempts
    - Identifying C2 communication
    - Blocking malware domains
    - Enforcing acceptable use policies
    - Tracking DNS-based data exfiltration
    """
    return {
        "timestamp": _ts(),
        "identity": f"ACME-Laptop{random.randint(10,99)}",
        "identity_types": f"ACME-Laptop{random.randint(10,99)};Finance",
        "internal_ip": f"10.0.1.{random.randint(1,254)}",
        "external_ip": "8.8.8.8",
        "action": random.choice(["Allowed", "Blocked"]),
        "query_type": random.choice(["A", "AAAA", "CNAME", "TXT"]),
        "response_code": random.choice(["NOERROR", "NXDOMAIN"]),
        "domain": random.choice(["example.com", "malware.test", "phishing.example"]),
        "categories": random.choice(["Malware", "Phishing;Malware", "None"]),
        "policy_identity": "Roaming Computer",
        "policy_identity_type": "Roaming Computer;Group", 
        "blocked_categories": "" if random.random() < 0.8 else "Malware",
        **ATTR_FIELDS
    }
