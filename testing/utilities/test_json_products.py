#!/usr/bin/env python3
"""Test JSON products from enterprise scenario to verify they're working"""

import os
os.environ['S1_HEC_TOKEN'] = '1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7'

from hec_sender import send_one, JSON_PRODUCTS

# Test each JSON product from our enterprise scenario
json_products_to_test = [
    "cisco_duo",
    "cisco_umbrella", 
    "pingone_mfa",
    "microsoft_windows_eventlog",
    "cisco_ise",
    "f5_networks",
    "imperva_waf",
    "github_audit",
    "pingprotect",
    "aws_cloudtrail",
    "zscaler",
    "microsoft_azuread",
    "okta_authentication",
    "proofpoint",
    "netskope",
    "hashicorp_vault"
]

print("Testing JSON products from enterprise attack scenario...")
print("=" * 60)

success_count = 0
total_count = 0

for product in json_products_to_test:
    total_count += 1
    
    # Check if product is in JSON_PRODUCTS
    is_json = product in JSON_PRODUCTS
    
    try:
        # Import and test the generator
        module = __import__(product)
        func_name = f"{product}_log"
        
        if hasattr(module, func_name):
            generator_func = getattr(module, func_name)
            event = generator_func()
            
            # Test sending
            result = send_one(event, product, {
                "dataSource.vendor": product.split('_')[0].title(),
                "dataSource.name": product.replace('_', ' ').title(),
                "dataSource.category": "security"
            })
            
            if result and (result.get('text') == 'Success' or result.get('status') == 'success'):
                print(f"✅ {product:30s} - JSON: {str(is_json):5s} - SUCCESS")
                success_count += 1
            else:
                print(f"❌ {product:30s} - JSON: {str(is_json):5s} - FAILED: {result}")
        else:
            print(f"⚠️  {product:30s} - JSON: {str(is_json):5s} - Missing function {func_name}")
            
    except Exception as e:
        print(f"❌ {product:30s} - JSON: {str(is_json):5s} - ERROR: {str(e)}")

print("=" * 60)
print(f"Results: {success_count}/{total_count} products working ({success_count/total_count*100:.1f}%)")
print("=" * 60)

# Show which products are going to /event vs /raw
print("\nRouting Summary:")
print("JSON Products (→ /event endpoint):")
for product in json_products_to_test:
    if product in JSON_PRODUCTS:
        print(f"  ✅ {product}")

print("\nRAW Products (→ /raw endpoint):")        
for product in json_products_to_test:
    if product not in JSON_PRODUCTS:
        print(f"  📄 {product}")