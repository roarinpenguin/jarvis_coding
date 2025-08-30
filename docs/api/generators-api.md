# Generators API Reference

## Overview

The Generators API provides endpoints for listing, executing, and validating security event generators. With 100+ generators across 7 categories, you can generate realistic security events for testing and validation.

## Endpoints

### List All Generators

```http
GET /api/v1/generators
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by category (cloud_infrastructure, network_security, etc.) |
| vendor | string | Filter by vendor (aws, cisco, microsoft, etc.) |
| search | string | Search in generator names and descriptions |
| page | integer | Page number (default: 1) |
| per_page | integer | Items per page (default: 20, max: 100) |

#### Response

```json
{
  "success": true,
  "data": {
    "generators": [
      {
        "id": "crowdstrike_falcon",
        "name": "CrowdStrike Falcon",
        "category": "endpoint_security",
        "vendor": "CrowdStrike",
        "description": "CrowdStrike Falcon endpoint detection and response events",
        "supported_formats": ["json"],
        "star_trek_enabled": true,
        "fields_count": 135,
        "ocsf_compliance": 80
      },
      // ... more generators
    ],
    "total": 106
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_pages": 6
  }
}
```

### Get Generator Details

```http
GET /api/v1/generators/{generator_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| generator_id | string | Generator identifier (e.g., "crowdstrike_falcon") |

#### Response

```json
{
  "success": true,
  "data": {
    "id": "crowdstrike_falcon",
    "name": "CrowdStrike Falcon",
    "category": "endpoint_security",
    "vendor": "CrowdStrike",
    "description": "CrowdStrike Falcon endpoint detection and response events",
    "supported_formats": ["json"],
    "default_format": "json",
    "star_trek_enabled": true,
    "configurable_options": {
      "severity": ["low", "medium", "high", "critical"],
      "event_type": ["detection", "prevention", "audit"]
    },
    "sample_output": {
      "timestamp": "2025-01-29T10:45:32Z",
      "user": "jean.picard@starfleet.corp",
      "event_type": "ProcessRollup2",
      "severity": "high"
    },
    "compatible_parsers": [
      "crowdstrike_falcon",
      "marketplace-crowdstrike-latest"
    ],
    "fields_count": 135,
    "ocsf_compliance": 80
  }
}
```

### Execute Generator

```http
POST /api/v1/generators/{generator_id}/execute
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| generator_id | string | Generator identifier |

#### Request Body

```json
{
  "count": 10,
  "format": "json",
  "star_trek_theme": true,
  "options": {
    "severity": "high",
    "include_timestamps": true,
    "time_range": "last_10_minutes"
  }
}
```

#### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| count | integer | 1 | Number of events to generate (1-1000) |
| format | string | "json" | Output format (json, syslog, csv, keyvalue) |
| star_trek_theme | boolean | true | Use Star Trek themed data |
| options | object | {} | Generator-specific options |

#### Response

```json
{
  "success": true,
  "data": {
    "generator_id": "crowdstrike_falcon",
    "events": [
      {
        "timestamp": "2025-01-29T10:45:32.123Z",
        "user": "jean.picard@starfleet.corp",
        "ComputerName": "ENTERPRISE-BRIDGE-01",
        "event_simpleName": "ProcessRollup2",
        "DetectDescription": "Suspicious process detected",
        "SeverityName": "High",
        "SourceIP": "10.0.0.50",
        "CommandLine": "/usr/bin/sudo systemctl restart warp-core"
      },
      // ... more events
    ],
    "count": 10,
    "format": "json",
    "execution_time_ms": 145,
    "metadata": {
      "star_trek_theme": true,
      "timestamp_range": {
        "start": "2025-01-29T10:35:00Z",
        "end": "2025-01-29T10:45:32Z"
      }
    }
  }
}
```

### Validate Generator Output

```http
POST /api/v1/generators/{generator_id}/validate
```

#### Request Body

```json
{
  "format": "json",
  "sample_size": 5,
  "check_schema": true,
  "check_timestamps": true
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "valid": true,
    "generator_id": "crowdstrike_falcon",
    "validation_results": {
      "format_valid": true,
      "schema_valid": true,
      "timestamps_valid": true,
      "required_fields_present": true,
      "star_trek_theme_present": true
    },
    "sample_events": 5,
    "issues": [],
    "warnings": []
  }
}
```

### Get Generator Schema

```http
GET /api/v1/generators/{generator_id}/schema
```

#### Response

```json
{
  "success": true,
  "data": {
    "generator_id": "crowdstrike_falcon",
    "schema": {
      "type": "object",
      "properties": {
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "Event timestamp in ISO 8601 format"
        },
        "user": {
          "type": "string",
          "pattern": "^[a-z]+\\.[a-z]+@starfleet\\.corp$",
          "description": "User in Star Trek format"
        },
        "ComputerName": {
          "type": "string",
          "pattern": "^ENTERPRISE-[A-Z]+-\\d{2}$",
          "description": "Starfleet computer name"
        },
        "event_simpleName": {
          "type": "string",
          "enum": ["ProcessRollup2", "NetworkConnectIP4", "DnsRequest"],
          "description": "CrowdStrike event type"
        },
        "SeverityName": {
          "type": "string",
          "enum": ["Low", "Medium", "High", "Critical"]
        }
      },
      "required": ["timestamp", "event_simpleName"]
    }
  }
}
```

### List Generator Categories

```http
GET /api/v1/generators/categories
```

#### Response

```json
{
  "success": true,
  "data": {
    "categories": [
      {
        "id": "cloud_infrastructure",
        "name": "Cloud Infrastructure",
        "description": "AWS, Google Cloud, Azure services",
        "icon": "☁️",
        "generator_count": 9,
        "top_generators": ["aws_cloudtrail", "aws_guardduty", "google_workspace"]
      },
      {
        "id": "network_security",
        "name": "Network Security",
        "description": "Firewalls, NDR, network devices",
        "icon": "🔒",
        "generator_count": 34,
        "top_generators": ["cisco_firewall_threat_defense", "fortinet_fortigate", "paloalto_firewall"]
      },
      {
        "id": "endpoint_security",
        "name": "Endpoint Security",
        "description": "EDR, endpoint protection platforms",
        "icon": "🖥️",
        "generator_count": 6,
        "top_generators": ["crowdstrike_falcon", "sentinelone_endpoint", "microsoft_windows_eventlog"]
      },
      {
        "id": "identity_access",
        "name": "Identity & Access",
        "description": "IAM, SSO, PAM solutions",
        "icon": "👤",
        "generator_count": 20,
        "top_generators": ["okta_authentication", "microsoft_azuread", "cyberark_pas"]
      },
      {
        "id": "email_security",
        "name": "Email Security",
        "description": "Email protection platforms",
        "icon": "📧",
        "generator_count": 4,
        "top_generators": ["mimecast", "proofpoint", "abnormal_security"]
      },
      {
        "id": "web_security",
        "name": "Web Security",
        "description": "WAF, web proxies, CDN security",
        "icon": "🌐",
        "generator_count": 13,
        "top_generators": ["cloudflare_waf", "zscaler", "imperva_waf"]
      },
      {
        "id": "infrastructure",
        "name": "Infrastructure",
        "description": "IT management, backup, DevOps",
        "icon": "🔧",
        "generator_count": 20,
        "top_generators": ["veeam_backup", "github_audit", "buildkite"]
      }
    ]
  }
}
```

### Batch Execute Generators

```http
POST /api/v1/generators/batch/execute
```

#### Request Body

```json
{
  "executions": [
    {
      "generator_id": "crowdstrike_falcon",
      "count": 10,
      "format": "json"
    },
    {
      "generator_id": "aws_cloudtrail",
      "count": 5,
      "format": "json"
    },
    {
      "generator_id": "okta_authentication",
      "count": 15,
      "format": "json"
    }
  ],
  "parallel": true
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "batch_id": "batch_abc123",
    "executions": [
      {
        "generator_id": "crowdstrike_falcon",
        "success": true,
        "events_count": 10,
        "execution_time_ms": 120
      },
      {
        "generator_id": "aws_cloudtrail",
        "success": true,
        "events_count": 5,
        "execution_time_ms": 80
      },
      {
        "generator_id": "okta_authentication",
        "success": true,
        "events_count": 15,
        "execution_time_ms": 150
      }
    ],
    "total_events": 30,
    "total_execution_time_ms": 165,
    "parallel_execution": true
  }
}
```

## Error Codes

| Code | Description |
|------|-------------|
| GENERATOR_NOT_FOUND | The specified generator ID does not exist |
| INVALID_FORMAT | The requested format is not supported by this generator |
| COUNT_EXCEEDED | Event count exceeds maximum (1000) |
| EXECUTION_FAILED | Generator execution failed |
| VALIDATION_FAILED | Generator output validation failed |

## Examples

### Python Example

```python
import requests

API_BASE = "https://api.jarvis-coding.io/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# List all endpoint security generators
response = requests.get(
    f"{API_BASE}/generators",
    params={"category": "endpoint_security"},
    headers=headers
)
generators = response.json()["data"]["generators"]

# Execute CrowdStrike generator
response = requests.post(
    f"{API_BASE}/generators/crowdstrike_falcon/execute",
    json={"count": 25, "format": "json"},
    headers=headers
)
events = response.json()["data"]["events"]
print(f"Generated {len(events)} CrowdStrike events")
```

### cURL Example

```bash
# Get generator details
curl -X GET "https://api.jarvis-coding.io/api/v1/generators/fortinet_fortigate" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Execute generator with options
curl -X POST "https://api.jarvis-coding.io/api/v1/generators/aws_cloudtrail/execute" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "count": 50,
    "format": "json",
    "options": {
      "event_type": "security",
      "include_errors": true
    }
  }'
```

### JavaScript Example

```javascript
const API_BASE = 'https://api.jarvis-coding.io/api/v1';
const headers = { 'Authorization': 'Bearer YOUR_TOKEN' };

// List generators with search
fetch(`${API_BASE}/generators?search=cisco`, { headers })
  .then(res => res.json())
  .then(data => {
    console.log(`Found ${data.data.generators.length} Cisco generators`);
  });

// Execute multiple generators in batch
fetch(`${API_BASE}/generators/batch/execute`, {
  method: 'POST',
  headers: { ...headers, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    executions: [
      { generator_id: 'crowdstrike_falcon', count: 10 },
      { generator_id: 'sentinelone_endpoint', count: 10 }
    ],
    parallel: true
  })
})
.then(res => res.json())
.then(data => {
  console.log(`Generated ${data.data.total_events} events in ${data.data.total_execution_time_ms}ms`);
});
```

## Rate Limits

- Single generator execution: 100 requests/minute
- Batch execution: 20 requests/minute
- Schema/details queries: 1000 requests/minute

## See Also

- [Parsers API](parsers-api.md) - Test generator output with parsers
- [Validation API](validation-api.md) - Validate generator-parser compatibility
- [Scenarios API](scenarios-api.md) - Run complex attack scenarios