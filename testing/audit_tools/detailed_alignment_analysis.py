#!/usr/bin/env python3
"""
Detailed Generator-Parser Alignment Analysis
Provides specific mapping recommendations and fixes for misaligned pairs
"""

import json
from pathlib import Path

def create_detailed_mapping_analysis():
    """Create detailed analysis with specific fix recommendations"""
    
    # Load audit results
    audit_path = Path("/Users/nathanial.smalley/projects/jarvis_coding/comprehensive_audit_results.json")
    with open(audit_path) as f:
        audit_results = json.load(f)
    
    # Manual mapping corrections based on domain knowledge
    correct_mappings = {
        # Identity & Access Management
        "okta_authentication": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/okta_ocsf_logs-latest/okta_ocsf_logs.json",
            "fix": "MAPPING_FIX - Parser exists but naming mismatch",
            "priority": "HIGH"
        },
        "microsoft_azure_ad_signin": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/microsoft_azure_ad_logs-latest/microsoft_azure_ad_logs.json",
            "fix": "MAPPING_FIX - Parser exists but naming mismatch",
            "priority": "HIGH"
        },
        
        # Endpoint Security
        "sentinelone_endpoint": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/singularityidentity_singularityidentity_logs-latest/singularityidentity_singularityidentity_logs.json",
            "fix": "MAPPING_FIX - SentinelOne parser exists under different name",
            "priority": "CRITICAL"
        },
        "crowdstrike_falcon": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/crowdstrike_endpoint-latest/crowdstrike_endpoint.json",
            "fix": "MAPPING_FIX - Parser exists but naming mismatch",
            "priority": "CRITICAL"
        },
        
        # Network Security - Format Fixes
        "cisco_asa": {
            "parser": "CREATE_PARSER",
            "fix": "PARSER_MISSING - Need to create cisco_asa parser for SYSLOG format",
            "priority": "CRITICAL"
        },
        "paloalto_firewall": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/paloalto_paloalto_logs-latest/paloalto_paloalto.json",
            "fix": "MAPPING_FIX - Parser exists but naming mismatch",
            "priority": "CRITICAL"
        },
        "cisco_meraki": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/cisco_meraki-latest/cisco_meraki.json", 
            "fix": "FORMAT_FIX - Generator produces JSON but parser expects SYSLOG",
            "priority": "CRITICAL"
        },
        "cisco_meraki_flow": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/cisco_meraki_flow_logs-latest/cisco_meraki_flow.json",
            "fix": "FORMAT_FIX - Generator produces JSON but parser expects SYSLOG", 
            "priority": "CRITICAL"
        },
        
        # Format conversion fixes
        "zscaler_firewall": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/zscaler_firewall_logs-latest/zscaler_firewall.json",
            "fix": "FORMAT_FIX - Convert generator from CSV to JSON format",
            "priority": "CRITICAL"
        },
        "cisco_ise": {
            "parser": "/Users/nathanial.smalley/projects/jarvis_coding/parsers/community/cisco_ise_logs-latest/cisco_ise.json",
            "fix": "FORMAT_FIX - Convert generator from CSV to expected format",
            "priority": "CRITICAL"
        },
        
        # AWS CloudTrail - Critical Enterprise Fix
        "aws_cloudtrail": {
            "parser": "MARKETPLACE_PARSER",
            "fix": "MARKETPLACE_FIX - Use marketplace-awscloudtrail-latest parser",
            "priority": "CRITICAL"
        }
    }
    
    # Create comprehensive fix plan
    fix_plan = {
        "critical_fixes": [],
        "high_priority_fixes": [],
        "medium_priority_fixes": [],
        "mapping_fixes": [],
        "format_fixes": [],
        "parser_creation_needed": []
    }
    
    print("🔍 DETAILED GENERATOR-PARSER ALIGNMENT ANALYSIS")
    print("=" * 60)
    print()
    
    print("📋 CRITICAL ENTERPRISE VENDOR FIXES (Top Priority)")
    print("-" * 50)
    
    critical_enterprise_fixes = []
    
    # AWS CloudTrail - Missing parser
    critical_enterprise_fixes.append({
        "generator": "aws_cloudtrail",
        "issue": "No parser mapping found",
        "solution": "Map to marketplace-awscloudtrail-latest parser",
        "action": "Update HEC sender to use marketplace parser",
        "complexity": "LOW - Configuration change only"
    })
    
    # Okta Authentication - Mapping issue
    critical_enterprise_fixes.append({
        "generator": "okta_authentication", 
        "issue": "Parser exists but name mismatch",
        "solution": "Map to okta_ocsf_logs-latest parser",
        "action": "Update name matching logic",
        "complexity": "LOW - Mapping correction"
    })
    
    # SentinelOne Endpoint - Mapping issue
    critical_enterprise_fixes.append({
        "generator": "sentinelone_endpoint",
        "issue": "Parser exists under different name", 
        "solution": "Map to singularityidentity parser",
        "action": "Correct product name mapping",
        "complexity": "LOW - Mapping correction"
    })
    
    # CrowdStrike Falcon - Mapping issue
    critical_enterprise_fixes.append({
        "generator": "crowdstrike_falcon",
        "issue": "Parser exists but name mismatch",
        "solution": "Map to crowdstrike_endpoint parser", 
        "action": "Update name matching logic",
        "complexity": "LOW - Mapping correction"
    })
    
    # Cisco ASA - Missing parser
    critical_enterprise_fixes.append({
        "generator": "cisco_asa",
        "issue": "No parser exists for SYSLOG format",
        "solution": "Create cisco_asa parser for syslog events",
        "action": "Develop new parser configuration",
        "complexity": "MEDIUM - New parser needed"
    })
    
    # Palo Alto Firewall - Mapping issue  
    critical_enterprise_fixes.append({
        "generator": "paloalto_firewall",
        "issue": "Parser exists but name mismatch",
        "solution": "Map to paloalto_paloalto_logs parser",
        "action": "Update name matching logic", 
        "complexity": "LOW - Mapping correction"
    })
    
    for i, fix in enumerate(critical_enterprise_fixes, 1):
        print(f"{i}. **{fix['generator']}**")
        print(f"   Issue: {fix['issue']}")
        print(f"   Solution: {fix['solution']}")
        print(f"   Action: {fix['action']}")
        print(f"   Complexity: {fix['complexity']}")
        print()
    
    print("🔧 FORMAT MISMATCH FIXES (High Priority)")
    print("-" * 50)
    
    format_fixes = [
        {
            "generator": "cisco_meraki",
            "current_format": "JSON",
            "expected_format": "SYSLOG",
            "fix": "Convert generator to produce syslog format",
            "complexity": "MEDIUM"
        },
        {
            "generator": "cisco_meraki_flow", 
            "current_format": "JSON",
            "expected_format": "SYSLOG",
            "fix": "Convert generator to produce syslog format",
            "complexity": "MEDIUM"
        },
        {
            "generator": "zscaler_firewall",
            "current_format": "CSV", 
            "expected_format": "JSON",
            "fix": "Convert generator from CSV to JSON format",
            "complexity": "MEDIUM"
        },
        {
            "generator": "cisco_ise",
            "current_format": "CSV",
            "expected_format": "SYSLOG/JSON",
            "fix": "Convert generator from CSV to proper format",
            "complexity": "MEDIUM"
        }
    ]
    
    for i, fix in enumerate(format_fixes, 1):
        print(f"{i}. **{fix['generator']}**")
        print(f"   Current: {fix['current_format']} → Expected: {fix['expected_format']}")
        print(f"   Fix: {fix['fix']}")
        print(f"   Complexity: {fix['complexity']}")
        print()
    
    print("🎯 IMPLEMENTATION PRIORITY ORDER")
    print("-" * 50)
    print()
    print("**Phase 1 (Immediate - 1-2 days):**")
    print("1. Fix name mapping issues (okta, crowdstrike, sentinelone, paloalto)")
    print("2. Configure AWS CloudTrail marketplace parser")
    print("3. Test corrected mappings")
    print()
    print("**Phase 2 (Short-term - 3-5 days):**") 
    print("1. Convert format mismatches (cisco_meraki, zscaler_firewall)")
    print("2. Create cisco_asa parser")
    print("3. Validate format conversions")
    print()
    print("**Phase 3 (Medium-term - 1-2 weeks):**")
    print("1. Address remaining format mismatches")
    print("2. Create missing parsers for non-enterprise vendors") 
    print("3. Comprehensive validation testing")
    print()
    
    print("📊 SUCCESS METRICS")
    print("-" * 50)
    print(f"• Current working pairs: {len(audit_results.get('working_pairs', []))}")
    print(f"• Current success rate: 56.9%")
    print(f"• Potential working pairs after Phase 1: ~60-65 pairs")
    print(f"• Target success rate after Phase 1: ~75-80%")
    print(f"• Target success rate after all phases: ~90%+")
    print()
    
    print("🔗 RECOMMENDED NEXT STEPS")
    print("-" * 50)
    print("1. **Fix Name Mapping Script**: Update generator-parser matching logic")
    print("2. **Test Critical Mappings**: Validate okta, crowdstrike, sentinelone connections")
    print("3. **AWS CloudTrail Priority**: Configure marketplace parser immediately")
    print("4. **Format Converter Tool**: Create utility to convert generator formats")
    print("5. **Validation Framework**: Implement end-to-end testing for each fix")
    
    return {
        "critical_enterprise_fixes": critical_enterprise_fixes,
        "format_fixes": format_fixes,
        "total_potential_improvements": len(critical_enterprise_fixes) + len(format_fixes)
    }

if __name__ == "__main__":
    analysis = create_detailed_mapping_analysis()
    print(f"\n🎯 Total potential improvements: {analysis['total_potential_improvements']}")
    print("📈 Estimated success rate improvement: +20-25%")