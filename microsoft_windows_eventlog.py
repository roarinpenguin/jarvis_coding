#!/usr/bin/env python3
"""
Microsoft Windows Event Log generator
Generates synthetic Windows Event Log events (Security, System, Application)
"""
import json
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Microsoft",
    "dataSource.name": "Windows Event Log",
    "dataSource.category": "security",
}

# Common Windows Event IDs by category
SECURITY_EVENTS = [
    {"id": 4624, "name": "Successful Logon", "level": "Information"},
    {"id": 4625, "name": "Failed Logon", "level": "Information"},
    {"id": 4634, "name": "Account Logoff", "level": "Information"},
    {"id": 4648, "name": "Logon with Explicit Credentials", "level": "Information"},
    {"id": 4720, "name": "User Account Created", "level": "Information"},
    {"id": 4726, "name": "User Account Deleted", "level": "Information"},
    {"id": 4728, "name": "Member Added to Security Group", "level": "Information"},
    {"id": 4729, "name": "Member Removed from Security Group", "level": "Information"},
    {"id": 4732, "name": "Member Added to Local Group", "level": "Information"},
    {"id": 4740, "name": "User Account Locked", "level": "Information"},
    {"id": 4767, "name": "User Account Unlocked", "level": "Information"},
    {"id": 4778, "name": "Session Reconnected", "level": "Information"},
    {"id": 4779, "name": "Session Disconnected", "level": "Information"},
    {"id": 5156, "name": "Windows Filtering Platform Connection", "level": "Information"},
    {"id": 1102, "name": "Audit Log Cleared", "level": "Information"}
]

SYSTEM_EVENTS = [
    {"id": 7034, "name": "Service Crashed", "level": "Error"},
    {"id": 7035, "name": "Service Control Manager", "level": "Information"},
    {"id": 7036, "name": "Service Start/Stop", "level": "Information"},
    {"id": 7040, "name": "Service Start Type Changed", "level": "Information"},
    {"id": 6005, "name": "Event Log Service Started", "level": "Information"},
    {"id": 6006, "name": "Event Log Service Stopped", "level": "Information"},
    {"id": 6008, "name": "Unexpected Shutdown", "level": "Error"},
    {"id": 6009, "name": "System Started", "level": "Information"},
    {"id": 1074, "name": "System Shutdown Initiated", "level": "Information"},
    {"id": 41, "name": "System Rebooted Without Shutdown", "level": "Critical"}
]

APPLICATION_EVENTS = [
    {"id": 1000, "name": "Application Error", "level": "Error"},
    {"id": 1001, "name": "Application Hang", "level": "Error"},
    {"id": 1002, "name": "Application Recovery", "level": "Information"},
    {"id": 2, "name": "Application Start", "level": "Information"},
    {"id": 4, "name": "Application Stop", "level": "Information"}
]

# Logon types
LOGON_TYPES = {
    2: "Interactive",
    3: "Network", 
    4: "Batch",
    5: "Service",
    7: "Unlock",
    8: "NetworkCleartext",
    9: "NewCredentials",
    10: "RemoteInteractive",
    11: "CachedInteractive"
}

# Authentication packages
AUTH_PACKAGES = ["NTLM", "Kerberos", "Negotiate", "PKU2U", "WDigest"]

# Windows services
SERVICES = [
    "Windows Update", "DHCP Client", "DNS Client", "Print Spooler",
    "Task Scheduler", "Windows Firewall", "Remote Registry", "Server",
    "Workstation", "Windows Time", "BITS", "Themes", "Audio Service"
]

# Computer names and users
COMPUTERS = [f"WKS-{random.randint(1000, 9999)}" for _ in range(20)]
USERS = [f"user{i:03d}" for i in range(1, 101)]
ADMIN_USERS = ["administrator", "admin", "sysadmin", "domainadmin"]

def generate_ip() -> str:
    """Generate a random IP address"""
    return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def microsoft_windows_eventlog_log() -> str:
    """Generate a single Windows Event Log entry"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 1440))
    
    # Choose event type and log channel
    log_channel = random.choice(["Security", "System", "Application"])
    
    if log_channel == "Security":
        event_info = random.choice(SECURITY_EVENTS)
    elif log_channel == "System":
        event_info = random.choice(SYSTEM_EVENTS)
    else:
        event_info = random.choice(APPLICATION_EVENTS)
    
    computer_name = random.choice(COMPUTERS)
    
    event = {
        "TimeCreated": event_time.isoformat(),
        "EventID": event_info["id"],
        "LogName": log_channel,
        "Level": event_info["level"],
        "Task": event_info["name"],
        "Keywords": "Audit Success" if event_info["level"] == "Information" and log_channel == "Security" else event_info["level"],
        "Computer": computer_name + ".company.local",
        "EventRecordID": random.randint(1000000, 9999999),
        "ProcessID": random.randint(1000, 8000),
        "ThreadID": random.randint(1000, 8000),
        "Channel": log_channel,
        "Message": f"{event_info['name']} event occurred on {computer_name}",
        **ATTR_FIELDS
    }
    
    # Add event-specific data
    if log_channel == "Security":
        if event_info["id"] in [4624, 4625]:  # Logon events
            logon_type = random.choice(list(LOGON_TYPES.keys()))
            user = random.choice(USERS + ADMIN_USERS)
            
            event.update({
                "SubjectUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserName": user,
                "SubjectDomainName": "COMPANY",
                "SubjectLogonId": f"0x{random.randint(100000, 999999):x}",
                "TargetUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "TargetUserName": user,
                "TargetDomainName": "COMPANY",
                "TargetLogonId": f"0x{random.randint(100000, 999999):x}",
                "LogonType": logon_type,
                "LogonProcessName": random.choice(["Advapi", "User32", "Negotiate", "Kerberos"]),
                "AuthenticationPackageName": random.choice(AUTH_PACKAGES),
                "WorkstationName": computer_name,
                "LogonGuid": f"{{{random.randint(10000000, 99999999):08x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{random.randint(100000000000, 999999999999):012x}}}",
                "TransmittedServices": "-",
                "LmPackageName": "NTLM V2" if "NTLM" in event.get("AuthenticationPackageName", "") else "-",
                "KeyLength": random.choice([0, 128, 256]),
                "ProcessName": random.choice(["C:\\Windows\\System32\\winlogon.exe", "C:\\Windows\\System32\\svchost.exe", "-"]),
                "IpAddress": generate_ip() if logon_type in [3, 8, 10] else "127.0.0.1",
                "IpPort": random.randint(49152, 65535) if logon_type in [3, 8, 10] else 0
            })
            
            if event_info["id"] == 4625:  # Failed logon
                event.update({
                    "Status": f"0x{random.choice(['c000006d', 'c000006a', 'c000006f', 'c0000064', 'c000015b']):s}",
                    "SubStatus": f"0x{random.choice(['c000006a', 'c000006d', 'c0000064']):s}",
                    "FailureReason": random.choice([
                        "Unknown user name or bad password",
                        "User logon with misspelled or bad password",
                        "Account currently disabled",
                        "User has not been granted the requested logon type",
                        "The specified account's password has expired"
                    ])
                })
        
        elif event_info["id"] in [4720, 4726]:  # User account events
            target_user = random.choice(USERS)
            event.update({
                "TargetUserName": target_user,
                "TargetDomainName": "COMPANY",
                "TargetSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserName": random.choice(ADMIN_USERS),
                "SubjectDomainName": "COMPANY",
                "PrivilegeList": "SeSecurityPrivilege\nSeTakeOwnershipPrivilege"
            })
        
        elif event_info["id"] in [4728, 4729, 4732]:  # Group membership events
            event.update({
                "MemberName": f"CN={random.choice(USERS)},CN=Users,DC=company,DC=local",
                "MemberSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "TargetUserName": random.choice(["Administrators", "Users", "Power Users", "Remote Desktop Users"]),
                "TargetDomainName": "COMPANY",
                "TargetSid": f"S-1-5-32-{random.randint(500, 600)}",
                "SubjectUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserName": random.choice(ADMIN_USERS),
                "SubjectDomainName": "COMPANY"
            })
        
        elif event_info["id"] == 1102:  # Audit log cleared
            event.update({
                "SubjectUserSid": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}",
                "SubjectUserName": random.choice(ADMIN_USERS),
                "SubjectDomainName": "COMPANY"
            })
    
    elif log_channel == "System":
        if event_info["id"] in [7034, 7035, 7036, 7040]:  # Service events
            service_name = random.choice(SERVICES)
            event.update({
                "param1": service_name,
                "Binary": f"{''.join(f'{random.randint(0, 255):02x}' for _ in range(16))}",
                "ServiceName": service_name.replace(" ", "").lower(),
                "ServiceDisplayName": service_name
            })
            
            if event_info["id"] == 7034:  # Service crashed
                event.update({
                    "ExitCode": random.choice(["-1073741819", "-1073741512", "-2147024894"]),
                    "TerminationCount": random.randint(1, 5)
                })
        
        elif event_info["id"] in [6005, 6006]:  # Event log service
            event.update({
                "LogName": "System",
                "LogSize": random.randint(1000000, 50000000)
            })
        
        elif event_info["id"] in [1074, 6008, 6009]:  # Shutdown/startup events
            event.update({
                "UserName": random.choice(USERS + ADMIN_USERS),
                "ComputerName": computer_name,
                "ShutdownReason": random.choice([
                    "Other (Planned)",
                    "Hardware Maintenance (Planned)", 
                    "Operating System Reconfiguration (Planned)",
                    "Application Installation (Planned)"
                ]) if event_info["id"] == 1074 else None
            })
    
    elif log_channel == "Application":
        if event_info["id"] in [1000, 1001]:  # Application errors
            app_name = random.choice([
                "chrome.exe", "firefox.exe", "outlook.exe", "excel.exe",
                "word.exe", "notepad.exe", "calculator.exe", "explorer.exe"
            ])
            event.update({
                "ApplicationName": app_name,
                "ApplicationVersion": f"{random.randint(1, 20)}.{random.randint(0, 9)}.{random.randint(0, 9)}.{random.randint(1000, 9999)}",
                "ApplicationPath": f"C:\\Program Files\\{app_name}",
                "ModuleName": random.choice([app_name, "ntdll.dll", "kernel32.dll", "user32.dll"]),
                "ModuleVersion": f"{random.randint(6, 10)}.{random.randint(0, 9)}.{random.randint(0, 9)}.{random.randint(1000, 9999)}",
                "ExceptionCode": f"0x{random.choice(['c0000005', 'c0000374', 'c000013a']):s}",
                "FaultingModuleOffset": f"0x{random.randint(1000, 99999):05x}"
            })
    
    # Add common Windows event fields
    event.update({
        "Source": random.choice(["Microsoft-Windows-Security-Auditing", "Service Control Manager", "Application Error"]),
        "OpcodeName": random.choice(["Info", "Start", "Stop"]),
        "TaskName": event_info["name"],
        "ActivityID": f"{{{random.randint(10000000, 99999999):08x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{random.randint(100000000000, 999999999999):012x}}}",
        "RelatedActivityID": f"{{{random.randint(10000000, 99999999):08x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{random.randint(1000, 9999):04x}-{random.randint(100000000000, 999999999999):012x}}}",
        "UserID": f"S-1-5-21-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000000000, 9999999999)}-{random.randint(1000, 9999)}"
    })
    
    # Remove None values
    event = {k: v for k, v in event.items() if v is not None}
    
    return json.dumps(event, separators=(',', ':'))

if __name__ == "__main__":
    # Generate sample events
    print("Sample Microsoft Windows Event Log Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(microsoft_windows_eventlog_log())