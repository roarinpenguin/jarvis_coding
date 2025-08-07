#!/usr/bin/env python3
"""
Cohesity backup event generator
Generates synthetic Cohesity backup system events
"""
import random
from datetime import datetime, timezone, timedelta

ATTR_FIELDS = {
    "dataSource.vendor": "Cohesity",
    "dataSource.name": "Cohesity Backup",
    "dataSource.category": "system",
}

# Backup job types
JOB_NAMES = [
    "Daily_VM_Backup", "Weekly_SQL_Backup", "Monthly_Archive", "Adhoc_DB_Backup",
    "Exchange_Backup", "File_Server_Backup", "NAS_Backup", "Cloud_Sync", 
    "Disaster_Recovery", "Compliance_Archive"
]

# Object types being backed up
OBJECT_NAMES = [
    "vm-Prod01", "vm-Web01", "vm-App01", "db-sql01", "db-oracle01",
    "exchange-mail01", "nas-files01", "fs-data01", "vm-Dev01", "vm-Test01"
]

# Backup statuses
STATUSES = ["STARTED", "SUCCESS", "FAILED", "WARNING"]

# Initiators
INITIATORS = ["schedule", "manual", "policy", "admin"]

# Error messages for failed backups
ERROR_MESSAGES = [
    "Snapshot creation failed",
    "Network timeout during transfer", 
    "Insufficient storage space",
    "VM powered off during backup",
    "Database locked for exclusive use",
    "Authentication failure to source",
    "Disk read error encountered"
]

def generate_run_id():
    """Generate a run ID."""
    return f"r-{random.randint(1000, 9999)}"

def generate_duration():
    """Generate backup duration in HH:MM:SS format."""
    hours = random.randint(0, 8)
    minutes = random.randint(0, 59)
    seconds = random.randint(0, 59)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def generate_bytes_protected():
    """Generate bytes protected with unit."""
    value = random.randint(1, 2000)
    unit = random.choice(["MB", "GB", "TB"])
    return f"{value}{unit}"

def generate_throughput():
    """Generate throughput with unit."""
    value = random.randint(1, 50)
    unit = random.choice(["MB/min", "GB/min"])
    return f"{value}{unit}"

def cohesity_backup_log() -> str:
    """Generate a single Cohesity backup event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 240))
    
    # Generate basic event components
    run_id = generate_run_id()
    job_name = random.choice(JOB_NAMES)
    object_name = random.choice(OBJECT_NAMES)
    status = random.choice(STATUSES)
    initiator = random.choice(INITIATORS)
    
    # Build log components
    timestamp = event_time.isoformat().replace('+00:00', 'Z')
    log_parts = [
        f'{timestamp} Cohesity',
        f'runId="{run_id}"',
        f'jobName="{job_name}"',
        f'objectName="{object_name}"',
        f'status="{status}"'
    ]
    
    # Add status-specific fields
    if status in ["SUCCESS", "FAILED", "WARNING"]:
        duration = generate_duration()
        log_parts.append(f'duration="{duration}"')
        
        if status == "SUCCESS":
            bytes_protected = generate_bytes_protected()
            throughput = generate_throughput()
            log_parts.append(f'bytesProtected={bytes_protected}')
            log_parts.append(f'throughput="{throughput}"')
            
        elif status == "FAILED":
            error = random.choice(ERROR_MESSAGES)
            log_parts.append(f'error="{error}"')
    
    # Add initiator for STARTED events
    if status == "STARTED":
        log_parts.append(f'initiatedBy="{initiator}"')
    
    # Generate appropriate message
    if status == "STARTED":
        message = "Protection run started"
    elif status == "SUCCESS":
        message = "Backup completed successfully"
    elif status == "FAILED":
        if "error" in locals():
            message = f"Backup run failed during {error.lower().split()[0]} {error.lower().split()[1] if len(error.split()) > 1 else 'operation'}"
        else:
            message = "Backup run failed"
    elif status == "WARNING":
        message = "Backup completed with warnings"
    else:
        message = "Backup operation in progress"
    
    log_parts.append(f'message="{message}"')
    
    return ' '.join(log_parts)

if __name__ == "__main__":
    # Generate sample events
    print("Sample Cohesity Backup Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(cohesity_backup_log())