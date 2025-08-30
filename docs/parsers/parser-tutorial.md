# Parser Development Guide

Learn how to create, modify, and test log parsers for the Jarvis Coding platform to achieve optimal OCSF compliance and field extraction.

## 📚 Table of Contents
1. [Understanding Parsers](#understanding-parsers)
2. [Parser Structure](#parser-structure)
3. [Creating a Parser](#creating-a-parser)
4. [Field Mapping](#field-mapping)
5. [OCSF Compliance](#ocsf-compliance)
6. [Testing Parsers](#testing-parsers)
7. [Marketplace vs Community](#marketplace-vs-community)
8. [Best Practices](#best-practices)

## Understanding Parsers

### What is a Parser?

A parser is a JSON configuration that defines how to extract and normalize fields from raw security events. Parsers:
- Extract fields from various log formats (JSON, Syslog, CSV, Key-Value)
- Map vendor-specific fields to OCSF standard fields
- Enable unified querying across different security products
- Support threat intelligence extraction

### Parser Performance Metrics

Top performing parsers achieve:
- **Field Extraction**: 240-294 fields
- **OCSF Compliance**: 100%
- **Processing Time**: <50ms per event
- **Success Rate**: >99%

## Parser Structure

### Basic Parser Schema

```json
{
  "name": "vendor_product_parser",
  "version": "1.0.0",
  "description": "Parser for Vendor Product logs",
  "author": "Your Name",
  "created": "2025-01-29",
  "updated": "2025-01-29",
  
  "log_format": "json|syslog|csv|keyvalue",
  
  "field_mappings": {
    "timestamp": {
      "source_field": "@timestamp",
      "type": "timestamp",
      "format": "ISO8601"
    },
    "source_ip": {
      "source_field": "src_ip",
      "type": "ip_address"
    },
    "user": {
      "source_field": "username",
      "type": "string",
      "transform": "lowercase"
    }
  },
  
  "ocsf_mapping": {
    "class_name": "Network Activity",
    "class_uid": 4001,
    "category_name": "Network Activity",
    "category_uid": 4
  },
  
  "parsing_rules": {
    "pre_processing": [],
    "field_extraction": [],
    "post_processing": []
  }
}
```

### Directory Structure

```
parsers/
├── community/                           # Community parsers
│   └── vendor_product-latest/
│       ├── vendor_product.json         # Parser configuration
│       └── metadata.yaml               # Parser metadata
└── sentinelone/                        # Marketplace parsers
    └── marketplace-vendorproduct-latest/
        ├── vendor_product.json
        └── metadata.yaml
```

## Creating a Parser

### Step 1: Analyze Log Format

First, understand your log format:

```python
# Generate sample logs
python event_generators/network_security/acme_firewall.py

# Sample output (JSON):
{
  "timestamp": "2025-01-29T10:30:00Z",
  "source_ip": "10.0.0.50",
  "dest_ip": "192.168.1.100",
  "action": "allow",
  "protocol": "tcp",
  "port": 443
}

# Sample output (Syslog):
Jan 29 10:30:00 ENTERPRISE-FW-01 firewall[1234]: action=allow src=10.0.0.50 dst=192.168.1.100

# Sample output (Key-Value):
timestamp=2025-01-29T10:30:00Z source_ip=10.0.0.50 dest_ip=192.168.1.100 action=allow

# Sample output (CSV):
2025-01-29T10:30:00Z,10.0.0.50,192.168.1.100,allow,tcp,443
```

### Step 2: Create Parser Directory

```bash
# Create parser directory
mkdir -p parsers/community/acme_firewall-latest

# Navigate to parser directory
cd parsers/community/acme_firewall-latest
```

### Step 3: Define Field Mappings

Create `acme_firewall.json`:

```json
{
  "name": "acme_firewall_parser",
  "version": "1.0.0",
  "description": "Parser for ACME Firewall security events",
  "author": "Security Team",
  "created": "2025-01-29",
  "updated": "2025-01-29",
  
  "log_format": "json",
  "supported_formats": ["json", "syslog"],
  
  "field_mappings": {
    "timestamp": {
      "source_field": "timestamp",
      "type": "timestamp",
      "format": "ISO8601",
      "required": true,
      "ocsf_field": "time"
    },
    
    "source_address": {
      "source_field": "source_ip",
      "type": "ip_address",
      "required": true,
      "ocsf_field": "src_endpoint.ip"
    },
    
    "destination_address": {
      "source_field": "dest_ip",
      "type": "ip_address",
      "required": true,
      "ocsf_field": "dst_endpoint.ip"
    },
    
    "source_port": {
      "source_field": "source_port",
      "type": "integer",
      "ocsf_field": "src_endpoint.port"
    },
    
    "destination_port": {
      "source_field": "dest_port",
      "type": "integer",
      "ocsf_field": "dst_endpoint.port"
    },
    
    "network_protocol": {
      "source_field": "protocol",
      "type": "string",
      "transform": "uppercase",
      "ocsf_field": "connection_info.protocol_name"
    },
    
    "action": {
      "source_field": "action",
      "type": "string",
      "value_mapping": {
        "allow": "allowed",
        "deny": "denied",
        "drop": "dropped",
        "reject": "rejected"
      },
      "ocsf_field": "activity_name"
    },
    
    "user_name": {
      "source_field": "user",
      "type": "string",
      "transform": "extract_username",
      "ocsf_field": "actor.user.name"
    },
    
    "user_email": {
      "source_field": "user",
      "type": "string",
      "ocsf_field": "actor.user.email_addr"
    },
    
    "device_hostname": {
      "source_field": "device_name",
      "type": "string",
      "ocsf_field": "device.hostname"
    },
    
    "bytes_in": {
      "source_field": "bytes_received",
      "type": "long",
      "ocsf_field": "traffic.bytes_in"
    },
    
    "bytes_out": {
      "source_field": "bytes_sent",
      "type": "long",
      "ocsf_field": "traffic.bytes_out"
    },
    
    "session_id": {
      "source_field": "session_id",
      "type": "string",
      "ocsf_field": "connection_info.session_uid"
    },
    
    "rule_name": {
      "source_field": "rule_name",
      "type": "string",
      "ocsf_field": "firewall_rule.name"
    },
    
    "threat_name": {
      "source_field": "threat_name",
      "type": "string",
      "ocsf_field": "malware.name"
    },
    
    "severity": {
      "source_field": "severity",
      "type": "string",
      "value_mapping": {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical"
      },
      "ocsf_field": "severity"
    }
  },
  
  "ocsf_mapping": {
    "class_name": "Network Activity",
    "class_uid": 4001,
    "category_name": "Network Activity",
    "category_uid": 4,
    "type_name": "Network Connection",
    "type_uid": 400101,
    "severity_id": {
      "Low": 1,
      "Medium": 2,
      "High": 3,
      "Critical": 4
    },
    "activity_id": {
      "allowed": 1,
      "denied": 2,
      "dropped": 3
    }
  },
  
  "parsing_rules": {
    "pre_processing": [
      {
        "type": "regex_extract",
        "condition": "log_format == 'syslog'",
        "pattern": "^(\\w+ \\d+ \\d+:\\d+:\\d+) (\\S+) (\\S+)\\[(\\d+)\\]: (.+)$",
        "fields": ["timestamp", "hostname", "process", "pid", "message"]
      }
    ],
    
    "field_extraction": [
      {
        "type": "json_parse",
        "condition": "log_format == 'json'",
        "source": "raw_message"
      },
      {
        "type": "kv_parse",
        "condition": "log_format == 'keyvalue'",
        "delimiter": " ",
        "separator": "="
      }
    ],
    
    "post_processing": [
      {
        "type": "enrich_user",
        "source_field": "user",
        "extract": {
          "username": "^([^@]+)@",
          "domain": "@(.+)$"
        }
      },
      {
        "type": "calculate_duration",
        "start_field": "session_start",
        "end_field": "session_end",
        "target_field": "duration_ms"
      },
      {
        "type": "geoip_lookup",
        "source_field": "source_ip",
        "target_fields": {
          "country": "src_location.country",
          "city": "src_location.city",
          "latitude": "src_location.lat",
          "longitude": "src_location.lon"
        }
      }
    ]
  },
  
  "threat_intelligence": {
    "ioc_extraction": {
      "ip_addresses": ["source_ip", "dest_ip"],
      "domains": ["hostname", "fqdn"],
      "file_hashes": ["file_hash", "sha256"],
      "urls": ["url", "referrer"]
    },
    
    "threat_enrichment": {
      "enabled": true,
      "sources": ["virustotal", "abuseipdb", "alienvault"]
    }
  },
  
  "performance": {
    "batch_size": 1000,
    "timeout_ms": 5000,
    "max_field_length": 10000,
    "truncate_fields": true
  }
}
```

### Step 4: Create Metadata

Create `metadata.yaml`:

```yaml
name: acme_firewall_parser
version: 1.0.0
vendor: ACME Corporation
product: ACME Firewall
category: network_security

description: |
  Parser for ACME Firewall logs supporting JSON and Syslog formats.
  Provides full OCSF compliance for Network Activity events.

supported_versions:
  - "5.x"
  - "6.x"
  - "7.x"

log_formats:
  - json
  - syslog
  - keyvalue

ocsf_compliance:
  version: "1.1.0"
  classes:
    - name: "Network Activity"
      uid: 4001
      coverage: 95

field_extraction:
  average_fields: 150
  required_fields:
    - timestamp
    - source_ip
    - dest_ip
    - action
  
  optional_fields:
    - user
    - session_id
    - bytes_sent
    - bytes_received
    - threat_name

performance:
  average_parse_time_ms: 25
  max_parse_time_ms: 100
  success_rate: 99.5

testing:
  sample_logs_available: true
  test_coverage: 85
  last_tested: "2025-01-29"

author:
  name: "Security Team"
  email: "security@example.com"
  organization: "ACME Corp"

changelog:
  - version: 1.0.0
    date: "2025-01-29"
    changes:
      - "Initial release"
      - "Full OCSF compliance"
      - "Support for JSON and Syslog formats"
```

## Field Mapping

### Standard Field Types

```json
{
  "field_types": {
    "string": "Text field",
    "integer": "Whole number",
    "long": "Large whole number",
    "float": "Decimal number",
    "boolean": "True/false",
    "timestamp": "Date/time value",
    "ip_address": "IPv4 or IPv6 address",
    "mac_address": "MAC address",
    "url": "URL/URI",
    "email": "Email address",
    "json": "Nested JSON object",
    "array": "Array of values"
  }
}
```

### Field Transformations

```json
{
  "transformations": {
    "lowercase": "Convert to lowercase",
    "uppercase": "Convert to uppercase",
    "trim": "Remove whitespace",
    "extract_username": "Extract username from email",
    "extract_domain": "Extract domain from email/URL",
    "parse_json": "Parse JSON string",
    "split": "Split string into array",
    "join": "Join array into string",
    "regex_extract": "Extract using regex",
    "hash": "Generate hash of value",
    "mask": "Mask sensitive data"
  }
}
```

### Conditional Mapping

```json
{
  "conditional_mapping": {
    "user_type": {
      "condition": "user != null",
      "mappings": [
        {
          "condition": "user.contains('@starfleet.corp')",
          "value": "internal"
        },
        {
          "condition": "user.contains('@')",
          "value": "external"
        },
        {
          "default": "system"
        }
      ]
    }
  }
}
```

## OCSF Compliance

### OCSF Classes

Common OCSF classes for security events:

```json
{
  "ocsf_classes": {
    "1001": "File System Activity",
    "2001": "Process Activity", 
    "3001": "Authentication",
    "3002": "Authorization",
    "4001": "Network Activity",
    "4003": "DNS Activity",
    "4004": "DHCP Activity",
    "4005": "RDP Activity",
    "4006": "SMB Activity",
    "4007": "SSH Activity",
    "4008": "FTP Activity",
    "4009": "Email Activity",
    "5001": "Discovery",
    "6001": "Application Activity",
    "6002": "API Activity",
    "6003": "Web Resources Activity",
    "6004": "Datastore Activity"
  }
}
```

### Required OCSF Fields

```json
{
  "required_ocsf_fields": {
    "time": "Event timestamp",
    "severity": "Event severity",
    "class_uid": "OCSF class identifier",
    "category_uid": "OCSF category identifier",
    "type_uid": "Event type identifier",
    "activity_id": "Activity identifier",
    "activity_name": "Activity name",
    "status": "Event status",
    "status_id": "Status identifier"
  }
}
```

### OCSF Compliance Levels

```yaml
compliance_levels:
  excellent: 
    score: "90-100%"
    fields: "200+"
    description: "Full OCSF compliance with extensive field extraction"
  
  good:
    score: "70-89%"
    fields: "100-199"
    description: "Strong OCSF compliance with good field coverage"
  
  fair:
    score: "50-69%"
    fields: "50-99"
    description: "Basic OCSF compliance with essential fields"
  
  poor:
    score: "<50%"
    fields: "<50"
    description: "Limited OCSF compliance, needs improvement"
```

## Testing Parsers

### Unit Testing

Create test file `tests/test_acme_firewall_parser.py`:

```python
import json
import pytest
from parsers.community.acme_firewall import parse_log

def test_parse_json_log():
    """Test parsing JSON formatted log"""
    raw_log = '''
    {
      "timestamp": "2025-01-29T10:30:00Z",
      "source_ip": "10.0.0.50",
      "dest_ip": "192.168.1.100",
      "action": "allow",
      "protocol": "tcp",
      "dest_port": 443
    }
    '''
    
    parsed = parse_log(raw_log, format="json")
    
    assert parsed["time"] == "2025-01-29T10:30:00Z"
    assert parsed["src_endpoint"]["ip"] == "10.0.0.50"
    assert parsed["dst_endpoint"]["ip"] == "192.168.1.100"
    assert parsed["activity_name"] == "allowed"
    assert parsed["connection_info"]["protocol_name"] == "TCP"

def test_parse_syslog():
    """Test parsing syslog formatted log"""
    raw_log = "Jan 29 10:30:00 FW-01 firewall[1234]: action=allow src=10.0.0.50 dst=192.168.1.100"
    
    parsed = parse_log(raw_log, format="syslog")
    
    assert parsed["src_endpoint"]["ip"] == "10.0.0.50"
    assert parsed["dst_endpoint"]["ip"] == "192.168.1.100"
    assert parsed["activity_name"] == "allowed"

def test_ocsf_compliance():
    """Test OCSF field compliance"""
    raw_log = generate_sample_log()
    parsed = parse_log(raw_log)
    
    # Check required OCSF fields
    assert "class_uid" in parsed
    assert parsed["class_uid"] == 4001  # Network Activity
    assert "category_uid" in parsed
    assert "time" in parsed
    assert "severity" in parsed

def test_field_extraction_count():
    """Test number of fields extracted"""
    raw_log = generate_complete_log()
    parsed = parse_log(raw_log)
    
    field_count = count_fields(parsed)
    assert field_count >= 100  # Should extract at least 100 fields
```

### Integration Testing

Test with actual generator output:

```python
def test_parser_with_generator():
    """Test parser with actual generator output"""
    from event_generators.network_security.acme_firewall import acme_firewall_log
    
    # Generate event
    event = acme_firewall_log()
    raw_log = json.dumps(event)
    
    # Parse event
    parsed = parse_log(raw_log)
    
    # Verify all generator fields are captured
    for key in event.keys():
        assert find_mapped_field(parsed, key) is not None
```

### Validation Testing

```bash
# Test parser with validation framework
python testing/validation/parser_validator.py \
  --parser acme_firewall \
  --generator acme_firewall \
  --count 100

# Check field compatibility
python testing/field_compatibility_checker.py \
  --generator acme_firewall \
  --parser acme_firewall
```

## Marketplace vs Community

### Community Parsers

- **Location**: `parsers/community/`
- **Naming**: `vendor_product-latest/`
- **Quality**: Variable, community-maintained
- **Support**: Community support
- **Updates**: Irregular

### Marketplace Parsers

- **Location**: `parsers/sentinelone/marketplace-*`
- **Naming**: `marketplace-vendorproduct-latest/`
- **Quality**: Production-grade, tested
- **Support**: Vendor supported
- **Updates**: Regular updates
- **Benefits**:
  - 15-40% better OCSF scores
  - Enhanced field extraction
  - Optimized performance
  - Professional support

### Migration Path

```bash
# Community parser
parsers/community/cisco_firewall-latest/

# Marketplace parser (enhanced)
parsers/sentinelone/marketplace-ciscofirewallthreatdefense-latest/

# Usage difference
# Community:
python hec_sender.py --product cisco_firewall

# Marketplace:
python hec_sender.py --marketplace-parser marketplace-ciscofirewallthreatdefense-latest
```

## Best Practices

### 1. Maximize Field Extraction

```json
{
  "comprehensive_extraction": {
    "always_extract": [
      "timestamp",
      "source_ip",
      "dest_ip", 
      "user",
      "action",
      "severity"
    ],
    
    "conditional_extract": {
      "threat_fields": "if threat_detected",
      "user_fields": "if authenticated",
      "network_fields": "if network_activity"
    },
    
    "enrichment_fields": {
      "geoip": "from ip_addresses",
      "user_details": "from user_lookup",
      "threat_intel": "from ioc_matching"
    }
  }
}
```

### 2. Handle Multiple Formats

```json
{
  "format_handlers": {
    "json": {
      "parser": "json_parse",
      "validation": "valid_json"
    },
    "syslog": {
      "parser": "syslog_parse",
      "patterns": ["RFC3164", "RFC5424"]
    },
    "csv": {
      "parser": "csv_parse",
      "headers": "auto_detect"
    },
    "keyvalue": {
      "parser": "kv_parse",
      "separators": ["=", ":"]
    }
  }
}
```

### 3. Optimize Performance

```json
{
  "performance_optimizations": {
    "field_caching": true,
    "compiled_regex": true,
    "lazy_evaluation": true,
    "batch_processing": {
      "enabled": true,
      "size": 1000
    },
    "field_limits": {
      "max_length": 10000,
      "truncate": true
    }
  }
}
```

### 4. Error Handling

```json
{
  "error_handling": {
    "malformed_logs": {
      "action": "tag_and_continue",
      "tag": "parse_error"
    },
    "missing_fields": {
      "action": "use_defaults",
      "defaults": {
        "severity": "unknown",
        "action": "unknown"
      }
    },
    "type_errors": {
      "action": "type_coercion",
      "fallback": "string"
    }
  }
}
```

### 5. Testing Coverage

```yaml
test_scenarios:
  - name: "Basic JSON parsing"
    input_format: "json"
    expected_fields: 50
    
  - name: "Syslog with KV pairs"
    input_format: "syslog"
    expected_fields: 40
    
  - name: "Malformed input"
    input_format: "invalid"
    expected_behavior: "graceful_failure"
    
  - name: "High volume"
    event_count: 10000
    max_time_ms: 5000
    
  - name: "Field extraction completeness"
    validation: "all_generator_fields_mapped"
```

## Parser Validation Checklist

Before deploying your parser:

- [ ] Parser configuration is valid JSON
- [ ] All required OCSF fields mapped
- [ ] Field extraction rate >80%
- [ ] Supports all generator output formats
- [ ] Handles malformed logs gracefully
- [ ] Performance <50ms per event
- [ ] Unit tests pass
- [ ] Integration tests with generator pass
- [ ] Field compatibility validated
- [ ] Documentation complete
- [ ] Metadata.yaml accurate
- [ ] Sample logs included

## 🎯 Next Steps

After creating your parser:

1. [Test Field Compatibility](field-mappings.md) with generators
2. [Validate OCSF Compliance](ocsf-compliance.md)
3. [Submit to Marketplace](../development/contributing.md#marketplace)
4. [Monitor Performance](../deployment/monitoring.md)

## 📚 Resources

- [OCSF Schema Documentation](https://schema.ocsf.io/)
- [Parser Examples](https://github.com/natesmalley/jarvis_coding/tree/main/parsers)
- [Field Mapping Guide](field-mappings.md)
- [Performance Tuning](../deployment/performance.md)

Need help? Check existing parsers for examples or open an issue!