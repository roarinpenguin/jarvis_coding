# Security Event Generation and Parsing Project

A comprehensive toolkit for generating synthetic security log events and parsing configurations for 68+ security products and platforms.

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

## Available Event Generators (68 Total)

### Cloud & Infrastructure
- `abnormal_security`: Abnormal Security email security events
- `apache_http`: Apache HTTP server access logs
- `aws_cloudtrail`: AWS CloudTrail events
- `aws_elb`: AWS Elastic Load Balancer logs
- `aws_guardduty`: AWS GuardDuty findings
- `aws_vpc_dns`: AWS VPC DNS query logs
- `aws_vpcflowlogs`: AWS VPC Flow Logs
- `google_cloud_dns`: Google Cloud DNS query and audit events
- `google_workspace`: Google Workspace admin and user activity events

### Network Security & Infrastructure
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
- `extreme_networks`: Extreme Networks switch and access point events
- `f5_networks`: F5 BIG-IP load balancer and security events
- `fortinet_fortigate`: FortiGate firewall logs (multiple types)
- `juniper_networks`: Juniper Networks device events
- `paloalto_prismasase`: Palo Alto Prisma SASE security and network events
- `ubiquiti_unifi`: Ubiquiti UniFi network equipment events
- `zscaler`: Zscaler proxy logs
- `zscaler_firewall`: Zscaler firewall and security events

### Endpoint & Identity Security
- `armis`: Armis IoT device discovery and security events
- `crowdstrike_falcon`: CrowdStrike Falcon endpoint events
- `microsoft_azure_ad_signin`: Microsoft Azure AD signin events
- `microsoft_azuread`: Azure AD audit logs
- `microsoft_defender_email`: Microsoft Defender for Office 365 events
- `microsoft_windows_eventlog`: Microsoft Windows Event Log events
- `okta_authentication`: Okta authentication events
- `sentinelone_endpoint`: SentinelOne XDR endpoint events (servers, workstations, Kubernetes)
- `sentinelone_identity`: SentinelOne Ranger AD identity/authentication events

### Email Security
- `mimecast`: Mimecast email security events
- `proofpoint`: Proofpoint email security events

### Web Application Security
- `imperva_waf`: Imperva Web Application Firewall security events
- `incapsula`: Imperva Incapsula WAF security events

### Privileged Access & Identity Management
- `beyondtrust_passwordsafe`: BeyondTrust Password Safe audit events
- `cyberark_pas`: CyberArk Privileged Access Security events
- `hashicorp_vault`: HashiCorp Vault secrets management events
- `securelink`: SecureLink privileged remote access events

### SIEM & Analytics
- `darktrace`: Darktrace AI-powered threat detection events
- `extrahop`: ExtraHop network detection and response events
- `manch_siem`: Manchester SIEM security events and alerts
- `vectra_ai`: Vectra AI network detection and response events

### IT Management
- `manageengine_general`: ManageEngine IT management and security events
- `microsoft_365_mgmt_api`: Microsoft 365 Management API events
- `sap`: SAP ERP, HANA, and security audit events

### DevOps & CI/CD
- `buildkite`: Buildkite CI/CD audit and pipeline events
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

The repository includes comprehensive detection rules in `detections.conf`:
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
├── event_python_writer/                  # Event generators
│   ├── hec_sender.py                     # HEC client for sending events
│   ├── attack_scenario_orchestrator.py   # APT campaign generator
│   ├── scenario_hec_sender.py            # Scenario event sender
│   ├── quick_scenario.py                 # Quick scenario generator
│   └── [vendor]_[product].py             # Individual event generators (68 total)
└── parsers/community/                    # Log parser configurations
    └── [vendor]_[product]_[description]-latest/  # Parser definitions (68 total)
```

## Development

### Adding New Generators
1. Create new generator following naming convention
2. Implement `<product>_log()` function returning JSON
3. Add to `PROD_MAP` in `hec_sender.py`
4. Add sourcetype mapping to `SOURCETYPE_MAP`
5. Add to `JSON_PRODUCTS` set if generating JSON
6. Update documentation

### Testing Generators
```bash
# Test individual generator
python event_python_writer/your_generator.py

# Test via HEC sender
python event_python_writer/hec_sender.py --product your_product --count 5
```

## Contributing

1. Follow existing generator patterns
2. Include realistic field values and attack indicators
3. Add comprehensive event metadata
4. Test generators thoroughly
5. Update documentation

## License

This project is designed for defensive security testing and research purposes. Use responsibly and in accordance with your organization's security policies.