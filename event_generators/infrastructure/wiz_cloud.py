#!/usr/bin/env python3
"""
Wiz Cloud Security event generator
"""
from __future__ import annotations
import random
import time
import uuid
from datetime import datetime, timezone
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Wiz",
    "dataSource.name": "Wiz Cloud Security",
    "dataSource.category": "security",
    "metadata.product.vendor_name": "Wiz",
    "metadata.product.name": "Wiz Cloud Security",
    "metadata.version": "1.0.0",
    "class_uid": "8002",
    "class_name": "Cloud Activity",
    "category_uid": "8",
    "category_name": "System Activity",
    "activity_id": "1",
    "activity_name": "Cloud Audit",
    "type_uid": "800201"
}

def wiz_cloud_log() -> Dict:
    """Generate Wiz Cloud Security audit event"""
    
    # Cloud actions with their activity mappings
    actions = [
        # Authentication actions (activity_id: 1)
        {
            "action": "Login",
            "activity_id": 1,
            "activity_name": "Login",
            "severity": 1,
            "desc": "User or service account login"
        },
        {
            "action": "Logout",
            "activity_id": 1,
            "activity_name": "Logout",
            "severity": 1,
            "desc": "User or service account logout"
        },
        # Resource creation (activity_id: 2)
        {
            "action": "CreateSAMLUser",
            "activity_id": 2,
            "activity_name": "Create User",
            "severity": 2,
            "desc": "SAML user creation"
        },
        {
            "action": "CreateServiceAccount",
            "activity_id": 2,
            "activity_name": "Create Service Account",
            "severity": 2,
            "desc": "Service account creation"
        },
        # User management (activity_id: 3)
        {
            "action": "UpdateUserRole",
            "activity_id": 3,
            "activity_name": "Update User",
            "severity": 2,
            "desc": "User role modification"
        },
        {
            "action": "DeleteUser",
            "activity_id": 3,
            "activity_name": "Delete User",
            "severity": 3,
            "desc": "User account deletion"
        },
        # Access control (activity_id: 4)
        {
            "action": "GrantAccess",
            "activity_id": 4,
            "activity_name": "Grant Access",
            "severity": 2,
            "desc": "Access permission granted"
        },
        {
            "action": "RevokeAccess",
            "activity_id": 4,
            "activity_name": "Revoke Access",
            "severity": 2,
            "desc": "Access permission revoked"
        }
    ]
    
    # Status outcomes
    statuses = [
        {"name": "SUCCESS", "status_id": 1, "severity_modifier": 0, "weight": 7},
        {"name": "FAILED", "status_id": 2, "severity_modifier": 1, "weight": 3}
    ]
    
    # Service accounts
    service_accounts = [
        {"id": "xNgww7tONKtQK6zw", "name": "ax-us"},
        {"id": "service_account_id", "name": "Integration"},
        {"id": "yBhxz8uPOLrRL7xz", "name": "security-scanner"},
        {"id": "zChyz9vQPMsRM8yz", "name": "backup-service"},
        {"id": "aDizA0wRQNtRN9zA", "name": "monitoring"}
    ]
    
    # Users (nullable)
    users = [
        None, None, None,  # Most events are service account based
        {"id": "user123", "email": "john.doe@example.com"},
        {"id": "user456", "email": "jane.smith@example.com"},
        {"id": "admin789", "email": "admin@example.com"}
    ]
    
    # Source IPs
    source_ips = [
        "1.2.3.4", "5.6.7.8", "9.10.11.12",
        "198.51.100.50", "203.0.113.75", "192.0.2.100"
    ]
    
    # User agents
    user_agents = [
        "node", "python-requests/2.31.0", "curl/7.88.1",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "WizCLI/1.2.3", "terraform/1.5.0"
    ]
    
    # Generate event data
    event_id = str(uuid.uuid4())
    request_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%fZ')[:-3] + 'Z'
    action_info = random.choice(actions)
    status = random.choices(statuses, weights=[s["weight"] for s in statuses], k=1)[0]
    service_account = random.choice(service_accounts)
    user = random.choice(users)
    source_ip = random.choice(source_ips)
    user_agent = random.choice(user_agents)
    
    # Action-specific parameters
    action_parameters = {}
    if action_info["action"] == "CreateSAMLUser":
        action_parameters = {
            "filterBy": {"search": f"Test_{random.randint(1000000000000, 9999999999999)}_"},
            "first": 500
        }
    elif action_info["action"] == "Login":
        action_parameters = {
            "clientID": f"{random.randint(100000000000000000000, 999999999999999999999)}",
            "name": "Integration",
            "products": ["*"],
            "role": "admin" if random.random() < 0.3 else "readonly",
            "scopes": ["read:issues", "read:vulnerabilities", "admin:audit"],
            "userID": service_account["id"],
            "userpoolID": f"us-east-2_{random.randint(1000000000, 9999999999)}"
        }
    elif "User" in action_info["action"]:
        action_parameters = {
            "userEmail": f"user{random.randint(100, 999)}@example.com",
            "role": random.choice(["admin", "user", "readonly"]),
            "permissions": random.choice([["read"], ["read", "write"], ["admin"]])
        }
    
    # Add error details for failed events
    if status["name"] == "FAILED":
        action_parameters["error"] = random.choice([
            "failed authenticating service account",
            "insufficient permissions",
            "rate limit exceeded",
            "invalid request format",
            "resource not found"
        ])
    
    # Adjust severity based on status
    final_severity = min(6, action_info["severity"] + status["severity_modifier"])
    
    # Create OCSF-compliant event
    event = {
        "timestamp": timestamp,
        "time": int(time.time() * 1000),
        "class_uid": 8002,
        "class_name": "Cloud Activity",
        "category_uid": 8,
        "category_name": "System Activity",
        "activity_id": action_info["activity_id"],
        "activity_name": action_info["activity_name"],
        "type_uid": 800200 + action_info["activity_id"],
        "severity_id": final_severity,
        "status_id": status["status_id"],
        
        "src_endpoint": {
            "ip": source_ip
        },
        
        "user": {
            "name": user["email"].split("@")[0] if user else None,
            "email_addr": user["email"] if user else None,
            "account_uid": user["id"] if user else None,
            "account_type": "User" if user else None
        } if user else None,
        
        "service_account": {
            "uid": service_account["id"],
            "name": service_account["name"],
            "account_type": "Service"
        },
        
        "cloud": {
            "provider": "Wiz",
            "region": "us-east-1"
        },
        
        "status": status["name"],
        "message": action_info["desc"],
        
        "enrichments": {
            "action": action_info["action"],
            "action_parameters": action_parameters,
            "user_agent": user_agent
        },
        
        "metadata": {
            "correlation_uid": event_id,
            "request_id": request_id,
            "version": "1.0.0",
            "product": {
                "vendor_name": "Wiz",
                "name": "Wiz Cloud Security"
            }
        },
        
        "observables": [
            {
                "name": "src_ip",
                "type": "IP Address",
                "value": source_ip
            },
            {
                "name": "service_account",
                "type": "User",
                "value": service_account["name"]
            },
            {
                "name": "action",
                "type": "Other",
                "value": action_info["action"]
            }
        ],
        
        **ATTR_FIELDS
    }
    
    return event


if __name__ == "__main__":
    print(wiz_cloud_log())