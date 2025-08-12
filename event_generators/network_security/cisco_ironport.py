#!/usr/bin/env python3
"""
Cisco IronPort Email Security Appliance event generator
Generates synthetic Cisco IronPort ESA security logs in syslog format
"""
import random
from datetime import datetime, timezone, timedelta

# Anti-spam verdicts
ANTISPAM_VERDICTS = ["Negative", "Positive", "Suspected spam", "Bulk mail", "Marketing"]

# Anti-virus verdicts
ANTIVIRUS_VERDICTS = ["Clean", "Infected", "Quarantined", "Repaired", "Encrypted"]

# Email subjects
SUBJECTS = [
    "Quarterly report",
    "Meeting notes",
    "Invoice #12345",
    "Password reset request",
    "Urgent: Please review",
    "Your order has shipped",
    "Security alert",
    "Account verification required",
    "Congratulations! You won!",
    "Free software download"
]

# Domains
DOMAINS = [
    "example.com",
    "partner.com", 
    "customer.org",
    "supplier.net",
    "suspicious-domain.com",
    "phishing-site.org",
    "malware-delivery.net"
]

# Hostnames
HOSTNAMES = ["mail-esa1", "mail-esa2", "ironport-01", "esa-prod"]

def generate_email() -> str:
    """Generate email address"""
    names = ["alice", "bob", "charlie", "diana", "eve", "frank", "grace", "henry"]
    domain = random.choice(DOMAINS)
    return f"{random.choice(names)}@{domain}"

def generate_ip() -> str:
    """Generate IP address"""
    return f"{random.randint(1, 223)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

def generate_message_id() -> str:
    """Generate message ID"""
    return f"{random.randint(1000000, 9999999)}"

def cisco_ironport_log() -> str:
    """Generate a single Cisco IronPort email security event log in syslog format"""
    now = datetime.now(timezone.utc)
    event_time = now - timedelta(minutes=random.randint(0, 1440))
    
    timestamp = event_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    hostname = random.choice(HOSTNAMES)
    message_id = generate_message_id()
    from_addr = generate_email()
    to_addr = generate_email()
    subject = random.choice(SUBJECTS)
    src_ip = generate_ip()
    dst_ip = generate_ip()
    antispam_verdict = random.choice(ANTISPAM_VERDICTS)
    antivirus_verdict = random.choice(ANTIVIRUS_VERDICTS)
    
    # Determine if this is a threat
    is_threat = "suspicious" in from_addr or "phishing" in from_addr or "malware" in from_addr
    
    severity = "warn" if is_threat else "info"
    verdict = "BLOCKED" if is_threat or antispam_verdict == "Positive" or antivirus_verdict == "Infected" else "ACCEPTED"
    message_size = random.randint(1024, 10485760)
    attachment_count = random.randint(0, 5)
    connection_id = random.randint(1000, 9999)
    reputation_score = str(round(random.uniform(-10.0, 10.0), 1)) if random.random() > 0.5 else "null"
    
    # Generate syslog format
    log = (f'{timestamp} {hostname} facility=mail severity={severity} '
           f'message_id="{message_id}" from_address="{from_addr}" '
           f'to_address="{to_addr}" subject="{subject}" '
           f'src_ip="{src_ip}" dst_ip="{dst_ip}" '
           f'antispam_verdict="{antispam_verdict}" antivirus_verdict="{antivirus_verdict}" '
           f'verdict="{verdict}" message_size={message_size} '
           f'attachment_count={attachment_count} connection_id={connection_id} '
           f'reputation_score={reputation_score}')
    
    return log

# ATTR_FIELDS for AI-SIEM compatibility
ATTR_FIELDS = {
    "vendor": "cisco",
    "product": "ironport",
    "log_type": "email_security"
}

if __name__ == "__main__":
    # Generate sample events
    print("Sample Cisco IronPort Email Security Events:")
    print("=" * 50)
    for i in range(3):
        print(f"\nEvent {i+1}:")
        print(cisco_ironport_log())