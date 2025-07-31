#!/usr/bin/env python3
"""
direct_sample.py

Send quick synthetic events through hec_sender.py.

Usage
-----

# Use a built-in generator (old behaviour)
python3 direct_sample.py --product aws_guardduty -n 2

# Send a one-off raw payload
python3 direct_sample.py \
  --payload '<166>Jul 28 2025 18:09:02 asa-demo : %ASA-6-302015: ...>' \
  --sourcetype CommCiscoASA
"""
from __future__ import annotations
import importlib
import random
import argparse
import time
import sys
import os
from pathlib import Path
import requests

# --- Locate hec_sender in the same project ---------------------------------
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # allow "import hec_sender"
import hec_sender  # noqa: E402

_send_one = hec_sender.send_one


def _load_generator(product: str):
    mod_name, func_list = hec_sender.PROD_MAP[product]
    gen_mod = importlib.import_module(mod_name)
    gen_fn = getattr(gen_mod, func_list[0])     # first generator in the tuple
    attr    = getattr(gen_mod, "ATTR_FIELDS")   # static metadata
    return gen_fn, attr


def main() -> None:
    ap = argparse.ArgumentParser(description="Quick-send sample events via hec_sender")

    # Mutually-exclusive: either generator (--product) or one-off (--payload)
    group = ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--product", choices=hec_sender.PROD_MAP.keys(),
                       help="Use the built-in generator for this product")
    group.add_argument("--payload", help="Literal payload to send once")

    ap.add_argument("--sourcetype",
                    help="Required when --payload is used (HEC raw sourcetype)")

    ap.add_argument("-n", type=int, default=1,
                    help="Number of events to send (generator path only)")
    ap.add_argument("--min-delay", type=float, default=0.05)
    ap.add_argument("--max-delay", type=float, default=0.3)
    args = ap.parse_args()

    # ------------------------------------------------------------------#
    # RAW PAYLOAD MODE
    # ------------------------------------------------------------------#
    if args.payload:
        if not args.sourcetype:
            ap.error("--sourcetype is required when using --payload")

        raw_base = os.getenv("S1_HEC_RAW_URL_BASE",
                             "https://ingest.us1.sentinelone.net/services/collector/raw")
        url = f"{raw_base}?sourcetype={args.sourcetype}"

        resp = requests.post(
            url,
            headers=hec_sender.HEADERS,
            data=args.payload,
            timeout=10
        )
        print(f"Sent raw payload → {url}  (HTTP {resp.status_code})")
        print(resp.text)
        return

    # ------------------------------------------------------------------#
    # GENERATOR MODE
    # ------------------------------------------------------------------#
    gen_fn, attr = _load_generator(args.product)

    print(f"Sending {args.n} {args.product} event(s)…")
    for _ in range(args.n):
        line = gen_fn()
        _send_one(line, args.product, attr)
        time.sleep(random.uniform(args.min_delay, args.max_delay))
    print("Done.")


if __name__ == "__main__":
    main()