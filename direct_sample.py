
#!/usr/bin/env python3
"""
direct_sample.py

A **minimal** harness for quickly sending a few synthetic events through
hec_sender.py without invoking its CLI every time.

Example:
    python3 direct_sample.py --product aws_guardduty --n 2
"""

from __future__ import annotations
import importlib
import random
import argparse
import time
import sys
from pathlib import Path

# --- Locate hec_sender in the same project ---------------------------------
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # allow "import hec_sender"

import hec_sender  # noqa: E402

# Convenience shortcut to hec_sender internals
_send_one = hec_sender.send_one


def _load_generator(product: str):
    """
    Dynamically import the generator module and return
    (generator_function, attr_fields).
    """
    mod_name, func_name = hec_sender.PROD_MAP[product]
    gen_mod = importlib.import_module(mod_name)
    gen_fn = getattr(gen_mod, func_name[0])  # first generator entry
    attr_fields = getattr(gen_mod, "ATTR_FIELDS")
    return gen_fn, attr_fields


def main() -> None:
    ap = argparse.ArgumentParser(description="Quick‑send sample events via hec_sender")
    ap.add_argument("--product", required=True, choices=hec_sender.PROD_MAP.keys())
    ap.add_argument("-n", type=int, default=1, help="How many events to send (default: 1)")
    ap.add_argument("--min-delay", type=float, default=0.05, help="s between events (min)")
    ap.add_argument("--max-delay", type=float, default=0.3, help="s between events (max)")
    args = ap.parse_args()

    gen_fn, attr = _load_generator(args.product)

    print(f"Sending {args.n} {args.product} event(s) …")
    for _ in range(args.n):
        event_line = gen_fn()
        _send_one(event_line, args.product, attr)
        time.sleep(random.uniform(args.min_delay, args.max_delay))

    print("Done.")


if __name__ == "__main__":
    main()