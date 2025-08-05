# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a security event generation and parsing project with two main components:

1. **event_python_writer/**: Python generators that create synthetic security log events for various vendors (AWS, Cisco, Microsoft, etc.)
2. **parsers/community/**: JSON-based log parser configurations for various security products

## Development Commands

### Python Development
```bash
# Create virtual environment
python -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install -r event_python_writer/requirements.txt

# Run a specific generator
python event_python_writer/<vendor>_<product>.py

# Send logs to SentinelOne AI SIEM via HEC
python event_python_writer/hec_sender.py --product <product_name> --count <number>
```

### Available Event Generators
- `abnormal_security`: Abnormal Security email security events
- `apache_http`: Apache HTTP server access logs
- `armis`: Armis IoT device discovery and security events
- `aws_cloudtrail`: AWS CloudTrail events
- `aws_elb`: AWS Elastic Load Balancer logs
- `aws_guardduty`: AWS GuardDuty findings
- `aws_vpc_dns`: AWS VPC DNS query logs
- `aws_vpcflowlogs`: AWS VPC Flow Logs
- `beyondtrust_passwordsafe`: BeyondTrust Password Safe audit events
- `buildkite`: Buildkite CI/CD audit and pipeline events
- `cisco_asa`: Cisco ASA firewall logs
- `cisco_fmc`: Cisco Firepower Management Center security events
- `cisco_ios`: Cisco IOS network device syslog events
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
- `crowdstrike_falcon`: CrowdStrike Falcon endpoint events
- `cyberark_pas`: CyberArk Privileged Access Security events
- `darktrace`: Darktrace AI-powered threat detection events
- `extrahop`: ExtraHop network detection and response events
- `extreme_networks`: Extreme Networks switch and access point events
- `f5_networks`: F5 BIG-IP load balancer and security events
- `fortinet_fortigate`: FortiGate firewall logs (multiple types)
- `google_cloud_dns`: Google Cloud DNS query and audit events
- `google_workspace`: Google Workspace admin and user activity events
- `hashicorp_vault`: HashiCorp Vault secrets management events
- `imperva_waf`: Imperva Web Application Firewall security events
- `incapsula`: Imperva Incapsula WAF security events
- `juniper_networks`: Juniper Networks device events
- `microsoft_365_mgmt_api`: Microsoft 365 Management API events
- `microsoft_azure_ad_signin`: Microsoft Azure AD signin events
- `microsoft_azuread`: Azure AD audit logs
- `microsoft_defender_email`: Microsoft Defender for Office 365 events
- `microsoft_windows_eventlog`: Microsoft Windows Event Log events
- `mimecast`: Mimecast email security events
- `manageengine_general`: ManageEngine IT management and security events
- `manch_siem`: Manchester SIEM security events and alerts
- `netskope`: Netskope cloud security events
- `okta_authentication`: Okta authentication events
- `paloalto_prismasase`: Palo Alto Prisma SASE security and network events
- `proofpoint`: Proofpoint email security events
- `sap`: SAP ERP, HANA, and security audit events
- `securelink`: SecureLink privileged remote access events
- `sentinelone_endpoint`: SentinelOne XDR endpoint events (servers, workstations, Kubernetes)
- `sentinelone_identity`: SentinelOne Ranger AD identity/authentication events
- `tailscale`: Tailscale zero-trust network access events
- `teleport`: Teleport access proxy events (SSH, database, Kubernetes)
- `ubiquiti_unifi`: Ubiquiti UniFi network equipment events
- `vectra_ai`: Vectra AI network detection and response events
- `zscaler`: Zscaler proxy logs
- `zscaler_firewall`: Zscaler firewall and security events

## Architecture

### Event Generators
- Each generator is self-contained (<150 lines)
- Uses only Python standard library (except `hec_sender.py` which requires `requests`)
- Returns flat JSON-serializable dictionaries
- Includes AI-SIEM specific attributes for parser compatibility

### Parser Structure
Each parser directory contains:
- JSON or config file with parsing rules
- `metadata.yaml` with parser metadata
- Parser naming convention: `<vendor>_<product>-<version>/`

### Key Patterns
1. Generators follow naming convention: `<vendor>_<product>.py`
2. Each generator exports a `<product>_log()` function
3. `hec_sender.py` maps products to their respective generators
4. Parsers use JSON schema definitions for field mapping

## Attack Scenario Generation

### Available Scenario Tools
1. **attack_scenario_orchestrator.py** - Full 14-day APT campaign simulation
2. **scenario_hec_sender.py** - Send scenario events to HEC with timing control
3. **quick_scenario.py** - Generate focused attack scenarios for testing

### Quick Scenario Generation
```bash
# Generate and send a quick phishing attack scenario
python event_python_writer/quick_scenario.py

# Available scenarios: phishing_attack, insider_threat, malware_outbreak, 
# credential_stuffing, data_breach
```

### Full APT Campaign Simulation
```bash
# Generate a complete 14-day attack campaign
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

The repository includes comprehensive detection rules for attack scenarios:

### Detection Configuration
- **detections.conf**: SentinelOne AI-SIEM detection rules covering all attack phases
- **Coverage**: 30+ detection rules across reconnaissance, initial access, persistence, escalation, and exfiltration phases
- **Correlation**: Cross-platform correlation rules for campaign-wide detection
- **Platforms**: Supports SentinelOne, CrowdStrike, Microsoft, Darktrace, and other security vendors

### Key Detection Categories
1. **Reconnaissance**: Phishing campaigns, brute force attempts, external reconnaissance
2. **Initial Access**: Malware execution, successful compromises, email-to-auth correlation
3. **Persistence**: Registry modifications, lateral movement, account changes
4. **Escalation**: Credential theft, privilege escalation, secrets access
5. **Exfiltration**: Large file access, outbound traffic, cloud data theft
6. **Correlation**: Campaign detection, kill chain progression, user timeline analysis

## Environment Variables
- `S1_HEC_URL`: SentinelOne HEC endpoint URL
- `HEC_TOKEN`: Authentication token for HEC endpoint

## File Structure (Clean)
```
├── CLAUDE.md                                    # This file
├── detections.conf                              # SentinelOne detection rules
├── attack_scenario_op_digital_heist_91357427.json  # Sample attack scenario
├── event_python_writer/                        # Event generators
│   ├── attack_scenario_orchestrator.py         # APT campaign generator
│   ├── scenario_hec_sender.py                  # HEC event sender
│   ├── quick_scenario.py                       # Quick scenario generator
│   ├── hec_sender.py                           # HEC client
│   ├── sentinelone_endpoint.py                 # SentinelOne endpoint events
│   ├── sentinelone_identity.py                 # SentinelOne identity events
│   ├── attack_scenario_op_digital_heist_5a6b5421.json  # Large attack scenario
│   └── [vendor]_[product].py                   # Individual event generators
└── parsers/community/                          # Log parser configurations
    └── [vendor]_[product]-latest/              # Parser definitions
```