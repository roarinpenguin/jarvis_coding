# Event Python Writer  
_Synthetic security-event generators you can slot into any SIEM or pipeline_

---

## Overview
This repository contains lightweight, **self-contained Python generators** that
emit realistic—but wholly fabricated—security log events.  
Each generator is <150 lines, uses only the Python standard library, and
returns one flat JSON-serialisable dict per call, ready for your parser/mapper.

Current generators:

| Generator | Vendor / Source | Focus | Risk Scenarios Covered |
|-----------|-----------------|-------|------------------------|
| `imperva_log()` | Imperva Cloud WAF | Audit-trail activity | Site deletions, policy disable, API-key creation, rule deletes, account changes |

> **Why synthetic?**  
> * Load-test analytics & detections without touching production data  
> * Demo dashboards when real customer logs are unavailable  
> * Unit-test parsers / pipelines with deterministic fixtures

---

## Quick Start

```bash
python -m venv .venv && source .venv/bin/activate
python - <<'PY'
from imperva_generator import imperva_log   # file created earlier
from json import dumps
for _ in range(3):
    print(dumps(imperva_log(), indent=2))
PY