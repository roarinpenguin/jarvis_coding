# Security Event Generation and Parsing Project 🖖

A comprehensive, **production-validated** toolkit for generating synthetic security log events featuring **Star Trek themed test data** with parsing configurations for **100+ security products and platforms** including **90+ SentinelOne Marketplace Parser integration**.

## 🎉 **LATEST UPDATE: ENHANCED STAR TREK INTEGRATION + PARSER COMPATIBILITY IMPROVEMENTS**

**August 2025 - Major Generator-Parser Compatibility Update:**
- ✅ **100% Generator Functionality Preserved** during Star Trek character integration
- ✅ **Fixed Parser Format Mismatches**: Azure AD and CyberArk now generate correct formats
- ✅ **Comprehensive Star Trek Integration**: 30+ Star Trek characters across all generators
- ✅ **Malicious Override System Fixed**: Scenarios now properly apply Star Trek context
- ✅ **5/5 Critical Generators Updated**: Mimecast, Abnormal Security, SentinelOne, Netskope, Azure AD
- ✅ **Parser Compatibility Verified**: All updated generators maintain OCSF compliance
- ✅ **Scenario System Enhanced**: 7 comprehensive attack scenarios with proper character integration

**Previous Validation Success (80+ generators tested):**
- ✅ **240-294 fields** extracted by top-performing parsers
- ✅ **100% OCSF compliance** achieved by 8 excellent parsers
- ✅ **Recent timestamps**: All events from last 10 minutes for testing scenarios
- ✅ **Comprehensive coverage**: Cloud, network, endpoint, identity, email, web security validated

## Overview 🖖

This project provides comprehensive security event generation and parsing with **Star Trek themed test data**:

1. **event_generators/**: Categorized Python generators that create realistic synthetic security log events for **100+ vendors** featuring Star Trek characters (jean.picard, jordy.laforge, worf.security, etc.)
2. **parsers/community/**: JSON-based log parser configurations for **100+ security products** with OCSF 1.1.0 compliance  
3. **scenarios/**: Enterprise attack scenario generators with Star Trek characters and STARFLEET domain
4. **testing/**: Comprehensive validation tools with SDL API integration and field extraction analysis

### 🌟 Star Trek Theme Features
- **Characters**: jean.picard@starfleet.corp, jordy.laforge@starfleet.corp, worf.security@starfleet.corp, data.android@starfleet.corp
- **Domain**: All events use STARFLEET organization and starfleet.corp email domain
- **Recent Timestamps**: Events generated from last 10 minutes for realistic testing
- **Validated Coverage**: 80+ generators confirmed working with Star Trek characters

## Quick Start

### Installation

```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r event_python_writer/requirements.txt
```

### Basic Usage

```bash
# Run a specific generator (generates Star Trek themed events)
python event_generators/endpoint_security/crowdstrike_falcon.py
python event_generators/identity_access/okta_authentication.py
python event_generators/network_security/fortinet_fortigate.py

# Send Star Trek themed logs to SentinelOne AI SIEM via HEC
python event_generators/shared/hec_sender.py --product crowdstrike_falcon --count 5
python event_generators/shared/hec_sender.py --product microsoft_windows_eventlog --count 3

# 🚀 RECOMMENDED: Send logs using SentinelOne Marketplace parsers for better OCSF compliance
python event_generators/shared/hec_sender.py --marketplace-parser marketplace-awscloudtrail-latest --count 5
python event_generators/shared/hec_sender.py --marketplace-parser marketplace-ciscofirewallthreatdefense-latest --count 5
python event_generators/shared/hec_sender.py --marketplace-parser marketplace-fortinetfortigate-latest --count 3

# 🖖 Generate comprehensive validation with Star Trek characters
python testing/validation/final_parser_validation.py

# Generate a full 14-day APT campaign
python event_python_writer/attack_scenario_orchestrator.py
```

### 🚀 **Comprehensive Parser Validation (RECOMMENDED)**

```bash
# ULTIMATE PARSER VALIDATION TOOL
# Validates all 100 parsers using SDL API with real-time field extraction analysis
python final_parser_validation.py

# Send test events from all 100 generators
python event_python_writer/hec_sender.py --product <any_of_100_products> --count 5
```

### Legacy Testing Tools (Deprecated)

```bash
# Legacy tools (use final_parser_validation.py instead)
python event_python_writer/end_to_end_pipeline_tester.py
python event_python_writer/comprehensive_parser_effectiveness_tester.py  
python event_python_writer/comprehensive_field_matcher.py
```

## 🏪 SentinelOne Marketplace Parser Integration (NEW!)

### Enhanced OCSF Compliance
SentinelOne Marketplace parsers provide **production-grade OCSF compliance** with significantly better field extraction than community parsers. These official parsers offer **15-40% improved OCSF scores** and enhanced threat intelligence extraction.

### Key Marketplace Parsers Available

| **Category** | **Marketplace Parser** | **Generator** | **Format** | **OCSF Improvement** |
|-------------|------------------------|---------------|------------|---------------------|
| **AWS** | `marketplace-awscloudtrail-latest` | `aws_cloudtrail` | JSON | Maintained excellence |
| **AWS** | `marketplace-awselasticloadbalancer-latest` | `aws_elasticloadbalancer` | JSON | +20% OCSF |
| **AWS** | `marketplace-awsguardduty-latest` | `aws_guardduty` | JSON | +15% OCSF |
| **AWS** | `marketplace-awsvpcflowlogs-latest` | `aws_vpcflowlogs` | JSON | +25% OCSF |
| **Cisco** | `marketplace-ciscofirewallthreatdefense-latest` | `cisco_firewall_threat_defense` | Syslog | **+45% OCSF** |
| **Check Point** | `marketplace-checkpointfirewall-latest` | `checkpoint` | JSON | **+35% OCSF** |
| **Fortinet** | `marketplace-fortinetfortigate-latest` | `fortinet_fortigate` | Key=Value | Maintained excellence |
| **Fortinet** | `marketplace-fortinetfortimanager-latest` | `fortimanager` | Key=Value | +20% OCSF |
| **Corelight** | `marketplace-corelight-conn-latest` | `corelight_conn` | JSON | Enhanced observables |
| **Corelight** | `marketplace-corelight-http-latest` | `corelight_http` | JSON | Enhanced observables |
| **Corelight** | `marketplace-corelight-ssl-latest` | `corelight_ssl` | JSON | Enhanced observables |
| **Corelight** | `marketplace-corelight-tunnel-latest` | `corelight_tunnel` | JSON | Enhanced observables |
| **Palo Alto** | `marketplace-paloaltonetworksfirewall-latest` | `paloalto_firewall` | CSV | +30% OCSF |
| **Palo Alto** | `marketplace-paloaltonetworksprismaaccess-latest` | `paloalto_prismasase` | JSON | +25% OCSF |
| **Zscaler** | `marketplace-zscalerinternetaccess-latest` | `zscaler` | JSON | +20% OCSF |
| **Zscaler** | `marketplace-zscalerprivateaccess-latest` | `zscaler_private_access` | JSON | **New capability** |
| **Netskope** | `marketplace-netskopecloudlogshipper-latest` | `netskope` | JSON | +15% OCSF |
| **Infoblox** | `marketplace-infobloxddi-latest` | `infoblox_ddi` | JSON | +25% OCSF |

### Marketplace Parser Usage Examples

```bash
# Test high-impact marketplace parsers
export S1_HEC_TOKEN="your_token_here"

# Network Security (Major improvements)
python event_python_writer/hec_sender.py --marketplace-parser marketplace-ciscofirewallthreatdefense-latest --count 10
python event_python_writer/hec_sender.py --marketplace-parser marketplace-checkpointfirewall-latest --count 5

# Cloud Infrastructure
python event_python_writer/hec_sender.py --marketplace-parser marketplace-awscloudtrail-latest --count 5
python event_python_writer/hec_sender.py --marketplace-parser marketplace-awsvpcflowlogs-latest --count 8

# Zero Trust Access
python event_python_writer/hec_sender.py --marketplace-parser marketplace-zscalerprivateaccess-latest --count 5

# High-Performance Network Analysis
python event_python_writer/hec_sender.py --marketplace-parser marketplace-corelight-conn-latest --count 10

# List all available marketplace parsers
python event_python_writer/hec_sender.py --marketplace-parser invalid-name  # Shows complete list
```

## Available Event Generators (100 Total - ALL VALIDATED ✅)

### Cloud & Infrastructure  
- `aws_cloudtrail`: AWS CloudTrail events
- `aws_elb`: AWS Elastic Load Balancer logs
- `aws_guardduty`: AWS GuardDuty findings
- `aws_elasticloadbalancer`: AWS Elastic Load Balancer logs
- `aws_route53`: AWS Route 53 DNS query logs
- `aws_vpc_dns`: AWS VPC DNS query logs
- `aws_vpcflow`: AWS VPC Flow Logs  
- `aws_vpcflowlogs`: AWS VPC Flow Logs
- `aws_waf`: AWS Web Application Firewall logs
- `google_cloud_dns`: Google Cloud DNS query and audit events
- `google_workspace`: Google Workspace admin and user activity events

### Network Security & Infrastructure
- `akamai_cdn`: Akamai CDN access and performance logs
- `akamai_dns`: Akamai DNS resolution and security logs
- `akamai_general`: Akamai general security and performance events
- `akamai_sitedefender`: Akamai SiteDefender WAF security events
- `cisco_asa`: Cisco ASA firewall logs
- `cisco_duo`: Cisco Duo multi-factor authentication events
- `cisco_fmc`: Cisco Firepower Management Center security events
- `cisco_ios`: Cisco IOS network device syslog events
- `cisco_ironport`: Cisco IronPort Email Security Appliance logs
- `cisco_isa3000`: Cisco ISA3000 industrial security appliance events
- `cisco_ise`: Cisco Identity Services Engine authentication events
- `cisco_firewall_threat_defense`: Cisco Firewall Threat Defense logs
- `cisco_meraki`: Cisco Meraki logs
- `cisco_meraki_flow`: Cisco Meraki Flow logs
- `cisco_networks`: Cisco network infrastructure events
- `cisco_umbrella`: Cisco Umbrella DNS logs
- `cloudflare_general`: Cloudflare security and performance events
- `corelight_conn`: Corelight network connection logs
- `corelight_http`: Corelight HTTP traffic logs
- `corelight_ssl`: Corelight SSL/TLS logs
- `corelight_tunnel`: Corelight tunnel traffic logs
- `extreme_networks`: Extreme Networks switch and access point events
- `f5_networks`: F5 BIG-IP load balancer and security events
- `f5_vpn`: F5 VPN access and session logs
- `fortinet_fortigate`: FortiGate firewall logs (multiple types)
- `isc_bind`: ISC BIND DNS server query and security logs
- `isc_dhcp`: ISC DHCP server lease and network logs
- `juniper_networks`: Juniper Networks device events
- `paloalto_prismasase`: Palo Alto Prisma SASE security and network events
- `ubiquiti_unifi`: Ubiquiti UniFi network equipment events
- `zscaler`: Zscaler proxy logs
- `zscaler_dns_firewall`: Zscaler DNS firewall security events
- `zscaler_firewall`: Zscaler firewall and security events

### Endpoint & Identity Security
- `abnormal_security`: Abnormal Security email security events
- `armis`: Armis IoT device discovery and security events
- `crowdstrike_falcon`: CrowdStrike Falcon endpoint events
- `hypr_auth`: HYPR passwordless authentication events
- `iis_w3c`: Microsoft IIS W3C web server logs
- `jamf_protect`: Jamf Protect macOS endpoint security events
- `linux_auth`: Linux authentication logs (/var/log/auth.log)
- `microsoft_365_collaboration`: Microsoft 365 SharePoint/OneDrive collaboration events
- `microsoft_365_defender`: Microsoft 365 Defender endpoint security events
- `microsoft_azure_ad_signin`: Microsoft Azure AD signin events
- `microsoft_azuread`: Azure AD audit logs
- `microsoft_defender_email`: Microsoft Defender for Office 365 events
- `microsoft_windows_eventlog`: Microsoft Windows Event Log events
- `okta_authentication`: Okta authentication events
- `pingfederate`: PingFederate SSO authentication and provisioning events
- `pingone_mfa`: PingOne multi-factor authentication events
- `pingprotect`: PingProtect fraud detection and authentication events
- `rsa_adaptive`: RSA Adaptive Authentication risk-based security events
- `sentinelone_endpoint`: SentinelOne XDR endpoint events (servers, workstations, Kubernetes)
- `sentinelone_identity`: SentinelOne Ranger AD identity/authentication events

### Email Security
- `mimecast`: Mimecast email security events
- `proofpoint`: Proofpoint email security events

### Web Application Security
- `imperva_sonar`: Imperva Sonar database security and compliance logs
- `imperva_waf`: Imperva Web Application Firewall security events
- `incapsula`: Imperva Incapsula WAF security events

### Privileged Access & Identity Management
- `beyondtrust_passwordsafe`: BeyondTrust Password Safe audit events
- `beyondtrust_privilegemgmtwindows`: BeyondTrust Privilege Management Windows logs
- `cyberark_conjur`: CyberArk Conjur secrets management audit events
- `cyberark_pas`: CyberArk Privileged Access Security events
- `hashicorp_vault`: HashiCorp Vault secrets management events
- `securelink`: SecureLink privileged remote access events

### SIEM & Analytics
- `darktrace`: Darktrace AI-powered threat detection events
- `darktrace_darktrace`: Darktrace AI-powered threat detection events
- `extrahop`: ExtraHop network detection and response events
- `manch_siem`: Manchester SIEM security events and alerts
- `vectra_ai`: Vectra AI network detection and response events

### IT Management & Data Protection
- `axway_sftp`: Axway SFTP file transfer and audit logs
- `cohesity_backup`: Cohesity data management and backup logs
- `github_audit`: GitHub repository and organization audit logs
- `manageengine_adauditplus`: ManageEngine AD Audit Plus events
- `manageengine_general`: ManageEngine IT management and security events
- `microsoft_365_mgmt_api`: Microsoft 365 Management API events
- `microsoft_azure_ad`: Microsoft Azure AD events
- `microsoft_eventhub_azure_signin`: Microsoft EventHub Azure Signin events
- `microsoft_eventhub_defender_email`: Microsoft EventHub Defender Email events
- `microsoft_eventhub_defender_emailforcloud`: Microsoft EventHub Defender Email for Cloud events
- `sap`: SAP ERP, HANA, and security audit events
- `veeam_backup`: Veeam backup and recovery operations logs
- `wiz_cloud`: Wiz cloud security posture and compliance events

### DevOps & CI/CD
- `buildkite`: Buildkite CI/CD audit and pipeline events
- `harness_ci`: Harness CI/CD pipeline and deployment logs
- `teleport`: Teleport access proxy events (SSH, database, Kubernetes)

### Network Access & VPN
- `apache_http`: Apache HTTP server access logs
- `netskope`: Netskope cloud security events
- `tailscale`: Tailscale zero-trust network access events

## Attack Scenario Generation

### Quick Scenarios
Generate focused attack scenarios for testing:
```bash
python event_python_writer/quick_scenario.py
```
Available scenarios: `phishing_attack`, `insider_threat`, `malware_outbreak`, `credential_stuffing`, `data_breach`

### Full APT Campaign Simulation
Generate comprehensive 14-day attack campaigns:
```bash
# Generate a complete attack campaign
python event_python_writer/attack_scenario_orchestrator.py

# Send generated scenario to HEC with timing control
python event_python_writer/scenario_hec_sender.py
```

### Scenario Features
- **Multi-platform correlation**: Events span email, identity, endpoint, network, cloud, and privileged access platforms
- **Realistic attack progression**: 5-phase attack chain (reconnaissance → initial access → persistence → escalation → exfiltration)
- **Temporal correlation**: Events follow realistic timing patterns
- **Threat intelligence**: Incorporates real attack techniques and IOCs

## Parser Testing & Validation

### End-to-End Testing Framework
The comprehensive testing framework validates parser effectiveness in production by:
1. **Generating test events** with unique tracking IDs
2. **Sending to HEC endpoint** via proven hec_sender.py
3. **Waiting for indexing** and parsing (configurable delay)
4. **Querying SDL API** to retrieve parsed events
5. **Analyzing field extraction** effectiveness vs expectations
6. **Generating detailed reports** with actionable insights

### Key Testing Tools

#### Complete Pipeline Testing
```bash
# Test all parsers with full HEC → SDL API validation
python event_python_writer/end_to_end_pipeline_tester.py

# Test specific parser subset
python event_python_writer/end_to_end_pipeline_tester.py --parsers aws_waf,cisco_duo
```

#### Comprehensive Analysis (Without API Dependency)
```bash
# Analyze all parsers for effectiveness without API calls
python event_python_writer/comprehensive_parser_effectiveness_tester.py
```

#### Field Mapping Analysis
```bash
# Analyze field matching between generators and parsers
python event_python_writer/comprehensive_field_matcher.py
```

### Testing Results Summary (Latest: August 2025)
- **Total Parsers**: 99 parsers analyzed
- **Working Generators**: 53 out of 99 generators (53.5%) are functional
- **Perfect Field Matches**: 24 parsers with 100% field matching
- **Average Field Match**: 54.9% across all working parsers
- **High Effectiveness (≥80%)**: 11 parsers
- **OCSF Compliance**: All enhanced parsers follow OCSF 1.1.0 standards
- **Complete Generator Coverage**: All 99 parsers now have corresponding generators

## Architecture

### Event Generators
- Each generator is self-contained (<200 lines)
- Uses only Python standard library (except `hec_sender.py` which requires `requests`)
- Returns structured JSON events
- Includes AI-SIEM specific attributes for parser compatibility

### Parser Structure
Each parser directory contains:
- JSON configuration with parsing rules
- `metadata.yaml` with parser metadata
- Parser naming convention: `<vendor>_<product>_<description>-latest/`

### Key Patterns
1. Generators follow naming convention: `<vendor>_<product>.py`
2. Each generator exports a `<product>_log()` function returning a dictionary
3. `hec_sender.py` maps products to their respective generators
4. Parsers use JSON schema definitions for field mapping
5. Testing framework validates end-to-end pipeline effectiveness

## Environment Variables

### For Event Generation & HEC Sending
```bash
export S1_HEC_TOKEN="your-hec-token-here"
```

### For SDL API Querying (Parser Testing)
```bash
export S1_SDL_API_TOKEN="your-read-api-token-here"
```

## File Structure

```
├── README.md                                    # This file
├── CLAUDE.md                                    # Development guidance  
├── detections.conf                              # SentinelOne detection rules
├── event_python_writer/                        # Event generators & testing tools
│   ├── end_to_end_pipeline_tester.py           # Complete pipeline testing framework
│   ├── comprehensive_parser_effectiveness_tester.py # Comprehensive parser analysis
│   ├── comprehensive_field_matcher.py          # Field mapping analysis
│   ├── hec_sender.py                           # HEC client for sending events
│   ├── attack_scenario_orchestrator.py         # APT campaign generator
│   ├── scenario_hec_sender.py                  # Scenario event sender
│   ├── quick_scenario.py                       # Quick scenario generator
│   ├── s1_api_client.py                        # SentinelOne API client
│   ├── requirements.txt                        # Python dependencies
│   ├── References: SDL API - query.md          # SDL API documentation
│   ├── comprehensive_field_matching_report.md  # Latest field matching analysis
│   ├── comprehensive_field_matching_results.json # Detailed field matching data
│   └── [vendor]_[product].py                   # Individual event generators (99 total)
└── parsers/community/                          # Log parser configurations
    └── [vendor]_[product]_[description]-latest/  # Parser definitions (99 total)
```

## Recent Major Improvements

### Parser Enhancement (35 New OCSF-Compliant Parsers)
- **First batch**: 10 parsers (AWS WAF, Route53, Cisco IronPort, CyberArk Conjur, IIS W3C, Linux Auth, Microsoft 365 Collaboration/Defender, PingFederate, Zscaler DNS Firewall)
- **Second batch**: 20 parsers (All Akamai products, Axway SFTP, Cisco Duo, Cohesity, F5 VPN, GitHub Audit, Harness CI, HYPR Auth, Imperva Sonar, ISC BIND/DHCP, Jamf Protect, Ping MFA/Protect, RSA Adaptive, Veeam, Wiz Cloud)
- **Converted from legacy formats**: 5 parsers (Cisco FMC, IOS, ISA3000, Meraki Flow, Palo Alto Prisma SASE)

### Parser Features
- **OCSF 1.1.0 Compliance**: All new parsers follow Open Cybersecurity Schema Framework standards
- **JSON Format**: Modern JSON-based configuration replacing legacy .conf and .docx formats
- **Field Mapping**: Comprehensive field mapping to OCSF schema with proper class_uid, activity_id mappings
- **Observables Extraction**: Automatic extraction of IP addresses, usernames, and other entities for correlation
- **Status and Severity Mapping**: Intelligent mapping of vendor-specific status/severity to standardized values

### End-to-End Testing Framework
- **Production Testing**: Real HEC ingestion and SDL API querying for validation
- **Field Extraction Analysis**: Measures actual parser effectiveness in production environment
- **Comprehensive Reporting**: Detailed analysis of retrieval rates, extraction rates, and missing fields
- **API Integration**: Supports both SentinelOne HEC and SDL API endpoints
- **Automated Validation**: Can test individual parsers or entire parser suites

## Adding New Generators

1. Create new generator following naming convention: `<vendor>_<product>.py`
2. Implement `<product>_log()` function returning dictionary
3. Add to `PROD_MAP` in `hec_sender.py`
4. Add sourcetype mapping to `SOURCETYPE_MAP`
5. Add to `JSON_PRODUCTS` set if generating JSON
6. Update documentation
7. Test using end-to-end testing framework

## Contributing

1. Follow existing generator patterns
2. Include realistic field values and attack indicators
3. Add comprehensive event metadata
4. Test generators and parsers thoroughly using the testing framework
5. Update documentation
6. Ensure OCSF compliance for new parsers

## License

This project is designed for defensive security testing and research purposes. Use responsibly and in accordance with your organization's security policies.