# API Endpoints Reference

**Document Version:** 1.1  
**API Version:** v2.0.0  
**Last Updated:** August 30, 2025  
**Base URL:** `http://localhost:8000/api/v1`

## Authentication

### Methods
All endpoints except health checks require authentication using one of these methods:

**Header-based (Recommended):**
```bash
X-API-Key: your-api-key-here
```

**Query parameter:**
```bash
?api_key=your-api-key-here
```

### Role-based Access Control

| Role | Permissions | Endpoints |
|------|-------------|-----------|
| **Admin** | Full access + key management | All endpoints |
| **Write** | Execute generators, run scenarios | Read + Execute/Create endpoints |
| **Read-Only** | View data, run validation | GET endpoints only |

### API Key Management
```bash
# Generate keys
python app/utils/api_key_generator.py create --name "prod-api" --role write --rate-limit 1000

# List keys
python app/utils/api_key_generator.py list

# Revoke key
python app/utils/api_key_generator.py revoke <key-id>
```

---

## Response Format

### Success Response
```json
{
  "success": true,
  "data": {
    "key": "value"
  },
  "metadata": {
    "pagination": {},
    "request_id": "uuid"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  },
  "metadata": {
    "request_id": "uuid"
  }
}
```

### HTTP Status Codes
- **200** - Success
- **400** - Bad Request (invalid parameters)
- **401** - Unauthorized (missing/invalid API key)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **422** - Unprocessable Entity (validation errors)
- **429** - Rate Limited
- **500** - Internal Server Error

---

## Core Endpoints

### Health Check
**No authentication required**

#### Get Health Status
```http
GET /health
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "2.0.0",
    "uptime_seconds": 3600.5,
    "generators_available": 106,
    "parsers_available": 100,
    "database_connected": true,
    "timestamp": "2025-08-30T10:30:00Z"
  }
}
```

---

## Generators

### List All Generators
```http
GET /generators
```

**Query Parameters:**
- `category` (optional) - Filter by category
- `vendor` (optional) - Filter by vendor
- `search` (optional) - Search in names and descriptions
- `page` (default: 1) - Page number
- `per_page` (default: 20, max: 100) - Items per page

**Example Request:**
```bash
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/generators?category=cloud_infrastructure&page=1&per_page=10"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "generators": [
      {
        "id": "aws_cloudtrail",
        "name": "AWS CloudTrail",
        "category": "cloud_infrastructure",
        "vendor": "AWS",
        "description": "AWS CloudTrail API audit events",
        "supported_formats": ["json"],
        "star_trek_enabled": true,
        "fields_count": 45,
        "ocsf_compliance": 0.95
      }
    ],
    "total": 106
  },
  "metadata": {
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 106,
      "total_pages": 11
    }
  }
}
```

### Get Generator Categories
```http
GET /generators/categories
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "categories": [
      "cloud_infrastructure",
      "network_security", 
      "endpoint_security",
      "identity_access",
      "email_security",
      "web_security",
      "infrastructure"
    ]
  }
}
```

### Get Generator Details
```http
GET /generators/{generator_id}
```

**Example Request:**
```bash
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/generators/aws_cloudtrail"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "id": "aws_cloudtrail",
    "name": "AWS CloudTrail",
    "category": "cloud_infrastructure",
    "vendor": "AWS",
    "description": "AWS CloudTrail API audit events with Star Trek characters",
    "supported_formats": ["json"],
    "star_trek_enabled": true,
    "fields_count": 45,
    "ocsf_compliance": 0.95,
    "sample_event": {},
    "last_accessed": "2025-08-30T10:30:00Z"
  }
}
```

### Execute Generator
```http
POST /generators/{generator_id}/execute
```

**Request Body:**
```json
{
  "count": 5,
  "format": "json",
  "star_trek_theme": true,
  "options": {
    "custom_field": "value"
  }
}
```

**Field Validation:**
- `count`: integer, 1-1000 (required)
- `format`: string, one of "json", "csv", "syslog", "key_value" (required)
- `star_trek_theme`: boolean (default: true)
- `options`: object (optional)

**Example Request:**
```bash
curl -X POST \
  -H "X-API-Key: write-key" \
  -H "Content-Type: application/json" \
  -d '{"count": 3, "format": "json", "star_trek_theme": true}' \
  "http://localhost:8000/api/v1/generators/aws_cloudtrail/execute"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "generator_id": "aws_cloudtrail",
    "events": [
      {
        "eventTime": "2025-08-30T10:25:30Z",
        "eventName": "AssumeRole",
        "userIdentity": {
          "type": "IAMUser",
          "principalId": "AIDACKCEVSQ6C2EXAMPLE",
          "arn": "arn:aws:iam::123456789012:user/jean.picard",
          "accountId": "123456789012",
          "userName": "jean.picard"
        },
        "sourceIPAddress": "192.168.1.100",
        "userAgent": "aws-cli/2.0.0"
      }
    ],
    "count": 3,
    "format": "json",
    "execution_time_ms": 15.2,
    "metadata": {
      "star_trek_theme": true,
      "options": {}
    }
  }
}
```

### Batch Execute Generators
```http
POST /generators/batch/execute
```

**Request Body:**
```json
{
  "executions": [
    {
      "generator_id": "aws_cloudtrail",
      "count": 3,
      "format": "json"
    },
    {
      "generator_id": "crowdstrike_falcon", 
      "count": 2,
      "format": "json"
    }
  ]
}
```

**Validation Rules:**
- `executions`: array, 1-50 items (required)
- Each execution must have `generator_id` (required)
- `count` per execution: 1-1000 (default: 1)
- `format` per execution: valid format string (default: "json")

**Example Request:**
```bash
curl -X POST \
  -H "X-API-Key: write-key" \
  -H "Content-Type: application/json" \
  -d '{"executions": [{"generator_id": "aws_cloudtrail", "count": 3}, {"generator_id": "crowdstrike_falcon", "count": 2}]}' \
  "http://localhost:8000/api/v1/generators/batch/execute"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_1693401600",
    "executions": [
      {
        "generator_id": "aws_cloudtrail",
        "success": true,
        "events_count": 3,
        "execution_time_ms": 12.5
      },
      {
        "generator_id": "crowdstrike_falcon",
        "success": true,
        "events_count": 2,
        "execution_time_ms": 8.7
      }
    ],
    "total_events": 5,
    "total_execution_time_ms": 21.2,
    "parallel_execution": false
  }
}
```

### Validate Generator
```http
POST /generators/{generator_id}/validate
```

**Query Parameters:**
- `sample_size` (default: 5, max: 100) - Number of sample events to validate

**Example Response:**
```json
{
  "success": true,
  "data": {
    "generator_id": "aws_cloudtrail",
    "validation_status": "passed",
    "sample_events": 5,
    "issues": [],
    "warnings": ["Field 'timestamp' format inconsistent"],
    "ocsf_compliance": 0.95,
    "field_coverage": {
      "required_fields": 25,
      "optional_fields": 20,
      "custom_fields": 5
    }
  }
}
```

### Get Generator Schema
```http
GET /generators/{generator_id}/schema
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "generator_id": "aws_cloudtrail",
    "schema": {
      "type": "object",
      "properties": {
        "eventTime": {"type": "string", "format": "date-time"},
        "eventName": {"type": "string"},
        "userIdentity": {"type": "object"}
      },
      "required": ["eventTime", "eventName"]
    }
  }
}
```

---

## Parsers

### List Parsers
```http
GET /parsers
```

**Query Parameters:**
- `type` (optional) - Filter by "community" or "marketplace"
- `vendor` (optional) - Filter by vendor
- `page` (default: 1) - Page number
- `per_page` (default: 20, max: 100) - Items per page

**Example Response:**
```json
{
  "success": true,
  "data": {
    "parsers": [
      {
        "id": "aws_cloudtrail_community",
        "name": "AWS CloudTrail (Community)",
        "type": "community",
        "vendor": "AWS",
        "description": "Community parser for AWS CloudTrail",
        "input_format": "json",
        "ocsf_compliance": 0.85,
        "fields_extracted": 35,
        "version": "1.2.0",
        "last_updated": "2025-08-15T00:00:00Z"
      }
    ],
    "total": 100
  },
  "metadata": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### Get Parser Details
```http
GET /parsers/{parser_id}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "id": "aws_cloudtrail_community",
    "name": "AWS CloudTrail (Community)",
    "type": "community",
    "vendor": "AWS",
    "description": "Community parser for AWS CloudTrail events",
    "input_format": "json",
    "output_format": "ocsf",
    "ocsf_compliance": 0.85,
    "fields_extracted": 35,
    "version": "1.2.0",
    "schema_mapping": {},
    "last_updated": "2025-08-15T00:00:00Z"
  }
}
```

---

## Validation

### Validate Generator-Parser Compatibility
```http
POST /validation/compatibility
```

**Request Body:**
```json
{
  "generator_id": "aws_cloudtrail",
  "parser_id": "aws_cloudtrail_community"
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "generator_id": "aws_cloudtrail",
    "parser_id": "aws_cloudtrail_community", 
    "compatibility_score": 0.92,
    "format_compatible": true,
    "field_coverage": {
      "matched_fields": 32,
      "missing_fields": 3,
      "extra_fields": 8
    },
    "ocsf_compliance": {
      "score": 0.85,
      "issues": []
    },
    "issues": [],
    "warnings": ["Some optional fields not mapped"],
    "grade": "A"
  }
}
```

---

## Scenarios

### List Scenarios
```http
GET /scenarios
```

**Query Parameters:**
- `category` (optional) - Filter by attack category
- `search` (optional) - Search in scenario names
- `page` (default: 1) - Page number
- `per_page` (default: 20, max: 100) - Items per page

**Example Response:**
```json
{
  "success": true,
  "data": {
    "scenarios": [
      {
        "id": "phishing_campaign",
        "name": "Phishing Campaign",
        "description": "Multi-stage phishing attack with credential harvesting",
        "duration_minutes": 30,
        "generators": ["mimecast", "okta_authentication", "crowdstrike_falcon"],
        "severity": "high",
        "mitre_tactics": ["T1566", "T1078", "T1136"]
      }
    ],
    "total": 5
  }
}
```

### Get Scenario Templates
```http
GET /scenarios/templates
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "phishing_campaign",
        "name": "Phishing Campaign", 
        "description": "Multi-stage phishing attack with credential harvesting",
        "duration_minutes": 30,
        "generators": ["mimecast", "okta_authentication", "crowdstrike_falcon"],
        "severity": "high",
        "mitre_tactics": ["T1566", "T1078", "T1136"]
      },
      {
        "id": "ransomware_attack",
        "name": "Ransomware Attack",
        "description": "Ransomware deployment and lateral movement", 
        "duration_minutes": 60,
        "generators": ["crowdstrike_falcon", "microsoft_windows_eventlog", "veeam_backup"],
        "severity": "critical",
        "mitre_tactics": ["T1486", "T1021", "T1490"]
      }
    ]
  }
}
```

### Get Scenario Details
```http
GET /scenarios/{scenario_id}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "id": "phishing_campaign",
    "name": "Phishing Campaign",
    "description": "Multi-stage phishing attack with credential harvesting",
    "phases": [
      {
        "name": "Initial Email",
        "description": "Phishing email delivery",
        "generators": ["mimecast"],
        "duration_minutes": 5,
        "events_count": 10
      },
      {
        "name": "Credential Harvest", 
        "description": "User clicks and enters credentials",
        "generators": ["okta_authentication"],
        "duration_minutes": 10,
        "events_count": 5
      },
      {
        "name": "Lateral Movement",
        "description": "Attacker moves through network",
        "generators": ["crowdstrike_falcon"],
        "duration_minutes": 15,
        "events_count": 25
      }
    ],
    "total_duration_minutes": 30,
    "total_events": 40,
    "severity": "high",
    "mitre_tactics": ["T1566", "T1078", "T1136"]
  }
}
```

### Execute Scenario
```http
POST /scenarios/{scenario_id}/execute
```

**Request Body:**
```json
{
  "speed": "fast",
  "dry_run": false
}
```

**Field Validation:**
- `speed`: string, one of "realtime", "fast", "instant" (default: "fast")
- `dry_run`: boolean (default: false)

**Example Request:**
```bash
curl -X POST \
  -H "X-API-Key: write-key" \
  -H "Content-Type: application/json" \
  -d '{"speed": "fast", "dry_run": false}' \
  "http://localhost:8000/api/v1/scenarios/phishing_campaign/execute"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_550e8400-e29b-41d4-a716-446655440000",
    "scenario_id": "phishing_campaign", 
    "status": "started",
    "speed": "fast",
    "dry_run": false,
    "started_at": "2025-08-30T10:30:00Z",
    "estimated_completion": "2025-08-30T11:00:00Z"
  }
}
```

### Get Scenario Status
```http
GET /scenarios/{scenario_id}/status?execution_id={execution_id}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_550e8400-e29b-41d4-a716-446655440000",
    "scenario_id": "phishing_campaign",
    "status": "running",
    "progress": 65.5,
    "current_phase": "Lateral Movement",
    "events_generated": 26,
    "started_at": "2025-08-30T10:30:00Z",
    "estimated_completion": "2025-08-30T10:45:00Z"
  }
}
```

### Stop Scenario
```http
POST /scenarios/{scenario_id}/stop?execution_id={execution_id}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "scenario_id": "phishing_campaign",
    "execution_id": "exec_550e8400-e29b-41d4-a716-446655440000",
    "status": "stopped",
    "stopped_at": "2025-08-30T10:35:00Z",
    "events_generated": 15
  }
}
```

### Get Scenario Results
```http
GET /scenarios/{scenario_id}/results?execution_id={execution_id}&include_events=true
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "execution_id": "exec_550e8400-e29b-41d4-a716-446655440000",
    "scenario_id": "phishing_campaign",
    "status": "completed",
    "total_events": 40,
    "execution_time_ms": 1800000,
    "phases_completed": 3,
    "events": []
  }
}
```

### Create Custom Scenario
```http
POST /scenarios/custom
```

**Request Body:**
```json
{
  "name": "Custom Data Breach",
  "description": "Custom scenario for data breach simulation",
  "phases": [
    {
      "name": "Initial Access",
      "generators": ["crowdstrike_falcon"],
      "duration_minutes": 10
    },
    {
      "name": "Data Exfiltration",
      "generators": ["aws_cloudtrail", "netskope"],
      "duration_minutes": 20
    }
  ]
}
```

**Field Validation:**
- `name`: string, 3-100 characters (required)
- `description`: string, 10-500 characters (required)  
- `phases`: array, minimum 1 item (required)

**Example Response:**
```json
{
  "success": true,
  "data": {
    "scenario_id": "custom_1693401600",
    "name": "Custom Data Breach",
    "status": "created",
    "message": "Custom scenario created successfully"
  }
}
```

### Execute Batch Scenarios
```http
POST /scenarios/batch
```

**Request Body:**
```json
{
  "scenarios": [
    {
      "scenario_id": "phishing_campaign",
      "speed": "fast",
      "dry_run": false
    },
    {
      "scenario_id": "insider_threat",
      "speed": "instant", 
      "dry_run": true
    }
  ],
  "parallel": false
}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_1693401600",
    "executions": [
      {
        "scenario_id": "phishing_campaign",
        "execution_id": "exec_1",
        "status": "started"
      },
      {
        "scenario_id": "insider_threat", 
        "execution_id": "exec_2",
        "status": "started"
      }
    ],
    "parallel": false,
    "total": 2
  }
}
```

### Get Scenario Timeline
```http
GET /scenarios/analytics/timeline?scenario_id={scenario_id}&execution_id={execution_id}
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "scenario_id": "phishing_campaign",
    "execution_id": "exec_1",
    "timeline": [
      {
        "timestamp": "2025-08-30T10:30:00Z",
        "phase": "Initial Email",
        "status": "completed",
        "events_count": 10,
        "generators": ["mimecast"]
      },
      {
        "timestamp": "2025-08-30T10:35:00Z",
        "phase": "Credential Harvest",
        "status": "completed", 
        "events_count": 5,
        "generators": ["okta_authentication"]
      }
    ]
  }
}
```

---

## Export

### Export Generators List
```http
GET /export/generators?format={format}&category={category}
```

**Query Parameters:**
- `format`: string, one of "json", "csv", "yaml" (default: "json")
- `category` (optional): filter by category

**Example Requests:**
```bash
# JSON export
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/export/generators?format=json"

# CSV export  
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/export/generators?format=csv" \
  -o generators.csv

# YAML export with filter
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/export/generators?format=yaml&category=cloud_infrastructure" \
  -o cloud_generators.yaml
```

**JSON Response:**
```json
{
  "success": true,
  "data": {
    "generators": [
      {
        "id": "aws_cloudtrail",
        "name": "AWS CloudTrail",
        "category": "cloud_infrastructure",
        "vendor": "AWS"
      }
    ],
    "exported_at": "2025-08-30T10:30:00Z"
  }
}
```

**CSV Response:**
```csv
id,name,category,vendor,description
aws_cloudtrail,AWS CloudTrail,cloud_infrastructure,AWS,AWS CloudTrail API audit events
crowdstrike_falcon,CrowdStrike Falcon,endpoint_security,CrowdStrike,CrowdStrike endpoint events
```

### Export Generated Events
```http
POST /export/events
```

**Request Body:**
```json
{
  "generator_ids": ["aws_cloudtrail", "crowdstrike_falcon"],
  "count_per_generator": 5,
  "format": "json"
}
```

**Query Parameters:**
- `count_per_generator` (default: 5, max: 100): Events per generator
- `format`: string, one of "json", "csv" (default: "json")

**Example Request:**
```bash
curl -X POST \
  -H "X-API-Key: read-key" \
  -H "Content-Type: application/json" \
  -d '["aws_cloudtrail", "crowdstrike_falcon"]' \
  "http://localhost:8000/api/v1/export/events?count_per_generator=3&format=json"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "events": [
      {
        "eventTime": "2025-08-30T10:25:30Z",
        "eventName": "AssumeRole",
        "_generator": "aws_cloudtrail",
        "_exported_at": "2025-08-30T10:30:00Z"
      }
    ],
    "total_events": 6,
    "generators": ["aws_cloudtrail", "crowdstrike_falcon"],
    "exported_at": "2025-08-30T10:30:00Z"
  }
}
```

---

## Search

### Search Generators
```http
GET /search/generators?q={query}
```

**Query Parameters:**
- `q`: string, minimum 2 characters (required)
- `category` (optional): filter by category
- `vendor` (optional): filter by vendor  
- `page` (default: 1): page number
- `per_page` (default: 20, max: 100): items per page

**Example Request:**
```bash
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/search/generators?q=aws&category=cloud_infrastructure"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "aws_cloudtrail",
        "name": "AWS CloudTrail", 
        "category": "cloud_infrastructure",
        "vendor": "AWS",
        "description": "AWS CloudTrail API audit events",
        "search_score": 15
      },
      {
        "id": "aws_guardduty",
        "name": "AWS GuardDuty",
        "category": "cloud_infrastructure", 
        "vendor": "AWS",
        "description": "AWS GuardDuty threat detection",
        "search_score": 15
      }
    ],
    "total": 8,
    "query": "aws"
  },
  "metadata": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 8,
      "total_pages": 1
    },
    "search": {
      "query": "aws",
      "category": "cloud_infrastructure",
      "vendor": null
    }
  }
}
```

### Search Parsers
```http
GET /search/parsers?q={query}
```

**Query Parameters:**
- `q`: string, minimum 2 characters (required)
- `type` (optional): filter by "community" or "marketplace"

**Example Request:**
```bash
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/search/parsers?q=cloudtrail&type=community"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "id": "aws_cloudtrail_community",
        "name": "AWS CloudTrail (Community)",
        "type": "community",
        "vendor": "AWS",
        "description": "Community parser for AWS CloudTrail"
      }
    ],
    "total": 1,
    "query": "cloudtrail"
  }
}
```

### Search All Resources
```http
GET /search/all?q={query}
```

**Query Parameters:**
- `q`: string, minimum 2 characters (required)
- `types`: array, default ["generators", "parsers", "scenarios"]

**Example Request:**
```bash
curl -H "X-API-Key: read-key" \
  "http://localhost:8000/api/v1/search/all?q=phishing&types=generators,scenarios"
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "results": {
      "generators": [],
      "scenarios": [
        {
          "id": "phishing_campaign",
          "name": "Phishing Campaign",
          "description": "Multi-stage phishing attack"
        }
      ]
    },
    "total": 1,
    "query": "phishing",
    "types_searched": ["generators", "scenarios"]
  }
}
```

---

## Metrics

### Get Base Metrics
```http
GET /metrics
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "api_info": {
      "version": "2.0.0",
      "uptime_seconds": 86400,
      "last_restart": "2025-08-29T10:00:00Z"
    },
    "resource_counts": {
      "generators_total": 106,
      "generators_by_category": {
        "cloud_infrastructure": 9,
        "network_security": 34,
        "endpoint_security": 6,
        "identity_access": 20,
        "email_security": 4,
        "web_security": 13,
        "infrastructure": 20
      },
      "parsers_total": 100,
      "parsers_by_type": {
        "community": 85,
        "marketplace": 15
      }
    },
    "performance_metrics": {
      "average_response_time_ms": 45.2,
      "requests_per_minute": 120,
      "error_rate_percent": 0.5
    },
    "health_indicators": {
      "api_status": "healthy",
      "database_connected": true,
      "external_services": {
        "generator_service": "healthy",
        "parser_service": "healthy"
      }
    },
    "collected_at": "2025-08-30T10:30:00Z"
  }
}
```

### Get Generator Metrics
```http
GET /metrics/generators
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "execution_stats": {
      "total_executions_24h": 1205,
      "total_events_generated_24h": 15687,
      "average_execution_time_ms": 25.6,
      "most_used_generators": [
        {"id": "aws_cloudtrail", "executions": 156},
        {"id": "crowdstrike_falcon", "executions": 134},
        {"id": "microsoft_windows_eventlog", "executions": 98}
      ]
    },
    "format_distribution": {
      "json": 78.5,
      "csv": 12.3,
      "syslog": 6.7,
      "key_value": 2.5
    },
    "star_trek_usage": {
      "enabled_percent": 85.2,
      "total_star_trek_events": 13334
    }
  }
}
```

### Get Performance Metrics
```http
GET /metrics/performance
```

**Example Response:**
```json
{
  "success": true,
  "data": {
    "response_times": {
      "p50_ms": 25.5,
      "p95_ms": 98.2,
      "p99_ms": 245.8,
      "max_ms": 1205.6
    },
    "throughput": {
      "requests_per_second": 45.8,
      "events_per_second": 285.2
    },
    "error_rates": {
      "4xx_percent": 2.1,
      "5xx_percent": 0.3,
      "timeout_percent": 0.1
    },
    "resource_usage": {
      "cpu_percent": 15.8,
      "memory_mb": 156.7,
      "disk_usage_percent": 12.3
    }
  }
}
```

---

## Rate Limiting

### Rate Limits by Role

| Role | Requests/minute | Burst Limit |
|------|----------------|-------------|
| Admin | 1000 | 100 |
| Write | 500 | 50 |
| Read-Only | 200 | 20 |

### Rate Limit Headers

```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 487
X-RateLimit-Reset: 1693401660
```

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 30 seconds.",
    "details": {
      "limit": 500,
      "reset_time": "2025-08-30T10:31:00Z"
    }
  }
}
```

---

## Error Codes Reference

### Authentication Errors
- `MISSING_API_KEY` - API key not provided
- `INVALID_API_KEY` - API key is invalid or expired  
- `INSUFFICIENT_PERMISSIONS` - Role lacks required permissions

### Validation Errors
- `VALIDATION_ERROR` - Request validation failed
- `MISSING_REQUIRED_FIELD` - Required field not provided
- `INVALID_FIELD_VALUE` - Field value is invalid
- `INVALID_FORMAT` - Unsupported format specified

### Resource Errors
- `RESOURCE_NOT_FOUND` - Requested resource doesn't exist
- `GENERATOR_NOT_FOUND` - Generator ID doesn't exist
- `PARSER_NOT_FOUND` - Parser ID doesn't exist
- `SCENARIO_NOT_FOUND` - Scenario ID doesn't exist

### Execution Errors
- `EXECUTION_FAILED` - Generator/scenario execution failed
- `BATCH_EXECUTION_FAILED` - Batch execution had failures
- `SCENARIO_EXECUTION_FAILED` - Scenario execution failed

### System Errors
- `INTERNAL_SERVER_ERROR` - Unexpected server error
- `SERVICE_UNAVAILABLE` - External service unavailable
- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded

---

## SDK Examples

### Python SDK Example
```python
import requests

class JarvisAPI:
    def __init__(self, base_url="http://localhost:8000/api/v1", api_key=""):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
    
    def list_generators(self, category=None):
        params = {"category": category} if category else {}
        response = requests.get(f"{self.base_url}/generators", 
                               headers=self.headers, params=params)
        return response.json()
    
    def execute_generator(self, generator_id, count=1, format="json"):
        data = {"count": count, "format": format}
        response = requests.post(f"{self.base_url}/generators/{generator_id}/execute",
                               headers=self.headers, json=data)
        return response.json()
    
    def search_generators(self, query, category=None):
        params = {"q": query, "category": category}
        response = requests.get(f"{self.base_url}/search/generators",
                               headers=self.headers, params=params)
        return response.json()

# Usage
api = JarvisAPI(api_key="your-api-key")
generators = api.list_generators(category="cloud_infrastructure")
results = api.execute_generator("aws_cloudtrail", count=5)
search_results = api.search_generators("aws")
```

### cURL Examples Collection
```bash
# Save as api_examples.sh
#!/bin/bash

API_KEY="your-api-key-here"
BASE_URL="http://localhost:8000/api/v1"

# List generators
curl -H "X-API-Key: $API_KEY" "$BASE_URL/generators"

# Execute generator
curl -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"count": 3, "format": "json"}' \
  "$BASE_URL/generators/aws_cloudtrail/execute"

# Batch execute
curl -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"executions": [{"generator_id": "aws_cloudtrail", "count": 3}]}' \
  "$BASE_URL/generators/batch/execute"

# Search generators  
curl -H "X-API-Key: $API_KEY" "$BASE_URL/search/generators?q=aws"

# Execute scenario
curl -X POST -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"speed": "fast", "dry_run": false}' \
  "$BASE_URL/scenarios/phishing_campaign/execute"

# Export generators
curl -H "X-API-Key: $API_KEY" "$BASE_URL/export/generators?format=csv" -o generators.csv
```

---

**For additional support and examples, see:**
- Interactive API Documentation: http://localhost:8000/api/v1/docs
- ReDoc Documentation: http://localhost:8000/api/v1/redoc
- Implementation Guide: `/api/API_FIX_IMPLEMENTATION_GUIDE.md`
- Developer Checklist: `/api/API_FIX_CHECKLIST.md`