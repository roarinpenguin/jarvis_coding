#!/usr/bin/env python3
"""Send logs from vendor_product generators to SentinelOne AI SIEM (Splunk‑HEC) one‑by‑one."""
import argparse, json, os, time, random, requests, importlib

# Map product → (module_name, generator function names)
PROD_MAP = {
    "fortinet_fortigate": (
        "fortinet_fortigate",
        ["local_log", "forward_log", "rest_api_log", "vpn_log", "virus_log"],
    ),
    "zscaler": (
        "zscaler",
        ["zscaler_log"],
    ),
    "aws_cloudtrail": (
        "aws_cloudtrail",
        ["cloudtrail_log"],
    ),
    "aws_vpcflowlogs": (
        "aws_vpcflowlogs",
        ["vpcflow_log"],
    ),
    "aws_guardduty": (
        "aws_guardduty",
        ["guardduty_log"],
    ),
    "microsoft_azuread": (
        "microsoft_azuread",
        ["azuread_log"],
    ),
    "okta_authentication": (
        "okta_authentication",
        ["okta_authentication_log"],
    ),
    "cisco_asa": (
        "cisco_asa",
        ["asa_log"],
    ),
    "cisco_umbrella": (
        "cisco_umbrella",
        ["umbrella_dns_log"],
    ),
    "cisco_meraki": (
        "cisco_meraki",
        ["meraki_log"],
    ),
}
# I need to move this down below sourcetype_map so
#HEC_URL = os.getenv(
#    "S1_HEC_URL",
#   "https://ingest.us1.sentinelone.net/services/collector/raw?sourcetype=$sourcetype_map,
#)
HEC_TOKEN = os.getenv("S1_HEC_TOKEN")
if not HEC_TOKEN:
    raise RuntimeError("export S1_HEC_TOKEN=… first")

HEADERS = {
    "Authorization": f"Bearer {HEC_TOKEN}",
}

SOURCETYPE_MAP = {
    "fortinet_fortigate": "marketplace-fortinetfortigate-latest",
    "zscaler": "marketplace-zscalerinternetaccess-latest",
    "aws_cloudtrail": "marketplace-awscloudtrail-latest",
    "aws_vpcflowlogs": "marketplace-awsvpcflowlogs-latest",
    "aws_guardduty": "CommAwsGuardduty",
    "microsoft_azuread": "azuread",
    "okta_authentication": "json",
    "cisco_asa": "CommCiscoASA",
    "cisco_umbrella": "community-ciscoumbrella-latest",
    "cisco_meraki": "CommCiscoMeraki",
}

# Generators that already emit structured JSON events; these must be sent to /event
JSON_PRODUCTS = {
    "aws_cloudtrail",
    "microsoft_azuread",
    "okta_authentication",
}

def _envelope(line: str, product: str, attr_fields: dict) -> str:
    return json.dumps(
        {
            "time": round(time.time()),
            "event": line,
            "sourcetype": SOURCETYPE_MAP[product],
            "fields": attr_fields,
        },
        ensure_ascii=False,
        separators=(',', ':')
    )

def send_one(line: str, product: str, attr_fields: dict):
    """
    Route JSON‑structured products to the /event endpoint and all
    raw / CSV / syslog products to the /raw endpoint.
    """
    raw_base   = os.getenv("S1_HEC_RAW_URL_BASE",   "https://ingest.us1.sentinelone.net/services/collector/raw")
    event_base = os.getenv("S1_HEC_EVENT_URL_BASE", "https://ingest.us1.sentinelone.net/services/collector/event")

    if product in JSON_PRODUCTS:
        # ── JSON payload → /event ─────────────────────────
        url = event_base
        payload = _envelope(line, product, attr_fields)  # JSON envelope
        headers = {**HEADERS, "Content-Type": "application/json"}
    else:
        # ── Raw payload → /raw ───────────────────────────
        url = f"{raw_base}?sourcetype={SOURCETYPE_MAP[product]}"
        payload = line  # plain CSV/syslog/raw string
        headers = {**HEADERS, "Content-Type": "text/plain"}

    resp = requests.post(url, headers=headers, data=payload, timeout=10)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return {"status": "OK", "code": resp.status_code}

def send_many_with_spacing(lines, product: str, attr_fields: dict,
                           min_delay=0.020, max_delay=60.0):
    """Send events individually with random delay between each."""
    results = []
    for idx, line in enumerate(lines, 1):
        results.append(send_one(line, product, attr_fields))
        if idx != len(lines):
            time.sleep(random.uniform(min_delay, max_delay))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate & send FortiGate, Zscaler, CloudTrail, VPC Flow Logs, GuardDuty, Azure AD, Okta Authentication, Cisco ASA, Cisco Umbrella, or Cisco Meraki events (one‑by‑one) to S1"
    )
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="How many events to send (default 1)")
    parser.add_argument("--min-delay", type=float, default=0.020,
                        help="Minimum delay between events in seconds (default 0.02)")
    parser.add_argument("--max-delay", type=float, default=60.0,
                        help="Maximum delay between events in seconds (default 60)")
    parser.add_argument(
        "--product",
        choices=[
            "fortinet_fortigate",
            "zscaler",
            "aws_cloudtrail",
            "aws_vpcflowlogs",
            "aws_guardduty",
            "microsoft_azuread",
            "okta_authentication",
            "cisco_asa",
            "cisco_umbrella",
            "cisco_meraki",
        ],
        default="fortinet_fortigate",
        help="Which log generator to use (default: fortinet_fortigate)",
    )
    args = parser.parse_args()

    mod_name, func_names = PROD_MAP[args.product]
    gen_mod = importlib.import_module(mod_name)
    attr_fields = getattr(gen_mod, "ATTR_FIELDS")
    generators = [getattr(gen_mod, fn) for fn in func_names]

    events = [generators[i % len(generators)]() for i in range(args.count)]

    if args.count == 1:
        print("HEC response:", send_one(events[0], args.product, attr_fields))
    else:
        print(f"Sending {args.count} events one-by-one "
              f"(spacing {args.min_delay}s – {args.max_delay}s)…")
        print("Responses:", send_many_with_spacing(
            events, args.product, attr_fields, args.min_delay, args.max_delay
        ))