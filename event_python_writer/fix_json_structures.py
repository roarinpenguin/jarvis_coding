#!/usr/bin/env python3
"""
Fix all generators to use proper nested JSON structure instead of dot notation
"""
import os
import re

def fix_datasource_fields(filepath):
    """Fix dataSource.* fields to nested structure"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match ATTR_FIELDS with dataSource.* fields
    patterns = [
        # Match standard ATTR_FIELDS with dataSource fields
        (r'ATTR_FIELDS[^{]*\{[^}]*"dataSource\.vendor"[^}]*\}', 'fix_attr_fields'),
        # Match inline dataSource fields in dicts
        (r'"dataSource\.vendor":\s*"([^"]+)"[,\s]*"dataSource\.name":\s*"([^"]+)"[,\s]*"dataSource\.category":\s*"([^"]+)"', 'fix_inline'),
    ]
    
    fixes_made = []
    
    for pattern, fix_type in patterns:
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            if fix_type == 'fix_attr_fields':
                # Extract the vendor, name, category values
                block = match.group(0)
                vendor_match = re.search(r'"dataSource\.vendor":\s*"([^"]+)"', block)
                name_match = re.search(r'"dataSource\.name":\s*"([^"]+)"', block)
                category_match = re.search(r'"dataSource\.category":\s*"([^"]+)"', block)
                
                if vendor_match and name_match and category_match:
                    vendor = vendor_match.group(1)
                    name = name_match.group(1)
                    category = category_match.group(1)
                    
                    # Build nested structure
                    new_block = f'''ATTR_FIELDS = {{
    "dataSource": {{
        "vendor": "{vendor}",
        "name": "{name}",
        "category": "{category}"
    }}
}}'''
                    content = content.replace(match.group(0), new_block)
                    fixes_made.append(f"Fixed ATTR_FIELDS to nested structure")
                    
            elif fix_type == 'fix_inline':
                vendor = match.group(1)
                name = match.group(2)
                category = match.group(3)
                
                new_structure = f'''"dataSource": {{
        "vendor": "{vendor}",
        "name": "{name}",
        "category": "{category}"
    }}'''
                content = content.replace(match.group(0), new_structure)
                fixes_made.append(f"Fixed inline dataSource to nested structure")
    
    # Fix spread operator usage of ATTR_FIELDS
    if '**ATTR_FIELDS' in content and '"dataSource": {' in content:
        # Need to merge ATTR_FIELDS differently for nested structure
        content = re.sub(r'\*\*ATTR_FIELDS', '"dataSource": ATTR_FIELDS["dataSource"]', content)
        fixes_made.append("Fixed ATTR_FIELDS spread operator for nested structure")
    
    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        return fixes_made
    
    return []

def main():
    # List of generators identified as having dot notation issues
    generators_to_fix = [
        "abnormal_security", "akamai_sitedefender", "aws_vpc_dns", "aws_vpcflowlogs",
        "buildkite", "cisco_duo", "cisco_fmc", "cisco_ios", "cisco_isa3000", 
        "cisco_ise", "cisco_meraki", "cisco_networks", "cloudflare_general",
        "cyberark_conjur", "extreme_networks", "f5_networks", "google_cloud_dns",
        "google_workspace", "iis_w3c", "imperva_sonar", "imperva_waf", "incapsula",
        "isc_bind", "isc_dhcp", "juniper_networks", "linux_auth", "manageengine_general",
        "manch_siem", "microsoft_365_collaboration", "microsoft_365_defender",
        "microsoft_windows_eventlog", "okta_authentication", "paloalto_prismasase",
        "rsa_adaptive", "sap", "securelink", "sentinelone_endpoint", "sentinelone_identity",
        "teleport", "ubiquiti_unifi", "veeam_backup", "wiz_cloud", "zscaler_dns_firewall",
        "zscaler_firewall"
    ]
    
    fixed_count = 0
    for generator in generators_to_fix:
        filepath = f"/Users/nathanial.smalley/projects/jarvis_coding/event_python_writer/{generator}.py"
        if os.path.exists(filepath):
            fixes = fix_datasource_fields(filepath)
            if fixes:
                print(f"✅ Fixed {generator}: {', '.join(fixes)}")
                fixed_count += 1
            else:
                print(f"⚠️  {generator}: No automatic fixes applied (may need manual review)")
        else:
            print(f"❌ {generator}: File not found")
    
    print(f"\n{'='*60}")
    print(f"Fixed {fixed_count} generators")
    print(f"Remaining may need manual review")

if __name__ == "__main__":
    main()