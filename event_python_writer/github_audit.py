#!/usr/bin/env python3
"""
GitHub audit log event generator
"""
from __future__ import annotations
import random
import time
from datetime import datetime, timezone
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "GitHub",
    "dataSource.name": "GitHub Audit",
    "dataSource.category": "audit",
    "metadata.product.vendor_name": "GitHub",
    "metadata.product.name": "GitHub Audit",
    "metadata.version": "1.0.0",
    "class_uid": "8001",
    "class_name": "DevOps Activity",
    "category_uid": "8",
    "category_name": "System Activity",
    "activity_id": "1",
    "activity_name": "Repository Activity",
    "type_uid": "800101"
}

def github_audit_log() -> Dict:
    """Generate GitHub audit log event"""
    
    # Common actors/users
    actors = [
        "devuser", "admin", "buildbot", "security_team", 
        "john.doe", "jane.smith", "deploy_user", "ci_service"
    ]
    
    # Organizations
    orgs = [
        "acme-corp", "tech-startup", "enterprise-co",
        "open-source-org", "dev-team", "security-org"
    ]
    
    # Repositories
    repositories = [
        "new-repo", "legacy-repo", "app-service", "api-gateway",
        "frontend-app", "backend-service", "infrastructure", "configs"
    ]
    
    # GitHub actions with their activity mappings
    actions = [
        # Repository actions (activity_id: 1)
        {
            "action": "repo.create",
            "activity_id": 1,
            "activity_name": "Repository Create",
            "severity": 1,
            "desc_template": "Repository {org}/{repo} created"
        },
        {
            "action": "repo.delete", 
            "activity_id": 1,
            "activity_name": "Repository Delete",
            "severity": 3,
            "desc_template": "Attempt to delete repository {repo} {outcome}"
        },
        # Branch actions (activity_id: 2)
        {
            "action": "branch.protect",
            "activity_id": 2,
            "activity_name": "Branch Protection",
            "severity": 1,
            "desc_template": "Enabled branch protection on {repo}/main"
        },
        {
            "action": "branch.delete",
            "activity_id": 2,
            "activity_name": "Branch Delete",
            "severity": 2,
            "desc_template": "Branch {branch} deleted from {repo}"
        },
        # Code actions (activity_id: 3)
        {
            "action": "git.push",
            "activity_id": 3,
            "activity_name": "Code Push",
            "severity": 1,
            "desc_template": "Code pushed to {repo}"
        },
        {
            "action": "pull_request.merge",
            "activity_id": 3,
            "activity_name": "Pull Request Merge",
            "severity": 1,
            "desc_template": "Pull request merged in {repo}"
        },
        # Access actions (activity_id: 4)
        {
            "action": "repo.access",
            "activity_id": 4,
            "activity_name": "Repository Access",
            "severity": 2,
            "desc_template": "Repository access granted to {actor}"
        },
        {
            "action": "team.add_member",
            "activity_id": 4,
            "activity_name": "Team Member Add",
            "severity": 2,
            "desc_template": "User {actor} added to team"
        }
    ]
    
    # Outcomes with weights
    outcomes = [
        {"name": "success", "status_id": 1, "severity_modifier": 0, "weight": 8},
        {"name": "failure", "status_id": 2, "severity_modifier": 1, "weight": 2}
    ]
    
    # Client IPs
    client_ips = [
        "198.51.100.24", "203.0.113.10", "192.0.2.50",
        "198.51.100.100", "203.0.113.200", "192.168.1.50"
    ]
    
    # Generate event data
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    actor = random.choice(actors)
    org = random.choice(orgs)
    repository = random.choice(repositories)
    action_info = random.choice(actions)
    outcome = random.choices(outcomes, weights=[o["weight"] for o in outcomes], k=1)[0]
    client_ip = random.choice(client_ips)
    
    # Generate description based on action and outcome
    description = action_info["desc_template"].format(
        org=org,
        repo=repository,
        actor=actor,
        branch="main",
        outcome="denied due to policy" if outcome["name"] == "failure" else ""
    )
    
    # Adjust severity based on outcome
    final_severity = min(6, action_info["severity"] + outcome["severity_modifier"])
    
    # Create OCSF-compliant event
    event = {
        "timestamp": timestamp,
        "time": int(time.time() * 1000),
        "class_uid": 8001,
        "class_name": "DevOps Activity",
        "category_uid": 8,
        "category_name": "System Activity",
        "activity_id": action_info["activity_id"],
        "activity_name": action_info["activity_name"],
        "type_uid": 800100 + action_info["activity_id"],
        "severity_id": final_severity,
        "status_id": outcome["status_id"],
        
        "user": {
            "name": actor,
            "account_uid": actor,
            "account_type": "Service" if "bot" in actor or "service" in actor else "User"
        },
        
        "src_endpoint": {
            "ip": client_ip
        },
        
        "resource": {
            "name": repository,
            "type": "Repository",
            "uid": f"{org}/{repository}"
        },
        
        "status": outcome["name"],
        "message": description,
        
        "enrichments": {
            "organization": org,
            "action": action_info["action"],
            "repository_full_name": f"{org}/{repository}"
        },
        
        "metadata": {
            "tenant_uid": org,
            "version": "1.0.0",
            "product": {
                "vendor_name": "GitHub",
                "name": "GitHub Audit"
            }
        },
        
        "observables": [
            {
                "name": "user",
                "type": "User",
                "value": actor
            },
            {
                "name": "repository",
                "type": "Other", 
                "value": f"{org}/{repository}"
            },
            {
                "name": "src_ip",
                "type": "IP Address",
                "value": client_ip
            }
        ],
        
        **ATTR_FIELDS
    }
    
    return event


if __name__ == "__main__":
    print(github_audit_log())