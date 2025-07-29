#/usr/bin/python
# NOT WORKING 
"""
Azure AD / Entra ID faux‑log generator
--------------------------------------

Builds JSON payloads that satisfy the SentinelOne AI‑SIEM Azure AD parser
rules supplied by the user.  Two broad behaviour pools are modelled:

* Benign  – routine sign‑ins & directory changes initiated by normal users.
* Malicious – “Haxorsaurus” adversary abusing Jean’s tenant: creates a
  Bedrock‑style service principal, spins up a SageMaker‑analogue app and
  attempts a massive DynamoDB export (mirroring the CloudTrail scenarios).

The module exposes:

* ``azure_ad_log()`` – just‑in‑time JSON record.
* ``SOURCETYPE`` – constant string used by *hec_sender.py*.

Payload example:

Wrapper payload sent to HEC::

    {
        "time": 1753162831,
        "event": {
            "activityDateTime": "...",
            "activityDisplayName": "...",
            "initiatedByUserId": "...",
            "eventCategory": "...",
            "targetResources": [ { ... } ],
            ...
        },
        "fields": {
            "dataSource.category": "security",
            "dataSource.name": "Azure AD",
            "dataSource.vendor": "Azure"
        }
    }
"""

from __future__ import annotations

import random
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

# SOURCETYPE = "azure_entra_id"

# --------------------------------------------------------------------------- #
#  Static pools                                                               #
# --------------------------------------------------------------------------- #
_NOW = datetime.now(tz=timezone.utc)

_USERS = [
    {
        "userPrincipalName": "jean@example.com",
        "displayName": "Jean Thompson",
        "userId": "a812de4e-d47c-4f55-9a46-0f6e6e8b1dea",
        "ip": "80.91.32.22",
        "department": "Finance",
    },
    {
        "userPrincipalName": "alex@example.com",
        "displayName": "Alex Rivera",
        "userId": "4231c2dc-53bc-4428-83fd-38a9f7e3e415",
        "ip": "81.17.5.101",
        "department": "Engineering",
    },
]

_ATTACKER = {
    "userPrincipalName": "haxorsaurus@evilcorp.xyz",
    "displayName": "Haxorsaurus",
    "userId": "deadbeef-dead-beef-dead-beefdeadbeef",
    "ip": "185.199.108.153",
}

_NORMAL_APIS: List[Dict[str, str]] = [
    {
        "activityDisplayName": "User signed in",
        "category": "SignInLogs",
        "operationType": "SignIn",
        "result": "success",
        "resultReason": "SignInSucceeded",
    },
    {
        "activityDisplayName": "Changed user password",
        "category": "UserManagement",
        "operationType": "Update",
        "result": "success",
        "resultReason": "PasswordChange",
    },
    {
        "activityDisplayName": "Updated group membership",
        "category": "GroupManagement",
        "operationType": "Update",
        "result": "success",
        "resultReason": "AddMember",
    },
]

_MALICIOUS_APIS: List[Dict[str, Any]] = [
    # Mirrors Bedrock endpoint creation
    {
        "activityDisplayName": "Add service principal credentials",
        "category": "ApplicationManagement",
        "operationType": "AddServicePrincipal",
        "result": "success",
        "resultReason": "CredentialAdded",
        "targetType": "ServicePrincipal",
        "targetDisplay": "bedrock‑exfil‑sp",
    },
    # Mirrors SageMaker App creation
    {
        "activityDisplayName": "Create Enterprise Application",
        "category": "ApplicationManagement",
        "operationType": "Add",
        "result": "success",
        "resultReason": "NewApplication",
        "targetType": "Application",
        "targetDisplay": "SageMaker‑Stealth‑App",
    },
    # Mirrors DynamoDB Scan
    {
        "activityDisplayName": "Grant directory read permissions",
        "category": "RoleManagement",
        "operationType": "AddMemberToRole",
        "result": "success",
        "resultReason": "RoleAssigned",
        "targetType": "Role",
        "targetDisplay": "Directory Readers",
    },
]


def _random_dt() -> str:
    """Random ISO‑8601 timestamp within the past 12 hours."""
    delta = timedelta(seconds=random.randint(0, 12 * 3600))
    return (_NOW - delta).isoformat(timespec="seconds")


def _base_event() -> Dict[str, Any]:
    """Common skeleton."""
    return {
        "activityDateTime": _random_dt(),
        "correlationId": str(uuid.uuid4()),
        "id": str(uuid.uuid4()),
        # The parser flattens initiatedBy.* into initiatedByUserId etc.
        "initiatedBy": {},
        # Placeholder; filled later
        "targetResources": [],
    }


def _attach_user(ev: Dict[str, Any], user: Dict[str, str]) -> None:
    """Populate initiatedBy.* flattened fields."""
    ev["initiatedByUserId"] = user["userId"]
    ev["initiatedByUserIpAddress"] = user["ip"]
    ev["initiatedByUserUserPrincipalName"] = user["userPrincipalName"]


def _build_target(res_type: str, display: str) -> Dict[str, Any]:
    """Simple targetResources entry."""
    return {
        "displayName": display,
        "id": str(uuid.uuid4()),
        "type": res_type,
        "modifiedProperties": [],
        "userPrincipalName": None,
    }


def azure_ad_log() -> Dict[str, Any]:
    """Return **one** flat Azure AD audit‑log event."""
    malicious = random.random() < 0.3  # 30 % chance attacker event
    ev = _base_event()

    if malicious:
        api = random.choice(_MALICIOUS_APIS)
        ev.update(api)
        _attach_user(ev, _ATTACKER)
        ev["eventCategory"] = "Insight"
        ev["recipientAccountId"] = "000000000000"  # attacker’s dummy account
        # Construct targetResources reflecting the malicious intent
        ev["targetResources"].append(
            _build_target(api.get("targetType", "Unknown"), api.get("targetDisplay", "Unknown"))
        )
    else:
        api = random.choice(_NORMAL_APIS)
        ev.update(api)
        user = random.choice(_USERS)
        _attach_user(ev, user)
        ev["eventCategory"] = "Audit"
        # Map benign target (the user themselves)
        ev["targetResources"].append(
            _build_target("User", user["displayName"])
        )

    # Wrap for Splunk HEC /collector/event endpoint
    record = {
        "time": int(datetime.now(tz=timezone.utc).timestamp()),
        "event": ev,
        "fields": ATTR_FIELDS,  # metadata travels in "fields" per HEC spec
    }
    return record


# Sent inside the "fields" object of the HEC wrapper
ATTR_FIELDS = {
    "dataSource.category": "security",
    "dataSource.name": "Azure AD",
    "dataSource.vendor": "Azure",
}

# Alias expected by hec_sender.py
azuread_log = azure_ad_log