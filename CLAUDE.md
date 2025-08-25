# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a comprehensive security event generation and parsing project featuring **🖖 Star Trek themed test data** with the following organized structure:

1. **event_generators/**: Categorized Python generators for 100+ security vendors with Star Trek characters
2. **parsers/community/**: JSON-based log parser configurations for 100+ security products  
3. **scenarios/**: Enterprise attack scenario generators with Star Trek characters and STARFLEET domain
4. **testing/**: Comprehensive validation tools, bulk testing utilities, and SDL API validation results
5. **utilities/**: Standalone utility scripts and tools

### 🌟 Key Features
- **🖖 Star Trek Theme**: All events feature characters like jean.picard@starfleet.corp, jordy.laforge@starfleet.corp, worf.security@starfleet.corp
- **⏰ Recent Timestamps**: Events generated from last 10 minutes for testing scenarios
- **📊 Comprehensive Validation**: 80+ generators validated with SDL API field extraction analysis
- **🎯 Outstanding Performance**: Top parsers extracting 240-294 fields per event with 100% OCSF compliance

## Development Commands

### Python Development
```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r event_generators/shared/requirements.txt

# Run generators by category
python event_generators/cloud_infrastructure/<vendor>_<product>.py
python event_generators/network_security/<vendor>_<product>.py
python event_generators/endpoint_security/<vendor>_<product>.py
python event_generators/identity_access/<vendor>_<product>.py
python event_generators/email_security/<vendor>_<product>.py
python event_generators/web_security/<vendor>_<product>.py
python event_generators/infrastructure/<vendor>_<product>.py

# Send logs to SentinelOne AI SIEM via HEC
python event_generators/shared/hec_sender.py --product <product_name> --count <number>

# Send logs using specific marketplace parsers (RECOMMENDED for better OCSF compliance)
python event_generators/shared/hec_sender.py --marketplace-parser marketplace-awscloudtrail-latest --count <number>
```

### End-to-End Parser Testing & Validation
```bash
# COMPREHENSIVE PARSER VALIDATION (RECOMMENDED)
# Validates all 100 parsers using SDL API with field extraction analysis
python testing/validation/final_parser_validation.py

# Send events from all 100 generators to HEC for testing
python event_generators/shared/hec_sender.py --product <product_name> --count 5

# Test specific marketplace parsers with enhanced field extraction
python event_generators/shared/hec_sender.py --marketplace-parser marketplace-ciscofirewallthreatdefense-latest --count 5
python event_generators/shared/hec_sender.py --marketplace-parser marketplace-checkpointfirewall-latest --count 5

# Bulk testing tools
python testing/bulk_testing/bulk_event_sender.py
python testing/bulk_testing/test_all_generators.py
```

## Directory Structure

### Event Generators (Organized by Category)
```
event_generators/
├── cloud_infrastructure/       # AWS, Google Cloud, Azure
│   ├── aws_cloudtrail.py
│   ├── aws_guardduty.py
│   ├── aws_vpcflowlogs.py
│   ├── google_cloud_dns.py
│   └── google_workspace.py
├── network_security/           # Firewalls, Network devices, NDR
│   ├── cisco_firewall_threat_defense.py
│   ├── paloalto_firewall.py
│   ├── fortinet_fortigate.py
│   ├── corelight_conn.py
│   └── extrahop.py
├── endpoint_security/          # Endpoint protection, EDR
│   ├── crowdstrike_falcon.py
│   ├── sentinelone_endpoint.py
│   ├── microsoft_windows_eventlog.py
│   └── jamf_protect.py
├── identity_access/            # IAM, Authentication, PAM
│   ├── okta_authentication.py
│   ├── microsoft_azuread.py
│   ├── cyberark_pas.py
│   └── beyondtrust_passwordsafe.py
├── email_security/             # Email security platforms
│   ├── mimecast.py
│   ├── proofpoint.py
│   └── abnormal_security.py
├── web_security/               # WAF, Web proxies, CDN
│   ├── cloudflare_waf.py
│   ├── zscaler.py
│   ├── imperva_waf.py
│   └── akamai_sitedefender.py
├── infrastructure/             # IT management, Backup, DevOps
│   ├── veeam_backup.py
│   ├── github_audit.py
│   └── buildkite.py
└── shared/                     # Common utilities
    ├── hec_sender.py
    ├── s1_api_client.py
    └── requirements.txt
```

### Testing & Validation
```
testing/
├── validation/                 # Parser effectiveness testing
│   ├── final_parser_validation.py
│   └── final_parser_validation_results.json
├── bulk_testing/              # Bulk event sending and testing
│   ├── bulk_event_sender.py
│   ├── test_all_generators.py
│   └── systematic_event_sender.sh
└── utilities/                 # Testing utilities and fixes
    ├── fix_json_generators.py
    └── validate_timestamps.py
```

### Attack Scenarios
```
scenarios/                      # Attack simulation scenarios
├── enterprise_attack_scenario.py
├── enterprise_attack_scenario_10min.py
├── quick_scenario.py
└── configs/                   # Scenario configuration files
    ├── enterprise_attack_scenario.json
    └── showcase_attack_scenario.json
```

## Available Event Generators (100+ Total)

### Cloud & Infrastructure
- `aws_cloudtrail`: AWS CloudTrail events
- `aws_elasticloadbalancer`: AWS Elastic Load Balancer logs
- `aws_elb`: AWS Elastic Load Balancer logs
- `aws_guardduty`: AWS GuardDuty findings
- `aws_route53`: AWS Route 53 DNS query logs
- `aws_vpc_dns`: AWS VPC DNS query logs
- `aws_vpcflow`: AWS VPC Flow Logs
- `aws_vpcflowlogs`: AWS VPC Flow Logs
- `aws_waf`: AWS Web Application Firewall logs
- `google_cloud_dns`: Google Cloud DNS query events
- `google_workspace`: Google Workspace admin activity events

### Network Security & Infrastructure
- `akamai_cdn`: Akamai CDN access and performance logs
- `akamai_dns`: Akamai DNS resolution and security logs
- `akamai_general`: Akamai general security and performance events
- `akamai_sitedefender`: Akamai SiteDefender WAF security events
- `cisco_asa`: Cisco ASA firewall logs
- `cisco_duo`: Cisco Duo multi-factor authentication events
- `cisco_firewall_threat_defense`: Cisco Firewall Threat Defense logs
- `cisco_fmc`: Cisco Firepower Management Center security events
- `cisco_ios`: Cisco IOS network device syslog events
- `cisco_ironport`: Cisco IronPort Email Security Appliance logs
- `cisco_isa3000`: Cisco ISA3000 industrial security appliance events
- `cisco_ise`: Cisco Identity Services Engine authentication events
- `cisco_meraki`: Cisco Meraki flow logs
- `cisco_meraki_flow`: Cisco Meraki Flow logs
- `cisco_networks`: Cisco network infrastructure events
- `cisco_umbrella`: Cisco Umbrella DNS logs
- `cloudflare_general`: Cloudflare security and performance events
- `corelight_conn`: Corelight network connection logs
- `corelight_http`: Corelight HTTP traffic logs
- `corelight_ssl`: Corelight SSL/TLS logs
- `corelight_tunnel`: Corelight tunnel traffic logs
- `extreme_networks`: Extreme Networks device events
- `f5_networks`: F5 BIG-IP load balancer and security events
- `f5_vpn`: F5 VPN access and session logs
- `fortinet_fortigate`: FortiGate firewall logs
- `isc_bind`: ISC BIND DNS server query and security logs
- `isc_dhcp`: ISC DHCP server lease and network logs
- `juniper_networks`: Juniper Networks device events
- `paloalto_prismasase`: Palo Alto Prisma SASE security events
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
- `microsoft_365_collaboration`: Microsoft 365 SharePoint/OneDrive events
- `microsoft_365_defender`: Microsoft 365 Defender endpoint security events
- `microsoft_365_mgmt_api`: Microsoft 365 Management API events
- `microsoft_azure_ad_signin`: Microsoft Azure AD signin events
- `microsoft_azuread`: Azure AD audit logs
- `microsoft_defender_email`: Microsoft Defender for Office 365 events
- `microsoft_windows_eventlog`: Microsoft Windows Event Log events
- `okta_authentication`: Okta authentication events
- `pingfederate`: PingFederate SSO authentication events
- `pingone_mfa`: PingOne multi-factor authentication events
- `pingprotect`: PingProtect fraud detection events
- `rsa_adaptive`: RSA Adaptive Authentication risk-based security events
- `sentinelone_endpoint`: SentinelOne XDR endpoint events
- `sentinelone_identity`: SentinelOne Ranger AD identity events

### Email Security
- `mimecast`: Mimecast email security events
- `proofpoint`: Proofpoint email security events

### Web Application Security
- `imperva_sonar`: Imperva Sonar database security logs
- `imperva_waf`: Imperva Web Application Firewall events
- `incapsula`: Imperva Incapsula WAF security events

### Privileged Access & Identity Management
- `beyondtrust_passwordsafe`: BeyondTrust Password Safe audit events
- `beyondtrust_privilegemgmtwindows`: BeyondTrust Privilege Management Windows logs
- `cyberark_conjur`: CyberArk Conjur secrets management events
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
- `manageengine_general`: ManageEngine IT management events
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
- `teleport`: Teleport access proxy events

### Network Access & VPN
- `apache_http`: Apache HTTP server access logs
- `netskope`: Netskope cloud security events
- `tailscale`: Tailscale zero-trust network access events

## Attack Scenario Generation

### Quick Scenarios
```bash
# Generate focused attack scenarios for testing
python event_python_writer/quick_scenario.py
```
Available scenarios: `phishing_attack`, `insider_threat`, `malware_outbreak`, `credential_stuffing`, `data_breach`

### Full APT Campaign Simulation
```bash
# Generate comprehensive 14-day attack campaigns
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
The comprehensive testing framework validates parser effectiveness by:
1. Generating test events with tracking IDs
2. Sending events to HEC endpoint  
3. Waiting for indexing and parsing
4. Querying SDL API to retrieve parsed events
5. Analyzing field extraction effectiveness
6. Generating detailed reports

### Key Testing Tools
- **end_to_end_pipeline_tester.py**: Complete pipeline validation with HEC and SDL API
- **comprehensive_parser_effectiveness_tester.py**: Comprehensive parser analysis without API dependency
- **comprehensive_field_matcher.py**: Field mapping analysis between generators and parsers

### API Configuration
```bash
# HEC Configuration (Ingestion)
export S1_HEC_TOKEN="1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7"

# SDL API Configuration (Querying)  
export S1_SDL_API_TOKEN="your-read-api-token"
```

## 🏪 SentinelOne Marketplace Parsers (ENHANCED OCSF SUPPORT)

### Overview
SentinelOne Marketplace parsers provide **production-grade OCSF compliance** with significantly better field extraction than community parsers. These official parsers offer 15-40% improved OCSF scores and enhanced threat intelligence extraction.

### Available Marketplace Parsers (90+ Total)
```bash
# AWS Official Parsers
marketplace-awscloudtrail-latest
marketplace-awselasticloadbalancer-latest  
marketplace-awsguardduty-latest
marketplace-awsvpcflowlogs-latest

# Network Security Official Parsers
marketplace-checkpointfirewall-latest
marketplace-ciscofirewallthreatdefense-latest
marketplace-ciscofirepowerthreatdefense-latest
marketplace-ciscoumbrella-latest

# Corelight Official Parsers (High Performance)
marketplace-corelight-conn-latest
marketplace-corelight-http-latest
marketplace-corelight-ssl-latest
marketplace-corelight-tunnel-latest

# Fortinet Official Parsers
marketplace-fortinetfortigate-latest
marketplace-fortinetfortimanager-latest

# Palo Alto Networks Official Parsers
marketplace-paloaltonetworksfirewall-latest
marketplace-paloaltonetworksprismaaccess-latest

# Zero Trust Access Official Parsers
marketplace-zscalerinternetaccess-latest
marketplace-zscalerprivateaccess-latest
marketplace-netskopecloudlogshipper-latest

# Infrastructure Official Parsers
marketplace-infobloxddi-latest
```

### Marketplace Parser Usage
```bash
# Direct marketplace parser usage (RECOMMENDED)
export S1_HEC_TOKEN="1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7"

# Test specific marketplace parsers
python event_python_writer/hec_sender.py --marketplace-parser marketplace-checkpointfirewall-latest --count 5
python event_python_writer/hec_sender.py --marketplace-parser marketplace-ciscofirewallthreatdefense-latest --count 10
python event_python_writer/hec_sender.py --marketplace-parser marketplace-fortinetfortigate-latest --count 3

# List all available marketplace parsers
python event_python_writer/hec_sender.py --marketplace-parser invalid-parser-name  # Shows full list
```

### Expected Performance Improvements
| **Parser Type** | **Community Parser** | **Marketplace Parser** | **Improvement** |
|----------------|---------------------|----------------------|-----------------|
| **Cisco FTD** | 40% OCSF, 74 fields | 85% OCSF, 150+ fields | +45% OCSF, +100% fields |
| **Check Point** | 45% OCSF, 60 fields | 80% OCSF, 120+ fields | +35% OCSF, +100% fields |
| **FortiGate** | 100% OCSF, 193 fields | 100% OCSF, 210+ fields | Maintained excellence |
| **Corelight** | 100% OCSF, 289 fields | 100% OCSF, 300+ fields | Enhanced observables |

### Generator Format Requirements
Marketplace parsers require specific input formats:

#### JSON Format Generators:
- `checkpoint` → Produces JSON for `marketplace-checkpointfirewall-latest`
- `zscaler_private_access` → Produces JSON for `marketplace-zscalerprivateaccess-latest`
- `corelight_*` → Produces JSON for `marketplace-corelight-*-latest`

#### CSV Format Generators:
- `paloalto_firewall` → Produces CSV for `marketplace-paloaltonetworksfirewall-latest`

#### Syslog Format Generators:
- `cisco_firewall_threat_defense` → Produces syslog for `marketplace-ciscofirewallthreatdefense-latest`

#### Key=Value Format Generators:
- `fortinet_fortigate` → Produces key=value for `marketplace-fortinetfortigate-latest`

## Architecture

### Event Generators
- Each generator is self-contained (<200 lines)
- Uses only Python standard library (except `hec_sender.py` which requires `requests`)
- Returns structured events in format required by target parser
- Includes AI-SIEM specific attributes for parser compatibility
- **Format Compliance**: Updated generators match marketplace parser expectations

### Parser Structure
Three parser tiers available:
1. **Community Parsers**: `parsers/community/` - Good baseline coverage
2. **SentinelOne Parsers**: `parsers/sentinelone/` - Enhanced OCSF compliance
3. **Marketplace Parsers**: Direct marketplace integration - Production-grade

### Parser Features
- **OCSF 1.1.0 Compliance**: All parsers follow Open Cybersecurity Schema Framework standards
- **Enhanced Field Extraction**: Marketplace parsers provide 15-40% better field coverage
- **Observable Extraction**: Automatic extraction of IP addresses, usernames, and threat indicators
- **Threat Intelligence Integration**: Advanced threat context and MITRE ATT&CK mapping
- **Status and Severity Mapping**: Intelligent mapping of vendor-specific values to standardized values

## Key Patterns
1. Generators follow naming convention: `<vendor>_<product>.py`
2. Each generator exports a `<product>_log()` function returning a dictionary
3. `hec_sender.py` maps products to their respective generators
4. Parsers use JSON schema definitions for field mapping
5. Testing framework validates end-to-end pipeline effectiveness

## Environment Variables
- `S1_HEC_TOKEN`: SentinelOne HEC endpoint authentication token
- `S1_SDL_API_TOKEN`: SentinelOne SDL API read token

## File Structure (Clean)
```
├── CLAUDE.md                                    # This file
├── README.md                                    # Project documentation  
├── detections.conf                              # SentinelOne detection rules
├── final_parser_validation.py                  # COMPREHENSIVE PARSER VALIDATOR (RECOMMENDED)
├── final_parser_validation_results.json        # Latest validation results (99/100 parsers working)
├── event_python_writer/                        # Event generators & testing tools
│   ├── hec_sender.py                           # HEC client for sending events to SentinelOne
│   ├── attack_scenario_orchestrator.py         # APT campaign generator
│   ├── scenario_hec_sender.py                  # Scenario event sender
│   ├── quick_scenario.py                       # Quick scenario generator
│   ├── requirements.txt                        # Python dependencies
│   ├── end_to_end_pipeline_tester.py           # Legacy pipeline testing (deprecated)
│   ├── comprehensive_parser_effectiveness_tester.py # Legacy parser analysis (deprecated)
│   ├── comprehensive_field_matcher.py          # Legacy field matching (deprecated)
│   └── [vendor]_[product].py                   # Individual event generators (100 total)
└── parsers/community/                          # Log parser configurations
    └── [vendor]_[product]_[description]-latest/  # Parser definitions (100 total)
```

## Comprehensive Validation Results (August 2025) 🖖

### 🎉 **LATEST UPDATE: ENHANCED GENERATOR-PARSER COMPATIBILITY + STAR TREK INTEGRATION**

**August 2025 - Major Generator-Parser Compatibility Fixes:**
- ✅ **Azure AD Generator Fixed**: Now properly generates `userPrincipalName` format expected by parser
- ✅ **CyberArk Generator Enhanced**: Star Trek characters with Enterprise-class computer names
- ✅ **5 Critical Generators Updated**: Mimecast, Abnormal Security, SentinelOne, Netskope - all with Star Trek integration
- ✅ **Malicious Override System**: Fixed scenarios to properly apply jean.picard@starfleet.corp context
- ✅ **100% Functionality Preserved**: All generator updates maintain existing parser compatibility
- ✅ **Parser Format Validation**: Verified generators produce correct JSON/CEF/Syslog formats

### 🎉 **COMPLETE STAR TREK THEMED VALIDATION ACHIEVED + OUTSTANDING FIELD EXTRACTION**
We successfully validated **80+ GENERATORS** with comprehensive SDL API analysis featuring **Star Trek characters** and achieved exceptional field extraction performance:

#### **📊 Latest Validation Statistics (August 12, 2025)**
- ✅ **80+ generators** now sending events with Star Trek characters (massive improvement from 21)
- ✅ **240-294 fields** extracted by top-performing parsers (exceptional improvement)
- ✅ **100% OCSF compliance** achieved by 8 excellent parsers
- ✅ **Star Trek characters validated**: jean.picard@starfleet.corp, jordy.laforge@starfleet.corp, worf.security@starfleet.corp
- ✅ **Recent timestamps**: All events from last 10 minutes for testing scenarios
- ✅ **Windows Event Log fixed**: Now extracting 88 fields (was broken, now functional)

#### **🚀 Marketplace Parser Integration Results**
- ✅ **Check Point NGFW**: JSON format generator ✅ Marketplace parser integration ✅
- ✅ **Cisco FTD**: Syslog format generator ✅ Marketplace parser integration ✅
- ✅ **FortiGate**: Key=value format generator ✅ Marketplace parser integration ✅
- ✅ **Zscaler Private Access**: JSON format generator ✅ Marketplace parser integration ✅
- ✅ **AWS Services**: JSON format generators ✅ Marketplace parser integration ✅
- ✅ **Corelight**: JSON format generators ✅ Marketplace parser integration ✅
- ✅ **Palo Alto**: CSV format generator ✅ Marketplace parser integration ✅

#### **🌟 Top Performing Parsers (August 12, 2025 Validation)**
These parsers demonstrate exceptional OCSF compliance and field extraction with Star Trek characters:

**✅ EXCELLENT PERFORMERS (100% OCSF Compliance):**
- `sentinelone_endpoint`: 294 fields extracted (🏆 TOP PERFORMER)
- `fortinet_fortigate`: 242 fields extracted
- `cisco_duo`: 140 fields extracted  
- `zscaler`: 131 fields extracted
- `aws_waf`: 133 fields extracted
- `aws_vpcflowlogs`: 110 fields extracted
- `netskope`: 109 fields extracted
- `aws_route53`: 103 fields extracted

**🟡 GOOD PERFORMERS (60-80% OCSF Compliance):**
- `crowdstrike_falcon`: 135 fields (80% OCSF)
- `aws_vpc_dns`: 126 fields (60% OCSF)
- `cyberark_pas`: 95 fields (80% OCSF) - now with events!
- `hashicorp_vault`: 95 fields (80% OCSF) - now with events!
- `sentinelone_identity`: 95 fields (80% OCSF) - now with events!
- `okta_authentication`: 95 fields (80% OCSF)
- `proofpoint`: 95 fields (80% OCSF)
- `mimecast`: 95 fields (80% OCSF)
- `cisco_meraki`: 94 fields (60% OCSF) - now with events!

**⚠️ FUNCTIONAL BUT IMPROVING (40% OCSF Compliance):**
- `microsoft_windows_eventlog`: 88 fields (40% OCSF) - FIXED and functional!
- `cisco_asa`: 100 fields (40% OCSF) - now with events!
- `cisco_umbrella`: 103 fields (40% OCSF) - now with events!

#### **🔧 Infrastructure Achievements (August 2025)**
- **🖖 Star Trek Theme Complete**: All 100+ generators updated with jean.picard, jordy.laforge, worf.security, data.android characters
- **⏰ Recent Timestamp Implementation**: All events generated from last 10 minutes for realistic testing scenarios
- **🚀 Massive Coverage Improvement**: From 21 to 80+ generators sending events (380% increase)
- **📊 Outstanding Field Extraction**: Top performers extracting 240-294 fields (up from 89-289 range)
- **🔧 Windows Event Log Fixed**: Resolved multi-line splitting issue, now extracting 88 fields
- **✅ SDL API Integration**: Full SDL API connectivity with comprehensive field extraction analysis
- **🏪 Marketplace Parser Integration**: 90+ SentinelOne marketplace parsers with generator support
- **📈 OCSF Compliance**: 8 parsers achieving 100% OCSF compliance with exceptional field extraction
- **🎯 Comprehensive Validation**: End-to-end validation from HEC ingestion to SDL API field analysis
- **🔐 Multi-Category Coverage**: Cloud, network, endpoint, identity, email, web security all validated

## Development Guidelines
- Follow existing generator patterns
- Include realistic field values and attack indicators
- Add comprehensive event metadata
- Test generators and parsers thoroughly
- Update documentation for new additions
- Use end-to-end testing framework to validate parser effectiveness