#!/usr/bin/env python3
"""
Jamf Protect event generator
Generates synthetic Jamf Protect endpoint security events
"""
import random
from datetime import datetime, timezone, timedelta

ATTR_FIELDS = {
    "dataSource.vendor": "Jamf",
    "dataSource.name": "Jamf Protect",
    "dataSource.category": "security",
}

EVENT_TYPES = ["ProcessExecution", "MalwareDetection", "USBDevice"]
COMPUTER_IDS = ["mac-001", "mac-002", "mac-003", "mac-004"]
USERS = ["alice", "bob", "carol", "admin"]

PROCESSES = [
    "/Applications/Firefox.app/Contents/MacOS/firefox",
    "/Applications/Chrome.app/Contents/MacOS/Google Chrome",
    "/usr/bin/ssh", "/usr/bin/curl", "/bin/bash"
]

FILE_PATHS = [
    "/Users/alice/Downloads/EicarTestFile",
    "/Users/bob/Downloads/suspicious.dmg",
    "/tmp/malware.sh", "/Users/admin/Desktop/virus.exe"
]

USB_DEVICES = [
    {"name": "SanDisk Cruzer", "vendor": "0781", "product": "5567"},
    {"name": "Kingston DataTraveler", "vendor": "0951", "product": "1666"},
    {"name": "External HDD", "vendor": "1058", "product": "25a2"}
]

VERDICTS = ["allowed", "quarantined", "blocked"]

def generate_sha256():
    """Generate a fake SHA256 hash."""
    return f"{''.join(random.choices('abcdef0123456789', k=64))}"

def jamf_protect_log() -> str:
    """Generate a single Jamf Protect event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 60))
    
    event_type = random.choice(EVENT_TYPES)
    computer_id = random.choice(COMPUTER_IDS)
    user = random.choice(USERS)
    verdict = random.choice(VERDICTS)
    
    timestamp = event_time.isoformat().replace('+00:00', 'Z')
    log_parts = [
        f'{timestamp} JamfProtect',
        f'eventType="{event_type}"',
        f'computerId="{computer_id}"',
        f'user="{user}"'
    ]
    
    if event_type == "ProcessExecution":
        process = random.choice(PROCESSES)
        sha256 = generate_sha256()
        log_parts.extend([
            f'processName="{process}"',
            f'sha256="{sha256}"'
        ])
        
        app_name = process.split('/')[-1]
        if app_name == "firefox":
            app_name = "Firefox"
        elif "Chrome" in process:
            app_name = "Chrome"
        message = f"User launched {app_name}"
        
    elif event_type == "MalwareDetection":
        file_path = random.choice(FILE_PATHS)
        sha256 = "44d88612fea8a8f36de82e1278abb02f" if "EicarTestFile" in file_path else generate_sha256()
        verdict = random.choice(["quarantined", "blocked"])
        
        log_parts.extend([
            f'filePath="{file_path}"',
            f'sha256="{sha256}"'
        ])
        
        if "EicarTestFile" in file_path:
            message = "EICAR test file detected and quarantined"
        else:
            message = f"Malware detected and {verdict}"
    
    else:  # USBDevice
        device = random.choice(USB_DEVICES)
        action = random.choice(["allowed", "blocked"])
        
        log_parts.extend([
            f'deviceName="{device["name"]}"',
            f'vendorId="{device["vendor"]}"',
            f'productId="{device["product"]}"',
            f'action="{action}"'
        ])
        
        if action == "allowed":
            message = f"{device['name']} device connected"
        else:
            message = "USB mass storage device blocked by policy"
        verdict = action
    
    log_parts.extend([
        f'verdict="{verdict}"',
        f'message="{message}"'
    ])
    
    return ' '.join(log_parts)

if __name__ == "__main__":
    print("Sample Jamf Protect Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(jamf_protect_log())