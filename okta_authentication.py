#!/usr/bin/env python3
#WORKING
"""
okta_authentication.py
================================

This module generates synthetic Okta System Log events for testing
SentinelOne AI‑SIEM parsers.  The implementation follows the pattern
established in ``aws_cloudtrail_generator.py``: it defines a set of
static attributes identifying the data source and a function that
returns a fully‑populated event record serialized as JSON.  These
events mimic Okta authentication activity and should exercise most of
the common fields referenced by SentinelOne's Okta parser.

Usage example
-------------

>>> from okta_authentication_generator import okta_authentication_log
>>> print(okta_authentication_log())

The returned string contains a single Okta System Log event.  You can
wrap it alongside the ``ATTR_FIELDS`` dictionary (defined below) when
sending data to the SentinelOne ingestion endpoint.  See
``test_cloudtrail_ingest.py`` for an example of how to submit events.

"""

from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from ipaddress import IPv4Address
from typing import Dict, Any, List

# --------------------------------------------------------------------------- #
#  Static fields
# --------------------------------------------------------------------------- #

#: Attributes injected alongside each event.  These mirror the values
#: expected by the SentinelOne AI‑SIEM Okta parser and identify
#: the source of the data.  Update vendor/product names as needed.
ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Okta",
    "dataSource.name": "System Log",
    "dataSource.category": "authentication",
    "metadata.product.vendor_name": "Okta",
    "metadata.product.name": "Okta System Log",
    "metadata.version": "1.0.0",
}

# Helper lambdas for brevity
_NOW = lambda: datetime.now(timezone.utc)
_ISO = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
_IP = lambda: str(IPv4Address(random.getrandbits(32)))

# Possible outcome statuses and reasons
_OUTCOMES: List[Dict[str, str]] = [
    {"result": "SUCCESS", "reason": "User logged in successfully"},
    {"result": "FAILURE", "reason": "Invalid credentials"},
    {"result": "FAILURE", "reason": "MFA challenge failed"},
    {"result": "FAILURE", "reason": "Account locked"},
]

# Possible authentication contexts (e.g. login via web, API, mobile)
_AUTH_CONTEXTS = [
    "WEB", "MOBILE", "API", "SAML", "OIDC",
]

# Common Okta event types for authentication
_EVENT_TYPES = [
    "user.authentication.sso",         # Single sign‑on
    "user.authentication.auth_via_mfa",# MFA challenge passed
    "user.session.start",             # Session creation
    "user.session.end",               # Session termination
    "system.api_token.verify",        # API token verification
]

def _random_user() -> Dict[str, Any]:
    """Generate a pseudo‑random Okta user profile for the event.

    Returns a dictionary containing typical user identifiers used in
    Okta System Log entries.  These values are synthetic and do not
    correspond to real people.

    Returns
    -------
    Dict[str, Any]
        A dictionary with ``id``, ``type`` and ``displayName`` fields.
    """
    user_id = str(uuid.uuid4())
    username = f"user{random.randint(1000, 9999)}@example.com"
    return {
        "id": user_id,
        "type": "User",
        "alternateId": username,
        "displayName": username.split("@")[0].title(),
    }


def _random_client() -> Dict[str, Any]:
    """Generate client information for the event.

    This includes network and user agent details typically present in
    Okta System Log records.

    Returns
    -------
    Dict[str, Any]
        A dictionary with keys for ``userAgent`` and ``ipAddress``.
    """
    return {
        "userAgent": {
            "rawUserAgent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"
                " (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
                "okta-authenticator/6.1.0 (iOS) CFNetwork/1333.0.4"
            ]),
            "os": {
                "family": random.choice(["Windows", "macOS", "iOS", "Android", "Linux"]),
            },
            "browser": {
                "family": random.choice(["Chrome", "Safari", "Firefox", "Edge", "Opera"]),
            },
        },
        "ipAddress": _IP(),
    }


def okta_authentication_log() -> str:
    """
    Return a single synthetic Okta event that mirrors the flattened
    field layout used by the SentinelOne Okta parser (dot‑separated keys).
    """
    now = _NOW()
    original_time = _ISO(now)
    # nanoseconds since epoch, expressed as a string
    ts_ns = str(int(now.timestamp() * 1_000_000_000))
    # randomised values for correlation / user / ids
    user_stub = uuid.uuid4().hex[:12]
    correlation = uuid.uuid4().hex
    event: Dict[str, Any] = {
        "activity_id": 99,
        "activity_name": "OIDC token revocation request",
        "actor.user.email_addr": user_stub,
        "actor.user.name": "Okta Dashboard",
        "actor.user.type_id": 99,
        "actor.user.uid": f"okta.{uuid.uuid4()}",
        "category_name": "Uncategorized",
        "category_uid": 0,
        "class_name": "Base Event",
        "class_uid": 0,
        "dataSource.category": "security",
        "dataSource.name": "Okta",
        "dataSource.vendor": "Okta",
        "device.risk_level": "Other",
        "device.risk_level_id": 99,
        "event.type": "OIDC token revocation request",
        "metadata.correlation_uid": correlation,
        "metadata.original_time": original_time,
        "metadata.product.name": "Okta",
        "metadata.product.vendor_name": "Okta",
        "metadata.uid": str(uuid.uuid1()),
        "metadata.version": "1.0.0",
        "sca:RetentionType": "SDL",
        "severity_id": 99,
        "status": "FAILURE",
        "status_detail": "invalid_token",
        "status_id": 2,
        "timestamp": ts_ns,
        "type_name": "Base Event: Other",
        "type_uid": 99,
        "unmapped.actor.type": "PublicClientApp",
        "unmapped.authenticationContext.authenticationStep": 0,
        "unmapped.authenticationContext.externalSessionId": "unknown",
        "unmapped.authenticationContext.rootSessionId": "unknown",
        "unmapped.client.device": "Computer",
        "unmapped.client.geographicalContext.city": "Jersey City",
        "unmapped.client.geographicalContext.country": "United States",
        "unmapped.client.geographicalContext.geolocation.lat": 40.731,
        "unmapped.client.geographicalContext.geolocation.lon": -74.0771,
        "unmapped.client.geographicalContext.postalCode": "07395",
        "unmapped.client.geographicalContext.state": "New Jersey",
        "unmapped.client.ipAddress": _IP(),
        "unmapped.client.userAgent.browser": "CHROME",
        "unmapped.client.userAgent.os": "Windows 10",
        "unmapped.client.userAgent.rawUserAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "unmapped.debugContext.debugData.dtHash": uuid.uuid4().hex,
        "unmapped.debugContext.debugData.requestId": correlation,
        "unmapped.debugContext.debugData.requestUri": "/oauth2/v1/revoke",
        "unmapped.debugContext.debugData.threatSuspected": "false",
        "unmapped.debugContext.debugData.url": "/oauth2/v1/revoke?",
        "unmapped.displayMessage": "OIDC token revocation request",
        "unmapped.eventType": "app.oauth2.token.revoke",
        "unmapped.legacyEventType": "app.oauth2.token.revoke_failure",
        "unmapped.request.ipChain": f"[{{\"ip\":\"{_IP()}\",\"geographicalContext\":{{\"country\":\"United States\",\"city\":\"Jersey City\",\"postalCode\":\"07395\",\"state\":\"New Jersey\",\"geolocation\":{{\"lon\":-74.0771,\"lat\":40.731}}}},\"version\":\"V4\"}}]",
        "unmapped.securityContext.asNumber": 174,
        "unmapped.securityContext.asOrg": "private customer",
        "unmapped.securityContext.domain": ".",
        "unmapped.securityContext.isProxy": False,
        "unmapped.securityContext.isp": "cogent communications",
        "unmapped.severity": "WARN",
        "unmapped.transaction.type": "WEB",
        "unmapped.version": "0",
    }
    return json.dumps(event)


if __name__ == "__main__":  # pragma: no cover
    # Simple demo: print a few sample events to stdout
    for _ in range(3):
        print(okta_authentication_log())
