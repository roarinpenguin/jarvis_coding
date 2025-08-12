#!/usr/bin/env python3
"""
Script to identify and fix generators that return Dict but should return JSON string
"""
import os
import re
import importlib.util

# Generators that are marked as JSON_PRODUCTS but might still return Dict
JSON_PRODUCTS = {
    "zscaler", "microsoft_azuread", "okta_authentication", "cyberark_pas", "darktrace",
    "proofpoint", "microsoft_365_mgmt_api", "netskope", "mimecast", "microsoft_azure_ad_signin",
    "microsoft_defender_email", "hashicorp_vault", "corelight_conn", "corelight_http",
    "corelight_ssl", "corelight_tunnel", "tailscale", "github_audit", "extrahop",
    "sentinelone_endpoint", "sentinelone_identity", "abnormal_security", "buildkite",
    "teleport", "cisco_ise", "cisco_umbrella", "google_workspace", "aws_vpc_dns",
    "cisco_networks", "cloudflare_general", "extreme_networks", "f5_networks",
    "google_cloud_dns", "imperva_waf", "juniper_networks", "ubiquiti_unifi",
    "zscaler_firewall", "cisco_fmc", "cisco_ios", "cisco_isa3000", "incapsula",
    "manageengine_general", "manch_siem", "microsoft_windows_eventlog", "paloalto_prismasase",
    "sap", "securelink", "aws_waf", "cyberark_conjur", "iis_w3c", "linux_auth",
    "microsoft_365_collaboration", "microsoft_365_defender", "pingfederate", "zscaler_dns_firewall",
    "akamai_sitedefender", "cisco_duo", "pingone_mfa", "pingprotect", "rsa_adaptive",
    "veeam_backup", "wiz_cloud"
}

def check_generator_return_type(generator_path):
    """Check if a generator returns Dict instead of str"""
    try:
        with open(generator_path, 'r') as f:
            content = f.read()
        
        # Look for function definitions that return Dict
        dict_pattern = r'def\s+\w+.*-> Dict.*:'
        matches = re.findall(dict_pattern, content)
        
        if matches:
            # Check if it actually returns json.dumps() or a dict
            if 'return json.dumps(' in content:
                return "FIXED"  # Already returns JSON string
            elif 'return ' in content and 'json.dumps' not in content:
                return "NEEDS_FIX"  # Returns dict, needs fixing
            else:
                return "UNKNOWN"
        return "NO_DICT_RETURN"
    except Exception as e:
        return f"ERROR: {e}"

def test_generator(product_name):
    """Test if a generator can be imported and called"""
    try:
        # Import the module
        module_path = f"event_python_writer/{product_name}.py"
        if not os.path.exists(module_path):
            return "FILE_NOT_FOUND"
        
        spec = importlib.util.spec_from_file_location(product_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Find the main log function
        function_name = f"{product_name}_log"
        if hasattr(module, function_name):
            func = getattr(module, function_name)
            result = func()
            if isinstance(result, str):
                return "RETURNS_STRING"
            elif isinstance(result, dict):
                return "RETURNS_DICT"
            else:
                return f"RETURNS_OTHER: {type(result)}"
        else:
            return "FUNCTION_NOT_FOUND"
    except Exception as e:
        return f"ERROR: {e}"

def main():
    print("🔍 Checking JSON generators for return type mismatches...")
    print("=" * 70)
    
    problematic_generators = []
    
    for product in sorted(JSON_PRODUCTS):
        generator_path = f"event_python_writer/{product}.py"
        if os.path.exists(generator_path):
            status = check_generator_return_type(generator_path)
            test_result = test_generator(product)
            
            print(f"{product:30} | {status:12} | {test_result}")
            
            if status == "NEEDS_FIX" or test_result == "RETURNS_DICT":
                problematic_generators.append(product)
        else:
            print(f"{product:30} | FILE_NOT_FOUND")
    
    print("\n" + "=" * 70)
    print(f"Found {len(problematic_generators)} generators that need fixing:")
    
    for generator in problematic_generators:
        print(f"  - {generator}")
    
    print("\n💡 Generators already fixed:")
    fixed_count = 0
    for product in sorted(JSON_PRODUCTS):
        generator_path = f"event_python_writer/{product}.py"
        if os.path.exists(generator_path):
            test_result = test_generator(product)
            if test_result == "RETURNS_STRING":
                print(f"  ✅ {product}")
                fixed_count += 1
    
    print(f"\n📊 Summary: {fixed_count} fixed, {len(problematic_generators)} need fixing")

if __name__ == "__main__":
    main()