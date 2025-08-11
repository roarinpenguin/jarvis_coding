#!/usr/bin/env python3
"""
ManageEngine ADAuditPlus event generator
Generates Active Directory audit events in syslog + key-value format
"""
from __future__ import annotations
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.category": "security",
    "dataSource.name": "ADAuditPlus", 
    "dataSource.vendor": "ADAuditPlus"
}

# Event categories and sources
CATEGORIES = [
    "User Management", "Group Management", "Computer Management", "Account Management",
    "Logon Events", "Object Access", "Policy Changes", "System Events",
    "Directory Service Access", "Account Logon", "Privilege Use", "Process Tracking"
]

SOURCES = [
    "Active Directory", "Domain Controller", "LDAP", "Kerberos", "NTLM",
    "Group Policy", "DNS", "File System", "Registry", "Security Log"
]

# AD event types and details
AD_EVENTS = {
    "User Management": [
        ("User Created", "New user account created in Active Directory"),
        ("User Deleted", "User account deleted from Active Directory"), 
        ("User Modified", "User account properties modified"),
        ("User Enabled", "User account enabled"),
        ("User Disabled", "User account disabled"),
        ("Password Reset", "User password reset by administrator"),
        ("Password Changed", "User changed their password"),
        ("Account Locked", "User account locked due to failed logon attempts")
    ],
    "Group Management": [
        ("Group Created", "Security group created"),
        ("Group Deleted", "Security group deleted"),
        ("Group Modified", "Group properties modified"),
        ("Member Added", "User added to security group"),
        ("Member Removed", "User removed from security group"),
        ("Group Type Changed", "Group type or scope changed")
    ],
    "Logon Events": [
        ("Successful Logon", "User successfully logged on"),
        ("Failed Logon", "User logon attempt failed"),
        ("Logoff", "User logged off"),
        ("Session Disconnected", "Remote session disconnected"),
        ("Account Lockout", "Account locked due to logon failures"),
        ("Logon with Expired Password", "Attempted logon with expired password")
    ],
    "Object Access": [
        ("File Accessed", "File or folder accessed"),
        ("File Modified", "File or folder modified"),
        ("File Deleted", "File or folder deleted"),
        ("Registry Key Accessed", "Registry key accessed"),
        ("Registry Value Modified", "Registry value modified"),
        ("Printer Accessed", "Network printer accessed")
    ],
    "Policy Changes": [
        ("Group Policy Modified", "Group Policy Object modified"),
        ("Security Policy Changed", "Local security policy changed"),
        ("Audit Policy Changed", "Audit policy settings modified"),
        ("Trust Policy Changed", "Domain trust policy modified"),
        ("Account Policy Changed", "Account lockout or password policy changed")
    ]
}

# Users, computers, and domains
USERS = ["jdoe", "asmith", "bjohnson", "cwilliams", "admin", "service_account", "backup_user"]
COMPUTERS = ["DC01", "SERVER01", "WORKSTATION-001", "LAPTOP-ABC", "DEV-MACHINE", "FILE-SERVER"]
DOMAINS = ["CORP", "INTERNAL", "COMPANY"]

# Extra details for different event types
EXTRA_DETAILS = {
    "User Management": [
        "Account created with default security group membership",
        "User account properties updated via ADUC",
        "Password policy compliance check failed",
        "Account disabled due to inactivity",
        "User profile path modified",
        "Home directory permissions updated"
    ],
    "Group Management": [
        "Security group membership modified",
        "Distribution list updated", 
        "Nested group membership changed",
        "Group scope changed from global to universal",
        "Group policy permissions updated",
        "Administrative group membership modified"
    ],
    "Logon Events": [
        "Interactive logon via console",
        "Network logon from workstation",
        "Service logon for scheduled task",
        "Remote desktop session established",
        "Failed logon - bad username or password",
        "Failed logon - account restriction"
    ],
    "Object Access": [
        "Full control permissions granted",
        "Read access to sensitive file",
        "Modify permissions on system folder",
        "Delete operation on protected resource",
        "Registry key creation in HKLM",
        "Printer queue access granted"
    ],
    "Policy Changes": [
        "Group Policy Object linked to OU",
        "Security template imported",
        "Audit policy enabled for object access",
        "Password complexity requirements updated",
        "Account lockout threshold modified",
        "Kerberos policy settings changed"
    ]
}

def _generate_ip():
    """Generate IP address"""
    return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def manageengine_ad_audit_plus_log(overrides: dict | None = None) -> str:
    """
    Return a single ManageEngine ADAuditPlus event as syslog + key-value string.
    
    Pass `overrides` to force any field to a specific value:
        manageengine_ad_audit_plus_log({"Category": "User Management"})
    """
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(seconds=random.randint(0, 300))
    
    # Select event category and details
    category = random.choice(CATEGORIES)
    source = random.choice(SOURCES)
    
    # Get event details for the category
    if category in AD_EVENTS:
        event_name, event_desc = random.choice(AD_EVENTS[category])
        extra_detail = random.choice(EXTRA_DETAILS.get(category, ["Standard AD operation"]))
    else:
        event_name = f"{category} Event"
        event_desc = f"Active Directory {category.lower()} operation"
        extra_detail = "Standard AD operation"
    
    # Generate priority (local0.info = 134)
    priority = random.choice([133, 134, 135])  # local0 facility, various severities
    
    # Build syslog header
    timestamp = event_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    hostname = random.choice(COMPUTERS)
    
    # Build key-value pairs
    kvp_data = {
        "Category": category,
        "SOURCE": source,
        "EXTRA_COLUMN1": extra_detail,
        "CLIENT_IP_ADDRESS": _generate_ip(),
        "EVENT_NAME": event_name,
        "EVENT_DESCRIPTION": event_desc,
        "USER_NAME": random.choice(USERS),
        "COMPUTER_NAME": random.choice(COMPUTERS),
        "DOMAIN_NAME": random.choice(DOMAINS),
        "LOGON_ID": f"0x{random.randint(100000, 999999):X}",
        "PROCESS_ID": str(random.randint(1000, 9999)),
        "THREAD_ID": str(random.randint(100, 999)),
        "EVENT_ID": str(random.randint(4600, 4799)),
        "OBJECT_NAME": f"CN={random.choice(USERS)},OU=Users,DC={random.choice(DOMAINS).lower()},DC=local" if category in ["User Management", "Object Access"] else "",
        "OBJECT_TYPE": random.choice(["User", "Group", "Computer", "OrganizationalUnit", "File", "Registry"]) if category in ["User Management", "Group Management", "Object Access"] else "",
        "ACCESS_MASK": f"0x{random.randint(1, 255):02X}" if category == "Object Access" else "",
        "PRIVILEGES": random.choice(["SeBackupPrivilege", "SeRestorePrivilege", "SeSecurityPrivilege", "SeTakeOwnershipPrivilege"]) if category == "Privilege Use" else "",
        "SERVICE_NAME": random.choice(["KDC", "NTDS", "DNS", "NETLOGON"]) if source in ["Kerberos", "Active Directory", "DNS"] else "",
        "FAILURE_REASON": random.choice(["Bad username or password", "Account restriction", "Logon time restriction", "Account disabled"]) if "Failed" in event_name else "",
        "AUTHENTICATION_PACKAGE": random.choice(["NTLM", "Kerberos", "Negotiate"]) if category == "Logon Events" else "",
        "WORKSTATION_NAME": random.choice(COMPUTERS) if category == "Logon Events" else "",
        "TARGET_USER_NAME": random.choice(USERS) if category in ["User Management", "Group Management"] else "",
        "GROUP_NAME": f"CN={random.choice(['Domain Admins', 'Enterprise Admins', 'Backup Operators', 'Account Operators'])},CN=Users,DC={random.choice(DOMAINS).lower()},DC=local" if category == "Group Management" else "",
        "POLICY_NAME": random.choice(["Default Domain Policy", "Domain Controller Policy", "Fine-Grained Password Policy"]) if category == "Policy Changes" else "",
        "OLD_VALUE": f"Value_{random.randint(1, 100)}" if "Modified" in event_name else "",
        "NEW_VALUE": f"Value_{random.randint(101, 200)}" if "Modified" in event_name else "",
        "RESULT_CODE": "0x0" if "Successful" in event_name or "Created" in event_name else f"0x{random.randint(1, 255):X}",
        "ADDITIONAL_INFO": f"Operation completed via {random.choice(['ADUC', 'PowerShell', 'LDAP', 'Group Policy', 'API call'])}"
    }
    
    # Apply overrides
    if overrides:
        kvp_data.update(overrides)
    
    # Build the log message
    syslog_header = f"<{priority}>1 {timestamp} {hostname} ADAuditPlus - - - "
    
    # Build key-value pairs - only include non-empty values
    kvp_parts = []
    for key, value in kvp_data.items():
        if value:  # Only include non-empty values
            kvp_parts.append(f"[ {key} = {value} ]")
    
    return syslog_header + " ".join(kvp_parts)

if __name__ == "__main__":
    # Generate sample logs
    print("Sample ManageEngine ADAuditPlus events:")
    for category in ["User Management", "Logon Events", "Policy Changes"]:
        print(f"\n{category} event:")
        print(manageengine_ad_audit_plus_log({"Category": category}))
        print()