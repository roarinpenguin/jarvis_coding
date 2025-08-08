#!/usr/bin/env python3
"""
Analyze generators to categorize issues and prioritize fixes
"""
import importlib
import json
from hec_sender import PROD_MAP

def analyze_generator(product_name):
    """Detailed analysis of a generator"""
    try:
        if product_name not in PROD_MAP:
            return None
        
        mod_name, func_names = PROD_MAP[product_name]
        gen_mod = importlib.import_module(mod_name)
        
        if not func_names:
            return None
        
        func_name = func_names[0]
        if not hasattr(gen_mod, func_name):
            return None
        
        generator = getattr(gen_mod, func_name)
        event = generator()
        
        result = {
            "product": product_name,
            "module": mod_name,
            "function": func_name
        }
        
        # Check event type
        if isinstance(event, str):
            result["output_type"] = "string"
            # Try to parse as JSON
            try:
                parsed = json.loads(event)
                result["string_format"] = "json"
                event = parsed  # Use parsed for dot check
            except:
                result["string_format"] = "raw"
                result["dot_keys"] = []
                return result
        else:
            result["output_type"] = "dict"
            result["string_format"] = None
        
        # Check for dot notation in keys
        if isinstance(event, dict):
            dot_keys = [k for k in event.keys() if '.' in k]
            result["dot_keys"] = dot_keys
            
            # Check specifically for dataSource fields
            datasource_keys = [k for k in dot_keys if k.startswith('dataSource.')]
            result["has_datasource_dots"] = len(datasource_keys) > 0
            result["datasource_dot_keys"] = datasource_keys
        else:
            result["dot_keys"] = []
            result["has_datasource_dots"] = False
            result["datasource_dot_keys"] = []
        
        return result
        
    except Exception as e:
        return {"product": product_name, "error": str(e)}

if __name__ == "__main__":
    # Categorize all generators
    dict_with_dots = []  # Priority 1: Fix these
    string_json_with_dots = []  # Priority 2: Convert to dict and fix
    raw_strings = []  # Priority 3: These need different parsers anyway
    clean_dicts = []  # No fix needed
    errors = []
    
    for product in sorted(PROD_MAP.keys()):
        result = analyze_generator(product)
        
        if not result:
            continue
        
        if "error" in result:
            errors.append(product)
            continue
        
        if result["output_type"] == "dict":
            if result["dot_keys"]:
                dict_with_dots.append(result)
            else:
                clean_dicts.append(product)
        elif result["output_type"] == "string":
            if result["string_format"] == "json" and result["dot_keys"]:
                string_json_with_dots.append(result)
            elif result["string_format"] == "raw":
                raw_strings.append(product)
    
    print("="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    
    print(f"\n📊 STATISTICS:")
    print(f"  Total generators: {len(PROD_MAP)}")
    print(f"  Clean dicts (no fix needed): {len(clean_dicts)}")
    print(f"  Dicts with dot notation (NEED FIX): {len(dict_with_dots)}")
    print(f"  JSON strings with dots (consider fix): {len(string_json_with_dots)}")
    print(f"  Raw string format (different parser): {len(raw_strings)}")
    print(f"  Errors: {len(errors)}")
    
    print(f"\n🔴 PRIORITY 1: Dicts with dot notation ({len(dict_with_dots)} generators)")
    print("These return dicts but use flat dot notation - must be fixed:")
    for item in dict_with_dots[:10]:  # Show first 10
        print(f"  - {item['product']}: {item['datasource_dot_keys'][:3]}")
    if len(dict_with_dots) > 10:
        print(f"  ... and {len(dict_with_dots) - 10} more")
    
    print(f"\n🟡 PRIORITY 2: JSON strings with dots ({len(string_json_with_dots)} generators)")
    print("These return JSON strings with dot notation:")
    for item in string_json_with_dots[:5]:
        print(f"  - {item['product']}")
    
    print(f"\n🟢 CLEAN: No fixes needed ({len(clean_dicts)} generators)")
    print("These already use proper nested structure:")
    for product in clean_dicts[:10]:
        print(f"  - {product}")
    
    # Export priority 1 list for fixing
    print(f"\n📝 EXPORT: Priority 1 generators to fix:")
    priority1_products = [item['product'] for item in dict_with_dots]
    print(priority1_products)