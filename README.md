# Security Event Generator & Parser Repository
_Comprehensive synthetic security event generation and parsing for SIEM testing and security research_

---

## Overview

This repository provides a complete security event generation and parsing ecosystem, featuring:

- **42 Security Event Generators**: Lightweight Python generators for realistic security logs
- **50+ Community Parsers**: OCSF-compatible parsers for major security platforms  
- **Advanced Attack Scenarios**: Multi-day APT campaign simulation tools
- **HEC Integration**: Direct integration with SentinelOne AI-SIEM and Splunk HEC

Each generator is <150 lines, uses only Python standard library (except requests), and produces realistic but synthetic security events perfect for testing, training, and development.

---

## 🚀 Quick Start

### Setup
```bash
cd event_python_writer

# Set your HEC token (required for sending events)
export S1_HEC_TOKEN=your-token-here
```

### Generate and Send Events
```bash
# Send CrowdStrike events
python hec_sender.py --product crowdstrike_falcon -n 10 --min-delay 0.05 --max-delay 0.3

# Send Vectra AI detections  
python hec_sender.py --product vectra_ai -n 5 --min-delay 0.05 --max-delay 0.3

# Send network flow logs
python hec_sender.py --product corelight_conn -n 20 --min-delay 0.05 --max-delay 0.3

# Send Armis IoT security events
python hec_sender.py --product armis -n 15 --min-delay 0.05 --max-delay 0.3

# Available products: fortinet_fortigate, crowdstrike_falcon, vectra_ai, 
# tailscale, corelight_conn, corelight_http, corelight_ssl, corelight_tunnel,
# armis, extrahop, aws_elb, darktrace, proofpoint, mimecast, and many more...
```

### Test Individual Generators (without sending)
```bash
# Preview events before sending
python -c "from crowdstrike_falcon import crowdstrike_log; print(crowdstrike_log())"

# Generate with specific values
python -c "from proofpoint import proofpoint_log; print(proofpoint_log({'threatType': 'phish'}))"
```

### Generate Attack Scenarios
```bash
# Quick focused scenarios (30 minutes - 2 hours)
python quick_scenario.py

# Full APT campaign (14-day simulation)  
python attack_scenario_orchestrator.py

# Send scenario to HEC
python scenario_hec_sender.py
```

---

## 📊 Security Event Generators

### Network Security & Monitoring
| Generator | Product | Focus | Events Generated |
|-----------|---------|-------|------------------|
| `corelight_conn.py` | Corelight/Zeek | Network connections | TCP/UDP flows, connection states, protocols |
| `corelight_http.py` | Corelight/Zeek | HTTP activity | Web requests, responses, user agents, URIs |
| `corelight_ssl.py` | Corelight/Zeek | SSL/TLS connections | Certificate details, cipher suites, handshakes |
| `corelight_tunnel.py` | Corelight/Zeek | VPN/Tunnels | VXLAN, GRE, ESP, L2TP tunnel activities |
| `darktrace.py` | Darktrace | AI threat detection | Anomaly detection, threat scoring, device behavior |
| `extrahop.py` | ExtraHop Reveal(x) | Network analysis | Security detections, MITRE ATT&CK mapping |

### Identity & Access Management  
| Generator | Product | Focus | Events Generated |
|-----------|---------|-------|------------------|
| `microsoft_azure_ad_signin.py` | Microsoft Azure AD | Authentication | Sign-ins, MFA, conditional access, risk events |
| `microsoft_azuread.py` | Microsoft Azure AD | Directory changes | User/group management, role assignments |
| `okta_authentication.py` | Okta | Identity management | SSO, user lifecycle, policy evaluation |
| `cyberark_pas.py` | CyberArk PAS | Privileged access | Account checkouts, session monitoring |
| `beyondtrust_passwordsafe.py` | BeyondTrust Password Safe | Password management | Credential access, policy enforcement |
| `beyondtrust_privilegemgmt_windows.py` | BeyondTrust EPM | Endpoint privilege mgmt | Application elevation, privilege monitoring |
| `manageengine_ad_audit_plus.py` | ManageEngine ADAuditPlus | AD auditing | Directory changes, logon events, policy changes |
| `hashicorp_vault.py` | HashiCorp Vault | Secrets management | Secret access, authentication, audit trails |

### Endpoint & Device Security
| Generator | Product | Focus | Events Generated |
|-----------|---------|-------|------------------|
| `crowdstrike_falcon.py` | CrowdStrike Falcon | Endpoint detection | Malware, process monitoring, threat hunting |
| `armis.py` | Armis | IoT/Device security | Device discovery, risk scoring, vulnerabilities |
| `vectra_ai.py` | Vectra AI | AI-driven detection | Account/host scoring, behavioral analysis |

### Email & Communication Security
| Generator | Product | Focus | Events Generated |
|-----------|---------|-------|------------------|
| `proofpoint.py` | Proofpoint | Email security | Phishing, malware, email threats |
| `mimecast.py` | Mimecast | Email security | Message filtering, threat detection |
| `microsoft_defender_email.py` | Microsoft Defender | Email protection | Advanced threat protection, safe attachments |

### Cloud & Infrastructure Security
| Generator | Product | Focus | Events Generated |
|-----------|---------|-------|------------------|
| `aws_cloudtrail.py` | AWS CloudTrail | API auditing | AWS API calls, resource changes |
| `aws_guardduty.py` | AWS GuardDuty | Threat detection | Malicious IPs, crypto mining, data exfiltration |
| `aws_elb.py` | AWS ELB | Load balancer logs | HTTP requests, SSL connections, performance |
| `aws_vpcflowlogs.py` | AWS VPC | Network flows | Network traffic, protocols, bandwidth |
| `netskope.py` | Netskope | Cloud security | SaaS usage, DLP, threat protection |
| `microsoft_365_mgmt_api.py` | Microsoft 365 | Cloud collaboration | SharePoint, Teams, Exchange activities |
| `tailscale.py` | Tailscale | Zero-trust networking | VPN connections, access policies, device management |

### Network Infrastructure
| Generator | Product | Focus | Events Generated |
|-----------|---------|-------|------------------|
| `fortinet_fortigate.py` | Fortinet FortiGate | Firewall | Traffic logs, VPN, virus detection, web filtering |
| `forcepoint_firewall.py` | ForcePoint NGFW | Next-gen firewall | Traffic inspection, threat detection, policy enforcement |
| `cisco_asa.py` | Cisco ASA | Firewall | Connection logs, VPN sessions, threat detection |
| `cisco_meraki.py` | Cisco Meraki | Wireless/SD-WAN | WiFi access, network health, security events |
| `cisco_umbrella.py` | Cisco Umbrella | DNS security | DNS queries, threat intelligence, web filtering |
| `checkpoint.py` | Check Point | Firewall | Security policies, threat prevention, VPN |
| `paloalto_firewall.py` | Palo Alto Networks | Next-gen firewall | Application control, URL filtering, threat detection |
| `apache_http.py` | Apache HTTP Server | Web server | Access logs, error logs, HTTP transactions |
| `windows_dhcp.py` | Windows DHCP Server | Network services | IP assignments, lease operations, DNS updates |
| `zscaler.py` | Zscaler | Cloud proxy | Web traffic, threat protection, data loss prevention |

---

## 🎭 Attack Scenario Generation

### Scenario Types

#### 1. Quick Scenarios (`quick_scenario.py`)
Perfect for testing and demonstrations:
- **Phishing Attack**: Email → compromise → lateral movement (30 min)
- **Insider Threat**: Privileged user data exfiltration (60 min)  
- **Malware Outbreak**: Multi-endpoint infection (45 min)
- **Credential Stuffing**: Automated login attacks (20 min)
- **Data Breach**: Complete attack chain (120 min)

#### 2. APT Campaign (`attack_scenario_orchestrator.py`)
Full 14-day "Operation Digital Heist" simulation:
- **Days 1-2**: Reconnaissance & phishing
- **Days 3-4**: Initial access & credential harvesting  
- **Days 5-8**: Persistence & lateral movement
- **Days 9-11**: Privilege escalation & discovery
- **Days 12-14**: Data exfiltration & cover-up

#### 3. Retroactive Scenarios
Generate historical data that leads up to "now":
```bash
# Campaign that started 14 days ago and concludes today
python attack_scenario_orchestrator.py
# Answer "y" to retroactive mode

# Quick scenario from 2 hours ago to now  
python quick_scenario.py
# Answer "y" to retroactive mode
```

### Scenario Features
- **Correlated Events**: Activities span multiple security platforms
- **Realistic Timing**: Events distributed naturally over time
- **Progressive Escalation**: Attack complexity increases over time
- **MITRE ATT&CK Alignment**: Tactics and techniques map to MITRE framework
- **Customizable Parameters**: Adjust duration, intensity, and scope

---

## 🔗 HEC Integration

### Direct Event Transmission
```bash
# Send individual product events
python hec_sender.py --product vectra_ai -n 50

# Send with custom timing
python hec_sender.py --product armis -n 100 --min-delay 1.0 --max-delay 5.0
```

### Scenario Transmission
```bash
# Generate and send scenario
python quick_scenario.py
# Select scenario → Save to file → Send to HEC

# Send pre-generated scenario file  
python scenario_hec_sender.py
# Choose file → Configure timing → Transmit
```

### Configuration
```bash
# Required: HEC token
export S1_HEC_TOKEN=your-hec-token

# Optional: Custom endpoints
export S1_HEC_RAW_URL_BASE=https://your-instance.sentinelone.net/services/collector/raw
export S1_HEC_EVENT_URL_BASE=https://your-instance.sentinelone.net/services/collector/event
```

---

## 🗂️ Community Parsers

Located in `parsers/community/`, includes OCSF-compatible parsers for:

### Security Platforms (29 with generators)
- **Network**: Corelight, Darktrace, ExtraHop, Tailscale
- **Endpoint**: CrowdStrike, Armis, Vectra AI  
- **Identity**: Azure AD, Okta, CyberArk, BeyondTrust
- **Cloud**: AWS (CloudTrail, GuardDuty, ELB, VPC), Microsoft 365, Netskope
- **Email**: Proofpoint, Mimecast, Microsoft Defender
- **Infrastructure**: FortiGate, Cisco ASA/Meraki/Umbrella, Zscaler

### Additional Parsers (21 without generators)
- Apache HTTP, Checkpoint, VMware vCenter, Windows EventLog
- Palo Alto (multiple variants), Aruba ClearPass, ManageEngine AD Audit Plus
- Industrial/IoT platforms and specialized security tools

---

## 🛠️ Development & Customization

### Generator Template
Each generator follows this pattern:
```python
def product_log(overrides: dict | None = None) -> str:
    """Return a single product event as JSON string."""
    # Generate realistic event data
    event = {...}
    
    # Apply overrides for testing
    if overrides:
        event.update(overrides)
    
    return json.dumps(event, separators=(",", ":"))

# ATTR_FIELDS for HEC integration
ATTR_FIELDS = {
    "dataSource.vendor": "Vendor Name",
    "dataSource.name": "Product Name", 
    "dataSource.category": "security"
}
```

### Adding New Generators
1. Create generator file in `event_python_writer/`
2. Add to `PROD_MAP` in `hec_sender.py`
3. Update `SOURCETYPE_MAP` and `JSON_PRODUCTS`
4. Add to argument parser choices

### Customizing Events
```python
# Force specific values
crowdstrike_log({"Severity": 10, "ThreatFamily": "Emotet"})

# Generate malicious events  
proofpoint_log({"threatType": "phish", "subject": "Urgent: Security Alert"})

# Create specific scenarios
vectra_ai_log({"category": "account", "threat": 95, "certainty": 90})
```

---

## 📈 Use Cases

### Security Operations
- **SIEM Testing**: Load test detection rules and dashboards
- **Analyst Training**: Realistic scenarios for training exercises  
- **Detection Engineering**: Test new detection logic
- **Incident Response**: Practice with known attack patterns

### Development & Testing
- **Parser Development**: Test OCSF mapping and field extraction
- **Pipeline Testing**: Validate data processing workflows
- **Performance Testing**: Generate load for capacity planning
- **Integration Testing**: End-to-end security stack validation

### Research & Education
- **Security Research**: Generate datasets for analysis
- **Student Labs**: Hands-on cybersecurity education
- **Vendor Demos**: Showcase security products with realistic data
- **Compliance Testing**: Validate security controls and monitoring

---

## 🔒 Security Considerations

- **Synthetic Data Only**: All events are fabricated - no real security data
- **Non-Malicious**: Generators create logs, not actual security threats
- **Safe Testing**: Isolated environment recommended for scenario testing
- **Rate Limiting**: Built-in delays prevent overwhelming target systems
- **Audit Trails**: All generated events include scenario context for tracking

---

## 📝 Requirements

- **Python 3.8+** (uses modern type hints and f-strings)
- **Standard Library Only** (except `requests` for HEC integration)
- **Minimal Dependencies**: `requirements.txt` includes only `requests`
- **Cross-Platform**: Works on Windows, macOS, and Linux

---

## 🤝 Contributing

1. **New Generators**: Follow the established pattern and add ATTR_FIELDS
2. **Parser Updates**: Maintain OCSF compatibility
3. **Scenario Enhancement**: Add new attack patterns and techniques
4. **Documentation**: Update README for new features

---

## 📄 License

Open source - designed for security community collaboration and education.

---

## 🔍 Additional Resources

- **CLAUDE.md**: Detailed technical documentation for developers
- **Parser Documentation**: See individual parser metadata.yaml files
- **OCSF Schema**: [Open Cybersecurity Schema Framework](https://schema.ocsf.io/)
- **MITRE ATT&CK**: [Enterprise Matrix](https://attack.mitre.org/)

---

*Generate realistic security events, test your defenses, train your team - all without compromising real data or systems.*