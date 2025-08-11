# Official SentinelOne Parser Implementation Plan

## 🎯 Key Findings from Analysis

### Discovered Official Parsers
- **13 official parser definitions** found in sentinelone_parsers.json
- **9 unique products** with production-grade OCSF compliance
- **5 Corelight variants** - conn, http, ssl, tunnel, general

### Performance Gap Analysis
- **Current Average OCSF Score**: 65.7% for parsers with official versions
- **Target with Official Parsers**: 80-95% OCSF compliance  
- **Potential Improvement**: +19.3% average increase

### Critical Discovery
**Corelight parsers already performing excellently**:
- corelight_conn: 100% OCSF, 289 fields ✅
- corelight_http: 100% OCSF, 271 fields ✅

**Major improvement opportunities**:
- cisco_firewall_threat_defense: 40% → 85%+ potential
- paloalto_prismasase: 40% → 80%+ potential  
- corelight_ssl/tunnel: 40% → 90%+ potential

## 🚀 Implementation Strategy

### Phase 1: High-Impact Replacements (Week 1)

#### 1. Cisco Firewall Threat Defense - PRIORITY 1
**Current State**: 40% OCSF, 74 fields, generic template generator
**Official Parser**: Supports 5 event types (430001-430005) with proper OCSF mapping

**Generator Update Required**:
```python
def cisco_firewall_threat_defense_log():
    """Generate actual Cisco FTD syslog format matching official parser"""
    import uuid
    import random
    
    event_types = [
        ("430001", "Intrusion event", "EventPriority: High, DeviceUUID: {uuid}"),
        ("430002", "Open", "SrcIP: {src_ip}, DstIP: {dst_ip}, SrcPort: {src_port}"),
        ("430003", "Close", "SrcIP: {src_ip}, DstIP: {dst_ip}, Duration: {duration}"),
        ("430004", "File events", "FileName: {filename}, Action: {action}"),
        ("430005", "File malware events", "ThreatName: {threat}, Severity: {severity}")
    ]
    
    event_id, event_name, template = random.choice(event_types)
    timestamp = datetime.now().strftime("%b %d %H:%M:%S")
    hostname = f"ftd-{random.randint(100,999)}"
    
    # Generate proper syslog format that matches official parser
    log_message = template.format(
        uuid=str(uuid.uuid4()),
        src_ip=f"192.168.{random.randint(1,254)}.{random.randint(1,254)}",
        dst_ip=f"203.0.113.{random.randint(1,254)}",
        src_port=random.randint(1024, 65535),
        duration=random.randint(1, 3600),
        filename=f"file_{random.randint(1000,9999)}.exe",
        action=random.choice(["CREATE", "DELETE", "MODIFY"]),
        threat=random.choice(["Trojan.Generic", "Malware.Detected"]),
        severity=random.choice(["High", "Medium", "Low"])
    )
    
    return {
        "raw": f"<165>{timestamp} {hostname} : FTD-1-{event_id}: {log_message}",
        "vendor": "Cisco",
        "product": "Firewall Threat Defense"
    }
```

**Expected Improvement**: 40% → 85% OCSF score

#### 2. Update Palo Alto Prisma SASE - PRIORITY 2  
**Current State**: 40% OCSF, basic parsing
**Official Parser**: Advanced network activity classification available

**Action**: Replace current parser with official "Prisma Access" configuration

#### 3. Fix Corelight SSL/Tunnel - PRIORITY 3
**Issue**: ssl and tunnel parsers underperforming despite having good official versions
**Solution**: Ensure generators produce format matching Corelight conn/http success

### Phase 2: Extract and Deploy Official Parsers (Week 2)

#### Parser Extraction Process
1. **Extract Individual Parsers**:
   ```bash
   # Create extraction script
   python extract_official_parsers.py --extract cisco_firewall_threat_defense
   python extract_official_parsers.py --extract palo_alto_firewall  
   python extract_official_parsers.py --extract check_point_ngfw
   ```

2. **Create Proper Directory Structure**:
   ```
   parsers/official/
   ├── cisco_firewall_threat_defense-official/
   │   ├── cisco_ftd.json
   │   └── metadata.yaml
   ├── palo_alto_firewall-official/  
   │   ├── palo_alto_fw.json
   │   └── metadata.yaml
   └── check_point_ngfw-official/
       ├── checkpoint_ngfw.json
       └── metadata.yaml
   ```

3. **Update hec_sender.py Mappings**:
   ```python
   SOURCETYPE_MAP = {
       # Use official parsers where available
       "cisco_firewall_threat_defense": "marketplace-ciscoftd-official",
       "paloalto_firewall": "marketplace-paloaltofw-official",
       "checkpoint": "marketplace-checkpointngfw-official",
       # Keep existing for others
       "fortinet_fortigate": "marketplace-fortinetfortigate-latest",
       "corelight_conn": "json",  # Already working well
   }
   ```

### Phase 3: Create Missing Parsers (Week 3)

#### New Parser Creation Priority

1. **Infoblox DDI** - DNS/DHCP critical for network security
   ```python
   def infoblox_ddi_log():
       """Generate Infoblox DNS/DHCP logs"""
       log_types = ["DNS_QUERY", "DHCP_LEASE", "DNS_RESPONSE"]
       # Generate format matching official parser expectations
   ```

2. **Check Point NGFW** - Update existing checkpoint.py
   ```python  
   def checkpoint_ngfw_log():
       """Generate Check Point Next Generation Firewall logs"""
       # Use official parser format requirements
   ```

3. **FortiManager** - Management platform logs
   ```python
   def fortimanager_log():
       """Generate FortiManager management logs"""
       # Configuration and audit events
   ```

## 📊 Expected Impact Analysis

### Before Implementation
| Parser | Current OCSF | Current Fields | Status |
|--------|---------------|----------------|---------|
| cisco_firewall_threat_defense | 40% | 74 | Poor |
| paloalto_prismasase | 40% | 74 | Poor |
| corelight_ssl | 40% | 249 | Underperforming |
| corelight_tunnel | 40% | 196 | Underperforming |

### After Implementation (Projected)
| Parser | Target OCSF | Target Fields | Expected Status |
|--------|-------------|---------------|-----------------|
| cisco_firewall_threat_defense | 85% | 150+ | Excellent |
| paloalto_prismasase | 80% | 120+ | Good |
| corelight_ssl | 90% | 280+ | Excellent |
| corelight_tunnel | 90% | 250+ | Excellent |

### Overall Project Impact
- **Current "Good" Parsers**: 21/100 (21%)
- **Projected "Good" Parsers**: 28/100 (28%) 
- **New "Excellent" Parsers**: +4 additional
- **Average OCSF Score Increase**: 65.7% → 75%+

## 🔧 Technical Implementation Details

### Official Parser Format Analysis
The official parsers use advanced features:

1. **Multiple Format Patterns**:
   ```json
   "formats": [
     {"format": ".*430001:\\s$_=identifier$: $_=value$"},
     {"format": ".*430002:\\s$_=identifier$: $_=value$"},
     {"format": ".*430003:\\s$_=identifier$: $_=value$"}
   ]
   ```

2. **OCSF Class Mapping**:
   ```json
   "attributes": {
     "class_uid": 4001,
     "activity_id": 1, 
     "activity_name": "Open",
     "category_uid": 4,
     "class_name": "Network Activity"
   }
   ```

3. **Advanced Field Extraction**:
   ```json
   "repeat": true,
   "attrBlacklist": ["FTD-1-430001"]
   ```

### Generator Requirements
All generators must be updated to produce formats matching official parser expectations:

- **Cisco FTD**: Proper syslog with event IDs (430001-430005)
- **Palo Alto**: Network security event format
- **Corelight**: Structured network monitoring logs
- **Check Point**: NGFW security event format

## ⚠️ Risk Mitigation

### Testing Strategy
1. **Isolated Testing**: Test each parser replacement individually
2. **Small Batch Validation**: Send 5-10 events per test
3. **SDL API Verification**: Confirm improved OCSF scores
4. **Rollback Plan**: Keep current parsers as backup

### Validation Process
```bash
# For each updated parser
python event_python_writer/<generator>.py  # Test new format
python event_python_writer/hec_sender.py --product <product> --count 5
# Wait 60 seconds
python final_parser_validation.py --parser <product> --detailed
# Verify OCSF score improvement
```

## 🎯 Success Metrics

### Immediate Targets (End of Week 1)
- ✅ Cisco FTD: 40% → 85%+ OCSF score
- ✅ Palo Alto Prisma SASE: 40% → 80%+ OCSF score
- ✅ Corelight SSL/Tunnel: 40% → 90%+ OCSF score

### Project Completion Targets (End of Week 3)
- 🎯 **30+ parsers** with 60%+ OCSF scores (vs current 21)
- 🎯 **Average OCSF score**: 75%+ (vs current 42%)  
- 🎯 **Official parser coverage**: 9/100 parsers using production-grade configurations
- 🎯 **Field extraction**: 50%+ improvement for official parser products

## 📋 Immediate Action Items

### This Week
1. ✅ **Update Cisco FTD Generator** - Implement syslog format matching official parser
2. ✅ **Extract Official Parsers** - Create individual parser files from sentinelone_parsers.json
3. ✅ **Replace High-Impact Parsers** - Deploy official versions for Cisco FTD, Palo Alto Prisma
4. ✅ **Test and Validate** - Confirm improved OCSF scores with SDL API

### Next Week  
1. **Create Missing Generators** - Build Infoblox DDI, FortiManager, Zscaler Private Access
2. **Update Product Mappings** - Ensure hec_sender.py routes to official parsers
3. **Comprehensive Testing** - Validate all official parser integrations
4. **Document Improvements** - Update performance metrics and guidelines

This plan leverages the official SentinelOne parsers to achieve enterprise-grade OCSF compliance and significantly improve our parsing effectiveness across critical security products.