#!/usr/bin/env python3
"""
Enterprise Attack Scenario - SentinelOne AI-SIEM Platform Showcase
===================================================================

A sophisticated multi-phase attack campaign demonstrating cross-platform correlation
across the entire enterprise security stack:

- Fortinet Fortigate (DMZ Firewalls)
- Windows Corp Servers 
- Imperva SecureSphere Audit
- AWS CloudTrail
- Okta & Azure AD Authentication
- Cisco Duo MFA
- Zscaler Web Security
- Proofpoint Email Security  
- CrowdStrike Endpoint Detection
- HashiCorp Terraform Cloud
- Harness CI/CD
- PingOne MFA & PingProtect

Attack Phases:
1. RECONNAISSANCE: External probing via Fortigate, failed MFA attempts
2. INITIAL ACCESS: Phishing via Proofpoint, credential harvesting
3. PERSISTENCE: AWS CloudTrail privilege escalation, Azure AD backdoors
4. LATERAL MOVEMENT: Windows servers, Imperva database access attempts
5. DATA EXFILTRATION: Terraform secrets, CI/CD pipeline compromise
6. EVASION: Zscaler bypass attempts, CrowdStrike detection evasion
"""

from __future__ import annotations
import json
import random
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# Import all required generators
from fortinet_fortigate import forward_log as fortinet_fortigate_log
from microsoft_windows_eventlog import microsoft_windows_eventlog_log  
from imperva_waf import imperva_waf_log
from aws_cloudtrail import cloudtrail_log
from okta_authentication import okta_authentication_log
from microsoft_azuread import azuread_log as microsoft_azuread_log
from cisco_duo import cisco_duo_log
from zscaler import zscaler_log
from proofpoint import proofpoint_log
from crowdstrike_falcon import crowdstrike_log as crowdstrike_falcon_log
from hashicorp_vault import hashicorp_vault_log
from harness_ci import harness_ci_log
from pingone_mfa import pingone_mfa_log
from pingprotect import pingprotect_log

# Attack Campaign Variables
ATTACKER_IP = "203.0.113.42"  # External attacker
ATTACKER_EMAIL = "haxorsaurus@evil-corp.net"
ATTACKER_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
TARGET_DOMAIN = "enterprise-corp.com"
COMPROMISED_USER = "alice.johnson"
COMPROMISED_EMAIL = f"{COMPROMISED_USER}@{TARGET_DOMAIN}"
ADMIN_USER = "admin.smith"
SERVICE_ACCOUNT = "svc-terraform"

# Campaign Timeline
CAMPAIGN_START = datetime.now(timezone.utc)
PHASE_DURATION = timedelta(hours=2)

def generate_phase_1_reconnaissance() -> List[Dict[Any, Any]]:
    """Phase 1: External reconnaissance and probing"""
    events = []
    phase_start = CAMPAIGN_START
    
    print("🔍 Phase 1: RECONNAISSANCE (External Probing)")
    
    # Fortigate: Port scanning and vulnerability probing
    for i in range(12):
        event_time = phase_start + timedelta(minutes=i*5)
        events.append({
            "source": "fortinet_fortigate",
            "timestamp": event_time.isoformat(),
            "event": fortinet_fortigate_log({
                "srcip": ATTACKER_IP,
                "dstip": "10.0.1.100",  # DMZ web server
                "service": random.choice(["tcp/22", "tcp/3389", "tcp/445", "tcp/1433"]),
                "action": "deny",
                "attack": "Port.Scan.NMAP",
                "severity": "high"
            })
        })
    
    # Cisco Duo: Failed MFA bypass attempts
    for i in range(5):
        event_time = phase_start + timedelta(minutes=15 + i*3)
        events.append({
            "source": "cisco_duo",
            "timestamp": event_time.isoformat(),
            "event": cisco_duo_log({
                "username": COMPROMISED_USER,
                "ip": ATTACKER_IP,
                "result": "FAILURE",
                "reason": "Invalid second factor",
                "factor": "push"
            })
        })
    
    # PingOne MFA: Enumeration attempts
    for i in range(8):
        event_time = phase_start + timedelta(minutes=20 + i*2)
        events.append({
            "source": "pingone_mfa",
            "timestamp": event_time.isoformat(),
            "event": pingone_mfa_log({
                "user": f"user{random.randint(1,100)}@{TARGET_DOMAIN}",
                "source_ip": ATTACKER_IP,
                "event_type": "authentication_failure",
                "reason": "invalid_credentials"
            })
        })
    
    return events

def generate_phase_2_initial_access() -> List[Dict[Any, Any]]:
    """Phase 2: Initial access via phishing and credential harvesting"""
    events = []
    phase_start = CAMPAIGN_START + PHASE_DURATION
    
    print("🎣 Phase 2: INITIAL ACCESS (Phishing Campaign)")
    
    # Proofpoint: Malicious email delivery
    events.append({
        "source": "proofpoint",
        "timestamp": phase_start.isoformat(),
        "event": proofpoint_log({
            "sender": ATTACKER_EMAIL,
            "recipient": COMPROMISED_EMAIL,
            "subject": "URGENT: Security Update Required",
            "threat_type": "phishing",
            "action": "delivered",
            "attachment_name": "security_update.pdf.exe"
        })
    })
    
    # Zscaler: Malicious URL access from compromised user
    event_time = phase_start + timedelta(minutes=10)
    events.append({
        "source": "zscaler", 
        "timestamp": event_time.isoformat(),
        "event": zscaler_log({
            "user": COMPROMISED_EMAIL,
            "url": "https://enterprise-c0rp-security[.]net/update",
            "urlclass": "Phishing",
            "action": "Allowed",  # User clicked before blocking
            "threat": "Phishing.Credential.Harvester"
        })
    })
    
    # Okta: Successful authentication after credential harvest
    event_time = phase_start + timedelta(minutes=25)
    events.append({
        "source": "okta_authentication",
        "timestamp": event_time.isoformat(),
        "event": okta_authentication_log({
            "actor": {
                "alternateId": COMPROMISED_EMAIL,
                "displayName": "Alice Johnson"
            },
            "client": {
                "ipAddress": ATTACKER_IP,
                "userAgent": {
                    "rawUserAgent": ATTACKER_USER_AGENT
                }
            },
            "eventType": "user.session.start",
            "outcome": {"result": "SUCCESS"}
        })
    })
    
    # Azure AD: Suspicious sign-in location
    event_time = phase_start + timedelta(minutes=30)
    events.append({
        "source": "microsoft_azuread",
        "timestamp": event_time.isoformat(), 
        "event": microsoft_azuread_log({
            "userPrincipalName": COMPROMISED_EMAIL,
            "ipAddress": ATTACKER_IP,
            "location": {"city": "Unknown", "countryOrRegion": "Romania"},
            "riskLevel": "high",
            "riskEventType": "unfamiliarFeatures"
        })
    })
    
    return events

def generate_phase_3_persistence() -> List[Dict[Any, Any]]:
    """Phase 3: Establishing persistence via cloud and identity systems"""
    events = []
    phase_start = CAMPAIGN_START + (PHASE_DURATION * 2)
    
    print("🔒 Phase 3: PERSISTENCE (Cloud & Identity Backdoors)")
    
    # AWS CloudTrail: Creating backdoor IAM user
    events.append({
        "source": "aws_cloudtrail",
        "timestamp": phase_start.isoformat(),
        "event": cloudtrail_log({
            "eventName": "CreateUser",
            "userIdentity": {
                "userName": COMPROMISED_USER,
                "type": "IAMUser"
            },
            "requestParameters": {
                "userName": "backup-svc-user"  # Innocuous name
            },
            "sourceIPAddress": ATTACKER_IP
        })
    })
    
    # AWS CloudTrail: Attaching admin permissions
    event_time = phase_start + timedelta(minutes=5)
    events.append({
        "source": "aws_cloudtrail", 
        "timestamp": event_time.isoformat(),
        "event": cloudtrail_log({
            "eventName": "AttachUserPolicy",
            "requestParameters": {
                "userName": "backup-svc-user",
                "policyArn": "arn:aws:iam::aws:policy/AdministratorAccess"
            },
            "sourceIPAddress": ATTACKER_IP
        })
    })
    
    # Azure AD: Creating service principal backdoor
    event_time = phase_start + timedelta(minutes=10)
    events.append({
        "source": "microsoft_azuread",
        "timestamp": event_time.isoformat(),
        "event": microsoft_azuread_log({
            "operationName": "Add service principal",
            "initiatedBy": {"user": {"userPrincipalName": COMPROMISED_EMAIL}},
            "targetResources": [{"displayName": "BackupAutomationApp"}],
            "result": "success"
        })
    })
    
    # HashiCorp Vault: Accessing sensitive secrets
    event_time = phase_start + timedelta(minutes=15)
    events.append({
        "source": "hashicorp_vault",
        "timestamp": event_time.isoformat(),
        "event": hashicorp_vault_log({
            "type": "request",
            "auth": {"display_name": COMPROMISED_USER},
            "request": {
                "operation": "read",
                "path": "secret/terraform/aws-credentials"
            },
            "remote_address": ATTACKER_IP
        })
    })
    
    return events

def generate_phase_4_lateral_movement() -> List[Dict[Any, Any]]:
    """Phase 4: Lateral movement through Windows infrastructure and databases"""
    events = []
    phase_start = CAMPAIGN_START + (PHASE_DURATION * 3)
    
    print("🌐 Phase 4: LATERAL MOVEMENT (Windows & Database Access)")
    
    # Windows: Kerberoasting attack
    events.append({
        "source": "microsoft_windows_eventlog",
        "timestamp": phase_start.isoformat(),
        "event": microsoft_windows_eventlog_log({
            "EventID": 4769,  # Kerberos service ticket request
            "Account_Name": COMPROMISED_USER,
            "Service_Name": "MSSQL/prod-db-01.enterprise-corp.com",
            "Client_Address": "10.0.10.50",
            "Failure_Code": "0x0"  # Success
        })
    })
    
    # Imperva: Database access attempts
    event_time = phase_start + timedelta(minutes=5)
    for table in ["users", "financial_data", "customer_pii", "payment_info"]:
        events.append({
            "source": "imperva_waf",
            "timestamp": (event_time + timedelta(minutes=1)).isoformat(),
            "event": imperva_waf_log({
                "user": SERVICE_ACCOUNT,
                "source_ip": "10.0.10.50",
                "sql_command": f"SELECT * FROM {table} LIMIT 10000",
                "action": "alert",
                "severity": "high",
                "policy": "Mass Data Extraction"
            })
        })
    
    # CrowdStrike: Detecting lateral movement tools
    event_time = phase_start + timedelta(minutes=10)
    events.append({
        "source": "crowdstrike_falcon",
        "timestamp": event_time.isoformat(),
        "event": crowdstrike_falcon_log({
            "ComputerName": "PROD-WEB-01",
            "UserName": COMPROMISED_USER,
            "ProcessName": "psexec.exe",
            "CommandLine": "psexec.exe \\\\prod-db-01 -u administrator cmd.exe",
            "ParentProcessName": "powershell.exe",
            "Severity": "Critical",
            "TacticName": "Lateral Movement"
        })
    })
    
    # Windows: Admin account compromise
    event_time = phase_start + timedelta(minutes=15)
    events.append({
        "source": "microsoft_windows_eventlog",
        "timestamp": event_time.isoformat(),
        "event": microsoft_windows_eventlog_log({
            "EventID": 4624,  # Successful logon
            "Account_Name": ADMIN_USER,
            "Logon_Type": 3,  # Network logon
            "Source_Network_Address": "10.0.10.50",
            "Workstation_Name": "PROD-DB-01"
        })
    })
    
    return events

def generate_phase_5_data_exfiltration() -> List[Dict[Any, Any]]:
    """Phase 5: Data exfiltration via DevOps and infrastructure compromise"""
    events = []
    phase_start = CAMPAIGN_START + (PHASE_DURATION * 4)
    
    print("📤 Phase 5: DATA EXFILTRATION (DevOps & Infrastructure)")
    
    # Harness CI/CD: Compromising deployment pipeline
    events.append({
        "source": "harness_ci",
        "timestamp": phase_start.isoformat(),
        "event": harness_ci_log({
            "user": COMPROMISED_USER,
            "action": "pipeline.execution.start",
            "pipeline": "data-export-emergency",
            "environment": "production",
            "source_ip": ATTACKER_IP,
            "suspicious_activity": "off-hours execution"
        })
    })
    
    # AWS CloudTrail: Large S3 data export
    event_time = phase_start + timedelta(minutes=5)
    events.append({
        "source": "aws_cloudtrail",
        "timestamp": event_time.isoformat(),
        "event": cloudtrail_log({
            "eventName": "GetObject",
            "requestParameters": {
                "bucketName": "enterprise-customer-data-prod",
                "key": "exports/full_customer_database_export.zip"
            },
            "additionalEventData": {
                "bytesTransferredOut": 50000000000  # 50GB
            },
            "sourceIPAddress": ATTACKER_IP
        })
    })
    
    # HashiCorp Vault: Bulk secret extraction
    event_time = phase_start + timedelta(minutes=8)
    for secret_path in ["database/prod", "api-keys/stripe", "certificates/ssl", "terraform/state"]:
        events.append({
            "source": "hashicorp_vault",
            "timestamp": (event_time + timedelta(seconds=30)).isoformat(),
            "event": hashicorp_vault_log({
                "type": "request",
                "auth": {"display_name": "backup-svc-user"},
                "request": {
                    "operation": "read",
                    "path": f"secret/{secret_path}"
                },
                "remote_address": ATTACKER_IP
            })
        })
    
    # Zscaler: Large data transfers to external sites
    event_time = phase_start + timedelta(minutes=12)
    events.append({
        "source": "zscaler",
        "timestamp": event_time.isoformat(),
        "event": zscaler_log({
            "user": COMPROMISED_EMAIL,
            "url": "https://temp-file-hosting[.]net/upload",
            "urlclass": "File Sharing",
            "uploadsize": 5000000000,  # 5GB
            "action": "Allowed",
            "threat": "Data.Exfiltration.Risk"
        })
    })
    
    return events

def generate_phase_6_evasion() -> List[Dict[Any, Any]]:
    """Phase 6: Anti-forensics and detection evasion"""
    events = []
    phase_start = CAMPAIGN_START + (PHASE_DURATION * 5)
    
    print("👻 Phase 6: EVASION (Anti-Forensics & Cleanup)")
    
    # AWS CloudTrail: Log deletion attempts
    events.append({
        "source": "aws_cloudtrail",
        "timestamp": phase_start.isoformat(),
        "event": cloudtrail_log({
            "eventName": "DeleteTrail",
            "requestParameters": {
                "name": "enterprise-security-audit-trail"
            },
            "sourceIPAddress": ATTACKER_IP,
            "errorCode": "AccessDenied"  # Blocked by policy
        })
    })
    
    # CrowdStrike: Process hollowing detection
    event_time = phase_start + timedelta(minutes=3)
    events.append({
        "source": "crowdstrike_falcon",
        "timestamp": event_time.isoformat(),
        "event": crowdstrike_falcon_log({
            "ComputerName": "PROD-WEB-01",
            "ProcessName": "svchost.exe",
            "CommandLine": "svchost.exe -k netsvcs",
            "ParentProcessName": "services.exe",
            "Severity": "High",
            "TacticName": "Defense Evasion",
            "TechniqueName": "Process Hollowing",
            "IOAScore": 85
        })
    })
    
    # Windows: Event log clearing
    event_time = phase_start + timedelta(minutes=5)
    events.append({
        "source": "microsoft_windows_eventlog",
        "timestamp": event_time.isoformat(),
        "event": microsoft_windows_eventlog_log({
            "EventID": 1102,  # Security log cleared
            "Account_Name": ADMIN_USER,
            "Source_Name": "Microsoft-Windows-Eventlog",
            "LogonId": "0x3e7"
        })
    })
    
    # PingProtect: Fraud detection triggered
    event_time = phase_start + timedelta(minutes=8)
    events.append({
        "source": "pingprotect",
        "timestamp": event_time.isoformat(),
        "event": pingprotect_log({
            "user": COMPROMISED_EMAIL,
            "risk_score": 95,
            "fraud_indicators": ["impossible_travel", "device_mismatch", "behavior_anomaly"],
            "action": "block",
            "session_ip": ATTACKER_IP
        })
    })
    
    return events

def generate_enterprise_attack_scenario() -> Dict[str, Any]:
    """Generate complete enterprise attack scenario"""
    print("🚨 ENTERPRISE ATTACK SCENARIO - SentinelOne AI-SIEM Showcase")
    print("=" * 80)
    print(f"Campaign Duration: {CAMPAIGN_START.isoformat()} - {(CAMPAIGN_START + PHASE_DURATION * 6).isoformat()}")
    print(f"Attacker: {ATTACKER_EMAIL} from {ATTACKER_IP}")
    print(f"Primary Target: {COMPROMISED_EMAIL} at {TARGET_DOMAIN}")
    print()
    
    # Generate all phases
    all_events = []
    all_events.extend(generate_phase_1_reconnaissance())
    all_events.extend(generate_phase_2_initial_access())
    all_events.extend(generate_phase_3_persistence()) 
    all_events.extend(generate_phase_4_lateral_movement())
    all_events.extend(generate_phase_5_data_exfiltration())
    all_events.extend(generate_phase_6_evasion())
    
    scenario = {
        "scenario_name": "Enterprise Multi-Platform Attack Campaign",
        "description": "Sophisticated APT-style attack demonstrating cross-platform correlation",
        "attacker_profile": {
            "ip": ATTACKER_IP,
            "email": ATTACKER_EMAIL,
            "user_agent": ATTACKER_USER_AGENT
        },
        "target_profile": {
            "domain": TARGET_DOMAIN,
            "primary_victim": COMPROMISED_EMAIL,
            "admin_account": ADMIN_USER
        },
        "campaign_timeline": {
            "start": CAMPAIGN_START.isoformat(),
            "duration_hours": 12,
            "phases": 6
        },
        "data_sources": [
            "Fortinet Fortigate (DMZ Firewalls)",
            "Windows Corp Servers", 
            "Imperva SecureSphere Audit",
            "AWS CloudTrail",
            "Okta Authentication",
            "Azure AD Authentication", 
            "Cisco Duo MFA",
            "Zscaler Web Security",
            "Proofpoint Email Security",
            "CrowdStrike Endpoint Detection",
            "HashiCorp Vault",
            "Harness CI/CD",
            "PingOne MFA",
            "PingProtect Fraud Detection"
        ],
        "attack_phases": [
            "Phase 1: Reconnaissance & External Probing",
            "Phase 2: Initial Access via Phishing", 
            "Phase 3: Persistence through Cloud/Identity",
            "Phase 4: Lateral Movement & Database Access",
            "Phase 5: Data Exfiltration via DevOps",
            "Phase 6: Evasion & Anti-Forensics"
        ],
        "events": all_events,
        "event_count": len(all_events),
        "correlation_opportunities": [
            "Cross-platform user behavior analysis",
            "Temporal attack pattern recognition",
            "Infrastructure traversal mapping",
            "Data flow anomaly detection",
            "Multi-source threat hunting"
        ]
    }
    
    print(f"✅ Generated {len(all_events)} events across {len(scenario['data_sources'])} data sources")
    print(f"🔍 Attack demonstrates advanced multi-platform correlation capabilities")
    
    return scenario

def save_scenario(scenario: Dict[str, Any], filename: str = "enterprise_attack_scenario.json"):
    """Save scenario to JSON file"""
    with open(filename, 'w') as f:
        json.dump(scenario, f, indent=2, default=str)
    print(f"📁 Scenario saved to: {filename}")

if __name__ == "__main__":
    scenario = generate_enterprise_attack_scenario()
    save_scenario(scenario)