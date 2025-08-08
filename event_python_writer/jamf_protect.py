#!/usr/bin/env python3
"""
Jamf Protect event generator
Generates synthetic Jamf Protect endpoint security events in syslog format
"""
import random
from datetime import datetime, timezone, timedelta

# SentinelOne AI-SIEM specific field attributes
ATTR_FIELDS = {
    "dataSource.vendor": "Jamf",
    "dataSource.name": "Jamf Protect",
    "dataSource.category": "security"
}

# Event types
EVENT_TYPES = ["ProcessExecution", "MalwareDetection", "USBDevice", "FileAccess", "NetworkConnection"]

# Computer IDs
COMPUTER_IDS = ["mac-001", "mac-002", "mac-003", "mac-004", "mac-005"]

# Users
USERS = ["alice", "bob", "carol", "admin", "guest"]

# Processes
PROCESSES = [
    "/Applications/Firefox.app/Contents/MacOS/firefox",
    "/Applications/Chrome.app/Contents/MacOS/Google Chrome", 
    "/Applications/Safari.app/Contents/MacOS/Safari",
    "/Applications/TextEdit.app/Contents/MacOS/TextEdit",
    "/Applications/Terminal.app/Contents/MacOS/Terminal",
    "/usr/bin/ssh", "/usr/bin/curl", "/bin/bash", "/usr/bin/python3"
]

# Verdicts
VERDICTS = ["allowed", "blocked", "quarantined", "flagged"]

# Messages
MESSAGES = [
    "User launched Firefox", "User launched Chrome", "User opened Terminal",
    "SSH connection established", "File download detected", "Process executed",
    "Network connection blocked", "Suspicious activity detected"
]

def jamf_protect_log() -> str:
    """Generate a single Jamf Protect event log in syslog format"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 1440))
    
    timestamp = event_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z"  # Include milliseconds
    event_type = random.choice(EVENT_TYPES)
    computer_id = random.choice(COMPUTER_IDS)
    user = random.choice(USERS)
    process_name = random.choice(PROCESSES)
    
    # Generate SHA256 hash (simplified)
    sha256 = ''.join(random.choices('abcdef0123456789', k=64))
    verdict = random.choice(VERDICTS)
    message = random.choice(MESSAGES)
    
    # Generate syslog format matching the original test event
    log = (f'{timestamp} JamfProtect eventType="{event_type}" '
           f'computerId="{computer_id}" user="{user}" '
           f'processName="{process_name}" sha256="{sha256}" '
           f'verdict="{verdict}" message="{message}"')
    
    return log

if __name__ == "__main__":
    # Generate sample events
    print("Sample Jamf Protect Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(jamf_protect_log())