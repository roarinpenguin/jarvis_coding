#!/usr/bin/env python3
"""
End-to-end validation:
1) Generates and sends events for selected generators via HEC
2) Queries SDL API to verify parsing and field extraction

Usage examples:
  python3 scenarios/e2e_sdl_validation.py --count 5 --products crowdstrike_falcon,aws_cloudtrail
  python3 scenarios/e2e_sdl_validation.py --count 2 --settle-seconds 180 --community-only

Environment:
  S1_HEC_TOKEN           # required for sending (no defaults)
  S1_SDL_API_TOKEN       # required for querying SDL
  S1_SDL_API_URL         # optional (default: https://xdr.us1.sentinelone.net/api/query)
  S1_HEC_EVENT_URL_BASE  # optional override for /event endpoint
  S1_HEC_RAW_URL_BASE    # optional override for /raw endpoint
  REQUESTS_CA_BUNDLE     # optional org CA for TLS inspection
"""

import os
import sys
import time
import json
import argparse
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple

from env_loader import load_env_if_present
import importlib

# Load .env from repo root and scenarios/
THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, '..'))
load_env_if_present(os.path.join(REPO_ROOT, '.env'))
load_env_if_present(os.path.join(THIS_DIR, '.env'))

# Validate environment
if not os.getenv('S1_HEC_TOKEN'):
    sys.exit('S1_HEC_TOKEN not set. Create a .env or export it before running.')
if not os.getenv('S1_SDL_API_TOKEN'):
    print('⚠️  S1_SDL_API_TOKEN not set. SDL queries will be skipped.')

# Import hec_sender mappings
sys.path.insert(0, os.path.join(REPO_ROOT, 'event_generators', 'shared'))
import hec_sender  # type: ignore
from hec_sender import PROD_MAP, SOURCETYPE_MAP
import requests

SDL_API_URL = os.getenv('S1_SDL_API_URL', 'https://xdr.us1.sentinelone.net/api/query')
SDL_API_TOKEN = os.getenv('S1_SDL_API_TOKEN')


def send_events(product: str, count: int, min_delay: float, max_delay: float) -> Tuple[int, int]:
    mod_name, func_names = PROD_MAP[product]
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        print(f"  ❌ missing generator module '{mod_name}': {e}")
        return 0, count
    attr_fields = getattr(mod, 'ATTR_FIELDS')
    gens = [getattr(mod, fn) for fn in func_names]
    events = [gens[i % len(gens)]() for i in range(count)]
    try:
        results = hec_sender.send_many_with_spacing(events, product, attr_fields, min_delay, max_delay)
        ok = 0
        for r in results:
            if isinstance(r, dict) and (r.get('code') == 0 or r.get('status') == 'OK'):
                ok += 1
        return ok, len(results) - ok
    except Exception as e:
        print(f"  ❌ send error for {product}: {e}")
        return 0, count


def query_sdl(parser_name: str, hours_back: int = 2) -> List[dict]:
    if not SDL_API_TOKEN:
        return []
    headers = {
        'Authorization': f'Bearer {SDL_API_TOKEN}',
        'Content-Type': 'application/json'
    }
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours_back)
    payload = {
        'queryType': 'log',
        'filter': f'* contains "{parser_name}"',
        'startTime': start_time.isoformat(),
        'endTime': end_time.isoformat()
    }
    try:
        resp = requests.post(SDL_API_URL, headers=headers, json=payload, timeout=20)
        if resp.status_code != 200:
            return []
        data = resp.json()
        matches = data.get('matches', [])
        events = []
        for m in matches:
            ev = m.get('attributes', {}).copy()
            ev['timestamp'] = m.get('timestamp')
            ev['severity'] = m.get('severity')
            events.append(ev)
        return events
    except Exception:
        return []


def analyze_fields(events: List[dict]) -> Dict:
    if not events:
        return {"status": "no_events", "field_count": 0, "ocsf_fields": 0, "ocsf_score": 0}
    all_fields = set()
    ocsf = set()
    for ev in events:
        fields = set(ev.keys())
        all_fields |= fields
        for f in fields:
            if any(f.startswith(p) for p in (
                'activity_', 'category_', 'class_', 'severity_', 'status_',
                'time', 'metadata', 'actor', 'device', 'src_endpoint', 'dst_endpoint'
            )):
                ocsf.add(f)
    score = 100 if len(ocsf) >= 10 else 80 if len(ocsf) >= 5 else 60 if len(ocsf) >= 3 else 40 if len(ocsf) >= 1 else 0
    return {
        "status": "success",
        "event_count": len(events),
        "field_count": len(all_fields),
        "ocsf_fields": len(ocsf),
        "ocsf_score": score,
        "sample_fields": sorted(list(all_fields))[:20]
    }


def main():
    ap = argparse.ArgumentParser(description='End-to-end generator → SDL validation')
    ap.add_argument('--products', help='Comma-separated product IDs to test (default: all)')
    ap.add_argument('-n', '--count', type=int, default=3, help='Events per product to send')
    ap.add_argument('--min-delay', type=float, default=0.02)
    ap.add_argument('--max-delay', type=float, default=0.20)
    ap.add_argument('--settle-seconds', type=int, default=90, help='Wait after send before SDL query')
    ap.add_argument('--hours-back', type=int, default=2, help='SDL query lookback window')
    ap.add_argument('--community-only', action='store_true')
    args = ap.parse_args()

    if args.products:
        products = [p.strip() for p in args.products.split(',') if p.strip()]
    else:
        products = sorted(PROD_MAP.keys())

    print(f"E2E: sending {args.count} events for {len(products)} products...")
    send_summary = {}

    for i, prod in enumerate(products, 1):
        if prod not in PROD_MAP:
            print(f"[{i}/{len(products)}] skip unknown product: {prod}")
            continue
        print(f"[{i}/{len(products)}] {prod}: sending {args.count} events...", end=' ', flush=True)
        ok, fail = send_events(prod, args.count, args.min_delay, args.max_delay)
        print(f"ok={ok} fail={fail}")
        send_summary[prod] = {"sent": args.count, "ok": ok, "fail": fail}

    if not SDL_API_TOKEN:
        print('\n⚠️  Skipping SDL validation (S1_SDL_API_TOKEN not set).')
        return

    print(f"\nWaiting {args.settle_seconds}s for ingestion...")
    time.sleep(args.settle_seconds)

    print("\nQuerying SDL for parsed events and field extraction...")
    results = {}
    for i, prod in enumerate(products, 1):
        parser_id = SOURCETYPE_MAP.get(prod)
        if not parser_id:
            continue
        print(f"[{i}/{len(products)}] {prod} → {parser_id}", end=' ', flush=True)
        events = query_sdl(parser_id, hours_back=args.hours_back)
        analysis = analyze_fields(events)
        results[prod] = {"parser": parser_id, "analysis": analysis, "send": send_summary.get(prod, {})}
        status = analysis.get('status')
        if status == 'no_events':
            print('❌ no events')
        else:
            print(f"✅ {analysis['event_count']} events, {analysis['field_count']} fields, OCSF {analysis['ocsf_score']}%")

    out = {
        "timestamp": datetime.now().isoformat(),
        "sdl_api_url": SDL_API_URL,
        "products_tested": products,
        "results": results
    }
    out_file = os.path.join(THIS_DIR, 'e2e_sdl_validation_results.json')
    with open(out_file, 'w') as f:
        json.dump(out, f, indent=2)
    print(f"\n📄 Results saved to: {out_file}")


if __name__ == '__main__':
    main()
