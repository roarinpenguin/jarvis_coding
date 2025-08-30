# Generator Development Tutorial

Learn how to create, modify, and test security event generators for the Jarvis Coding platform.

## 📚 Table of Contents
1. [Understanding Generators](#understanding-generators)
2. [Generator Anatomy](#generator-anatomy)
3. [Creating Your First Generator](#creating-your-first-generator)
4. [Output Formats](#output-formats)
5. [Star Trek Theme Integration](#star-trek-theme-integration)
6. [Testing Your Generator](#testing-your-generator)
7. [Best Practices](#best-practices)
8. [Advanced Techniques](#advanced-techniques)

## Understanding Generators

### What is a Generator?

A generator is a Python module that creates realistic security event logs for a specific product or service. Each generator:
- Produces events in the format expected by its parser
- Includes Star Trek themed test data
- Generates timestamps from the last 10 minutes
- Returns structured data (dict/string)

### Generator Categories

Generators are organized by security domain:
```
event_generators/
├── cloud_infrastructure/     # AWS, GCP, Azure
├── network_security/         # Firewalls, NDR
├── endpoint_security/        # EDR, Antivirus
├── identity_access/          # IAM, SSO, PAM
├── email_security/           # Email gateways
├── web_security/            # WAF, proxies
└── infrastructure/          # Backup, DevOps
```

## Generator Anatomy

### Basic Structure

Every generator follows this pattern:

```python
#!/usr/bin/env python3
"""
Generator for [Product Name] security events
Generates [format] formatted events with Star Trek themed data
"""

import json
import random
from datetime import datetime, timedelta, timezone

# Star Trek themed data
STAR_TREK_USERS = [
    "jean.picard@starfleet.corp",
    "william.riker@starfleet.corp",
    "data.android@starfleet.corp",
    "worf.security@starfleet.corp",
    "geordi.laforge@starfleet.corp",
    "beverly.crusher@starfleet.corp",
    "deanna.troi@starfleet.corp"
]

STAR_TREK_HOSTS = [
    "ENTERPRISE-BRIDGE-01",
    "ENTERPRISE-ENGINEERING-01",
    "ENTERPRISE-MEDBAY-01",
    "ENTERPRISE-SECURITY-01",
    "DS9-OPS-01",
    "VOYAGER-BRIDGE-01"
]

def product_name_log():
    """Generate a single product_name event"""
    
    # Generate timestamp (last 10 minutes)
    current_time = datetime.now(timezone.utc)
    time_offset = random.randint(0, 600)  # 0-10 minutes
    event_time = current_time - timedelta(seconds=time_offset)
    
    # Build event
    event = {
        "timestamp": event_time.isoformat(),
        "user": random.choice(STAR_TREK_USERS),
        "host": random.choice(STAR_TREK_HOSTS),
        "action": random.choice(["login", "logout", "file_access"]),
        "result": random.choice(["success", "failure"]),
        "source_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
        "severity": random.choice(["low", "medium", "high", "critical"])
    }
    
    return event

def main():
    """Generate and print a sample event"""
    event = product_name_log()
    print(json.dumps(event, indent=2))

if __name__ == "__main__":
    main()
```

### Required Components

1. **Import statements** - Standard libraries only (no external deps except in hec_sender)
2. **Star Trek data arrays** - Users, hosts, domains, etc.
3. **Main generator function** - Named `<product>_log()`
4. **Timestamp generation** - Recent timestamps (last 10 minutes)
5. **Main block** - For standalone testing

## Creating Your First Generator

### Step 1: Choose Product and Category

Determine:
- Product vendor and name (e.g., `acme_firewall`)
- Security category (e.g., `network_security`)
- Expected parser format (JSON, Syslog, CSV, KeyValue)

### Step 2: Create Generator File

```bash
# Navigate to appropriate category
cd event_generators/network_security

# Create new generator
touch acme_firewall.py
chmod +x acme_firewall.py
```

### Step 3: Implement Basic Generator

```python
#!/usr/bin/env python3
"""
Generator for ACME Firewall security events
Generates JSON formatted firewall logs with Star Trek themed data
"""

import json
import random
from datetime import datetime, timedelta, timezone

# Import shared Star Trek data (if available)
try:
    from ..shared.starfleet_characters import STAR_TREK_USERS, STAR_TREK_HOSTS
except:
    # Fallback to local definitions
    STAR_TREK_USERS = [
        "jean.picard@starfleet.corp",
        "william.riker@starfleet.corp",
        "data.android@starfleet.corp"
    ]
    
    STAR_TREK_HOSTS = [
        "ENTERPRISE-FW-01",
        "ENTERPRISE-FW-02"
    ]

# Firewall-specific data
FIREWALL_ACTIONS = ["allow", "deny", "drop", "reject"]
FIREWALL_PROTOCOLS = ["tcp", "udp", "icmp", "gre"]
FIREWALL_DIRECTIONS = ["inbound", "outbound", "internal"]
FIREWALL_ZONES = ["trust", "untrust", "dmz", "wan", "lan"]

def acme_firewall_log():
    """Generate a single ACME Firewall event"""
    
    # Generate recent timestamp
    current_time = datetime.now(timezone.utc)
    time_offset = random.randint(0, 600)
    event_time = current_time - timedelta(seconds=time_offset)
    
    # Build firewall-specific event
    event = {
        "timestamp": event_time.isoformat(),
        "device_name": random.choice(STAR_TREK_HOSTS),
        "action": random.choice(FIREWALL_ACTIONS),
        "protocol": random.choice(FIREWALL_PROTOCOLS),
        "direction": random.choice(FIREWALL_DIRECTIONS),
        "source_zone": random.choice(FIREWALL_ZONES),
        "dest_zone": random.choice(FIREWALL_ZONES),
        "source_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
        "dest_ip": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
        "source_port": random.randint(1024, 65535),
        "dest_port": random.choice([80, 443, 22, 3389, 8080]),
        "bytes_sent": random.randint(100, 1000000),
        "bytes_received": random.randint(100, 1000000),
        "packets": random.randint(1, 1000),
        "session_id": f"SID-{random.randint(1000000, 9999999)}",
        "rule_name": f"RULE-{random.choice(['ALLOW', 'DENY'])}-{random.randint(1,100)}",
        "threat_name": random.choice([None, "suspicious.activity", "port.scan", "sql.injection"]),
        "severity": random.choice(["low", "medium", "high", "critical"]),
        "user": random.choice(STAR_TREK_USERS) if random.random() > 0.5 else None
    }
    
    # Remove None values for cleaner output
    return {k: v for k, v in event.items() if v is not None}

def main():
    """Generate and print sample firewall event"""
    event = acme_firewall_log()
    print(json.dumps(event, indent=2))

if __name__ == "__main__":
    main()
```

### Step 4: Add to HEC Sender

Edit `event_generators/shared/hec_sender.py` to add your generator:

```python
# In the imports section, add:
from ..network_security import acme_firewall

# In the generator_map dictionary, add:
generator_map = {
    # ... existing entries ...
    "acme_firewall": acme_firewall.acme_firewall_log,
}
```

## Output Formats

### JSON Format (Default)

```python
def json_generator_log():
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "Event occurred",
        "severity": "medium"
    }
    return event  # Return dict for JSON
```

### Syslog Format

```python
def syslog_generator_log():
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    hostname = "ENTERPRISE-01"
    process = "firewall[1234]"
    message = "Connection allowed from 10.0.0.1"
    
    syslog = f"{timestamp} {hostname} {process}: {message}"
    return syslog  # Return string for syslog
```

### Key-Value Format

```python
def keyvalue_generator_log():
    event_parts = [
        f"timestamp={datetime.now(timezone.utc).isoformat()}",
        f"user=jean.picard@starfleet.corp",
        f"action=login",
        f"result=success",
        f"source_ip=10.0.0.50"
    ]
    return " ".join(event_parts)  # Return key=value string
```

### CSV Format

```python
def csv_generator_log():
    fields = [
        datetime.now(timezone.utc).isoformat(),
        "jean.picard@starfleet.corp",
        "10.0.0.50",
        "192.168.1.100",
        "allow",
        "tcp",
        "443"
    ]
    return ",".join(fields)  # Return CSV string
```

## Star Trek Theme Integration

### Standard Character List

```python
# Primary Bridge Crew
BRIDGE_CREW = [
    "jean.picard@starfleet.corp",
    "william.riker@starfleet.corp",
    "data.android@starfleet.corp",
    "worf.security@starfleet.corp",
    "geordi.laforge@starfleet.corp",
    "beverly.crusher@starfleet.corp",
    "deanna.troi@starfleet.corp"
]

# Security Personnel
SECURITY_TEAM = [
    "worf.security@starfleet.corp",
    "tasha.yar@starfleet.corp",
    "odo.security@ds9.starfleet.corp"
]

# Engineering Team
ENGINEERING = [
    "geordi.laforge@starfleet.corp",
    "miles.obrien@starfleet.corp",
    "barclay.reg@starfleet.corp",
    "scotty.montgomery@starfleet.corp"
]

# Adversaries (for threat events)
ADVERSARIES = [
    "q.continuum@hostile.space",
    "borg.collective@hostile.space",
    "romulan.spy@hostile.space",
    "cardassian.agent@hostile.space"
]
```

### Standard Host Names

```python
# Starship Systems
STARSHIP_HOSTS = [
    "ENTERPRISE-BRIDGE-01",
    "ENTERPRISE-ENGINEERING-01",
    "ENTERPRISE-MEDBAY-01",
    "ENTERPRISE-TRANSPORTER-01",
    "VOYAGER-ASTROMETRICS-01",
    "DEFIANT-TACTICAL-01",
    "DS9-OPS-01"
]

# Workstations
WORKSTATIONS = [
    "PICARD-READY-ROOM",
    "RIKER-QUARTERS",
    "DATA-LAB-01",
    "CRUSHER-SICKBAY-01"
]
```

### Domain Structure

```python
# Starfleet Domains
DOMAINS = [
    "starfleet.corp",           # Primary domain
    "enterprise.starfleet.corp", # Ship subdomain
    "academy.starfleet.corp",    # Training
    "command.starfleet.corp",    # Leadership
    "security.starfleet.corp"    # Security ops
]

# External Domains
EXTERNAL_DOMAINS = [
    "memory-alpha.org",          # Federation database
    "vulcan.embassy.gov",        # Allied systems
    "bajor.planetary.gov"
]
```

## Testing Your Generator

### Unit Test

Create `tests/test_acme_firewall.py`:

```python
import pytest
import json
from datetime import datetime
from event_generators.network_security.acme_firewall import acme_firewall_log

def test_acme_firewall_generates_event():
    """Test that generator creates valid event"""
    event = acme_firewall_log()
    
    # Check required fields exist
    assert "timestamp" in event
    assert "source_ip" in event
    assert "dest_ip" in event
    assert "action" in event
    
def test_acme_firewall_timestamp_recent():
    """Test that timestamp is recent (last 10 minutes)"""
    event = acme_firewall_log()
    
    event_time = datetime.fromisoformat(event["timestamp"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    time_diff = (now - event_time).total_seconds()
    
    assert 0 <= time_diff <= 600  # Within 10 minutes

def test_acme_firewall_star_trek_theme():
    """Test Star Trek theme integration"""
    events_with_users = []
    
    # Generate multiple events to find ones with users
    for _ in range(20):
        event = acme_firewall_log()
        if "user" in event:
            events_with_users.append(event)
    
    # Check at least some events have Star Trek users
    assert len(events_with_users) > 0
    
    # Check user format
    for event in events_with_users:
        assert "@starfleet.corp" in event["user"]

def test_acme_firewall_valid_json():
    """Test that output is valid JSON"""
    event = acme_firewall_log()
    
    # Should be able to serialize to JSON
    json_str = json.dumps(event)
    assert json_str
    
    # Should be able to parse back
    parsed = json.loads(json_str)
    assert parsed == event
```

### Integration Test

```python
def test_acme_firewall_with_hec_sender():
    """Test generator works with HEC sender"""
    from event_generators.shared.hec_sender import generator_map
    
    # Check generator is registered
    assert "acme_firewall" in generator_map
    
    # Check generator function works
    generator_func = generator_map["acme_firewall"]
    event = generator_func()
    assert event is not None
```

### Manual Testing

```bash
# Test standalone
python event_generators/network_security/acme_firewall.py

# Test with HEC sender
python event_generators/shared/hec_sender.py --product acme_firewall --count 5

# Test with comprehensive validator
python testing/comprehensive_generator_test.py --generator acme_firewall
```

## Best Practices

### 1. Follow Naming Conventions

```python
# File name: vendor_product.py
cisco_asa.py         # ✅ Good
CiscoASA.py         # ❌ Bad
cisco-asa.py        # ❌ Bad

# Function name: vendor_product_log()
def cisco_asa_log(): # ✅ Good
def generate():      # ❌ Bad
def CiscoASA():     # ❌ Bad
```

### 2. Include Comprehensive Fields

```python
# Include all fields the parser expects
event = {
    # Required fields
    "timestamp": event_time.isoformat(),
    "source_ip": source_ip,
    "dest_ip": dest_ip,
    
    # Optional but valuable fields
    "user": user if authenticated else None,
    "session_id": session_id,
    "bytes_transferred": bytes_count,
    
    # Threat intelligence fields
    "threat_detected": threat_name,
    "ioc_matched": ioc_value,
    "mitre_technique": technique_id
}
```

### 3. Handle Different Event Types

```python
def firewall_log():
    event_type = random.choice(["connection", "threat", "system"])
    
    base_event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type
    }
    
    if event_type == "connection":
        base_event.update({
            "source_ip": generate_ip(),
            "dest_ip": generate_ip(),
            "action": random.choice(["allow", "deny"])
        })
    elif event_type == "threat":
        base_event.update({
            "threat_name": random.choice(THREATS),
            "severity": "critical",
            "action": "blocked"
        })
    elif event_type == "system":
        base_event.update({
            "system_event": random.choice(["startup", "shutdown", "config_change"]),
            "admin_user": random.choice(ADMIN_USERS)
        })
    
    return base_event
```

### 4. Use Realistic Values

```python
# Good: Realistic port numbers
"dest_port": random.choice([80, 443, 22, 3389, 8080, 3306, 5432])

# Bad: Random ports
"dest_port": random.randint(1, 65535)

# Good: Realistic byte counts
"bytes": random.randint(100, 10000) if small_transfer else random.randint(10000, 10000000)

# Bad: Unrealistic values
"bytes": random.randint(1, 999999999999)
```

### 5. Document Output Format

```python
"""
Generator for ACME Firewall security events

Output Format: JSON
Sample Output:
{
  "timestamp": "2025-01-29T10:30:00Z",
  "source_ip": "10.0.0.50",
  "dest_ip": "192.168.1.100",
  "action": "allow",
  "protocol": "tcp",
  "port": 443
}

Parser Compatibility: acme_firewall_logs-latest
OCSF Compliance: Network Activity [4001]
"""
```

## Advanced Techniques

### Scenario Support

Enable generators to work with attack scenarios:

```python
def firewall_log(scenario_override=None):
    """
    Generate firewall event with scenario support
    
    Args:
        scenario_override (dict): Override values for scenarios
    """
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_ip": generate_ip(),
        "action": "allow"
    }
    
    # Apply scenario overrides
    if scenario_override:
        if "attacker_ip" in scenario_override:
            event["source_ip"] = scenario_override["attacker_ip"]
        if "attack_action" in scenario_override:
            event["action"] = scenario_override["attack_action"]
        if "target_user" in scenario_override:
            event["user"] = scenario_override["target_user"]
    
    return event
```

### Stateful Generation

Maintain state between events for realistic sequences:

```python
class FirewallGenerator:
    def __init__(self):
        self.sessions = {}
        
    def generate_event(self):
        if random.random() < 0.3 and self.sessions:
            # Continue existing session
            session_id = random.choice(list(self.sessions.keys()))
            session = self.sessions[session_id]
            
            event = {
                "session_id": session_id,
                "source_ip": session["source_ip"],
                "dest_ip": session["dest_ip"],
                "action": "continue"
            }
        else:
            # New session
            session_id = f"SID-{random.randint(1000000, 9999999)}"
            source_ip = generate_ip()
            dest_ip = generate_ip()
            
            self.sessions[session_id] = {
                "source_ip": source_ip,
                "dest_ip": dest_ip
            }
            
            event = {
                "session_id": session_id,
                "source_ip": source_ip,
                "dest_ip": dest_ip,
                "action": "start"
            }
        
        return event

# Global instance for stateful generation
_generator = FirewallGenerator()

def firewall_log():
    return _generator.generate_event()
```

### Performance Optimization

For bulk generation:

```python
def generate_bulk_events(count=1000):
    """Generate multiple events efficiently"""
    
    # Pre-calculate values that don't change
    base_time = datetime.now(timezone.utc)
    
    # Pre-compile random choices
    users = STAR_TREK_USERS * (count // len(STAR_TREK_USERS) + 1)
    random.shuffle(users)
    
    events = []
    for i in range(count):
        # Use pre-calculated values
        event = {
            "timestamp": (base_time - timedelta(seconds=i)).isoformat(),
            "user": users[i],
            "event_id": i,
            # ... other fields
        }
        events.append(event)
    
    return events
```

## 🎓 Generator Checklist

Before submitting your generator:

- [ ] File named correctly: `vendor_product.py`
- [ ] Function named correctly: `vendor_product_log()`
- [ ] Returns correct format (dict for JSON, string for others)
- [ ] Includes Star Trek themed data
- [ ] Generates recent timestamps (last 10 minutes)
- [ ] All required fields included
- [ ] Realistic field values used
- [ ] No external dependencies (except in hec_sender)
- [ ] Standalone executable with `if __name__ == "__main__"`
- [ ] Added to hec_sender.py generator_map
- [ ] Unit tests written
- [ ] Manual test successful
- [ ] Documentation comments included

## 🚀 Next Steps

Now that you can create generators:
1. [Create a Parser](../parsers/parser-tutorial.md) to process your events
2. [Test Field Compatibility](../parsers/field-mappings.md)
3. [Build Attack Scenarios](../user-guide/scenarios.md)
4. [Contribute Your Generator](../development/contributing.md)

Need help? Check existing generators for examples or open an issue!