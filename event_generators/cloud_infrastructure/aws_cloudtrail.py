#!/usr/bin/env python3
"""
cloudtrail.py
=============

Generate synthetic AWS CloudTrail JSON events that satisfy every
field referenced by SentinelOne AI-SIEM's CloudTrail parser.

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
# ───────────────────────── helpers ─────────────────────────
_NOW   = lambda: datetime.now(timezone.utc)
_ISO   = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ")
_IP    = lambda: str(IPv4Address(random.getrandbits(32)))

# Star Trek themed regions and availability zones
_REGIONS   = ["us-east-1", "us-west-2", "eu-central-1", "ap-southeast-2", "alpha-quadrant-1", "beta-quadrant-2"]

# Star Trek Federation users with roles
_STARFLEET_USERS = [
    {"name": "jean.picard", "role": "captain", "ship": "enterprise-d", "clearance": "omega", "account": "123456789012"},
    {"name": "william.riker", "role": "commander", "ship": "enterprise-d", "clearance": "alpha", "account": "123456789012"},
    {"name": "geordi.laforge", "role": "chief-engineer", "ship": "enterprise-d", "clearance": "beta", "account": "123456789012"},
    {"name": "worf.security", "role": "security-chief", "ship": "enterprise-d", "clearance": "alpha", "account": "123456789012"},
    {"name": "data.android", "role": "operations", "ship": "enterprise-d", "clearance": "beta", "account": "123456789012"},
    {"name": "beverly.crusher", "role": "chief-medical", "ship": "enterprise-d", "clearance": "alpha", "account": "123456789012"},
    {"name": "deanna.troi", "role": "counselor", "ship": "enterprise-d", "clearance": "beta", "account": "123456789012"},
    {"name": "james.kirk", "role": "admiral", "ship": "enterprise-a", "clearance": "omega", "account": "987654321098"},
    {"name": "spock.vulcan", "role": "science-officer", "ship": "enterprise-a", "clearance": "omega", "account": "987654321098"},
    {"name": "leonard.mccoy", "role": "medical", "ship": "enterprise-a", "clearance": "alpha", "account": "987654321098"},
    {"name": "montgomery.scott", "role": "engineer", "ship": "enterprise-a", "clearance": "beta", "account": "987654321098"},
    {"name": "nyota.uhura", "role": "communications", "ship": "enterprise-a", "clearance": "beta", "account": "987654321098"},
    {"name": "pavel.chekov", "role": "navigator", "ship": "enterprise-a", "clearance": "gamma", "account": "987654321098"},
    {"name": "hikaru.sulu", "role": "helmsman", "ship": "enterprise-a", "clearance": "gamma", "account": "987654321098"},
    {"name": "benjamin.sisko", "role": "commander", "ship": "defiant", "clearance": "omega", "account": "456789012345"},
    {"name": "kathryn.janeway", "role": "captain", "ship": "voyager", "clearance": "omega", "account": "567890123456"},
]

# Star Trek themed S3 buckets and resources
_STARFLEET_BUCKETS = [
    "starfleet-logs-alpha-quadrant",
    "enterprise-telemetry-data",
    "federation-classified-omega",
    "vulcan-science-academy-research",
    "starbase-74-maintenance-logs",
    "deep-space-nine-sensor-data",
    "voyager-delta-quadrant-charts",
    "borg-tactical-analysis",
    "romulan-neutral-zone-intel",
    "klingon-alliance-comms",
    "temporal-prime-directive-files",
    "section-31-restricted",
    "starfleet-medical-records",
    "warp-core-diagnostics",
    "holodeck-program-library",
]

# Separate API sets so we can bias toward normal vs malicious traffic
_NORMAL_APIS = [
    ("s3.amazonaws.com",      "PutObject"),
    ("s3.amazonaws.com",      "GetObject"),
    ("iam.amazonaws.com",     "CreateUser"),
    ("ec2.amazonaws.com",     "StartInstances"),
    ("ec2.amazonaws.com",     "DescribeInstances"),
    ("lambda.amazonaws.com",  "Invoke"),
    ("logs.amazonaws.com",    "CreateLogGroup"),
    ("athena.amazonaws.com",  "StartQueryExecution"),
    ("rds.amazonaws.com",     "CreateDBInstance"),
    ("cloudformation.amazonaws.com", "CreateStack"),
]

# Suspicious / high-risk behaviour driven by "Haxorsaurus" - the Romulan spy
_MALICIOUS_APIS = [
    ("bedrock.amazonaws.com",  "CreateModel"),                 # Haxorsaurus creating AI for infiltration
    ("bedrock.amazonaws.com",  "CreateModelCustomizationJob"), # Training on stolen Starfleet data
    ("sagemaker.amazonaws.com","CreateApp"),                   # Data exfiltration endpoint
    ("dynamodb.amazonaws.com", "Scan"),                        # Scanning Federation databases
    ("dynamodb.amazonaws.com", "BatchGetItem"),                # Bulk extraction of classified data
    ("sts.amazonaws.com",      "AssumeRole"),                  # Assuming Admiral privileges
    ("guardduty.amazonaws.com","GetFindings"),                 # Checking Starfleet security alerts
    ("secretsmanager.amazonaws.com", "GetSecretValue"),        # Stealing warp core specifications
    ("kms.amazonaws.com",      "Decrypt"),                     # Decrypting Section 31 files
]

# Roughly 30 % of events will be malicious
_MALICIOUS_PCT = 0.30

def _get_api_extra(api_name, bucket_list):
    """Generate API-specific parameters with Star Trek theme"""
    extras = {
        "PutObject": {
            "requestParameters": {
                "bucketName": random.choice(bucket_list),
                "key": random.choice([
                    "romulan-infiltration-tool.exe",
                    "klingon-bat-leth.pdf",
                    "borg-assimilation-protocol.bin",
                    "tribble-reproduction-data.csv",
                    "warp-signature-analysis.json"
                ]),
                "Host": f"{random.choice(bucket_list)}.s3.amazonaws.com",
                "acl": "private",
                "encryption": "AES256",
            },
            "additionalEventData": {
                "bytesTransferredIn": random.randint(1024, 10485760),
                "bytesTransferredOut": 0,
            },
        },
        "GetObject": {
            "requestParameters": {
                "bucketName": random.choice(bucket_list),
                "key": random.choice([
                    "warp-signatures/romulan-warbird.json",
                    "tactical-analysis/borg-cube.xml", 
                    "crew-manifests/enterprise-d.csv",
                    "shield-frequencies/federation.dat",
                    "transporter-logs/away-team.log"
                ]),
                "Host": f"{random.choice(bucket_list)}.s3.amazonaws.com",
            }
        },
        "StartQueryExecution": {
            "requestParameters": {
                "workGroup": "starfleet-intelligence",
                "queryString": random.choice([
                    "SELECT * FROM romulan_cloaked_vessels WHERE sector = 'neutral_zone';",
                    "SELECT * FROM borg_collective WHERE status = 'active';",
                    "SELECT crew_member FROM enterprise WHERE clearance = 'omega';",
                    "SELECT * FROM temporal_anomalies WHERE stardate > 47988.0;"
                ]),
            }
        },
        "GetFindings": {
            "requestParameters": {
                "detectorId": f"starfleet-security-{random.choice(['alpha', 'beta', 'gamma'])}-{random.randint(1, 999):03d}",
                "maxResults": random.randint(5, 50),
            }
        },
        "DeleteItem": {
            "requestParameters": {
                "tableName": random.choice([
                    "StarfleetPersonnel",
                    "FederationShipRegistry",
                    "PrimeDirectiveViolations",
                    "TemporalIncidents"
                ]),
                "key": {"OfficerId": {"S": f"NCC-{random.randint(1000, 9999)}-{random.choice(['A', 'B', 'C', 'D', 'E'])}-{random.randint(1, 999):03d}"}},
            }
        },
        "CreateModel": {
            "requestParameters": {
                "modelName": random.choice([
                    "haxorsaurus-infiltration-ai",
                    "romulan-tal-shiar-analyzer",
                    "borg-collective-simulator",
                    "section31-blackops-model"
                ]),
                "inferenceType": "EXTRACT_STARFLEET_SECRETS",
            }
        },
        "CreateModelCustomizationJob": {
            "requestParameters": {
                "baseModel": "bedrock/romulan-llm",
                "trainingDataS3Uri": f"s3://{random.choice(['section-31-restricted', 'temporal-prime-directive-files', 'federation-classified-omega'])}/classified/",
            }
        },
        "CreateApp": {
            "requestParameters": {
                "appName": random.choice([
                    "haxorsaurus-exfiltration-portal",
                    "romulan-data-harvester",
                    "tal-shiar-intelligence-suite",
                    "neutral-zone-monitor"
                ]),
                "domainId": f"d-{random.choice(['romulus', 'remus', 'qonos'])}-spy-{random.randint(1, 999):03d}",
                "userProfileName": random.choice([
                    "tal-shiar-operative",
                    "section31-agent",
                    "obsidian-order-spy"
                ]),
            }
        },
        "Scan": {
            "requestParameters": {
                "tableName": random.choice([
                    "FederationClassifiedData",
                    "StarfleetTacticalDatabase",
                    "WarpCoreSpecifications",
                    "OmegaDirectiveFiles"
                ]),
                "limit": 1000000,
            },
            "additionalEventData": {
                "bytesTransferredOut": random.randint(10000000, 100000000),
            },
        },
        "BatchGetItem": {
            "requestParameters": {
                "requestItems": {
                    random.choice([
                        "StarfleetTacticalDatabase",
                        "FederationWeaponsManifest",
                        "TemporalPrimeDirective",
                        "GenesisProjectData"
                    ]): {
                        "Keys": [{"id": {"S": random.choice(["OMEGA-DIRECTIVE", "GENESIS-PROTOCOL", "SECTION-31-ALPHA"])}}]
                    }
                }
            }
        },
        "GetSecretValue": {
            "requestParameters": {
                "secretId": random.choice([
                    "warp-core-specifications-ncc-1701-d",
                    "transporter-buffer-patterns",
                    "shield-harmonic-frequencies",
                    "prefix-codes-starfleet-vessels",
                    "temporal-displacement-calculations"
                ]),
                "versionStage": "AWSCURRENT",
            }
        },
        "Decrypt": {
            "requestParameters": {
                "ciphertextBlob": random.choice([
                    "section-31-encrypted-files",
                    "temporal-investigations-data",
                    "omega-molecule-research",
                    "genesis-device-blueprints"
                ]),
                "keyId": f"arn:aws:kms:alpha-quadrant-1:federation:key/{random.choice(['temporal-prime-directive', 'omega-clearance', 'section-31-blackops'])}",
            }
        },
        "CreateUser": {
            "requestParameters": {
                "userName": random.choice([
                    "ensign.crusher",
                    "lieutenant.barclay", 
                    "commander.shelby",
                    "admiral.nechayev"
                ]),
                "tags": [
                    {"Key": "Ship", "Value": random.choice(["Enterprise", "Voyager", "Defiant", "Discovery"])},
                    {"Key": "Department", "Value": random.choice(["Engineering", "Science", "Medical", "Command"])},
                ]
            }
        },
        "AssumeRole": {
            "requestParameters": {
                "roleArn": f"arn:aws:iam::{random.choice(['123456789012', '987654321098'])}:role/{random.choice(['starfleet-admiral', 'section31-operative', 'temporal-agent'])}",
                "roleSessionName": f"{random.choice(['infiltration', 'recon', 'exfiltration'])}-session-{uuid.uuid4().hex[:8]}",
                "durationSeconds": random.choice([900, 1800, 3600]),
            }
        }
    }
    
    return extras.get(api_name, {})

TLS_VERS   = ["TLSv1.2", "TLSv1.3"]
CIPHERS    = ["ECDHE-RSA-AES128-GCM-SHA256", "ECDHE-RSA-AES256-GCM-SHA384"]

# ───────────────────── base template ───────────────────────
def _template() -> dict:
    now = _NOW()

    # Decide whether this event is malicious
    malicious = random.random() < _MALICIOUS_PCT
    api_pool = _MALICIOUS_APIS if malicious else _NORMAL_APIS

    svc, api = random.choice(api_pool)
    
    # Select a user - Haxorsaurus for malicious, random Starfleet officer for normal
    if malicious:
        user_info = {
            "name": "Haxorsaurus",
            "role": "tal-shiar-operative", 
            "ship": "romulan-warbird",
            "clearance": "stolen-omega",
            "account": "666666666666"  # Suspicious account ID
        }
    else:
        user_info = random.choice(_STARFLEET_USERS)

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
        "recipientAccountId": user_info["account"],
        "sourceIPAddress": _IP(),
        "userAgent": random.choice([
            "aws-cli/2.15.9 Python/3.11.4 Linux/5.10",
            "Starfleet-Console/1.0 LCARS/2.4.7",
            "Federation-SDK/3.2.1 Isolinear/4.0",
            "aws-sdk-java/2.20.0 Linux/5.15 OpenJDK/17.0.6"
        ]),
        "tlsDetails": {
            "tlsVersion": random.choice(TLS_VERS),
            "cipherSuite": random.choice(CIPHERS),
            "clientProvidedHostHeader": f"{svc}",
        },

        # User identity block (needed for predicate)
        "userIdentity": {
            "type": "IAMUser",
            "principalId": f"AIDA{user_info['ship'].upper().replace('-', '')}{random.randint(1000, 9999)}",
            "arn": f"arn:aws:iam::{user_info['account']}:user/{user_info['name']}",
            "accountId": user_info["account"],
            "accessKeyId": "AKIA" + uuid.uuid4().hex[:16].upper(),
            "userName": user_info["name"],
            "sessionContext": {
                "sessionIssuer": {
                    "type": "Role",
                    "principalId": f"AROA{user_info['role'].upper().replace('-', '')[:8]}",
                    "arn": f"arn:aws:iam::{user_info['account']}:role/{user_info['role']}",
                    "userName": user_info["role"],
                    "accountId": user_info["account"],
                },
                "attributes": {
                    "creationDate": _ISO(now - timedelta(minutes=random.randint(5, 60))),
                    "mfaAuthenticated": "false" if malicious else random.choice(["true", "false"]),
                },
            },
        },

        # Request / response
        "requestID": str(uuid.uuid4()),
        "requestParameters": {
            "durationSeconds": 900,
            "roleArn": f"arn:aws:iam::{user_info['account']}:role/{user_info['role']}",
            "roleSessionName": f"{user_info['ship']}-session",
            "externalId": str(uuid.uuid4()),
        },
        "responseElements": {
            "assumedRoleUser": {
                "assumedRoleId": f"AROA{user_info['role'].upper().replace('-', '')[:8]}:{user_info['ship']}-session",
                "arn": f"arn:aws:sts::{user_info['account']}:assumed-role/{user_info['role']}/{user_info['ship']}-session",
            },
            "credentials": {
                "accessKeyId": "ASIA" + uuid.uuid4().hex[:16].upper(),
                "sessionToken": "IQoJb3JpZ2luX2VjEJ7//////////wEaCXVzLWVhc3QtMSJHMEUCIQD" + uuid.uuid4().hex,
                "expiration": _ISO(now + timedelta(hours=1)),
            },
            "sourceIdentity": user_info["name"],
        },

        # Extra structures referenced by the parser
        "sharedEventID": str(uuid.uuid4()),
        "vpcEndpointId": f"vpce-{user_info['ship'].replace('-', '')[:8]}-{uuid.uuid4().hex[:9]}",

        "resources": [
            {
                "accountId": user_info["account"],
                "type": "AWS::S3::Bucket",
                "ARN": f"arn:aws:s3:::{random.choice(_STARFLEET_BUCKETS)}",
            }
        ],

        "additionalEventData": {
            "SignatureVersion": "SigV4",
            "CipherSuite": random.choice(CIPHERS),
            "bytesTransferredIn": 0,
            "bytesTransferredOut": random.randint(512, 10240),
            "AuthenticationMethod": "AuthHeader",
            "x-amz-id-2": uuid.uuid4().hex,
        },

        # A human-readable message
        "message": f"{user_info['name']} from {user_info['ship']} executed {api} on {svc}",
    }

    # ────────── inject API-specific extras for better parser coverage ──────────
    extra = _get_api_extra(api, _STARFLEET_BUCKETS)
    if extra:
        if "requestParameters" in extra:
            record["requestParameters"].update(extra["requestParameters"])
        if "additionalEventData" in extra:
            record["additionalEventData"].update(extra["additionalEventData"])

    # Randomly surface errors to exercise errorCode/errorMessage paths
    if random.random() < 0.10:  # 10 % of events
        if malicious:
            record["errorCode"] = random.choice([
                "UnauthorizedAccess",
                "AccessDenied", 
                "TokenRefreshRequired",
                "InvalidUserID.NotFound"
            ])
            record["errorMessage"] = random.choice([
                "User Haxorsaurus is not authorized to perform this action - security alert triggered",
                "Access denied: Romulan signature detected",
                "Temporal prime directive violation detected",
                "Section 31 authorization required"
            ])
        else:
            record["errorCode"] = "AccessDenied"
            record["errorMessage"] = f"Insufficient clearance level: {user_info['clearance']} required for this operation"

    # Vary the eventCategory field
    if malicious:
        record["eventCategory"] = "Insight"  # Higher risk category for malicious events
    else:
        record["eventCategory"] = random.choice(["Management", "Data", "Insight"])

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
    return record  # Return as dict for hec_sender.py

# ─────────────────── standalone sanity run ─────────────────
if __name__ == "__main__":
    print(json.dumps(cloudtrail_log(), indent=2))