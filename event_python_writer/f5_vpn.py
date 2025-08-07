#!/usr/bin/env python3
"""
F5 VPN event generator
Generates synthetic F5 VPN session events
"""
import random
from datetime import datetime, timezone, timedelta

ATTR_FIELDS = {
    "dataSource.vendor": "F5",
    "dataSource.name": "F5 VPN", 
    "dataSource.category": "network",
}

# VPN events
EVENTS = ["SESSION_START", "SESSION_END", "SESSION_DENIED"]

# Users
USERS = ["alice", "bob", "charlie", "diana", "admin", "service_account"]

# Client devices
DEVICES = ["Windows10", "MacOS", "iOS", "Android", "Linux"]

# Session end reasons
END_REASONS = ["USER_LOGOUT", "IDLE_TIMEOUT", "ADMIN_TERMINATE", "CONNECTION_LOST", "POLICY_VIOLATION"]

def get_random_ip():
    """Generate a random IP address."""
    if random.random() < 0.7:  # 70% external IPs for VPN
        return f"198.51.100.{random.randint(1, 255)}"
    else:
        return f"203.0.113.{random.randint(1, 255)}"

def generate_session_id():
    """Generate a session ID."""
    return f"sid-{random.randint(100, 999):03d}"

def generate_duration():
    """Generate session duration in HH:MM:SS format."""
    hours = random.randint(0, 12)
    minutes = random.randint(0, 59) 
    seconds = random.randint(0, 59)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def generate_traffic_bytes(duration_str):
    """Generate realistic traffic bytes based on session duration."""
    if not duration_str:
        return 0, 0
    
    # Parse duration to get total minutes
    h, m, s = map(int, duration_str.split(':'))
    total_minutes = h * 60 + m + s / 60
    
    # Generate bytes based on usage patterns
    if total_minutes < 10:  # Short session - minimal traffic
        bytes_in = random.randint(1000000, 50000000)  # 1-50 MB
        bytes_out = random.randint(500000, 20000000)  # 0.5-20 MB
    elif total_minutes < 60:  # Medium session
        bytes_in = random.randint(50000000, 200000000)  # 50-200 MB
        bytes_out = random.randint(20000000, 100000000)  # 20-100 MB
    else:  # Long session - heavy usage
        bytes_in = random.randint(200000000, 1000000000)  # 200MB-1GB
        bytes_out = random.randint(100000000, 500000000)  # 100-500 MB
    
    return bytes_in, bytes_out

def f5_vpn_log() -> str:
    """Generate a single F5 VPN event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 120))
    
    # Generate basic components
    session_id = generate_session_id()
    user = random.choice(USERS)
    client_ip = get_random_ip()
    event = random.choice(EVENTS)
    device = random.choice(DEVICES)
    
    # Build log components
    timestamp = event_time.isoformat().replace('+00:00', 'Z')
    log_parts = [
        f'{timestamp} F5VPN',
        f'session_id="{session_id}"',
        f'user="{user}"',
        f'client_ip="{client_ip}"'
    ]
    
    # Add event-specific fields
    if event == "SESSION_START":
        start_time = event_time.isoformat().replace('+00:00', 'Z')
        log_parts.append(f'start_time="{start_time}"')
        log_parts.append(f'event="{event}"')
        log_parts.append(f'device="{device}"')
        message = "VPN session established"
        
    elif event == "SESSION_END":
        duration = generate_duration()
        bytes_in, bytes_out = generate_traffic_bytes(duration)
        reason = random.choice(END_REASONS)
        
        log_parts.append(f'bytes_in={bytes_in}')
        log_parts.append(f'bytes_out={bytes_out}') 
        log_parts.append(f'duration="{duration}"')
        log_parts.append(f'event="{event}"')
        log_parts.append(f'reason="{reason}"')
        
        if reason == "USER_LOGOUT":
            message = "User terminated VPN session"
        elif reason == "IDLE_TIMEOUT":
            message = "Session deleted due to user inactivity"
        elif reason == "ADMIN_TERMINATE":
            message = "Session terminated by administrator"
        elif reason == "CONNECTION_LOST":
            message = "Session ended due to connection failure"
        else:
            message = "Session terminated due to policy violation"
            
    else:  # SESSION_DENIED
        log_parts.append(f'event="{event}"')
        log_parts.append(f'device="{device}"')
        denial_reason = random.choice([
            "AUTHENTICATION_FAILED", 
            "POLICY_VIOLATION", 
            "MAX_SESSIONS_EXCEEDED",
            "INVALID_CERTIFICATE"
        ])
        log_parts.append(f'reason="{denial_reason}"')
        
        if denial_reason == "AUTHENTICATION_FAILED":
            message = "VPN access denied - authentication failure"
        elif denial_reason == "POLICY_VIOLATION":
            message = "VPN access denied - policy violation"
        elif denial_reason == "MAX_SESSIONS_EXCEEDED":
            message = "VPN access denied - maximum concurrent sessions exceeded"
        else:
            message = "VPN access denied - invalid certificate"
    
    log_parts.append(f'message="{message}"')
    
    return ' '.join(log_parts)

if __name__ == "__main__":
    # Generate sample events
    print("Sample F5 VPN Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(f5_vpn_log())