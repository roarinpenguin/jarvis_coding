#!/usr/bin/env python3
"""
Axway SFTP event generator
Generates synthetic Axway SFTP file transfer events
"""
import random
from datetime import datetime, timezone, timedelta

ATTR_FIELDS = {
    "dataSource.vendor": "Axway",
    "dataSource.name": "Axway SFTP",
    "dataSource.category": "system",
}

# SFTP event types
EVENTS = ["LOGIN", "UPLOAD", "DOWNLOAD", "DELETE", "RENAME", "LOGOUT"]

# Common file paths and names
FILE_PATHS = [
    "/incoming/report.csv", "/incoming/data.xml", "/incoming/batch_001.txt",
    "/outgoing/ack.txt", "/outgoing/response.json", "/outgoing/summary.pdf",
    "/archive/old_data.zip", "/temp/processing.tmp", "/uploads/document.docx",
    "/downloads/export.xlsx", "/processed/final_report.csv"
]

# User names
USERS = ["sftp_user", "batch_user", "backup_user", "sync_user", "transfer_user", "service_account"]

# Results
RESULTS = ["SUCCESS", "FAILURE"]

def get_random_ip():
    """Generate a random IP address."""
    if random.random() < 0.8:  # 80% internal IPs
        return f"10.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"
    else:  # External IPs
        return f"198.51.100.{random.randint(1, 255)}"

def generate_file_size():
    """Generate realistic file size in bytes."""
    size_type = random.choice(["small", "medium", "large"])
    if size_type == "small":
        return random.randint(1024, 50000)  # 1KB - 50KB
    elif size_type == "medium":
        return random.randint(50000, 10000000)  # 50KB - 10MB  
    else:
        return random.randint(10000000, 1000000000)  # 10MB - 1GB

def axway_sftp_log() -> str:
    """Generate a single Axway SFTP event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 60))
    
    # Generate session ID
    session_id = f"sftp-{random.randint(1000, 9999)}"
    
    # Select user and event
    user = random.choice(USERS)
    event = random.choice(EVENTS)
    
    # Get IP address
    remote_ip = get_random_ip()
    
    # Determine result (90% success rate)
    result = "SUCCESS" if random.random() < 0.9 else "FAILURE"
    
    # Build log components
    timestamp = event_time.isoformat().replace('+00:00', 'Z')
    log_parts = [
        f'{timestamp} AxwaySFTP',
        f'session_id="{session_id}"',
        f'user="{user}"',
        f'event="{event}"'
    ]
    
    # Add file-specific fields for file operations
    if event in ["UPLOAD", "DOWNLOAD", "DELETE", "RENAME"]:
        file_path = random.choice(FILE_PATHS)
        log_parts.append(f'filePath="{file_path}"')
        
        if event in ["UPLOAD", "DOWNLOAD"]:
            file_size = generate_file_size()
            log_parts.append(f'fileSize={file_size}')
            # For successful transfers, bytes transferred equals file size
            bytes_transferred = file_size if result == "SUCCESS" else random.randint(0, file_size)
            log_parts.append(f'bytesTransferred={bytes_transferred}')
    
    # Add remote IP for LOGIN events
    if event == "LOGIN":
        log_parts.append(f'remote_ip="{remote_ip}"')
    
    # Add result and message
    log_parts.append(f'result="{result}"')
    
    # Generate appropriate message
    if event == "LOGIN":
        if result == "SUCCESS":
            auth_method = random.choice(["public key", "password", "certificate"])
            message = f"User authenticated via {auth_method}"
        else:
            message = "Authentication failed"
    elif event == "UPLOAD":
        if result == "SUCCESS":
            message = "File uploaded"
        else:
            message = "Upload failed - insufficient permissions"
    elif event == "DOWNLOAD":
        if result == "SUCCESS":
            message = "File downloaded"
        else:
            message = "Download failed - file not found"
    elif event == "DELETE":
        if result == "SUCCESS":
            message = "File deleted"
        else:
            message = "Delete failed - file in use"
    elif event == "RENAME":
        if result == "SUCCESS":
            message = "File renamed"
        else:
            message = "Rename failed - target exists"
    else:  # LOGOUT
        message = "User disconnected"
    
    log_parts.append(f'message="{message}"')
    
    return ' '.join(log_parts)

if __name__ == "__main__":
    # Generate sample events
    print("Sample Axway SFTP Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(axway_sftp_log())