# Evaluation: 10 Newest Generators and Their Parsers

## Overview

Analysis of the 10 most recently created generators and their corresponding parser performance based on SDL API validation results.

## Parser Performance Summary

| Generator | Parser | Events | Fields | OCSF Score | Category | Status |
|-----------|---------|---------|---------|------------|----------|---------|
| `aws_elasticloadbalancer` | community-awselasticloadbalancer-latest | 9 | 99 | 60% | **Good** | ✅ Working |
| `aws_vpcflow` | community-awsvpcflowlogs-latest | 9 | 74 | 40% | Basic | ⚠️ Limited |
| `cisco_firewall_threat_defense` | community-ciscofirewallthreatdefense-latest | 10 | 74 | 40% | Basic | ⚠️ Limited |
| `cisco_meraki_flow` | community-ciscomerkiflow-latest | 10 | 74 | 40% | Basic | ⚠️ Limited |
| `darktrace_darktrace` | community-darktrace-latest | 9 | 74 | 40% | Basic | ⚠️ Limited |
| `manageengine_adauditplus` | community-manageengineadauditplus-latest | 10 | 74 | 40% | Basic | ⚠️ Limited |
| `microsoft_azure_ad` | community-microsoftazuread-latest | 10 | 74 | 40% | Basic | ⚠️ Limited |
| `microsoft_eventhub_azure_signin` | community-microsofteventhubazuresignin-latest | 10 | 74 | 40% | Basic | ⚠️ Limited |
| `microsoft_eventhub_defender_email` | community-microsofteventhhubdefenderemail-latest | 10 | 74 | 40% | Basic | ⚠️ Limited |
| `microsoft_eventhub_defender_emailforcloud` | community-microsofteventhubdefenderemailforcloud-latest | 10 | 74 | 40% | Basic | ⚠️ Limited |

## Key Findings

### 🟢 Performing Well (1/10)
- **aws_elasticloadbalancer**: Only parser with 60% OCSF score (Good category)
  - 99 fields extracted
  - 4 OCSF fields detected
  - Successfully processing events

### 🟡 Need Improvement (9/10)
All other parsers are in "Basic" category with similar characteristics:
- **40% OCSF score** (minimal compliance)
- **74 fields extracted** (standard SentinelOne metadata)
- **Only 1 OCSF field** (typically just timestamp)
- **No observables extraction**

## Detailed Analysis

### 1. AWS Elastic Load Balancer ✅ **Best Performer**

**Generator Quality**: Good - Has specific ELB fields
**Parser Quality**: Moderate - 60% OCSF score, needs enhancement

**Current Strengths**:
- Custom ELB-specific fields in generator
- Parser extracting meaningful network connection data
- Processing HTTP access logs correctly

**Missing OCSF Elements**:
- No proper class_uid mapping (should be 4002 - HTTP Activity)
- Missing activity_id mapping  
- No observable extraction for IPs and URLs
- Limited severity mapping

### 2. AWS VPC Flow ⚠️ **Basic Parser**

**Generator Issue**: Generic template, not VPC Flow specific
**Parser Issue**: Using wrong parser (marketplace-awsvpcflowlogs-latest)

**Problems**:
- Generator creates generic security events, not VPC Flow logs
- Parser expects specific VPC Flow format
- Mismatch between generator output and parser expectations

### 3. Cisco Firewall Threat Defense ⚠️ **Parser Mismatch**

**Generator Issue**: Generic template, lacks FTD specifics
**Parser Quality**: Complex syslog parser, but generators don't match format

**Problems**:
- Parser expects structured syslog with event IDs (430001, 430002, etc.)
- Generator produces generic JSON
- Missing threat intelligence fields
- No MITRE ATT&CK mapping

### 4-10. Microsoft EventHub Parsers ⚠️ **All Similar Issues**

**Common Problems Across All Microsoft Parsers**:
- Generic generators not producing Microsoft-specific event formats
- All parsers showing identical field counts (74 fields)
- Missing Azure AD specific attributes
- No authentication context
- No Office 365 security events

## Critical Issues Identified

### 1. Template-Based Generator Problem
**Issue**: Most newest generators use a generic template rather than product-specific logic

**Evidence**:
```python
# Generic template pattern found in all generators
event = {
    "timestamp": timestamp,
    "vendor": "...",
    "product": "...",
    "event_type": "security_event",
    "message": f"Sample ... event at {timestamp}",
    "severity": random.choice(["low", "medium", "high", "critical"]),
    "source_ip": f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
    "user": f"user{random.randint(1000,9999)}",
}
```

### 2. Parser-Generator Mismatch
**Issue**: Parsers expect specific formats, but generators produce generic events

**Examples**:
- VPC Flow parser expects AWS VPC Flow log format
- Cisco FTD parser expects syslog with specific event IDs  
- Microsoft parsers expect EventHub JSON format
- Generators produce generic security events

### 3. Missing Product-Specific Fields
**Issue**: Parsers can't extract meaningful data because generators don't include expected fields

## Improvement Recommendations

### Phase 1: Fix Generator-Parser Alignment (Week 1)

#### 1. AWS VPC Flow - Complete Rewrite
```python
def aws_vpcflow_log():
    """Generate actual VPC Flow log format"""
    return {
        "account_id": f"123456789{random.randint(10,99)}",
        "interface_id": f"eni-{random.randint(10000000,99999999):08x}",
        "srcaddr": f"10.0.{random.randint(1,254)}.{random.randint(1,254)}",
        "dstaddr": f"203.0.113.{random.randint(1,254)}",
        "srcport": random.randint(1024, 65535),
        "dstport": random.choice([80, 443, 22, 25, 53, 993]),
        "protocol": random.choice([6, 17]),  # TCP, UDP
        "packets": random.randint(1, 100),
        "bytes": random.randint(40, 4000),
        "windowstart": int(time.time()) - random.randint(0, 300),
        "windowend": int(time.time()),
        "action": random.choice(["ACCEPT", "REJECT"]),
        "flowlogstatus": random.choice(["OK", "NODATA", "SKIPDATA"])
    }
```

#### 2. Cisco FTD - Add Syslog Format
```python
def cisco_firewall_threat_defense_log():
    """Generate Cisco FTD syslog format"""
    event_id = random.choice([430001, 430002, 430003, 430004, 430005])
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    
    if event_id == 430001:
        return {
            "raw": f"{timestamp} ftd-hostname FTD-1-{event_id}: EventPriority: High, DeviceUUID: {uuid.uuid4()}, SourceIP: 192.168.1.10, DestinationIP: 203.0.113.5"
        }
```

#### 3. Microsoft EventHub - Add Proper JSON Structure
```python
def microsoft_eventhub_azure_signin_log():
    """Generate Azure AD Sign-in log in EventHub format"""
    return {
        "time": datetime.now(timezone.utc).isoformat(),
        "resourceId": f"/tenants/{uuid.uuid4()}/providers/Microsoft.aadiam",
        "operationName": "Sign-in activity",
        "category": "SignInLogs",
        "properties": {
            "id": str(uuid.uuid4()),
            "createdDateTime": datetime.now(timezone.utc).isoformat(),
            "userPrincipalName": f"user{random.randint(1000,9999)}@contoso.com",
            "userId": str(uuid.uuid4()),
            "appDisplayName": random.choice(["Microsoft Office 365 Portal", "Azure Portal"]),
            "ipAddress": f"203.0.113.{random.randint(1,254)}",
            "status": {
                "errorCode": random.choice([0, 50126, 50140]),
                "signInStatus": random.choice(["Success", "Failure"])
            },
            "location": {
                "city": random.choice(["Seattle", "New York", "London"]),
                "countryOrRegion": random.choice(["US", "GB"])
            }
        }
    }
```

### Phase 2: Enhance Parser OCSF Compliance (Week 2)

#### Add Missing OCSF Fields to All Parsers

**Required Additions**:
1. **Class/Category Mapping**:
   ```json
   "class_uid": 3001,  // Authentication for Azure AD
   "class_name": "Authentication",
   "category_uid": 3,
   "category_name": "Identity & Access Management"
   ```

2. **Activity Mapping**:
   ```json
   "activity_id": 1,  // Logon/Logoff
   "activity_name": "Logon"
   ```

3. **Observable Extraction**:
   ```json
   "observables": [
     {"name": "user", "type": "user_name", "value": "${user}"},
     {"name": "src_ip", "type": "ip_address", "value": "${src_ip}"}
   ]
   ```

### Phase 3: Validation and Testing (Week 3)

#### Test Each Fixed Parser
```bash
# For each generator
python event_python_writer/<generator>.py  # Test generator output
python event_python_writer/hec_sender.py --product <product> --count 10
# Wait 60 seconds
python final_parser_validation.py --parser <product> --detailed
```

#### Target Improvements
- **9/10 parsers** move from Basic (40%) to Good (60%+)
- **All parsers** extract observables
- **Field counts** increase to 50+ meaningful fields
- **Event alignment** between generators and parsers

## Priority Order for Fixes

### Week 1 - Critical Fixes (High Impact)
1. **microsoft_azure_ad** - High security value, widely used
2. **aws_vpcflow** - Network security critical for cloud
3. **cisco_firewall_threat_defense** - Network security essential
4. **darktrace_darktrace** - AI security detection important

### Week 2 - Microsoft EventHub Suite  
5. **microsoft_eventhub_azure_signin** - Authentication logging
6. **microsoft_eventhub_defender_email** - Email security
7. **microsoft_eventhub_defender_emailforcloud** - Cloud email security

### Week 3 - Remaining Parsers
8. **cisco_meraki_flow** - Network flow analysis  
9. **manageengine_adauditplus** - Active Directory auditing
10. **aws_elasticloadbalancer** - Enhance from Good to Excellent

## Success Metrics

### Current State
- ✅ 1/10 parsers in "Good" category
- ⚠️ 9/10 parsers in "Basic" category
- Average OCSF Score: 42%

### Target State (After Improvements)
- ✅ 8/10 parsers in "Good" category (60%+)
- ✅ 2/10 parsers in "Excellent" category (80%+)
- 🎯 Average OCSF Score: 70%+
- 🔍 100% observable extraction
- 📊 Meaningful field extraction (50+ fields per parser)

This evaluation reveals that while the newest generators exist, most need significant work to properly align with their parsers and achieve meaningful OCSF compliance for enterprise security operations.