# Parsers API Reference

## Overview

The Parsers API provides endpoints for managing log parsers, testing parser configurations, and checking compatibility with generators. Support for both community and marketplace parsers.

## Endpoints

### List All Parsers

```http
GET /api/v1/parsers
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | Filter by parser type (community, marketplace) |
| vendor | string | Filter by vendor name |
| search | string | Search in parser names and descriptions |
| ocsf_compliant | boolean | Filter by OCSF compliance (true/false) |
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |

#### Response

```json
{
  "success": true,
  "data": {
    "parsers": [
      {
        "id": "fortinet_fortigate",
        "name": "Fortinet FortiGate",
        "type": "community",
        "vendor": "Fortinet",
        "description": "FortiGate firewall log parser",
        "input_format": "keyvalue",
        "ocsf_compliance": 100,
        "fields_extracted": 242,
        "version": "1.0.0",
        "last_updated": "2025-01-15T00:00:00Z"
      },
      {
        "id": "marketplace-fortinetfortigate-latest",
        "name": "Fortinet FortiGate (Marketplace)",
        "type": "marketplace",
        "vendor": "Fortinet",
        "description": "Official FortiGate parser with enhanced OCSF support",
        "input_format": "keyvalue",
        "ocsf_compliance": 100,
        "fields_extracted": 260,
        "version": "2.1.0",
        "last_updated": "2025-01-28T00:00:00Z"
      }
    ],
    "total": 190
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 10
  }
}
```

### Get Parser Details

```http
GET /api/v1/parsers/{parser_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| parser_id | string | Parser identifier (e.g., "fortinet_fortigate") |

#### Response

```json
{
  "success": true,
  "data": {
    "id": "crowdstrike_falcon",
    "name": "CrowdStrike Falcon",
    "type": "community",
    "vendor": "CrowdStrike",
    "description": "CrowdStrike Falcon EDR log parser",
    "input_format": "json",
    "ocsf_compliance": 80,
    "fields_extracted": 135,
    "version": "1.2.0",
    "last_updated": "2025-01-20T00:00:00Z",
    "configuration": {
      "event_types": ["ProcessRollup2", "NetworkConnectIP4", "DnsRequest"],
      "timestamp_format": "ISO8601",
      "field_mappings": {
        "user": "user_name",
        "ComputerName": "device.hostname",
        "SourceIP": "src_endpoint.ip"
      }
    },
    "compatible_generators": ["crowdstrike_falcon"],
    "sample_input": {
      "timestamp": "2025-01-29T10:45:32Z",
      "event_simpleName": "ProcessRollup2",
      "user": "jean.picard@starfleet.corp"
    },
    "sample_output": {
      "activity_id": 1,
      "activity_name": "Process Activity",
      "user_name": "jean.picard@starfleet.corp",
      "device": {
        "hostname": "ENTERPRISE-BRIDGE-01"
      }
    }
  }
}
```

### Test Parser

```http
POST /api/v1/parsers/{parser_id}/test
```

#### Request Body

```json
{
  "input_event": {
    "timestamp": "2025-01-29T10:45:32Z",
    "user": "jean.picard@starfleet.corp",
    "event_simpleName": "ProcessRollup2",
    "ComputerName": "ENTERPRISE-BRIDGE-01",
    "CommandLine": "/usr/bin/sudo systemctl restart warp-core"
  },
  "input_format": "json"
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "parser_id": "crowdstrike_falcon",
    "parsing_success": true,
    "parsed_event": {
      "activity_id": 1,
      "activity_name": "Process Activity",
      "user_name": "jean.picard@starfleet.corp",
      "device": {
        "hostname": "ENTERPRISE-BRIDGE-01"
      },
      "process": {
        "cmd_line": "/usr/bin/sudo systemctl restart warp-core"
      },
      "metadata": {
        "product": {
          "vendor_name": "CrowdStrike",
          "name": "Falcon"
        },
        "version": "1.1.0"
      }
    },
    "fields_extracted": 12,
    "ocsf_fields_mapped": 10,
    "parsing_time_ms": 5,
    "warnings": []
  }
}
```

### Get Parser Fields

```http
GET /api/v1/parsers/{parser_id}/fields
```

#### Response

```json
{
  "success": true,
  "data": {
    "parser_id": "fortinet_fortigate",
    "total_fields": 242,
    "required_fields": [
      "timestamp",
      "srcip",
      "dstip",
      "action"
    ],
    "ocsf_fields": [
      {
        "field_name": "activity_id",
        "ocsf_type": "integer",
        "description": "Activity identifier",
        "required": true
      },
      {
        "field_name": "activity_name",
        "ocsf_type": "string",
        "description": "Activity name",
        "required": true
      },
      {
        "field_name": "src_endpoint.ip",
        "ocsf_type": "ip_address",
        "description": "Source IP address",
        "required": false
      }
    ],
    "custom_fields": [
      {
        "field_name": "fortinet_severity",
        "type": "string",
        "description": "FortiGate specific severity level"
      }
    ],
    "field_mappings": {
      "srcip": "src_endpoint.ip",
      "dstip": "dst_endpoint.ip",
      "user": "user.name",
      "action": "disposition"
    }
  }
}
```

### Check Parser Compatibility

```http
GET /api/v1/parsers/{parser_id}/compatibility
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| generator_id | string | Generator to check compatibility with |

#### Response

```json
{
  "success": true,
  "data": {
    "parser_id": "fortinet_fortigate",
    "generator_id": "fortinet_fortigate",
    "compatible": true,
    "compatibility_score": 95,
    "format_match": true,
    "field_coverage": {
      "total_generator_fields": 45,
      "matched_fields": 43,
      "missing_fields": ["session_id", "policy_id"],
      "coverage_percentage": 95.6
    },
    "recommendations": [
      "Consider adding session_id field to generator output",
      "Policy_id field recommended for complete logging"
    ],
    "test_result": {
      "sample_tested": true,
      "parse_success": true,
      "ocsf_compliance": 100
    }
  }
}
```

### Validate Parser Configuration

```http
POST /api/v1/parsers/{parser_id}/validate
```

#### Request Body

```json
{
  "check_schema": true,
  "check_ocsf_compliance": true,
  "test_samples": true,
  "sample_count": 10
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "parser_id": "aws_cloudtrail",
    "validation_passed": true,
    "checks": {
      "schema_valid": true,
      "ocsf_compliant": true,
      "sample_parsing": {
        "tested": 10,
        "passed": 10,
        "failed": 0
      }
    },
    "ocsf_compliance_score": 100,
    "performance_metrics": {
      "avg_parse_time_ms": 2.5,
      "max_parse_time_ms": 5,
      "events_per_second": 400
    },
    "issues": [],
    "warnings": []
  }
}
```

### List Marketplace Parsers

```http
GET /api/v1/parsers/marketplace
```

#### Response

```json
{
  "success": true,
  "data": {
    "parsers": [
      {
        "id": "marketplace-awscloudtrail-latest",
        "name": "AWS CloudTrail (Official)",
        "vendor": "AWS",
        "description": "Official AWS CloudTrail parser with enhanced OCSF support",
        "version": "3.2.0",
        "ocsf_compliance": 100,
        "fields_extracted": 180,
        "advantages": [
          "15% better field extraction than community parser",
          "Full OCSF 1.1.0 compliance",
          "Automatic threat intelligence extraction",
          "Official AWS support"
        ],
        "pricing": "included",
        "last_updated": "2025-01-28T00:00:00Z"
      },
      {
        "id": "marketplace-ciscofirewallthreatdefense-latest",
        "name": "Cisco FTD (Official)",
        "vendor": "Cisco",
        "description": "Official Cisco Firewall Threat Defense parser",
        "version": "2.5.0",
        "ocsf_compliance": 85,
        "fields_extracted": 150,
        "advantages": [
          "45% improvement over community parser",
          "Enhanced threat detection fields",
          "Cisco TAC supported"
        ],
        "pricing": "included",
        "last_updated": "2025-01-25T00:00:00Z"
      }
    ],
    "total": 90
  }
}
```

### Compare Parsers

```http
POST /api/v1/parsers/compare
```

#### Request Body

```json
{
  "parser_ids": [
    "fortinet_fortigate",
    "marketplace-fortinetfortigate-latest"
  ],
  "test_event": {
    "date": "2025-01-29",
    "time": "10:45:32",
    "srcip": "10.0.0.50",
    "user": "jean.picard@starfleet.corp",
    "action": "accept"
  }
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "comparison": [
      {
        "parser_id": "fortinet_fortigate",
        "type": "community",
        "parsing_success": true,
        "fields_extracted": 25,
        "ocsf_fields": 23,
        "parse_time_ms": 3,
        "ocsf_compliance": 100
      },
      {
        "parser_id": "marketplace-fortinetfortigate-latest",
        "type": "marketplace",
        "parsing_success": true,
        "fields_extracted": 32,
        "ocsf_fields": 30,
        "parse_time_ms": 2,
        "ocsf_compliance": 100
      }
    ],
    "recommendation": "marketplace-fortinetfortigate-latest",
    "reasons": [
      "28% more fields extracted",
      "33% faster parsing",
      "Better threat intelligence extraction",
      "Official vendor support"
    ]
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| PARSER_NOT_FOUND | The specified parser ID does not exist |
| INVALID_INPUT_FORMAT | Input format not supported by parser |
| PARSING_FAILED | Failed to parse the provided event |
| VALIDATION_FAILED | Parser configuration validation failed |
| COMPATIBILITY_CHECK_FAILED | Could not determine compatibility |

## Examples

### Python Example

```python
import requests

API_BASE = "https://api.jarvis-coding.io/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# List all marketplace parsers
response = requests.get(
    f"{API_BASE}/parsers",
    params={"type": "marketplace"},
    headers=headers
)
marketplace_parsers = response.json()["data"]["parsers"]

# Test parser with sample event
event = {
    "timestamp": "2025-01-29T10:45:32Z",
    "user": "jean.picard@starfleet.corp",
    "action": "login_success"
}

response = requests.post(
    f"{API_BASE}/parsers/okta_authentication/test",
    json={"input_event": event, "input_format": "json"},
    headers=headers
)

parsed = response.json()["data"]["parsed_event"]
print(f"Extracted {len(parsed)} fields with OCSF compliance")
```

### cURL Example

```bash
# Get parser fields
curl -X GET "https://api.jarvis-coding.io/api/v1/parsers/sentinelone_endpoint/fields" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check compatibility
curl -X GET "https://api.jarvis-coding.io/api/v1/parsers/crowdstrike_falcon/compatibility?generator_id=crowdstrike_falcon" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Compare parsers
curl -X POST "https://api.jarvis-coding.io/api/v1/parsers/compare" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "parser_ids": ["aws_cloudtrail", "marketplace-awscloudtrail-latest"],
    "test_event": {"eventName": "AssumeRole", "userIdentity": {"type": "IAMUser"}}
  }'
```

### JavaScript Example

```javascript
const API_BASE = 'https://api.jarvis-coding.io/api/v1';
const headers = { 'Authorization': 'Bearer YOUR_TOKEN' };

// Search for OCSF compliant parsers
fetch(`${API_BASE}/parsers?ocsf_compliant=true`, { headers })
  .then(res => res.json())
  .then(data => {
    const compliantParsers = data.data.parsers;
    console.log(`Found ${compliantParsers.length} OCSF compliant parsers`);
  });

// Validate parser configuration
fetch(`${API_BASE}/parsers/fortinet_fortigate/validate`, {
  method: 'POST',
  headers: { ...headers, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    check_schema: true,
    check_ocsf_compliance: true,
    test_samples: true
  })
})
.then(res => res.json())
.then(data => {
  if (data.data.validation_passed) {
    console.log('Parser validation passed!');
    console.log(`OCSF Compliance: ${data.data.ocsf_compliance_score}%`);
  }
});
```

## Rate Limits

- Parser testing: 100 requests/minute
- Compatibility checks: 200 requests/minute
- Field/schema queries: 1000 requests/minute

## See Also

- [Generators API](generators-api.md) - Generate events for parser testing
- [Validation API](validation-api.md) - Comprehensive field validation
- [Scenarios API](scenarios-api.md) - Test parsers with attack scenarios