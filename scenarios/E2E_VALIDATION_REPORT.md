# End-to-End Validation Report

## Summary
- Scope: Send 1–2 events per generator via HEC, validate parsing via SDL API.
- Tokens: Used env (`S1_HEC_TOKEN`, `S1_SDL_API_TOKEN`).
- Sender: Auto endpoint/TLS/auth fallback; fast pacing; summary on completion.
- Output: Raw results saved to `scenarios/e2e_sdl_validation_results.json`.

## Smoke (3 Generators)
- crowdstrike_falcon: 2/2 sent; SDL 52 events, 6 fields, OCSF 40%.
- aws_cloudtrail: 2/2 sent; SDL 1 event, 100 fields, OCSF 100%.
- cisco_duo: 2/2 sent; SDL 2 events, 59 fields, OCSF 100%.

## Full Run (All Generators, 1 each)
- Sent: 103 products processed; 1 module missing (`aws_vpcflow`).
- High OCSF (≥80%): aws_cloudtrail, netskope, okta_authentication, microsoft_365_mgmt_api, pingone_mfa, pingprotect, mimecast, hashicorp_vault, sentinelone_endpoint, microsoft_azure_signin (eventhub), zscaler, wiz_cloud, cisco_duo.
- Moderate/Basic (40–60%): Many community parsers (expected lower extraction vs marketplace).
- No events yet (likely settle window): harness_ci, imperva_waf, juniper_networks, microsoft_eventhub_azure_signin (community id), paloalto_firewall, paloalto_prismasase, pingfederate, rsa_adaptive.

## Notable Findings
- Missing module: `aws_vpcflow` in `PROD_MAP` (no corresponding module file). `aws_vpcflowlogs` exists and works.
- SDL extraction aligns strongly for marketplace parsers and first‑party sources (e.g., zscaler, S1 endpoint).

## How to Reproduce
- Smoke: `python3 scenarios/e2e_sdl_validation.py --products crowdstrike_falcon,aws_cloudtrail,cisco_duo -n 2 --settle-seconds 120`
- Full: `python3 scenarios/e2e_sdl_validation.py -n 1 --settle-seconds 120`

## Recommendations
- Fix `aws_vpcflow` mapping or remove from `PROD_MAP`.
- Re‑query “no events” set with longer settle (300–600s) to account for ingest delays.
- Consider HTML/CSV summary export for leadership readouts; can be generated from the JSON results.
