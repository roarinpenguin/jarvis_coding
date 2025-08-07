#!/usr/bin/env python3
"""
HYPR authentication event generator
Generates synthetic HYPR FIDO2 and passwordless authentication events
"""
import json
import random
from datetime import datetime, timezone, timedelta

ATTR_FIELDS = {
    "dataSource.vendor": "HYPR",
    "dataSource.name": "HYPR Authentication",
    "dataSource.category": "security",
}

EVENT_TYPES = ["REGISTRATION", "AUTHENTICATION"]
USERS = ["alice@example.com", "bob@example.com", "charlie@example.com", "admin@example.com"]
DEVICES = ["iPhone13", "Windows10", "MacBookPro", "Android", "iPad"]
AUTHENTICATORS = ["FIDO2", "Biometric", "PIN"]
FACTORS = ["passwordless", "FIDO2", "biometric", "pin"]

ERROR_CODES = [
    "1203003", "1203004", "1203005", "AUTH_FAILED", "DEVICE_NOT_REGISTERED"
]

ERROR_MESSAGES = [
    "FIDO2_SETTINGS_NULL_EC",
    "DEVICE_NOT_FOUND",
    "INVALID_AUTHENTICATOR", 
    "USER_NOT_FOUND",
    "AUTHENTICATION_TIMEOUT"
]

def generate_session_id():
    """Generate a session ID."""
    import uuid
    return str(uuid.uuid4())

def hypr_auth_log() -> str:
    """Generate a single HYPR authentication event log"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 60))
    
    event_type = random.choice(EVENT_TYPES)
    user = random.choice(USERS)
    device = random.choice(DEVICES)
    is_successful = random.choice([True, True, True, False])  # 75% success rate
    
    timestamp = event_time.isoformat().replace('+00:00', 'Z')
    log_parts = [
        f'{timestamp} HYPR',
        f'eventType="{event_type}"',
        f'user="{user}"',
        f'device="{device}"',
        f'isSuccessful={str(is_successful).lower()}'
    ]
    
    if event_type == "REGISTRATION":
        authenticator = random.choice(AUTHENTICATORS)
        log_parts.append(f'authenticator="{authenticator}"')
        
        if is_successful:
            message = f"User registered new {authenticator} credential"
        else:
            error_code = random.choice(ERROR_CODES)
            error = random.choice(ERROR_MESSAGES)
            log_parts.append(f'errorCode="{error_code}"')
            log_parts.append(f'error="{error}"')
            message = f"Registration failed - {error.lower().replace('_', ' ')}"
    
    else:  # AUTHENTICATION
        factor = random.choice(FACTORS)
        log_parts.append(f'factor="{factor}"')
        
        if is_successful:
            session_id = generate_session_id()
            log_parts.append(f'sessionId="{session_id}"')
            message = f"{factor.capitalize()} login completed"
        else:
            error_code = random.choice(ERROR_CODES)
            error = random.choice(ERROR_MESSAGES)
            log_parts.append(f'errorCode="{error_code}"')
            log_parts.append(f'error="{error}"')
            
            if "FIDO2" in error:
                message = "Authentication failed due to missing relying party settings"
            elif "DEVICE_NOT_FOUND" in error:
                message = "Authentication failed - device not registered"
            else:
                message = f"Authentication failed - {error.lower().replace('_', ' ')}"
    
    log_parts.append(f'message="{message}"')
    return ' '.join(log_parts)

if __name__ == "__main__":
    print("Sample HYPR Authentication Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(hypr_auth_log())