#!/usr/bin/env python3
"""
Cisco Meraki MX syslog event generator (vpn_firewall, ip_flow, flows)
"""
from __future__ import annotations
import random, time, uuid
from typing import Dict

ATTR_FIELDS: Dict[str, str] = {
    "dataSource.vendor": "Cisco",
    "dataSource.name": "Meraki",
    "dataSource.category": "network",
    "metadata.product.vendor_name": "Cisco",
    "metadata.product.name": "Cisco Meraki",
    "metadata.version": "1.0.0",
}

_PRI = "<134>"       # local0.notice
_DEV = "meraki-mx64"

def meraki_log(log_type: str | None = None) -> str:
    """
    Generate a Meraki syslog line that matches one of the parser's
    three accepted formats:

      • vpn_firewall
      • ip_flow
      • flows

    Pass `log_type` to force a specific format, otherwise one is chosen at random.
    """
    log_type = log_type or random.choice(["vpn_firewall", "ip_flow", "flows"])
    now_unix = str(int(time.time()))
    host = _DEV
    code = random.choice(["<134>", "<135>"])  # informational / notice

    src_ip = f"10.0.{random.randint(0, 255)}.{random.randint(1, 254)}"
    dst_ip = f"93.184.{random.randint(0, 255)}.{random.randint(1, 254)}"
    sport = str(random.randint(1024, 65535))
    dport = str(random.choice([80, 443, 500, 4500, 53]))
    proto = random.choice(["tcp", "udp", "icmp"])
    connection_status = random.choice(["start", "allowed", "tear"])

    if log_type == "vpn_firewall":
        pattern_val = random.choice(["allowed 12345", "blocked 443"])
        message = (
            f"{code} {now_unix} {host} vpn_firewall src={src_ip} dst={dst_ip} "
            f"protocol={proto} sport={sport} dport={dport} pattern: {pattern_val}"
        )
    elif log_type == "ip_flow":
        trans_src = f"172.16.{random.randint(0,255)}.{random.randint(1,254)}"
        trans_port = dport
        message = (
            f"{code} {now_unix} {host} ip_flow src={src_ip} dst={dst_ip} "
            f"protocol={proto} sport={sport} dport={dport} "
            f"translated_src_ip={trans_src} translated_port={trans_port}"
        )
    else:  # flows
        mac = "00:11:22:33:44:{:02x}".format(random.randint(0, 255))
        message = (
            f"{code} {now_unix} {host} flows {connection_status} "
            f"src={src_ip} dst={dst_ip} mac={mac} protocol={proto} "
            f"sport={sport} dport={dport}"
        )

    return message