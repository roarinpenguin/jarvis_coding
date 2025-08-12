#!/usr/bin/env python3
"""
AWS VPC Flow Log record generator
"""
from __future__ import annotations
import json, random, time, uuid
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "AWS",
    "dataSource.name": "AWS VPC Flow",
    "dataSource.category": "security",
    "metadata.product.vendor_name": "AWS",
    "metadata.product.name": "AWS VPC Flow Logs",
    "metadata.version": "1.0.0-rc.3",
    "category_uid": "4",
    "category_name": "Network Activity",
    "class_uid": "4001",
    "class_name": "Network Activity",
}

def _flow_record() -> str:
    """
    Create one VPC Flow Log line in *version 2 IPv4* format:

        version accountID interfaceID srcaddr dstaddr
        srcport dstport protocol packets bytes
        start end action status
    """
    version = "2"
    account_id = f"{random.randint(10**11, 10**12 - 1)}"
    interface_id = "eni-" + uuid.uuid4().hex[:17]
    src_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    dst_ip = f"203.0.113.{random.randint(1,254)}"
    src_port = str(random.randint(1024, 65535))
    dst_port = str(random.choice([22, 53, 80, 443, 3389]))
    protocol = str(random.choice([6, 17]))          # 6 = TCP, 17 = UDP
    packets = str(random.randint(1, 500))
    bytes_ = str(random.randint(40, 50000))
    now = int(time.time())
    start = str(now - random.randint(10, 60))
    end = str(now)
    action = random.choice(["ACCEPT", "REJECT"])
    status = "OK"
    return " ".join([
        version, account_id, interface_id,
        src_ip, dst_ip,
        src_port, dst_port, protocol,
        packets, bytes_,
        start, end,
        action, status,
    ])

def vpcflow_log() -> str:
    """
    Generate a VPC Flow Log record in space-separated format for marketplace parser.
    Returns the raw space-separated string format expected by marketplace-awsvpcflowlogs-latest.
    """
    return _flow_record()