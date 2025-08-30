# Validation API Reference (Phase 3)

## Overview

The Validation API provides comprehensive field validation between generators and parsers, ensuring data compatibility and OCSF compliance. This API is critical for maintaining data quality and parser effectiveness.

## Endpoints

### Check Generator-Parser Compatibility

```http
POST /api/v1/validation/check
```

#### Request Body

```json
{
  "generator_id": "crowdstrike_falcon",
  "parser_id": "marketplace-crowdstrike-latest",
  "sample_size": 10,
  "deep_validation": true,
  "check_ocsf": true
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "generator_id": "crowdstrike_falcon",
    "parser_id": "marketplace-crowdstrike-latest",
    "compatibility_score": 92.5,
    "format_compatible": true,
    "field_analysis": {
      "total_generator_fields": 45,
      "parsed_fields": 42,
      "missing_fields": ["agent_version", "policy_id", "scan_id"],
      "extra_parser_fields": ["enrichment.threat_intel", "enrichment.mitre_tactics"],
      "field_coverage": 93.3
    },
    "ocsf_compliance": {
      "score": 85,
      "required_fields_present": 18,
      "required_fields_total": 20,
      "missing_required": ["activity_id", "status_id"],
      "recommendations": [
        "Add activity_id mapping for full OCSF compliance",
        "Map status field to status_id enumeration"
      ]
    },
    "sample_validation": {
      "events_tested": 10,
      "parse_success": 10,
      "parse_failures": 0,
      "avg_fields_extracted": 135,
      "avg_parse_time_ms": 3.2
    },
    "issues": [],
    "warnings": [
      "Generator timestamp format differs from parser expectation"
    ],
    "grade": "A-"
  }
}
```

### Get Validation Report

```http
GET /api/v1/validation/report/{generator_id}/{parser_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| generator_id | string | Generator identifier |
| parser_id | string | Parser identifier |

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| format | string | Report format (json, html, pdf) |
| include_samples | boolean | Include sample events in report |

#### Response

```json
{
  "success": true,
  "data": {
    "report_id": "rpt_abc123",
    "generated_at": "2025-01-29T10:45:00Z",
    "generator": {
      "id": "fortinet_fortigate",
      "name": "Fortinet FortiGate",
      "version": "1.2.0",
      "format": "keyvalue"
    },
    "parser": {
      "id": "marketplace-fortinetfortigate-latest",
      "name": "Fortinet FortiGate (Marketplace)",
      "version": "2.1.0",
      "ocsf_version": "1.1.0"
    },
    "validation_summary": {
      "overall_score": 98.5,
      "grade": "A+",
      "status": "EXCELLENT",
      "recommendation": "Fully compatible - production ready"
    },
    "detailed_analysis": {
      "format_compatibility": {
        "generator_format": "keyvalue",
        "parser_expects": "keyvalue",
        "compatible": true,
        "conversion_needed": false
      },
      "field_mapping": {
        "perfect_matches": 40,
        "partial_matches": 3,
        "unmapped_fields": 2,
        "mapping_quality": 95.6
      },
      "data_quality": {
        "timestamp_format": "compatible",
        "ip_address_format": "valid",
        "user_format": "star_trek_compliant",
        "special_characters": "properly_escaped"
      },
      "performance": {
        "avg_parse_time_ms": 1.8,
        "max_parse_time_ms": 3.5,
        "throughput_eps": 555
      }
    },
    "field_details": [
      {
        "generator_field": "srcip",
        "parser_field": "src_endpoint.ip",
        "ocsf_field": "src_endpoint.ip",
        "mapping_status": "perfect",
        "data_type": "ip_address",
        "sample_value": "10.0.0.50"
      },
      {
        "generator_field": "user",
        "parser_field": "user.name",
        "ocsf_field": "actor.user.name",
        "mapping_status": "perfect",
        "data_type": "string",
        "sample_value": "jean.picard@starfleet.corp"
      }
    ],
    "test_results": {
      "sample_events": [
        {
          "input": "date=2025-01-29 time=10:45:32 srcip=10.0.0.50 user=jean.picard@starfleet.corp action=accept",
          "parsed_fields": 25,
          "ocsf_fields": 23,
          "parse_time_ms": 1.5,
          "success": true
        }
      ]
    },
    "recommendations": [
      "All critical fields are properly mapped",
      "Consider adding 'session_id' field for enhanced correlation",
      "Parser fully supports Star Trek themed data"
    ]
  }
}
```

### Auto-Fix Field Mismatches

```http
POST /api/v1/validation/fix/{generator_id}
```

#### Path Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| generator_id | string | Generator to fix |

#### Request Body

```json
{
  "target_parser": "marketplace-crowdstrike-latest",
  "fix_strategy": "add_missing_fields",
  "backup": true,
  "test_after_fix": true,
  "fixes_to_apply": [
    "add_missing_ocsf_fields",
    "fix_timestamp_format",
    "normalize_field_names",
    "add_star_trek_fields"
  ]
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "generator_id": "crowdstrike_falcon",
    "backup_created": "generators/backups/crowdstrike_falcon_20250129_104532.py",
    "fixes_applied": [
      {
        "type": "add_field",
        "field": "activity_id",
        "description": "Added OCSF activity_id field",
        "value_mapping": "ProcessRollup2 -> 1 (Process Activity)"
      },
      {
        "type": "add_field",
        "field": "status_id",
        "description": "Added OCSF status_id field",
        "value_mapping": "success -> 1, failure -> 2"
      },
      {
        "type": "format_change",
        "field": "timestamp",
        "description": "Normalized timestamp to ISO 8601",
        "old_format": "Unix epoch",
        "new_format": "ISO 8601"
      },
      {
        "type": "add_field",
        "field": "metadata.product.name",
        "description": "Added product metadata for OCSF",
        "value": "Falcon"
      }
    ],
    "validation_after_fix": {
      "compatibility_score": 98.5,
      "ocsf_compliance": 100,
      "field_coverage": 100,
      "parse_success": true,
      "grade": "A+"
    },
    "code_changes": {
      "lines_added": 15,
      "lines_modified": 3,
      "functions_updated": ["crowdstrike_log"]
    },
    "test_results": {
      "before_fix": {
        "compatibility": 85,
        "fields_extracted": 135
      },
      "after_fix": {
        "compatibility": 98.5,
        "fields_extracted": 140
      }
    }
  }
}
```

### Get Field Coverage Matrix

```http
GET /api/v1/validation/coverage
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| category | string | Filter by generator category |
| min_score | integer | Minimum compatibility score |
| parser_type | string | Filter by parser type (community, marketplace) |

#### Response

```json
{
  "success": true,
  "data": {
    "coverage_matrix": [
      {
        "generator": "fortinet_fortigate",
        "parsers": [
          {
            "parser_id": "fortinet_fortigate",
            "type": "community",
            "compatibility": 95,
            "field_coverage": 93,
            "ocsf_compliance": 100,
            "grade": "A"
          },
          {
            "parser_id": "marketplace-fortinetfortigate-latest",
            "type": "marketplace",
            "compatibility": 99,
            "field_coverage": 98,
            "ocsf_compliance": 100,
            "grade": "A+"
          }
        ]
      },
      {
        "generator": "crowdstrike_falcon",
        "parsers": [
          {
            "parser_id": "crowdstrike_falcon",
            "type": "community",
            "compatibility": 85,
            "field_coverage": 82,
            "ocsf_compliance": 80,
            "grade": "B+"
          },
          {
            "parser_id": "marketplace-crowdstrike-latest",
            "type": "marketplace",
            "compatibility": 92,
            "field_coverage": 90,
            "ocsf_compliance": 95,
            "grade": "A-"
          }
        ]
      }
    ],
    "summary": {
      "total_generators": 106,
      "total_parsers": 190,
      "excellent_pairs": 45,
      "good_pairs": 62,
      "needs_improvement": 28,
      "incompatible": 5,
      "avg_compatibility": 87.5,
      "avg_ocsf_compliance": 82.3
    },
    "recommendations": [
      "45 generator-parser pairs ready for production (A+ grade)",
      "28 pairs need field mapping improvements",
      "5 pairs require format conversion",
      "Marketplace parsers average 15% better compatibility"
    ]
  }
}
```

### Validate Batch

```http
POST /api/v1/validation/batch
```

#### Request Body

```json
{
  "validations": [
    {
      "generator_id": "aws_cloudtrail",
      "parser_id": "marketplace-awscloudtrail-latest"
    },
    {
      "generator_id": "cisco_firewall_threat_defense",
      "parser_id": "marketplace-ciscofirewallthreatdefense-latest"
    },
    {
      "generator_id": "okta_authentication",
      "parser_id": "okta_authentication"
    }
  ],
  "parallel": true,
  "include_recommendations": true
}
```

#### Response

```json
{
  "success": true,
  "data": {
    "batch_id": "batch_val_xyz789",
    "validations": [
      {
        "generator_id": "aws_cloudtrail",
        "parser_id": "marketplace-awscloudtrail-latest",
        "compatibility_score": 100,
        "grade": "A+",
        "status": "EXCELLENT"
      },
      {
        "generator_id": "cisco_firewall_threat_defense",
        "parser_id": "marketplace-ciscofirewallthreatdefense-latest",
        "compatibility_score": 85,
        "grade": "B+",
        "status": "GOOD",
        "recommendations": [
          "Add threat_id field for better threat intelligence"
        ]
      },
      {
        "generator_id": "okta_authentication",
        "parser_id": "okta_authentication",
        "compatibility_score": 95,
        "grade": "A",
        "status": "EXCELLENT"
      }
    ],
    "summary": {
      "total_validated": 3,
      "excellent": 2,
      "good": 1,
      "needs_improvement": 0,
      "failed": 0,
      "avg_compatibility": 93.3,
      "execution_time_ms": 250
    }
  }
}
```

### Get Validation History

```http
GET /api/v1/validation/history
```

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| generator_id | string | Filter by generator |
| parser_id | string | Filter by parser |
| days | integer | Number of days of history (default: 30) |

#### Response

```json
{
  "success": true,
  "data": {
    "history": [
      {
        "validation_id": "val_123",
        "timestamp": "2025-01-29T10:00:00Z",
        "generator_id": "crowdstrike_falcon",
        "parser_id": "marketplace-crowdstrike-latest",
        "compatibility_score": 92.5,
        "fixes_applied": 0
      },
      {
        "validation_id": "val_124",
        "timestamp": "2025-01-29T11:00:00Z",
        "generator_id": "crowdstrike_falcon",
        "parser_id": "marketplace-crowdstrike-latest",
        "compatibility_score": 98.5,
        "fixes_applied": 4
      }
    ],
    "trends": {
      "compatibility_improvement": "+6.0%",
      "most_improved": "crowdstrike_falcon",
      "most_validated": "fortinet_fortigate"
    }
  }
}
```

## Grading System

| Grade | Score Range | Description |
|-------|------------|-------------|
| A+ | 98-100% | Perfect compatibility, production ready |
| A | 94-97% | Excellent compatibility |
| A- | 90-93% | Very good compatibility |
| B+ | 86-89% | Good compatibility, minor improvements needed |
| B | 82-85% | Good compatibility |
| B- | 78-81% | Acceptable compatibility |
| C+ | 74-77% | Fair compatibility, improvements recommended |
| C | 70-73% | Fair compatibility |
| C- | 66-69% | Poor compatibility |
| D | 60-65% | Very poor compatibility |
| F | <60% | Incompatible, major fixes required |

## Error Codes

| Code | Description |
|------|-------------|
| VALIDATION_FAILED | Validation process failed |
| GENERATOR_PARSER_MISMATCH | Generator and parser formats incompatible |
| FIX_FAILED | Auto-fix operation failed |
| BACKUP_FAILED | Failed to create backup before fix |
| INSUFFICIENT_SAMPLES | Not enough sample events for validation |

## Examples

### Python Example

```python
import requests

API_BASE = "https://api.jarvis-coding.io/api/v1"
headers = {"Authorization": "Bearer YOUR_TOKEN"}

# Check compatibility
response = requests.post(
    f"{API_BASE}/validation/check",
    json={
        "generator_id": "aws_cloudtrail",
        "parser_id": "marketplace-awscloudtrail-latest",
        "deep_validation": True
    },
    headers=headers
)

result = response.json()["data"]
print(f"Compatibility: {result['compatibility_score']}% (Grade: {result['grade']})")

# Auto-fix if needed
if result['compatibility_score'] < 95:
    fix_response = requests.post(
        f"{API_BASE}/validation/fix/aws_cloudtrail",
        json={
            "target_parser": "marketplace-awscloudtrail-latest",
            "fix_strategy": "add_missing_fields",
            "backup": True
        },
        headers=headers
    )
    print(f"Fixes applied: {len(fix_response.json()['data']['fixes_applied'])}")
```

### cURL Example

```bash
# Get coverage matrix
curl -X GET "https://api.jarvis-coding.io/api/v1/validation/coverage?category=endpoint_security" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Generate validation report
curl -X GET "https://api.jarvis-coding.io/api/v1/validation/report/fortinet_fortigate/marketplace-fortinetfortigate-latest?format=html" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o validation_report.html
```

### JavaScript Example

```javascript
const API_BASE = 'https://api.jarvis-coding.io/api/v1';
const headers = { 'Authorization': 'Bearer YOUR_TOKEN' };

// Batch validation
const validations = [
  { generator_id: 'crowdstrike_falcon', parser_id: 'marketplace-crowdstrike-latest' },
  { generator_id: 'sentinelone_endpoint', parser_id: 'sentinelone_endpoint' },
  { generator_id: 'fortinet_fortigate', parser_id: 'marketplace-fortinetfortigate-latest' }
];

fetch(`${API_BASE}/validation/batch`, {
  method: 'POST',
  headers: { ...headers, 'Content-Type': 'application/json' },
  body: JSON.stringify({ validations, parallel: true })
})
.then(res => res.json())
.then(data => {
  const summary = data.data.summary;
  console.log(`Validated ${summary.total_validated} pairs`);
  console.log(`Average compatibility: ${summary.avg_compatibility}%`);
  console.log(`Excellent: ${summary.excellent}, Good: ${summary.good}`);
});
```

## Rate Limits

- Validation checks: 100 requests/minute
- Auto-fix operations: 20 requests/minute
- Coverage matrix: 200 requests/minute
- Report generation: 50 requests/minute

## See Also

- [Generators API](generators-api.md) - Manage event generators
- [Parsers API](parsers-api.md) - Configure log parsers
- [Field Validation System Design](../architecture/phase3_field_validation_system.md)