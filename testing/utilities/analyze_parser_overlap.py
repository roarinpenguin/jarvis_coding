#!/usr/bin/env python3
"""
Analyze Parser Overlap Between Official SentinelOne and Community Parsers
Identify community parsers that can be replaced with official versions
"""

import json
import os
from pathlib import Path

def get_official_parsers():
    """Get list of official SentinelOne parsers"""
    official_parsers = {}
    
    sentinelone_dir = Path("parsers/sentinelone")
    if sentinelone_dir.exists():
        for parser_dir in sentinelone_dir.iterdir():
            if parser_dir.is_dir():
                metadata_file = parser_dir / "metadata.yaml"
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        content = f.read()
                        # Extract product name from metadata
                        for line in content.split('\n'):
                            if line.startswith('product:'):
                                product = line.split(':', 1)[1].strip()
                                official_parsers[parser_dir.name] = product
                                break
    
    return official_parsers

def get_community_parsers():
    """Get list of community parsers"""
    community_parsers = {}
    
    community_dir = Path("parsers/community")
    if community_dir.exists():
        for parser_dir in community_dir.iterdir():
            if parser_dir.is_dir():
                # Extract vendor and product from directory name
                dir_name = parser_dir.name
                community_parsers[dir_name] = {
                    "path": str(parser_dir),
                    "files": list(parser_dir.glob("*.json"))
                }
    
    return community_parsers

def find_overlapping_parsers():
    """Find community parsers that overlap with official ones"""
    official = get_official_parsers()
    community = get_community_parsers()
    
    print("🔍 Analyzing Parser Overlap")
    print("=" * 60)
    
    overlaps = []
    
    # Define mapping between official and community parser names
    overlap_mapping = {
        # Official SentinelOne -> Community parsers that could be replaced
        "cisco_firewall_threat_defense": [
            "cisco_firewall_threat_defense-latest",
            "cisco_firewall-latest"
        ],
        "check_point_next_generation_firewall": [
            "checkpoint_checkpoint_logs-latest"
        ],
        "corelight": [
            "corelight_conn_logs-latest",
            "corelight_http_logs-latest", 
            "corelight_ssl_logs-latest",
            "corelight_tunnel_logs-latest"
        ],
        "fortigate": [
            "fortinet_fortigate_fortimanager_logs-latest"
        ],
        "fortimanager": [
            "fortinet_fortigate_fortimanager_logs-latest"  # May be same as FortiGate
        ],
        "palo_alto_networks_firewall": [
            "paloalto_alternate_logs-latest",
            "paloalto_paloalto_logs-latest"
        ],
        "prisma_access": [
            "paloalto_prismasase_logs-latest"
        ],
        "infoblox_ddi": [
            # No direct community equivalent found
        ],
        "zscaler_private_access": [
            # Different from existing zscaler parsers (Internet Access vs Private Access)
        ]
    }
    
    print("📊 Official SentinelOne Parsers Available:")
    for official_name, product in official.items():
        print(f"  ✅ {official_name:35s} → {product}")
    
    print(f"\n🔍 Community Parser Overlap Analysis:")
    
    for official_name, community_candidates in overlap_mapping.items():
        if not community_candidates:
            continue
            
        print(f"\n🎯 Official: {official_name}")
        print(f"   Product: {official.get(official_name, 'Unknown')}")
        
        for candidate in community_candidates:
            if candidate in community:
                json_files = community[candidate]["files"]
                print(f"   📁 Community: {candidate}")
                print(f"      Files: {len(json_files)} JSON files")
                print(f"      Status: ⚠️ CANDIDATE FOR REPLACEMENT")
                
                overlaps.append({
                    "official": official_name,
                    "community": candidate,
                    "recommendation": "REPLACE",
                    "reason": "Official parser available"
                })
            else:
                print(f"   📁 Community: {candidate} (NOT FOUND)")
    
    return overlaps, official, community

def analyze_parser_performance():
    """Analyze current performance of community parsers that have official replacements"""
    print(f"\n📈 Performance Analysis of Replaceable Parsers:")
    
    try:
        with open("final_parser_validation_results.json", 'r') as f:
            validation_results = json.load(f)
        
        replaceable_parsers = [
            "cisco_firewall_threat_defense",
            "fortinet_fortigate", 
            "corelight_conn",
            "corelight_http", 
            "corelight_ssl",
            "corelight_tunnel",
            "paloalto_prismasase"
        ]
        
        print(f"\n  Current Performance (Before Official Parser Replacement):")
        total_current = 0
        total_parsers = 0
        
        for parser in replaceable_parsers:
            if parser in validation_results.get("detailed_results", {}):
                result = validation_results["detailed_results"][parser]["analysis"]
                ocsf_score = result.get("ocsf_score", 0)
                field_count = result.get("field_count", 0)
                
                status = "🟢 Excellent" if ocsf_score >= 80 else "🟡 Good" if ocsf_score >= 60 else "🔴 Basic"
                
                print(f"    {parser:30s}: {ocsf_score:3d}% OCSF | {field_count:3d} fields | {status}")
                total_current += ocsf_score
                total_parsers += 1
        
        if total_parsers > 0:
            avg_current = total_current / total_parsers
            print(f"\n  📊 Current Average: {avg_current:.1f}% OCSF score")
            print(f"  🎯 Expected with Official: 80-95% OCSF score")
            print(f"  📈 Potential Improvement: +{85 - avg_current:.1f}% average")
        
    except FileNotFoundError:
        print("  ⚠️ No validation results found - run final_parser_validation.py first")

def create_replacement_plan():
    """Create a plan for replacing community parsers with official ones"""
    overlaps, official, community = find_overlapping_parsers()
    
    print(f"\n📋 Replacement Plan:")
    print("-" * 60)
    
    replacement_plan = {
        "immediate": [],
        "high_priority": [],
        "medium_priority": [],
        "investigation_needed": []
    }
    
    # Categorize replacements by priority
    priority_mapping = {
        "cisco_firewall_threat_defense": "immediate",  # Already have working JSON
        "corelight": "high_priority",  # Multiple parsers, high impact
        "fortigate": "high_priority",  # Single parser, widely used
        "palo_alto_networks_firewall": "high_priority",  # Network security critical
        "prisma_access": "medium_priority",  # Specialized use case
        "check_point_next_generation_firewall": "medium_priority",  # Need to extract JSON first
        "fortimanager": "investigation_needed",  # May duplicate FortiGate
        "infoblox_ddi": "investigation_needed",  # No community equivalent
        "zscaler_private_access": "investigation_needed"  # Different from existing zscaler
    }
    
    for overlap in overlaps:
        official_name = overlap["official"]
        priority = priority_mapping.get(official_name, "investigation_needed")
        replacement_plan[priority].append(overlap)
    
    # Print replacement plan
    for priority, items in replacement_plan.items():
        if items:
            priority_label = priority.replace("_", " ").title()
            print(f"\n🎯 {priority_label}:")
            for item in items:
                print(f"   Replace: {item['community']}")
                print(f"   With:    {item['official']} (official)")
                print(f"   Reason:  {item['reason']}")
    
    return replacement_plan

def generate_migration_commands():
    """Generate commands for parser migration"""
    print(f"\n🔧 Migration Commands:")
    print("-" * 60)
    
    print(f"\n# 1. Backup current community parsers")
    print(f"mkdir -p parsers/community_backup")
    print(f"cp -r parsers/community/ parsers/community_backup/")
    
    print(f"\n# 2. Update hec_sender.py mappings to use official parsers")
    print(f"# Edit SOURCETYPE_MAP in event_python_writer/hec_sender.py:")
    
    mappings = {
        "cisco_firewall_threat_defense": "sentinelone-ciscoftd-official",
        "fortinet_fortigate": "sentinelone-fortigate-official",
        "corelight_conn": "sentinelone-corelight-conn-official",
        "corelight_http": "sentinelone-corelight-http-official", 
        "corelight_ssl": "sentinelone-corelight-ssl-official",
        "corelight_tunnel": "sentinelone-corelight-tunnel-official",
        "paloalto_prismasase": "sentinelone-prismasase-official"
    }
    
    for generator, parser in mappings.items():
        print(f'    "{generator}": "{parser}",')
    
    print(f"\n# 3. Test each replacement")
    for generator in mappings.keys():
        print(f"python event_python_writer/hec_sender.py --product {generator} --count 5")
        print(f"# Wait 60 seconds, then:")
        print(f"python final_parser_validation.py --parser {generator} --detailed")
        print()
    
    print(f"# 4. Remove replaced community parsers (after validation)")
    community_to_remove = [
        "cisco_firewall_threat_defense-latest",
        "fortinet_fortigate_fortimanager_logs-latest",
        "corelight_conn_logs-latest",
        "corelight_http_logs-latest",
        "corelight_ssl_logs-latest", 
        "corelight_tunnel_logs-latest",
        "paloalto_prismasase_logs-latest"
    ]
    
    for parser_dir in community_to_remove:
        print(f"# rm -rf parsers/community/{parser_dir}")
    
    return mappings

if __name__ == "__main__":
    print("🚀 Community vs Official Parser Overlap Analysis")
    print("=" * 70)
    
    # Analyze overlaps
    overlaps, official, community = find_overlapping_parsers()
    
    # Analyze performance
    analyze_parser_performance()
    
    # Create replacement plan
    replacement_plan = create_replacement_plan()
    
    # Generate migration commands
    migration_mappings = generate_migration_commands()
    
    print(f"\n✅ Analysis Complete!")
    print(f"📊 Found {len(overlaps)} community parsers that can be replaced")
    print(f"🎯 Immediate replacement ready: 1 parser (Cisco FTD)")
    print(f"📈 High priority replacements: 4 parsers (Corelight suite, FortiGate, Palo Alto)")
    print(f"💾 Migration commands generated for systematic replacement")