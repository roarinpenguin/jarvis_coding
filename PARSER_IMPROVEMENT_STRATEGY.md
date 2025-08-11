# Parser Improvement Strategy for OCSF & OTEL Compliance

## Current State Analysis

### Parser Performance Distribution
Based on SDL API validation of 100 parsers with 3,415 events analyzed:

- **21 parsers (21%)**: Good OCSF compliance (60-100% score)
- **78 parsers (78%)**: Basic OCSF compliance (40% score)  
- **1 parser (1%)**: No events found

### Key Issues Identified

#### 1. Limited OCSF Field Extraction
Most parsers in the "basic" category only extract 1-2 OCSF fields (typically just `timestamp`), missing critical fields for proper event correlation and analysis.

#### 2. Missing Core OCSF Fields
Common missing fields across parsers:
- `class_uid` / `class_name` - Event classification
- `category_uid` / `category_name` - Event categorization
- `activity_id` / `activity_name` - Specific activity identification
- `severity_id` / `severity_name` - Event severity mapping
- `status_id` / `status_name` - Event status/outcome
- `metadata.*` - Product and version information
- `observables` - Extracted entities for correlation

#### 3. Incomplete Observable Extraction
Most parsers lack observable extraction for:
- IP addresses (`src_endpoint.ip`, `dst_endpoint.ip`)
- User identities (`actor.user.name`, `actor.user.uid`)
- File hashes (`file.hashes`)
- Domain names (`dst_endpoint.domain`)
- Process information (`process.name`, `process.pid`)

## Improvement Strategy

### Phase 1: Enhance High-Impact Parsers (Week 1-2)

Focus on the 78 "basic" parsers that need immediate improvement:

#### Priority 1 - Cloud Infrastructure (10 parsers)
```
aws_cloudtrail, aws_vpcflowlogs, aws_guardduty, aws_elb,
google_workspace, microsoft_azuread, microsoft_azure_ad_signin,
microsoft_365_mgmt_api, hashicorp_vault, cloudflare_waf
```

**Required Enhancements:**
1. Add proper OCSF class mapping:
   ```json
   "class_uid": 3001,  // For authentication events
   "class_name": "Authentication",
   "category_uid": 3,
   "category_name": "Identity & Access Management"
   ```

2. Map severity levels:
   ```json
   "rewrites": [
     {
       "input": "severity",
       "output": "severity_id",
       "match": "critical|high",
       "replace": "4"
     }
   ]
   ```

3. Extract observables:
   ```json
   "observables": [
     {
       "name": "src_ip",
       "type": "ip",
       "value": "${src_endpoint.ip}"
     }
   ]
   ```

#### Priority 2 - Security Tools (15 parsers)
```
darktrace, proofpoint, mimecast, netskope, sentinelone_endpoint,
sentinelone_identity, vectra_ai, armis, extrahop, crowdstrike_falcon,
beyondtrust_passwordsafe, cyberark_conjur, cisco_ise, teleport, abnormal_security
```

**Required Enhancements:**
1. Add threat intelligence fields:
   ```json
   "threat.name": "${alert.name}",
   "threat.uid": "${alert.id}",
   "malware.name": "${malware_family}",
   "malware.classification_ids": ["${classification}"]
   ```

2. Add MITRE ATT&CK mapping:
   ```json
   "attacks": [
     {
       "tactics": ["${tactic_id}"],
       "technique": {
         "uid": "${technique_id}",
         "name": "${technique_name}"
       }
     }
   ]
   ```

### Phase 2: Add OTEL Support (Week 3-4)

#### OpenTelemetry Fields to Add

1. **Trace Context**:
   ```json
   "trace_id": "${otel.trace_id}",
   "span_id": "${otel.span_id}",
   "trace_flags": "${otel.trace_flags}"
   ```

2. **Resource Attributes**:
   ```json
   "resource": {
     "service.name": "${service_name}",
     "service.version": "${service_version}",
     "deployment.environment": "${environment}"
   }
   ```

3. **Metrics Context**:
   ```json
   "metrics": {
     "duration_ms": "${response_time}",
     "bytes_sent": "${bytes_out}",
     "bytes_received": "${bytes_in}"
   }
   ```

### Phase 3: Standardize Parser Templates (Week 5-6)

#### Create Standard Parser Templates by Category

1. **Authentication Events Template**:
   - Standard fields for login/logout events
   - User identity extraction
   - Session tracking
   - MFA status

2. **Network Security Template**:
   - Connection metadata
   - Protocol details
   - Firewall decisions
   - Traffic volume metrics

3. **Cloud Activity Template**:
   - Cloud resource identifiers
   - API operations
   - IAM context
   - Cost/usage metrics

4. **Endpoint Security Template**:
   - Process information
   - File operations
   - Registry changes
   - System calls

## Implementation Checklist

### For Each Parser Enhancement:

- [ ] Add proper OCSF class/category/activity mappings
- [ ] Implement severity normalization (1-5 scale)
- [ ] Add status/disposition mapping
- [ ] Extract all available observables
- [ ] Add metadata.product information
- [ ] Include metadata.version from parser
- [ ] Map vendor-specific fields to OCSF equivalents
- [ ] Add OTEL trace/span fields where applicable
- [ ] Include resource attributes for service context
- [ ] Test with real event samples
- [ ] Validate field extraction with SDL API
- [ ] Document field mappings

## Success Metrics

### Target Goals (After Implementation):
- **90% of parsers** with OCSF score ≥ 60%
- **50% of parsers** with OCSF score ≥ 80%
- **100% of parsers** extracting observables
- **Average field extraction**: 50+ fields per parser
- **OTEL support**: 30% of parsers with trace context

### Validation Process:
1. Generate test events with all possible fields
2. Send to HEC endpoint for parsing
3. Query SDL API for parsed events
4. Verify field extraction completeness
5. Check observable extraction accuracy
6. Validate OCSF compliance scoring

## Quick Wins (Immediate Actions)

### 1. Add Missing Class UIDs
For all 78 "basic" parsers, add appropriate class_uid based on data type:
- Authentication: 3001
- Network Activity: 4001
- System Activity: 1001
- Application Activity: 6001
- Security Finding: 2001

### 2. Standardize Severity Mapping
Create consistent severity mapping across all parsers:
```json
"rewrites": [
  {"match": "critical|emergency", "replace": "5"},
  {"match": "high|alert", "replace": "4"},
  {"match": "medium|warning", "replace": "3"},
  {"match": "low|notice", "replace": "2"},
  {"match": "info|debug", "replace": "1"}
]
```

### 3. Extract Basic Observables
At minimum, extract:
- Source IP addresses
- Destination IP addresses
- Usernames
- Domain names
- File hashes (if present)

## Testing Framework

### Automated Validation Script
```python
# Use final_parser_validation.py with enhanced checks:
python final_parser_validation.py --check-ocsf --check-otel --verbose
```

### Per-Parser Testing
```python
# Test individual parser improvements:
python event_python_writer/hec_sender.py --product <parser> --count 10
# Wait 60 seconds
python final_parser_validation.py --parser <parser> --detailed
```

## Priority Order for Implementation

### Week 1: Critical Infrastructure
1. aws_cloudtrail - Add OCSF class mapping, extract AWS-specific observables
2. microsoft_azuread - Add authentication fields, user observables
3. okta_authentication - Already good, use as reference template
4. google_workspace - Add activity mapping, extract workspace entities

### Week 2: Security Tools
1. sentinelone_endpoint - Add threat fields, process observables
2. crowdstrike_falcon - Add MITRE ATT&CK, endpoint observables
3. darktrace - Add AI detection fields, network observables
4. proofpoint - Add email security fields, threat intelligence

### Week 3: Network Infrastructure
1. cisco_asa - Add firewall decision fields, connection observables
2. paloalto_prismasase - Add SASE-specific fields, user/device context
3. zscaler_firewall - Add proxy fields, URL categorization
4. f5_networks - Add load balancer fields, application context

### Week 4: OTEL Integration
1. Add trace context to all cloud service parsers
2. Add resource attributes to all infrastructure parsers
3. Add metrics context to all performance-related parsers

## Next Steps

1. **Create parser enhancement tickets** for each group
2. **Build automated testing suite** for OCSF/OTEL validation
3. **Document field mapping guidelines** for consistency
4. **Establish parser quality gates** for new additions
5. **Create parser development SDK** with templates and validators

This strategy will bring all parsers to enterprise-grade OCSF compliance with OTEL observability support, enabling better security analytics and operational visibility.