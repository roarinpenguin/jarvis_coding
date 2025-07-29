#!/usr/bin/env python3
"""
cloudtrail.py
=============

Generate synthetic AWS CloudTrail JSON events that satisfy every
field referenced by SentinelOne AI-SIEM’s CloudTrail parser.

Example
-------
>>> from cloudtrail import cloudtrail_log
>>> print(cloudtrail_log())                     # one default event
>>> print(cloudtrail_log({"eventName": "PutObject"}))
"""

from __future__ import annotations
from datetime import datetime, timezone, timedelta
from ipaddress import IPv4Address
import json
import random
import uuid

# ────────────────────── AI‑SIEM attributes ─────────────────────
# These attributes are injected by hec_sender.py under the `fields`
# envelope key so the CloudTrail parser can populate constant values.
ATTR_FIELDS = {
    "metadata.product.vendor_name": "AWS",
    "metadata.product.name": "AWS CloudTrail",
    "metadata.version": "1.0.0-rc3",
    "dataSource.vendor": "AWS",
    "dataSource.name": "CloudTrail",
    "dataSource.category": "security",
    "category_uid": 4,
    "category_name": "Network Activity",
    "class_uid": 4002,
    "class_name": "HTTP Activity",
    "type_uid": 400299,
    "type_name": "HTTP Activity: Other",
    "activity_id": 99,
    "severity_id": 99,
    "status_id": 99,
    "status": "Other",
}

# ───────────────────────── helpers ─────────────────────────
_NOW   = lambda: datetime.now(timezone.utc)
_ISO   = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ")
_IP    = lambda: str(IPv4Address(random.getrandbits(32)))

_REGIONS   = ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-2"]

# Separate API sets so we can bias toward normal vs malicious traffic
_NORMAL_APIS = [
    ("s3.amazonaws.com",      "PutObject"),
    ("s3.amazonaws.com",      "GetObject"),
    ("iam.amazonaws.com",     "CreateUser"),
    ("ec2.amazonaws.com",     "StartInstances"),
    ("ec2.amazonaws.com",     "DescribeInstances"),
    ("lambda.amazonaws.com",  "Invoke"),
    ("logs.amazonaws.com",    "CreateLogGroup"),
    ("athena.amazonaws.com",  "StartQueryExecution"),
]

# Suspicious / high‑risk behaviour driven by “Haxorsaurus”
_MALICIOUS_APIS = [
    ("bedrock.amazonaws.com",  "CreateModel"),                 # standing‑up generative model
    ("bedrock.amazonaws.com",  "CreateModelCustomizationJob"), # fine‑tune potentially harmful model
    ("sagemaker.amazonaws.com","CreateApp"),                   # SageMaker Studio app for exfil
    ("dynamodb.amazonaws.com", "Scan"),                        # full‑table scan
    ("dynamodb.amazonaws.com", "BatchGetItem"),                # bulk extraction
    ("sts.amazonaws.com",      "AssumeRole"),                  # privilege escalation
    ("guardduty.amazonaws.com","GetFindings"),                 # enumerating detections
]

# Roughly 30 % of events will be malicious
_MALICIOUS_PCT = 0.30

_API_EXTRA = {
    "PutObject": {
        "requestParameters": {
            "bucketName": "demo-bucket",
            "key": "malicious.exe",
            "Host": "demo-bucket.s3.amazonaws.com",
            "acl": "private",
            "encryption": "AES256",
        },
        "additionalEventData": {
            "bytesTransferredIn": 2048,
            "bytesTransferredOut": 0,
        },
    },
    "GetObject": {
        "requestParameters": {
            "bucketName": "demo-bucket",
            "key": "public/readme.txt",
            "Host": "demo-bucket.s3.amazonaws.com",
        }
    },
    "StartQueryExecution": {
        "requestParameters": {
            "workGroup": "primary",
            "queryString": "SELECT * FROM malicious_ips;",
        }
    },
    "GetFindings": {
        "requestParameters": {
            "detectorId": "12abc34d567e89f012g3h45678i90jkl",
            "maxResults": 5,
        }
    },
    "DeleteItem": {
        "requestParameters": {
            "tableName": "Customers",
            "key": {"CustomerId": {"S": "12345"}},
        }
    },
    "CreateModel": {
        "requestParameters": {
            "modelName": "bedrock-haxor-endpoint",
            "inferenceType": "HALLUCINATE_ALL_DATA",
        }
    },
    "CreateModelCustomizationJob": {
        "requestParameters": {
            "baseModel": "bedrock/llama2",
            "trainingDataS3Uri": "s3://jean-personal-data/full_dump/",
        }
    },
    "CreateApp": {
        "requestParameters": {
            "appName": "jean-data-exfil",
            "domainId": "d-abc123",
            "userProfileName": "haxorsaurus-profile",
        }
    },
    "Scan": {
        "requestParameters": {
            "tableName": "JeanPrivateTable",
            "limit": 1000000,
        },
        "additionalEventData": {
            "bytesTransferredOut": 50000000,
        },
    },
    "BatchGetItem": {
        "requestParameters": {
            "requestItems": {
                "JeanPrivateTable": {
                    "Keys": [{"id": {"S": "ALL"}}]
                }
            }
        }
    },
}

TLS_VERS   = ["TLSv1.2", "TLSv1.3"]
CIPHERS    = ["ECDHE-RSA-AES128-GCM-SHA256", "ECDHE-RSA-AES256-GCM-SHA384"]

# ───────────────────── base template ───────────────────────
def _template() -> dict:
    now = _NOW()

    # Decide whether this event is malicious
    malicious = random.random() < _MALICIOUS_PCT
    api_pool = _MALICIOUS_APIS if malicious else _NORMAL_APIS

    svc, api = random.choice(api_pool)

    record = {
        # Top-level searchable keys
        "eventCategory": "Management",
        "eventName": api,
        "eventSource": svc,
        "eventTime": _ISO(now),
        "eventVersion": "1.09",
        "eventID": str(uuid.uuid4()),
        "eventType": "AwsApiCall",
        "awsRegion": random.choice(_REGIONS),
        "readOnly": random.choice([True, False]),
        "managementEvent": True,
        "recipientAccountId": "123456789012",
        "sourceIPAddress": _IP(),
        "userAgent": "aws-cli/2.15.9 Python/3.11.4 Linux/5.10",
        "tlsDetails": {
            "tlsVersion": random.choice(TLS_VERS),
            "cipherSuite": random.choice(CIPHERS),
            "clientProvidedHostHeader": f"{svc}",
        },

        # User identity block (needed for predicate)
        "userIdentity": {
            "type": "IAMUser",
            "principalId": "AIDAEXAMPLE" + str(random.randint(1000, 9999)),
            "arn": "arn:aws:iam::123456789012:user/demo",
            "accountId": "123456789012",
            "accessKeyId": "AKIA" + uuid.uuid4().hex[:16].upper(),
            "userName": "demo",
            "sessionContext": {
                "sessionIssuer": {
                    "type": "Role",
                    "principalId": "AROAEXAMPLE",
                    "arn": "arn:aws:iam::123456789012:role/demo-role",
                    "userName": "demo-role",
                    "accountId": "123456789012",
                },
                "attributes": {
                    "creationDate": _ISO(now - timedelta(minutes=5)),
                    "mfaAuthenticated": "false",
                },
            },
        },

        # Request / response
        "requestID": str(uuid.uuid4()),
        "requestParameters": {
            "durationSeconds": 900,
            "roleArn": "arn:aws:iam::123456789012:role/demo-role",
            "roleSessionName": "demo-session",
            "externalId": str(uuid.uuid4()),
        },
        "responseElements": {
            "assumedRoleUser": {
                "assumedRoleId": "AROAEXAMPLE:demo-session",
                "arn": "arn:aws:sts::123456789012:assumed-role/demo-role/demo-session",
            },
            "credentials": {
                "accessKeyId": "ASIA" + uuid.uuid4().hex[:16].upper(),
                "sessionToken": "IQoJb3JpZ2luX2VjEJ7//////////wEaCXVzLWVhc3QtMSJHMEUCIQD...",
                "expiration": _ISO(now + timedelta(hours=1)),
            },
            "sourceIdentity": "demo",
        },

        # Extra structures referenced by the parser
        "sharedEventID": str(uuid.uuid4()),
        "vpcEndpointId": "vpce-0" + uuid.uuid4().hex[:9],

        "resources": [
            {
                "accountId": "123456789012",
                "type": "AWS::S3::Bucket",
                "ARN": "arn:aws:s3:::demo-bucket",
            }
        ],

        "additionalEventData": {
            "SignatureVersion": "SigV4",
            "CipherSuite": random.choice(CIPHERS),
            "bytesTransferredIn": 0,
            "bytesTransferredOut": 1024,
            "AuthenticationMethod": "AuthHeader",
            "x-amz-id-2": uuid.uuid4().hex,
        },

        # A human-readable string (copied then dropped by the parser)
        "message": f"{api} on {svc}",
    }

    # ────────── inject API‑specific extras for better parser coverage ──────────
    extra = _API_EXTRA.get(api)
    if extra:
        record["requestParameters"].update(extra.get("requestParameters", {}))
        record.setdefault("additionalEventData", {}).update(extra.get("additionalEventData", {}))

    # Randomly surface errors to exercise errorCode/errorMessage paths
    if random.random() < 0.10:  # 10 % of events
        record["errorCode"] = "AccessDenied"
        record["errorMessage"] = "User is not authorized to perform this action"

    # Vary the eventCategory field beyond the default
    record["eventCategory"] = random.choice(["Management", "Data", "Insight"])

    if malicious:
        # Overwrite identity to represent the attacker “Haxorsaurus”
        record["userIdentity"].update(
            {
                "type": "IAMUser",
                "userName": "Haxorsaurus",
                "arn": "arn:aws:iam::210987654321:user/Haxorsaurus",
                "principalId": "AIDAHAXOR" + str(random.randint(1000, 9999)),
                "accountId": "210987654321",
            }
        )
        record["recipientAccountId"] = "210987654321"
        record["eventCategory"] = "Insight"  # surfaces as higher‑risk in parser

    return record


# ───────────────────── public factory ──────────────────────
def cloudtrail_log(overrides: dict | None = None) -> str:
    """
    Return a single CloudTrail event JSON string.

    Pass `overrides` to force any field to a specific value:
        cloudtrail_log({"eventName": "PutObject"})
    """
    record = _template()
    if overrides:
        record.update(overrides)
    return json.dumps(record, separators=(",", ":"))  # compact


# ─────────────────── standalone sanity run ─────────────────
if __name__ == "__main__":
    print(cloudtrail_log())