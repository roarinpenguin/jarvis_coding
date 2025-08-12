# Project Reorganization Plan

## Current Issues
1. **Duplicate parsers**: Entire parser tree duplicated inside `zscaler_firewall_logs-latest/`
2. **Scattered root files**: Test scripts, validation tools, and scenarios mixed in root
3. **100+ event generators** in single directory with no categorization
4. **Inconsistent naming** between parsers and generators

## Proposed Structure

```
jarvis_coding/
├── README.md
├── CLAUDE.md
├── requirements.txt
│
├── docs/                           # Documentation
│   ├── attack_correlation_guide.md
│   ├── FINAL_TEST_REPORT.md
│   └── validation_results/
│
├── event_generators/               # Event generators organized by category
│   ├── cloud_infrastructure/       # AWS, Google Cloud, Azure
│   │   ├── aws_cloudtrail.py
│   │   ├── aws_guardduty.py
│   │   └── ...
│   ├── network_security/           # Firewalls, Network devices
│   │   ├── cisco_firewall_threat_defense.py
│   │   ├── paloalto_firewall.py
│   │   └── ...
│   ├── endpoint_security/          # Endpoint protection
│   │   ├── crowdstrike_falcon.py
│   │   ├── sentinelone_endpoint.py
│   │   └── ...
│   ├── identity_access/            # IAM, Authentication
│   │   ├── okta_authentication.py
│   │   ├── microsoft_azuread.py
│   │   └── ...
│   ├── email_security/             # Email security platforms
│   │   ├── mimecast.py
│   │   ├── proofpoint.py
│   │   └── ...
│   ├── web_security/               # WAF, Web proxies
│   │   ├── cloudflare_waf.py
│   │   ├── zscaler.py
│   │   └── ...
│   ├── infrastructure/             # IT management, Backup
│   │   ├── veeam_backup.py
│   │   ├── vmware_vcenter.py
│   │   └── ...
│   └── shared/                     # Common utilities
│       ├── __init__.py
│       ├── hec_sender.py
│       └── s1_api_client.py
│
├── parsers/                        # Clean parser structure
│   ├── community/                  # Community parsers (cleaned)
│   └── sentinelone/               # SentinelOne marketplace parsers
│
├── scenarios/                      # Attack scenarios
│   ├── enterprise_attack_scenario.py
│   ├── enterprise_attack_scenario_10min.py
│   ├── quick_scenario.py
│   ├── showcase_attack_scenario.py
│   └── configs/                    # Scenario JSON configs
│       ├── enterprise_attack_scenario.json
│       ├── enterprise_attack_scenario_10min.json
│       └── showcase_attack_scenario.json
│
├── testing/                        # All testing and validation
│   ├── validation/
│   │   ├── final_parser_validation.py
│   │   ├── comprehensive_generator_test_results.json
│   │   └── final_parser_validation_results.json
│   ├── bulk_testing/
│   │   ├── bulk_event_sender.py
│   │   ├── systematic_event_sender.sh
│   │   └── test_all_generators.py
│   └── utilities/
│       ├── fix_json_generators.py
│       ├── analyze_parser_overlap.py
│       └── extract_official_parsers.py
│
└── utilities/                      # Standalone utilities
    ├── create_sentinelone_parsers.py
    ├── send_key_events.py
    └── official_parser_mapping.json
```

## Migration Steps

### Phase 1: Clean Parser Duplicates
- Remove duplicate parsers from `zscaler_firewall_logs-latest/` nested structure
- Fix any parser naming inconsistencies

### Phase 2: Organize Event Generators
- Create category directories
- Move generators to appropriate categories
- Update import paths in hec_sender.py

### Phase 3: Move Testing & Scenarios
- Create dedicated directories for testing and scenarios
- Move all validation scripts and results

### Phase 4: Documentation
- Consolidate documentation in docs/ directory
- Update CLAUDE.md with new structure

## Benefits
1. **Clear categorization** of 100+ event generators
2. **Separated concerns** (generators, parsers, testing, scenarios)
3. **Easier navigation** and discovery
4. **Consistent naming** and structure
5. **Better maintainability**