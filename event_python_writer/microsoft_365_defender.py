#!/usr/bin/env python3
"""
Microsoft 365 Defender event generator
Generates synthetic Microsoft 365 Defender endpoint security logs
"""
import json
import random
import time
from datetime import datetime, timezone, timedelta
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Microsoft",
    "dataSource.name": "Microsoft 365 Defender",
    "dataSource.category": "security",
}

# Action types
ACTION_TYPES = [
    "ProcessCreated",
    "NetworkConnectionFailed", 
    "NetworkConnectionSuccess",
    "Quarantine",
    "FileCreated",
    "FileDeleted",
    "RegistryValueSet",
    "PowerShellCommand",
    "SuspiciousProcess",
    "MalwareDetected"
]

# Device names
DEVICE_NAMES = [
    "DESKTOP-01", "DESKTOP-02", "DESKTOP-03",
    "LAPTOP-01", "LAPTOP-02", "LAPTOP-03",
    "SERVER-01", "SERVER-02", "WKS-001", "WKS-002"
]

# Account names
ACCOUNT_NAMES = ["alice", "bob", "charlie", "admin", "system", "service"]

# Account domains
ACCOUNT_DOMAINS = ["CONTOSO", "WORKGROUP", "NT AUTHORITY"]

# File names
FILE_NAMES = [
    "chrome.exe", "powershell.exe", "cmd.exe", "notepad.exe",
    "malicious.exe", "virus.dll", "trojan.scr", "document.pdf",
    "script.ps1", "config.xml", "data.txt"
]

# Folder paths
FOLDER_PATHS = [
    "C:\\Windows\\System32",
    "C:\\Program Files\\Google\\Chrome\\Application", 
    "C:\\Users\\alice\\Downloads",
    "C:\\Users\\bob\\Documents",
    "C:\\Temp",
    "C:\\Windows\\Temp"
]

# Process names
PROCESS_NAMES = [
    "chrome.exe", "firefox.exe", "powershell.exe", "cmd.exe",
    "explorer.exe", "svchost.exe", "winlogon.exe", "lsass.exe"
]

# Remote URLs
REMOTE_URLS = [
    "https://google.com",
    "https://microsoft.com",
    "https://malicious.example.com",
    "https://c2-server.net",
    "https://phishing-site.org"
]

# Malware detection IDs
DETECTION_IDS = [
    "Trojan:Win32/Phish",
    "Virus:Win32/Malware",
    "Adware:Win32/Suspicious", 
    "Ransomware:Win32/Cryptor",
    "Backdoor:Win32/Remote"
]

def generate_device_id() -> str:
    """Generate device ID"""
    return f"{random.randint(1000000000000000, 9999999999999999):016x}".upper()

def generate_hash() -> str:
    """Generate SHA1 hash"""
    return ''.join(random.choices('0123456789abcdef', k=40))

def generate_md5() -> str:
    """Generate MD5 hash"""
    return ''.join(random.choices('0123456789abcdef', k=32))

def generate_ip() -> str:
    """Generate IP address"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def microsoft_365_defender_log() -> str:
    """Generate a single Microsoft 365 Defender event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 1440))
    
    action_type = random.choice(ACTION_TYPES)
    device_name = random.choice(DEVICE_NAMES)
    device_id = generate_device_id()
    account_name = random.choice(ACCOUNT_NAMES)
    account_domain = random.choice(ACCOUNT_DOMAINS)
    
    # Base event structure
    event = {
        "Timestamp": event_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "DeviceName": device_name,
        "DeviceId": device_id,
        "AccountName": account_name,
        "AccountDomain": account_domain,
        "ActionType": action_type,
        **ATTR_FIELDS
    }
    
    # Add specific fields based on action type
    if action_type == "ProcessCreated":
        event.update({
            "ProcessId": random.randint(1000, 65535),
            "ProcessName": random.choice(PROCESS_NAMES),
            "ProcessCommandLine": f"\"{random.choice(FOLDER_PATHS)}\\{random.choice(PROCESS_NAMES)}\" --args",
            "ParentProcessId": random.randint(100, 999),
            "ParentProcessName": "explorer.exe",
            "FolderPath": random.choice(FOLDER_PATHS),
            "SHA1": generate_hash(),
            "MD5": generate_md5()
        })
        
    elif "NetworkConnection" in action_type:
        event.update({
            "RemoteUrl": random.choice(REMOTE_URLS),
            "RemoteIP": generate_ip(),
            "RemotePort": random.choice([80, 443, 8080, 8443, 9999]),
            "Protocol": random.choice(["HTTP", "HTTPS", "TCP", "UDP"]),
            "ProcessName": random.choice(PROCESS_NAMES),
            "ProcessCommandLine": f"\"{random.choice(FOLDER_PATHS)}\\{random.choice(PROCESS_NAMES)}\"",
            "FailureReason": "Domain blocked by policy" if "Failed" in action_type else None
        })
        
    elif action_type == "Quarantine" or action_type == "MalwareDetected":
        event.update({
            "FileName": random.choice(FILE_NAMES),
            "FolderPath": random.choice(FOLDER_PATHS),
            "SHA1": generate_hash(),
            "MD5": generate_md5(),
            "DetectionId": random.choice(DETECTION_IDS),
            "AdditionalFields": {
                "ThreatName": random.choice(DETECTION_IDS),
                "Severity": random.choice(["Low", "Medium", "High", "Critical"])
            }
        })
        
    elif "File" in action_type:
        event.update({
            "FileName": random.choice(FILE_NAMES),
            "FolderPath": random.choice(FOLDER_PATHS),
            "SHA1": generate_hash(),
            "MD5": generate_md5()
        })
        
    elif action_type == "PowerShellCommand":
        event.update({
            "ProcessName": "powershell.exe",
            "ProcessCommandLine": "powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"Get-Process\"",
            "FolderPath": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0"
        })
    
    # Remove None values
    event = {k: v for k, v in event.items() if v is not None}
    
    return json.dumps(event, separators=(',', ':'))

if __name__ == "__main__":
    # Generate sample events
    print("Sample Microsoft 365 Defender Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(microsoft_365_defender_log())