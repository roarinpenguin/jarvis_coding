#\!/usr/bin/env python3
"""
Enhanced Enterprise Attack Scenario - 300+ Events
==================================================

Comprehensive APT simulation with clear attack progression:
1. Initial Reconnaissance (50+ events)
2. Initial Compromise via Phishing (30+ events)  
3. Credential Harvesting & MFA Bypass (40+ events)
4. Lateral Movement Across Network (60+ events)
5. Privilege Escalation (40+ events)
6. Data Discovery & Collection (40+ events)
7. Data Exfiltration (40+ events)
8. Persistence & Cleanup (20+ events)

Total: 300+ security events across 20+ data sources
"""

import json
import sys
import os
import random
from datetime import datetime, timezone, timedelta

# Add the event_python_writer directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Import all generators
from fortinet_fortigate import forward_log
from microsoft_windows_eventlog import microsoft_windows_eventlog_log
from imperva_waf import imperva_waf_log  
from aws_cloudtrail import cloudtrail_log
from okta_authentication import okta_authentication_log
from microsoft_azuread import azuread_log
from cisco_duo import cisco_duo_log
from zscaler import zscaler_log
from proofpoint import proofpoint_log
from crowdstrike_falcon import crowdstrike_log
from hashicorp_vault import hashicorp_vault_log
from harness_ci import harness_ci_log
from pingone_mfa import pingone_mfa_log
from pingprotect import pingprotect_log
from cisco_umbrella import cisco_umbrella_log
from paloalto_firewall import paloalto_firewall_log as paloalto_log
from cisco_ise import cisco_ise_log
from f5_networks import f5_networks_log as f5_log
from netskope import netskope_log
from github_audit import github_audit_log

# Attack timeline
BASE_TIME = datetime.now(timezone.utc) - timedelta(hours=12)

def get_attack_time(phase_offset_minutes):
    """Get timestamp for attack phase"""
    return (BASE_TIME + timedelta(minutes=phase_offset_minutes)).isoformat()

def generate_enhanced_attack_scenario():
    """Generate 300+ event comprehensive attack scenario"""
    
    print("🚨 ENHANCED ENTERPRISE ATTACK SCENARIO - 300+ Events")
    print("=" * 80)
    print("🎯 Simulating Advanced Persistent Threat (APT) Campaign")
    
    events = []
    attack_phases = []
    data_sources = set()
    
    # Attacker IPs and domains
    attacker_ips = ["185.220.101.45", "185.220.101.46", "185.220.101.47"]  # Tor exit nodes
    c2_domains = ["update-service[.]net", "secure-analytics[.]com", "cdn-delivery[.]org"]
    exfil_domains = ["storage-backup[.]net", "cloud-sync[.]org"]
    
    # Target users
    target_users = ["john.admin", "sarah.cfo", "mike.developer", "lisa.hr", "bob.contractor"]
    compromised_user = "sarah.cfo"  # CFO will be main compromise
    
    print("\n📊 ATTACK PHASES:")
    print("-" * 60)
    
    # ========================================
    # PHASE 1: RECONNAISSANCE (50+ events)
    # ========================================
    print("🔍 Phase 1: RECONNAISSANCE (0-60 minutes)")
    attack_phases.append("reconnaissance")
    
    # External port scanning detected by Fortigate
    for i in range(15):
        event = {
            "timestamp": get_attack_time(i * 2),
            "source": "fortinet_fortigate",
            "phase": "reconnaissance",
            "event": forward_log()
        }
        events.append(event)
        data_sources.add("fortinet_fortigate")
    
    # DNS reconnaissance via Cisco Umbrella
    for i in range(10):
        event = {
            "timestamp": get_attack_time(15 + i * 3),
            "source": "cisco_umbrella",
            "phase": "reconnaissance", 
            "event": cisco_umbrella_log()
        }
        events.append(event)
        data_sources.add("cisco_umbrella")
    
    # Web application scanning on Imperva WAF
    for i in range(15):
        event = {
            "timestamp": get_attack_time(30 + i * 2),
            "source": "imperva_waf",
            "phase": "reconnaissance",
            "event": imperva_waf_log()
        }
        events.append(event)
        data_sources.add("imperva_waf")
    
    # Palo Alto firewall detecting scan attempts
    for i in range(10):
        event = {
            "timestamp": get_attack_time(45 + i * 2),
            "source": "paloalto_firewall",
            "phase": "reconnaissance",
            "event": paloalto_log()
        }
        events.append(event)
        data_sources.add("paloalto_firewall")
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'reconnaissance'])} reconnaissance events")
    
    # ========================================
    # PHASE 2: INITIAL COMPROMISE - PHISHING (30+ events)
    # ========================================
    print("📧 Phase 2: INITIAL COMPROMISE via Phishing (60-90 minutes)")
    attack_phases.append("initial_compromise")
    
    # Phishing emails detected by Proofpoint
    for i in range(10):
        event = {
            "timestamp": get_attack_time(60 + i * 2),
            "source": "proofpoint",
            "phase": "initial_compromise",
            "event": proofpoint_log()
        }
        events.append(event)
        data_sources.add("proofpoint")
    
    # User clicks phishing link - Zscaler logs
    for i in range(5):
        event = {
            "timestamp": get_attack_time(75 + i),
            "source": "zscaler",
            "phase": "initial_compromise",
            "event": zscaler_log()
        }
        events.append(event)
        data_sources.add("zscaler")
    
    # Netskope detecting suspicious downloads
    for i in range(5):
        event = {
            "timestamp": get_attack_time(80 + i),
            "source": "netskope",
            "phase": "initial_compromise",
            "event": netskope_log()
        }
        events.append(event)
        data_sources.add("netskope")
    
    # CrowdStrike detects initial payload execution
    for i in range(10):
        event = {
            "timestamp": get_attack_time(85 + i),
            "source": "crowdstrike_falcon",
            "phase": "initial_compromise",
            "event": crowdstrike_log()
        }
        events.append(event)
        data_sources.add("crowdstrike_falcon")
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'initial_compromise'])} initial compromise events")
    
    # ========================================
    # PHASE 3: CREDENTIAL HARVESTING & MFA BYPASS (40+ events)
    # ========================================
    print("🔐 Phase 3: CREDENTIAL HARVESTING & MFA Bypass (90-120 minutes)")
    attack_phases.append("credential_access")
    
    # Failed login attempts in Okta
    for i in range(8):
        event = {
            "timestamp": get_attack_time(90 + i * 2),
            "source": "okta_authentication",
            "phase": "credential_access",
            "event": okta_authentication_log()
        }
        events.append(event)
        data_sources.add("okta_authentication")
    
    # Azure AD suspicious sign-ins
    for i in range(8):
        event = {
            "timestamp": get_attack_time(95 + i * 2),
            "source": "microsoft_azuread",
            "phase": "credential_access",
            "event": azuread_log()
        }
        events.append(event)
        data_sources.add("microsoft_azuread")
    
    # Cisco Duo MFA bypass attempts
    for i in range(6):
        event = {
            "timestamp": get_attack_time(100 + i),
            "source": "cisco_duo",
            "phase": "credential_access",
            "event": cisco_duo_log()
        }
        events.append(event)
        data_sources.add("cisco_duo")
    
    # PingOne MFA anomalies
    for i in range(6):
        event = {
            "timestamp": get_attack_time(105 + i),
            "source": "pingone_mfa",
            "phase": "credential_access",
            "event": pingone_mfa_log()
        }
        events.append(event)
        data_sources.add("pingone_mfa")
    
    # Windows credential dump attempts
    for i in range(12):
        event = {
            "timestamp": get_attack_time(110 + i),
            "source": "microsoft_windows_eventlog",
            "phase": "credential_access",
            "event": microsoft_windows_eventlog_log()
        }
        events.append(event)
        data_sources.add("microsoft_windows_eventlog")
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'credential_access'])} credential access events")
    
    # ========================================
    # PHASE 4: LATERAL MOVEMENT (60+ events)
    # ========================================
    print("➡️  Phase 4: LATERAL MOVEMENT (120-180 minutes)")
    attack_phases.append("lateral_movement")
    
    # RDP/SMB movement in Windows logs
    for i in range(20):
        event = {
            "timestamp": get_attack_time(120 + i * 2),
            "source": "microsoft_windows_eventlog",
            "phase": "lateral_movement",
            "event": microsoft_windows_eventlog_log()
        }
        events.append(event)
    
    # Cisco ISE detecting device hopping
    for i in range(10):
        event = {
            "timestamp": get_attack_time(140 + i * 2),
            "source": "cisco_ise",
            "phase": "lateral_movement",
            "event": cisco_ise_log()
        }
        events.append(event)
        data_sources.add("cisco_ise")
    
    # F5 load balancer unusual traffic patterns
    for i in range(10):
        event = {
            "timestamp": get_attack_time(150 + i * 2),
            "source": "f5_networks",
            "phase": "lateral_movement",
            "event": f5_log()
        }
        events.append(event)
        data_sources.add("f5_networks")
    
    # Database access via Imperva
    for i in range(10):
        event = {
            "timestamp": get_attack_time(160 + i * 2),
            "source": "imperva_waf",
            "phase": "lateral_movement",
            "event": imperva_waf_log()
        }
        events.append(event)
    
    # CrowdStrike detecting lateral movement tools
    for i in range(10):
        event = {
            "timestamp": get_attack_time(170 + i),
            "source": "crowdstrike_falcon",
            "phase": "lateral_movement",
            "event": crowdstrike_log()
        }
        events.append(event)
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'lateral_movement'])} lateral movement events")
    
    # ========================================
    # PHASE 5: PRIVILEGE ESCALATION (40+ events)
    # ========================================
    print("⬆️  Phase 5: PRIVILEGE ESCALATION (180-210 minutes)")
    attack_phases.append("privilege_escalation")
    
    # AWS IAM privilege escalation attempts
    for i in range(15):
        event = {
            "timestamp": get_attack_time(180 + i * 2),
            "source": "aws_cloudtrail",
            "phase": "privilege_escalation",
            "event": cloudtrail_log()
        }
        events.append(event)
        data_sources.add("aws_cloudtrail")
    
    # HashiCorp Vault access to secrets
    for i in range(10):
        event = {
            "timestamp": get_attack_time(190 + i * 2),
            "source": "hashicorp_vault",
            "phase": "privilege_escalation",
            "event": hashicorp_vault_log()
        }
        events.append(event)
        data_sources.add("hashicorp_vault")
    
    # Windows privilege escalation events
    for i in range(10):
        event = {
            "timestamp": get_attack_time(195 + i),
            "source": "microsoft_windows_eventlog",
            "phase": "privilege_escalation",
            "event": microsoft_windows_eventlog_log()
        }
        events.append(event)
    
    # Azure AD admin role changes
    for i in range(5):
        event = {
            "timestamp": get_attack_time(200 + i * 2),
            "source": "microsoft_azuread",
            "phase": "privilege_escalation",
            "event": azuread_log()
        }
        events.append(event)
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'privilege_escalation'])} privilege escalation events")
    
    # ========================================
    # PHASE 6: DATA DISCOVERY & COLLECTION (40+ events)
    # ========================================
    print("🔎 Phase 6: DATA DISCOVERY & COLLECTION (210-240 minutes)")
    attack_phases.append("data_discovery")
    
    # Database queries via Imperva
    for i in range(15):
        event = {
            "timestamp": get_attack_time(210 + i * 2),
            "source": "imperva_waf",
            "phase": "data_discovery",
            "event": imperva_waf_log()
        }
        events.append(event)
    
    # AWS S3 bucket enumeration
    for i in range(10):
        event = {
            "timestamp": get_attack_time(220 + i * 2),
            "source": "aws_cloudtrail",
            "phase": "data_discovery",
            "event": cloudtrail_log()
        }
        events.append(event)
    
    # GitHub repository access
    for i in range(8):
        event = {
            "timestamp": get_attack_time(225 + i * 2),
            "source": "github_audit",
            "phase": "data_discovery",
            "event": github_audit_log()
        }
        events.append(event)
        data_sources.add("github_audit")
    
    # File access in Windows
    for i in range(7):
        event = {
            "timestamp": get_attack_time(230 + i),
            "source": "microsoft_windows_eventlog",
            "phase": "data_discovery",
            "event": microsoft_windows_eventlog_log()
        }
        events.append(event)
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'data_discovery'])} data discovery events")
    
    # ========================================
    # PHASE 7: DATA EXFILTRATION (40+ events)
    # ========================================
    print("📤 Phase 7: DATA EXFILTRATION (240-270 minutes)")
    attack_phases.append("data_exfiltration")
    
    # Large data transfers via Zscaler
    for i in range(10):
        event = {
            "timestamp": get_attack_time(240 + i * 2),
            "source": "zscaler",
            "phase": "data_exfiltration",
            "event": zscaler_log()
        }
        events.append(event)
    
    # DNS tunneling via Cisco Umbrella
    for i in range(10):
        event = {
            "timestamp": get_attack_time(245 + i * 2),
            "source": "cisco_umbrella",
            "phase": "data_exfiltration",
            "event": cisco_umbrella_log()
        }
        events.append(event)
    
    # Netskope detecting cloud uploads
    for i in range(8):
        event = {
            "timestamp": get_attack_time(250 + i * 2),
            "source": "netskope",
            "phase": "data_exfiltration",
            "event": netskope_log()
        }
        events.append(event)
    
    # Palo Alto detecting exfil traffic
    for i in range(7):
        event = {
            "timestamp": get_attack_time(255 + i * 2),
            "source": "paloalto_firewall",
            "phase": "data_exfiltration",
            "event": paloalto_log()
        }
        events.append(event)
    
    # Fortigate outbound anomalies
    for i in range(5):
        event = {
            "timestamp": get_attack_time(260 + i * 2),
            "source": "fortinet_fortigate",
            "phase": "data_exfiltration",
            "event": forward_log()
        }
        events.append(event)
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'data_exfiltration'])} data exfiltration events")
    
    # ========================================
    # PHASE 8: PERSISTENCE & CLEANUP (20+ events)
    # ========================================
    print("🔧 Phase 8: PERSISTENCE & CLEANUP (270-300 minutes)")
    attack_phases.append("persistence")
    
    # CI/CD pipeline backdoor via Harness
    for i in range(5):
        event = {
            "timestamp": get_attack_time(270 + i * 3),
            "source": "harness_ci",
            "phase": "persistence",
            "event": harness_ci_log()
        }
        events.append(event)
        data_sources.add("harness_ci")
    
    # AWS persistence mechanisms
    for i in range(5):
        event = {
            "timestamp": get_attack_time(275 + i * 3),
            "source": "aws_cloudtrail",
            "phase": "persistence",
            "event": cloudtrail_log()
        }
        events.append(event)
    
    # Windows scheduled tasks
    for i in range(5):
        event = {
            "timestamp": get_attack_time(280 + i * 3),
            "source": "microsoft_windows_eventlog",
            "phase": "persistence",
            "event": microsoft_windows_eventlog_log()
        }
        events.append(event)
    
    # Log deletion attempts
    for i in range(5):
        event = {
            "timestamp": get_attack_time(285 + i * 3),
            "source": "crowdstrike_falcon",
            "phase": "persistence",
            "event": crowdstrike_log()
        }
        events.append(event)
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'persistence'])} persistence events")
    
    # ========================================
    # DETECTION & RESPONSE
    # ========================================
    print("🚨 Phase 9: DETECTION & RESPONSE (300+ minutes)")
    attack_phases.append("detection")
    
    # PingProtect fraud detection
    for i in range(5):
        event = {
            "timestamp": get_attack_time(300 + i),
            "source": "pingprotect",
            "phase": "detection",
            "event": pingprotect_log()
        }
        events.append(event)
        data_sources.add("pingprotect")
    
    # Additional CrowdStrike alerts
    for i in range(5):
        event = {
            "timestamp": get_attack_time(305 + i),
            "source": "crowdstrike_falcon",
            "phase": "detection",
            "event": crowdstrike_log()
        }
        events.append(event)
    
    print(f"   ✅ Generated {len([e for e in events if e['phase'] == 'detection'])} detection events")
    
    # Summary
    print("\n" + "=" * 80)
    print("🎯 SCENARIO SUMMARY:")
    print(f"   📊 Total Events: {len(events)}")
    print(f"   🏢 Data Sources: {len(data_sources)}")
    print(f"   🔥 Attack Phases: {len(attack_phases)}")
    print(f"   ⏰ Timeline: {BASE_TIME.isoformat()} to {get_attack_time(310)}")
    
    return {
        "events": events,
        "attack_phases": attack_phases,
        "data_sources": list(data_sources),
        "metadata": {
            "total_events": len(events),
            "duration_minutes": 310,
            "attacker_ips": attacker_ips,
            "c2_domains": c2_domains,
            "exfil_domains": exfil_domains,
            "compromised_user": compromised_user,
            "attack_type": "Advanced Persistent Threat (APT)",
            "mitre_techniques": [
                "T1595 - Active Scanning",
                "T1566 - Phishing",
                "T1078 - Valid Accounts",
                "T1110 - Brute Force",
                "T1556 - MFA Bypass",
                "T1003 - Credential Dumping",
                "T1021 - Remote Services",
                "T1570 - Lateral Tool Transfer",
                "T1068 - Privilege Escalation",
                "T1083 - File Discovery",
                "T1005 - Data from Local System",
                "T1030 - Data Transfer Size Limits",
                "T1048 - Exfiltration Over Alternative Protocol",
                "T1053 - Scheduled Task",
                "T1070 - Indicator Removal"
            ]
        }
    }

def save_scenario(scenario, filename="enterprise_attack_scenario.json"):
    """Save scenario to file"""
    with open(filename, 'w') as f:
        json.dump(scenario, f, indent=2, default=str)
    print(f"\n📁 Scenario saved to: {filename}")
    return filename

if __name__ == "__main__":
    scenario = generate_enhanced_attack_scenario()
    save_scenario(scenario)
    print("\n✅ Enhanced enterprise attack scenario with 300+ events ready!")
    print("🎯 Use enterprise_scenario_sender.py to send events to SentinelOne AI-SIEM")