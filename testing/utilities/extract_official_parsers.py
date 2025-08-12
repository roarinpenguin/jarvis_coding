#!/usr/bin/env python3
"""
Extract Official SentinelOne Parsers
Parses sentinelone_parsers.json and creates individual parser files
"""

import json
import os
from pathlib import Path

def extract_parsers_from_official_file():
    """Extract individual parsers from the official SentinelOne parsers file"""
    
    # Read the official parsers file
    with open('sentinelone_parsers.json', 'r') as f:
        content = f.read()
    
    # This file appears to contain multiple parser configurations
    # We need to parse it carefully as it might not be standard JSON
    
    print("🔍 Analyzing sentinelone_parsers.json structure...")
    print(f"File size: {len(content)} characters")
    
    # Look for parser boundaries
    parser_starts = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        if '"dataSource.name":' in line and 'field' not in line:
            parser_starts.append((i, line.strip()))
    
    print(f"\n📊 Found {len(parser_starts)} potential parser definitions:")
    for line_num, line_content in parser_starts:
        print(f"  Line {line_num}: {line_content}")
    
    return parser_starts

def extract_cisco_ftd_parser():
    """Extract the Cisco FTD parser as an example"""
    print("\n🎯 Extracting Cisco Firewall Threat Defense parser...")
    
    with open('sentinelone_parsers.json', 'r') as f:
        content = f.read()
    
    # Find the start of Cisco FTD parser
    lines = content.split('\n')
    start_line = None
    end_line = None
    
    for i, line in enumerate(lines):
        if '"dataSource.name": "Cisco Firewall Threat Defense"' in line:
            start_line = i - 2  # Start a bit before to get the attributes block
            print(f"  📍 Found Cisco FTD parser at line {i}")
            break
    
    if start_line is None:
        print("  ❌ Could not find Cisco FTD parser")
        return None
    
    # Find the end of this parser (next parser or end of file)
    for i in range(start_line + 10, len(lines)):
        line = lines[i]
        # Look for the start of another parser or end of configuration
        if ('"dataSource.name":' in line and 'Cisco Firewall Threat Defense' not in line) or \
           (line.strip().startswith('}') and i > start_line + 50):
            end_line = i
            print(f"  📍 Parser ends around line {i}")
            break
    
    if end_line is None:
        end_line = len(lines)
    
    # Extract the parser content
    parser_content = '\n'.join(lines[start_line:end_line])
    
    # Try to clean up and make it valid JSON
    # This is a bit tricky since the original might have syntax issues
    print(f"  📄 Extracted {end_line - start_line} lines")
    print(f"  🔧 Content preview:")
    print(parser_content[:500] + "..." if len(parser_content) > 500 else parser_content)
    
    # Save to a temporary file for analysis
    cisco_ftd_dir = Path("parsers/official/cisco_firewall_threat_defense-official")
    cisco_ftd_dir.mkdir(parents=True, exist_ok=True)
    
    with open(cisco_ftd_dir / "raw_extract.txt", 'w') as f:
        f.write(parser_content)
    
    print(f"  💾 Saved raw extract to {cisco_ftd_dir}/raw_extract.txt")
    
    return parser_content

def create_parser_mapping():
    """Create mapping between official parsers and current generators"""
    
    official_parsers = {
        "Cisco Firewall Threat Defense": {
            "current_generator": "cisco_firewall_threat_defense.py",
            "current_parser": "cisco_firewall_threat_defense-latest",
            "ocsf_class": "Network Activity (4001)",
            "priority": "HIGH"
        },
        "Corelight": {
            "current_generator": ["corelight_conn.py", "corelight_http.py", "corelight_ssl.py", "corelight_tunnel.py"],
            "current_parser": ["corelight_conn_logs-latest", "corelight_http_logs-latest", "corelight_ssl_logs-latest", "corelight_tunnel_logs-latest"],
            "ocsf_class": "Network Activity",
            "priority": "HIGH"
        },
        "FortiGate": {
            "current_generator": "fortinet_fortigate.py", 
            "current_parser": "fortinet_fortigate_fortimanager_logs-latest",
            "ocsf_class": "Network Activity",
            "priority": "HIGH"
        },
        "Palo Alto Networks Firewall": {
            "current_generator": "paloalto_firewall.py",
            "current_parser": "paloalto_alternate_logs-latest",
            "ocsf_class": "Network Activity", 
            "priority": "HIGH"
        },
        "Prisma Access": {
            "current_generator": "paloalto_prismasase.py",
            "current_parser": "paloalto_prismasase_logs-latest",
            "ocsf_class": "Network Activity",
            "priority": "MEDIUM"
        },
        "Check Point Next Generation Firewall": {
            "current_generator": "checkpoint.py",
            "current_parser": "checkpoint_checkpoint_logs-latest", 
            "ocsf_class": "Network Activity",
            "priority": "MEDIUM",
            "action": "UPDATE_WITH_OFFICIAL"
        },
        "FortiManager": {
            "current_generator": None,
            "current_parser": None,
            "ocsf_class": "System Activity",
            "priority": "LOW",
            "action": "CREATE_NEW"
        },
        "Infoblox DDI": {
            "current_generator": None,
            "current_parser": None,
            "ocsf_class": "Network Activity", 
            "priority": "MEDIUM",
            "action": "CREATE_NEW"
        },
        "Zscaler Private Access": {
            "current_generator": None,  # Different from zscaler.py
            "current_parser": None,
            "ocsf_class": "Network Activity",
            "priority": "LOW", 
            "action": "CREATE_NEW"
        }
    }
    
    # Save mapping to file
    with open("official_parser_mapping.json", 'w') as f:
        json.dump(official_parsers, f, indent=2)
    
    print("\n📋 Official Parser Mapping:")
    for parser_name, details in official_parsers.items():
        print(f"\n  🔹 {parser_name}")
        print(f"    Generator: {details['current_generator']}")
        print(f"    Parser: {details['current_parser']}")
        print(f"    OCSF Class: {details['ocsf_class']}")
        print(f"    Priority: {details['priority']}")
        if 'action' in details:
            print(f"    Action: {details['action']}")
    
    print(f"\n💾 Mapping saved to official_parser_mapping.json")
    
    return official_parsers

def analyze_current_vs_official():
    """Analyze gaps between current and official parsers"""
    print("\n🔍 Current vs Official Parser Analysis:")
    
    # Read current validation results
    try:
        with open("final_parser_validation_results.json", 'r') as f:
            validation_results = json.load(f)
        
        parsers_with_official = [
            "cisco_firewall_threat_defense",
            "corelight_conn", "corelight_http", "corelight_ssl", "corelight_tunnel", 
            "fortinet_fortigate",
            "paloalto_firewall", "paloalto_prismasase",
            "checkpoint"
        ]
        
        print("\n  📊 Current Performance of Parsers with Official Versions Available:")
        for parser in parsers_with_official:
            if parser in validation_results.get("detailed_results", {}):
                result = validation_results["detailed_results"][parser]["analysis"]
                print(f"    {parser:30s}: {result.get('ocsf_score', 0):3d}% OCSF | {result.get('field_count', 0):3d} fields")
        
        # Calculate improvement potential
        current_avg = sum(
            validation_results["detailed_results"][p]["analysis"].get("ocsf_score", 0) 
            for p in parsers_with_official 
            if p in validation_results.get("detailed_results", {})
        ) / len([p for p in parsers_with_official if p in validation_results.get("detailed_results", {})])
        
        print(f"\n  📈 Current Average OCSF Score: {current_avg:.1f}%")
        print(f"  🎯 Expected with Official Parsers: 80-95%")
        print(f"  📊 Potential Improvement: +{85 - current_avg:.1f}% average")
        
    except FileNotFoundError:
        print("  ⚠️ No validation results found - run final_parser_validation.py first")

if __name__ == "__main__":
    print("🚀 Official SentinelOne Parser Analysis")
    print("=" * 50)
    
    # Check if the official parsers file exists
    if not os.path.exists("sentinelone_parsers.json"):
        print("❌ sentinelone_parsers.json not found!")
        exit(1)
    
    # Extract parser information
    parser_starts = extract_parsers_from_official_file()
    
    # Extract Cisco FTD as example
    cisco_content = extract_cisco_ftd_parser()
    
    # Create mapping
    mapping = create_parser_mapping()
    
    # Analyze current vs official
    analyze_current_vs_official()
    
    print("\n✅ Analysis complete!")
    print("\nNext Steps:")
    print("1. Review extracted parser content in parsers/official/")
    print("2. Update generators to match official parser expectations") 
    print("3. Replace current parsers with official versions")
    print("4. Test with SDL API validation")