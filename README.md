# Security Event Generation and Parsing Project

A comprehensive toolkit for generating synthetic security log events and parsing configurations for 100+ security products and platforms.

## Overview

This project provides two main components:

1. **event_python_writer/**: Python generators that create realistic synthetic security log events for various vendors (AWS, Cisco, Microsoft, etc.)
2. **parsers/community/**: JSON-based log parser configurations for various security products

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
# Run a specific generator
python event_python_writer/<vendor>_<product>.py

# Send logs to SentinelOne AI SIEM via HEC
python event_python_writer/hec_sender.py --product <product_name> --count <number>

# Generate a quick attack scenario
python event_python_writer/quick_scenario.py

# Generate a full 14-day APT campaign
python event_python_writer/attack_scenario_orchestrator.py
```

## Available Event Generators (100+ Total)

### Cloud & Infrastructure  
- `abnormal_security`: Abnormal Security email security events
- `apache_http`: Apache HTTP server access logs
- `aws_cloudtrail`: AWS CloudTrail events
- `aws_elb`: AWS Elastic Load Balancer logs
- `aws_guardduty`: AWS GuardDuty findings
- `aws_route53`: AWS Route 53 DNS query logs
- `aws_vpc_dns`: AWS VPC DNS query logs
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
- `cisco_meraki`: Cisco Meraki logs
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
- `cyberark_conjur`: CyberArk Conjur secrets management audit events
- `cyberark_pas`: CyberArk Privileged Access Security events
- `hashicorp_vault`: HashiCorp Vault secrets management events
- `securelink`: SecureLink privileged remote access events

### SIEM & Analytics
- `darktrace`: Darktrace AI-powered threat detection events
- `extrahop`: ExtraHop network detection and response events
- `manch_siem`: Manchester SIEM security events and alerts
- `vectra_ai`: Vectra AI network detection and response events

### IT Management & Data Protection
- `axway_sftp`: Axway SFTP file transfer and audit logs
- `cohesity_backup`: Cohesity data management and backup logs
- `github_audit`: GitHub repository and organization audit logs
- `manageengine_general`: ManageEngine IT management and security events
- `microsoft_365_mgmt_api`: Microsoft 365 Management API events
- `sap`: SAP ERP, HANA, and security audit events
- `veeam_backup`: Veeam backup and recovery operations logs
- `wiz_cloud`: Wiz cloud security posture and compliance events

### DevOps & CI/CD
- `buildkite`: Buildkite CI/CD audit and pipeline events
- `harness_ci`: Harness CI/CD pipeline and deployment logs
- `teleport`: Teleport access proxy events (SSH, database, Kubernetes)

### Network Access & VPN
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

## Detection Rules

⚠️ **Note**: The detection rules in `detections.conf` are currently being reworked and are not yet ready for production use.

The repository will include comprehensive detection rules:
- **Coverage**: 30+ detection rules across all attack phases  
- **Platforms**: SentinelOne, CrowdStrike, Microsoft, Darktrace, and other security vendors
- **Correlation**: Cross-platform correlation rules for campaign-wide detection

## Architecture

### Event Generators
- Each generator is self-contained (<200 lines)
- Uses only Python standard library (except `hec_sender.py` which requires `requests`)
- Returns structured JSON events
- Includes AI-SIEM specific attributes for parser compatibility

### Parser Structure
Each parser directory contains:
- JSON or config file with parsing rules
- `metadata.yaml` with parser metadata
- Parser naming convention: `<vendor>_<product>_<description>-latest/`

### Key Patterns
1. Generators follow naming convention: `<vendor>_<product>.py`
2. Each generator exports a `<product>_log()` function
3. `hec_sender.py` maps products to their respective generators
4. Parsers use JSON schema definitions for field mapping

## Environment Variables

```bash
export S1_HEC_URL="https://ingest.us1.sentinelone.net/services/collector/raw"
export HEC_TOKEN="your-hec-token-here"
```

## File Structure

```
├── README.md                              # This file
├── CLAUDE.md                              # Development guidance  
├── detections.conf                        # SentinelOne detection rules
├── event_python_writer/                  # Event generators & testing tools
│   ├── hec_sender.py                     # HEC client for sending events
│   ├── attack_scenario_orchestrator.py   # APT campaign generator
│   ├── scenario_hec_sender.py            # Scenario event sender
│   ├── quick_scenario.py                 # Quick scenario generator
│   ├── s1_dv_api_client.py               # SentinelOne Data Visibility API client
│   ├── comprehensive_parser_tester.py    # End-to-end parser testing framework
│   ├── s1_config_setup.py                # Service account configuration tool
│   ├── SERVICE_ACCOUNT_SETUP.md          # Service account setup guide
│   ├── quick_parser_test.py              # Quick parser validation (offline)
│   └── [vendor]_[product].py             # Individual event generators (100+ total)
└── parsers/community/                    # Log parser configurations
    └── [vendor]_[product]_[description]-latest/  # Parser definitions (100+ total)
```

## Development

### Recently Added (35 New Parsers)
This project was recently expanded with 35 new OCSF-compliant parsers:
- **First batch**: 10 parsers (AWS WAF, Route53, Cisco IronPort, CyberArk Conjur, IIS W3C, Linux Auth, Microsoft 365 Collaboration/Defender, PingFederate, Zscaler DNS Firewall)
- **Second batch**: 20 parsers (All Akamai products, Axway SFTP, Cisco Duo, Cohesity, F5 VPN, GitHub Audit, Harness CI, HYPR Auth, Imperva Sonar, ISC BIND/DHCP, Jamf Protect, Ping MFA/Protect, RSA Adaptive, Veeam, Wiz Cloud)
- **Converted from legacy formats**: 5 parsers (Cisco FMC, IOS, ISA3000, Meraki Flow, Palo Alto Prisma SASE)

### Parser Features
- **OCSF 1.1.0 Compliance**: All parsers follow Open Cybersecurity Schema Framework standards
- **JSON Format**: Modern JSON-based configuration replacing legacy .conf and .docx formats
- **Field Mapping**: Comprehensive field mapping to OCSF schema with proper class_uid, activity_id mappings
- **Observables Extraction**: Automatic extraction of IP addresses, usernames, and other entities for correlation
- **Status and Severity Mapping**: Intelligent mapping of vendor-specific status/severity to standardized values

### Adding New Generators
1. Create new generator following naming convention
2. Implement `<product>_log()` function returning JSON
3. Add to `PROD_MAP` in `hec_sender.py`
4. Add sourcetype mapping to `SOURCETYPE_MAP`
5. Add to `JSON_PRODUCTS` set if generating JSON
6. Update documentation

## SentinelOne API Integration & Parser Testing

### Service Account Setup
Set up automated parser testing with SentinelOne service account authentication:

```bash
# Set up service account configuration
python event_python_writer/s1_config_setup.py --service-account

# Validate service account permissions
python event_python_writer/s1_config_setup.py --validate-service-account

# Test basic connectivity
python event_python_writer/s1_dv_api_client.py --test-connection
```

### End-to-End Parser Testing
Test parser effectiveness by sending events and validating field extraction:

```bash
# Test recently fixed parsers with comprehensive validation
python event_python_writer/comprehensive_parser_tester.py --fixed

# Test specific parser groups
python event_python_writer/comprehensive_parser_tester.py --ping
python event_python_writer/comprehensive_parser_tester.py --cisco
python event_python_writer/comprehensive_parser_tester.py --aws

# Test individual parser with custom parameters
python event_python_writer/comprehensive_parser_tester.py --parser pingfederate --count 5 --wait 90

# Validate parser configuration only (no API calls)
python event_python_writer/comprehensive_parser_tester.py --validate pingfederate
```

### Parser Testing Features
- **End-to-End Validation**: Send events via HEC → Query Data Visibility → Validate parsing
- **Service Account Authentication**: Secure automated testing with minimal required permissions
- **OCSF Compliance**: Verify parsed events follow Open Cybersecurity Schema Framework standards
- **Field Coverage Analysis**: Identify missing, optional, and unexpected fields
- **Comprehensive Reporting**: Generate detailed test reports with actionable insights

### Testing Environment Variables
```bash
# SentinelOne Service Account Configuration
export S1_API_URL="https://your-instance.sentinelone.net"
export S1_API_TOKEN="your-service-account-api-token"
export S1_HEC_TOKEN="your-hec-token"
export S1_SERVICE_USER_ID="service-user-id-optional"
export S1_ACCOUNT_ID="account-id-optional"
export S1_SITE_ID="site-id-optional"
```

### Legacy Testing (Without API Integration)
```bash
# Basic generator testing
python event_python_writer/your_generator.py

# Test via HEC sender only
python event_python_writer/hec_sender.py --product your_product --count 5

# Quick parser validation
python event_python_writer/quick_parser_test.py
```

## Contributing

1. Follow existing generator patterns
2. Include realistic field values and attack indicators
3. Add comprehensive event metadata
4. Test generators thoroughly
5. Update documentation

## License

This project is designed for defensive security testing and research purposes. Use responsibly and in accordance with your organization's security policies.