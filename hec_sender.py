#!/usr/bin/env python3
"""Send FortiGate or Zscaler logs to SentinelOne AI SIEM (Splunk-HEC) one-by-one."""
import argparse, json, os, time, random, requests, importlib

# Map product → (module_name, generator function names)
PROD_MAP = {
    "fortigate": (
        "fortigate",
        ["local_log", "forward_log", "rest_api_log", "vpn_log", "virus_log"],
    ),
    "zscaler": (
        "zscaler",
        ["zscaler_log"],
    ),
    "cloudtrail": (
        "cloudtrail",
        ["cloudtrail_log"],
    ),
    "azuread": (
        "azuread",
        ["azuread_log"],
    ),
}

HEC_URL = os.getenv(
    "S1_HEC_URL",
    "https://ingest.us1.sentinelone.net/services/collector/raw?sourcetype=azuread",
)
HEC_TOKEN = os.getenv("S1_HEC_TOKEN")
if not HEC_TOKEN:
    raise RuntimeError("export S1_HEC_TOKEN=… first")

HEADERS = {
    "Authorization": f"Splunk {HEC_TOKEN}",
    "Content-Type": "application/json",
}

SOURCETYPE_MAP = {
    "cloudtrail": "marketplace-awscloudtrail-latest",
    "fortigate": "marketplace-fortinetfortigate-latest",
    "azuread": "azuread",
    "zscaler":  "marketplace-zscalerinternetaccess-latest",
}

def _envelope(line: str, product: str, attr_fields: dict) -> str:
    return json.dumps(
        {
            "time": round(time.time()),
            "event": line,
            "sourcetype": SOURCETYPE_MAP[product],
            "fields": attr_fields,
        }
    )

def send_one(line: str, product: str, attr_fields: dict):
    r = requests.post(
        HEC_URL,
        headers=HEADERS,
        data=_envelope(line, product, attr_fields),
        timeout=10,
    )
    r.raise_for_status()
    return r.json()

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
        description="Generate & send FortiGate, Zscaler, CloudTrail, or Azure AD events (one‑by‑one) to S1"
    )
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="How many events to send (default 1)")
    parser.add_argument("--min-delay", type=float, default=0.020,
                        help="Minimum delay between events in seconds (default 0.02)")
    parser.add_argument("--max-delay", type=float, default=60.0,
                        help="Maximum delay between events in seconds (default 60)")
    parser.add_argument("--product", choices=["fortigate", "zscaler", "cloudtrail", "azuread"],
                        default="fortigate",
                        help="Which log generator to use (default: fortigate)")
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