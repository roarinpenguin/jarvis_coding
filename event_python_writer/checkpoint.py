#!/usr/bin/env python3
"""Generate synthetic Check Point Firewall logs."""
import json
import random
from datetime import datetime, timezone
import time

# Check Point log fields and values
ACTIONS = ["Accept", "Drop", "Reject", "Encrypt", "Decrypt", "Monitor", "Block", "Allow"]
SERVICES = ["http", "https", "ssh", "ftp", "smtp", "dns", "telnet", "rdp", "smb", "ldap", "ntp", "snmp"]
PROTOCOLS = ["tcp", "udp", "icmp", "esp", "ah", "gre"]
RULES = ["Clean_Traffic", "Block_Malware", "Allow_VPN", "Monitor_Suspicious", "Default_Drop", "Allow_Internal", "Block_External_Threats"]
PRODUCTS = ["VPN-1 & FireWall-1", "Threat Prevention", "URL Filtering", "Application Control", "IPS", "Anti-Bot", "Anti-Virus"]
BLADES = ["fw", "ips", "urlf", "appi", "av", "ab", "dlp", "vpn"]
ORIGINS = ["fw01", "fw02", "cluster-1", "sg80", "sg5000", "mgmt-server"]

def get_random_ip(internal_probability=0.5):
    """Generate a random IP address."""
    if random.random() < internal_probability:
        # Internal IP
        return random.choice([
            f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            f"172.{random.randint(16, 31)}.{random.randint(0, 255)}.{random.randint(1, 254)}",
            f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"
        ])
    else:
        # External IP
        return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def get_port_for_service(service):
    """Get standard port for a service."""
    port_map = {
        "http": 80, "https": 443, "ssh": 22, "ftp": 21, "smtp": 25,
        "dns": 53, "telnet": 23, "rdp": 3389, "smb": 445, "ldap": 389,
        "ntp": 123, "snmp": 161
    }
    return port_map.get(service, random.randint(1024, 65535))

def checkpoint_log(overrides: dict | None = None) -> str:
    """Generate a single Check Point Firewall log entry."""
    now = datetime.now(timezone.utc)
    
    # Determine action and related fields
    action = random.choice(ACTIONS)
    is_allowed = action in ["Accept", "Allow", "Encrypt", "Monitor"]
    
    # Generate source and destination IPs
    src_ip = get_random_ip(internal_probability=0.7 if is_allowed else 0.3)
    dst_ip = get_random_ip(internal_probability=0.3 if is_allowed else 0.7)
    
    # Select service and protocol
    service = random.choice(SERVICES)
    proto = "tcp" if service in ["http", "https", "ssh", "ftp", "smtp", "rdp", "smb", "ldap"] else random.choice(PROTOCOLS)
    
    # Generate ports
    if proto in ["tcp", "udp"]:
        dst_port = get_port_for_service(service)
        src_port = random.randint(1024, 65535)
    else:
        dst_port = 0
        src_port = 0
    
    # Build the log entry with key="value" format
    fields = {
        "time": now.strftime("%b %d %H:%M:%S"),
        "orig": src_ip,
        "origin": random.choice(ORIGINS),
        "action": action,
        "src": src_ip,
        "dst": dst_ip,
        "proto": proto,
        "service": str(dst_port) if dst_port else service,
        "s_port": str(src_port),
        "d_port": str(dst_port) if dst_port else "",
        "rule": random.choice(RULES),
        "rule_uid": f"{{{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}-{random.randint(100000000000, 999999999999)}}}",
        "product": random.choice(PRODUCTS),
        "blade": random.choice(BLADES),
        "ifdir": random.choice(["inbound", "outbound"]),
        "ifname": random.choice(["eth0", "eth1", "eth2", "bond0", "Internal", "External"]),
        "loguid": f"{{{random.randint(0, 9)}{random.choice(['a', 'b', 'c', 'd', 'e', 'f'])}{random.randint(100000, 999999)}}}",
        "version": "5",
        "fw_subproduct": "VPN-1",
        "__policy_id_tag": "Standard",
        "nat_rulenum": str(random.randint(1, 100)) if random.random() < 0.3 else "0",
        "nat_addtnl_rulenum": "0",
        "bytes": str(random.randint(100, 1000000)) if is_allowed else str(random.randint(40, 1500)),
        "packets": str(random.randint(1, 1000)) if is_allowed else str(random.randint(1, 10)),
        "elapsed": str(random.randint(0, 300)) if is_allowed else "0",
        "hostname": f"checkpoint-{random.randint(1, 5)}.company.com",
        "sequencenum": str(random.randint(1, 1000000)),
        "dataSource": {
            "category": "security",
            "name": "Check Point Firewall",
            "vendor": "Check Point"
        }
    }
    
    # Add threat-specific fields for certain actions
    if action in ["Drop", "Block", "Reject"] and random.random() < 0.5:
        fields.update({
            "attack": random.choice([
                "Malformed Packet", "Port Scan", "SQL Injection", 
                "Cross Site Scripting", "Buffer Overflow", "Malware",
                "Trojan", "Botnet Communication", "Brute Force"
            ]),
            "severity": random.choice(["Critical", "High", "Medium", "Low"]),
            "confidence_level": str(random.randint(1, 5)),
            "protection_type": "IPS",
            "malware_action": "Blocked"
        })
    
    # Format as key="value" pairs
    log_parts = []
    for key, value in fields.items():
        if key == "dataSource":
            continue  # Skip dataSource in the log string format
        if value:  # Only include non-empty values
            log_parts.append(f'{key}="{value}"')
    
    # Add timestamp prefix
    timestamp = now.strftime("%b %-d %H:%M:%S")
    hostname = fields["hostname"]
    
    # Apply overrides
    if overrides:
        for key, value in overrides.items():
            # Find and replace the key="value" pair in log_parts
            for i, part in enumerate(log_parts):
                if part.startswith(f'{key}="'):
                    log_parts[i] = f'{key}="{value}"'
                    break
            else:
                log_parts.append(f'{key}="{value}"')
    
    # Construct the final log string
    log_string = f"{timestamp} {hostname} " + " ".join(log_parts)
    
    return log_string

# OCSF-style attributes for HEC
ATTR_FIELDS = {
    "dataSource.category": "security",
    "dataSource.name": "Check Point Firewall",
    "dataSource.vendor": "Check Point"
}

if __name__ == "__main__":
    # Generate sample logs
    for _ in range(5):
        print(checkpoint_log())