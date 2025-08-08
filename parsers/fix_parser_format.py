#!/usr/bin/env python3
"""
Script to identify parsers using regex format that should use gron for JSON events.
These parsers need to be updated to handle JSON events sent by generators.
"""
import json
import os
import sys
from pathlib import Path

def check_parser_format(parser_file):
    """Check if parser uses regex or gron format"""
    try:
        with open(parser_file, 'r') as f:
            content = f.read()
            parser = json.loads(content)
        
        formats = parser.get('formats', [])
        if not formats:
            return 'no_format'
        
        format_str = formats[0].get('format', '')
        
        if 'parse=gron' in format_str:
            return 'gron'
        elif 'logPattern' in str(parser) or 'timestampPattern' in str(parser):
            return 'regex'
        else:
            return 'unknown'
            
    except json.JSONDecodeError:
        return 'invalid_json'
    except Exception as e:
        return f'error: {e}'

def get_corresponding_generator(parser_dir):
    """Map parser directory to generator name"""
    # Extract product name from parser directory
    dir_name = os.path.basename(parser_dir)
    
    # Remove version suffix
    product = dir_name.replace('-latest', '')
    
    # Map common variations
    mappings = {
        'pingone_mfa': 'pingone_mfa',
        'pingprotect': 'pingprotect',
        'pingfederate': 'pingfederate',
        'aws_waf': 'aws_waf',
        'aws_route53': 'aws_route53',
        'cisco_duo': 'cisco_duo',
        'cisco_ironport': 'cisco_ironport',
        'cyberark_conjur': 'cyberark_conjur',
        'iis_w3c': 'iis_w3c',
        'linux_auth': 'linux_auth',
        'microsoft_365_collaboration': 'microsoft_365_collaboration',
        'microsoft_365_defender': 'microsoft_365_defender',
        'zscaler_dns_firewall': 'zscaler_dns_firewall',
        'akamai_cdn': 'akamai_cdn',
        'akamai_dns': 'akamai_dns',
        'akamai_general': 'akamai_general',
        'akamai_sitedefender': 'akamai_sitedefender',
        'axway_sftp': 'axway_sftp',
        'cohesity_backup': 'cohesity_backup',
        'f5_vpn': 'f5_vpn',
        'github_audit': 'github_audit',
        'harness_ci': 'harness_ci',
        'hypr_auth': 'hypr_auth',
        'imperva_sonar': 'imperva_sonar',
        'isc_bind': 'isc_bind',
        'isc_dhcp': 'isc_dhcp',
        'jamf_protect': 'jamf_protect',
        'rsa_adaptive': 'rsa_adaptive',
        'veeam_backup': 'veeam_backup',
        'wiz_cloud': 'wiz_cloud',
    }
    
    return mappings.get(product, product)

def main():
    parsers_dir = Path('/Users/nathanial.smalley/projects/jarvis_coding/parsers/community')
    
    # Check if HEC_sender lists them as JSON products
    sys.path.append('/Users/nathanial.smalley/projects/jarvis_coding/event_python_writer')
    from hec_sender import JSON_PRODUCTS
    
    regex_parsers = []
    gron_parsers = []
    invalid_parsers = []
    
    for parser_dir in parsers_dir.iterdir():
        if not parser_dir.is_dir():
            continue
        
        # Find JSON files in parser directory
        json_files = list(parser_dir.glob('*.json'))
        if not json_files:
            continue
        
        parser_file = json_files[0]
        format_type = check_parser_format(parser_file)
        generator = get_corresponding_generator(parser_dir)
        
        if format_type == 'invalid_json':
            invalid_parsers.append((parser_dir.name, parser_file))
        elif format_type == 'regex':
            # Check if corresponding generator sends JSON
            if generator in JSON_PRODUCTS:
                regex_parsers.append((parser_dir.name, parser_file, generator))
        elif format_type == 'gron':
            gron_parsers.append((parser_dir.name, parser_file))
    
    print("="*80)
    print("PARSER FORMAT ANALYSIS")
    print("="*80)
    
    print(f"\n📊 Statistics:")
    print(f"  Parsers using gron (correct for JSON): {len(gron_parsers)}")
    print(f"  Parsers using regex but need gron: {len(regex_parsers)}")
    print(f"  Invalid JSON files: {len(invalid_parsers)}")
    
    if regex_parsers:
        print(f"\n🔴 PARSERS NEEDING UPDATE ({len(regex_parsers)}):")
        print("These parsers use regex format but their generators send JSON.")
        print("They should be updated to use gron format:\n")
        for name, path, gen in regex_parsers[:20]:
            print(f"  - {name} (generator: {gen})")
            print(f"    Path: {path}")
        
        if len(regex_parsers) > 20:
            print(f"\n  ... and {len(regex_parsers) - 20} more")
    
    if gron_parsers:
        print(f"\n✅ PARSERS ALREADY USING GRON ({len(gron_parsers)}):")
        for name, _ in gron_parsers[:10]:
            print(f"  - {name}")
    
    print("\n📝 RECOMMENDATION:")
    print("Update parsers listed above to use the gron format template.")
    print("See parsers/PARSER_TEMPLATE.json for the correct format.")

if __name__ == "__main__":
    main()