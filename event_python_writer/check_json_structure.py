#!/usr/bin/env python3
"""
Check JSON structure of all generators to find flat vs nested formats
"""
import importlib
import json
import sys
from hec_sender import PROD_MAP

def check_for_dot_notation(obj, path=""):
    """Recursively check if object has dot notation in keys"""
    dot_keys = []
    
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            
            # Check if key contains dots (flat structure)
            if '.' in key:
                dot_keys.append(key)
            
            # Recurse into nested structures
            dot_keys.extend(check_for_dot_notation(value, current_path))
    
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            dot_keys.extend(check_for_dot_notation(item, f"{path}[{i}]"))
    
    return dot_keys

def analyze_generator(product_name):
    """Analyze a single generator's output structure"""
    try:
        if product_name not in PROD_MAP:
            return None, f"Not in PROD_MAP"
        
        mod_name, func_names = PROD_MAP[product_name]
        gen_mod = importlib.import_module(mod_name)
        
        # Get first function
        if not func_names:
            return None, "No functions defined"
        
        func_name = func_names[0]
        if not hasattr(gen_mod, func_name):
            return None, f"Missing function {func_name}"
        
        # Generate an event
        generator = getattr(gen_mod, func_name)
        event = generator()
        
        # Check if it returns dict or string
        if isinstance(event, str):
            # Try to parse as JSON
            try:
                event = json.loads(event)
                event_type = "json_string"
            except:
                event_type = "raw_string"
        else:
            event_type = "dict"
        
        # Check for dot notation
        dot_keys = check_for_dot_notation(event)
        
        return {
            "type": event_type,
            "has_dot_notation": len(dot_keys) > 0,
            "dot_keys": dot_keys[:5]  # Show first 5 dot keys
        }, None
        
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    products_with_dots = []
    products_returning_strings = []
    products_clean = []
    
    for product in sorted(PROD_MAP.keys()):
        result, error = analyze_generator(product)
        
        if error:
            print(f"❌ {product}: ERROR - {error}")
        elif result:
            if result["has_dot_notation"]:
                products_with_dots.append(product)
                print(f"⚠️  {product}: Has dot notation - {result['dot_keys'][:3]}")
            elif result["type"] != "dict":
                products_returning_strings.append(product)
                print(f"📝 {product}: Returns {result['type']}")
            else:
                products_clean.append(product)
                print(f"✅ {product}: Clean nested structure")
    
    print("\n" + "="*80)
    print(f"SUMMARY:")
    print(f"Products with dot notation: {len(products_with_dots)}")
    print(f"Products returning strings: {len(products_returning_strings)}")
    print(f"Products with clean nested structure: {len(products_clean)}")
    print(f"Total: {len(PROD_MAP)}")
    
    if products_with_dots:
        print(f"\nGenerators needing nested structure fix ({len(products_with_dots)}):")
        for p in products_with_dots:
            print(f"  - {p}")