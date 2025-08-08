#!/usr/bin/env python3
"""
Test script that sends 5 events for all available generators using hec_sender.
This ensures all generators work correctly and can send events to the proper endpoint.
"""

import subprocess
import sys
import os
import time
from hec_sender import PROD_MAP

# List of all products from PROD_MAP
ALL_PRODUCTS = list(PROD_MAP.keys())

def test_single_product(product_name, count=5, dry_run=False):
    """Test a single product by sending events via hec_sender or dry-run mode."""
    print(f"\n{'='*60}")
    print(f"Testing {product_name} ({count} events){' - DRY RUN' if dry_run else ''}")
    print(f"{'='*60}")
    
    if dry_run:
        # Dry run - just test that the generator works
        try:
            from hec_sender import PROD_MAP
            import importlib
            
            if product_name not in PROD_MAP:
                print(f"❌ FAILED: {product_name} - Product not in PROD_MAP")
                return False
            
            mod_name, func_names = PROD_MAP[product_name]
            gen_mod = importlib.import_module(mod_name)
            
            # Test that the module has required attributes
            if not hasattr(gen_mod, "ATTR_FIELDS"):
                print(f"❌ FAILED: {product_name} - Missing ATTR_FIELDS")
                return False
            
            # Test each generator function
            for func_name in func_names:
                if not hasattr(gen_mod, func_name):
                    print(f"❌ FAILED: {product_name} - Missing function {func_name}")
                    return False
                
                # Try to generate an event
                generator = getattr(gen_mod, func_name)
                event = generator()
                if not event:
                    print(f"❌ FAILED: {product_name} - {func_name} returned empty event")
                    return False
            
            print(f"✅ SUCCESS: {product_name} - Generator working, {len(func_names)} functions tested")
            return True
            
        except Exception as e:
            print(f"❌ FAILED: {product_name} - Exception: {e}")
            return False
    
    else:
        # Real HEC sending test
        try:
            # Determine the correct path to hec_sender.py
            script_dir = os.path.dirname(os.path.abspath(__file__))
            hec_sender_path = os.path.join(script_dir, "hec_sender.py")
            
            # Run hec_sender with the product
            result = subprocess.run([
                sys.executable, hec_sender_path,
                "--product", product_name,
                "--count", str(count),
                "--min-delay", "0.1",
                "--max-delay", "0.2"
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"✅ SUCCESS: {product_name}")
                print(f"Output: {result.stdout}")
            else:
                print(f"❌ FAILED: {product_name}")
                print(f"Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ TIMEOUT: {product_name}")
            return False
        except Exception as e:
            print(f"💥 EXCEPTION: {product_name} - {e}")
            return False
    
    return True

def test_all_products(count=5, dry_run=False):
    """Test all products by sending events via hec_sender."""
    print(f"Testing all {len(ALL_PRODUCTS)} generators with {count} events each...")
    if not dry_run:
        print(f"Total events to be sent: {len(ALL_PRODUCTS) * count}")
    
    # Check if HEC token is set (only for real tests)
    if not dry_run and not os.getenv("S1_HEC_TOKEN"):
        print("❌ ERROR: S1_HEC_TOKEN environment variable not set!")
        print("Please set it with: export S1_HEC_TOKEN=your_token_here")
        print("Or use --dry-run to test generators without sending events")
        return
    
    successful = 0
    failed = 0
    failed_products = []
    
    start_time = time.time()
    
    for i, product in enumerate(ALL_PRODUCTS, 1):
        print(f"\n[{i}/{len(ALL_PRODUCTS)}] Testing {product}...")
        
        if test_single_product(product, count, dry_run):
            successful += 1
        else:
            failed += 1
            failed_products.append(product)
        
        # Brief pause between products to avoid overwhelming the endpoint
        if not dry_run:
            time.sleep(0.5)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Final summary
    print(f"\n{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total products tested: {len(ALL_PRODUCTS)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    if not dry_run:
        print(f"Total events sent: {successful * count}")
    print(f"Total duration: {duration:.1f} seconds")
    
    if failed_products:
        print(f"\nFailed products:")
        for product in failed_products:
            print(f"  - {product}")
    else:
        print(f"\n🎉 ALL TESTS PASSED! All {len(ALL_PRODUCTS)} generators working correctly!")

def test_subset(products_list, count=5, dry_run=False):
    """Test a specific subset of products."""
    print(f"Testing subset of {len(products_list)} generators...")
    
    if not dry_run and not os.getenv("S1_HEC_TOKEN"):
        print("❌ ERROR: S1_HEC_TOKEN environment variable not set!")
        print("Use --dry-run to test generators without sending events")
        return
    
    successful = 0
    failed = 0
    
    for i, product in enumerate(products_list, 1):
        print(f"\n[{i}/{len(products_list)}] Testing {product}...")
        
        if test_single_product(product, count, dry_run):
            successful += 1
        else:
            failed += 1
        
        if not dry_run:
            time.sleep(0.5)
    
    print(f"\nSubset test complete: {successful} successful, {failed} failed")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test all event generators with HEC sender")
    parser.add_argument("--count", type=int, default=5, 
                        help="Number of events to send per generator (default: 5)")
    parser.add_argument("--subset", nargs="+", 
                        help="Test only specific products (space-separated list)")
    parser.add_argument("--list", action="store_true", 
                        help="List all available products and exit")
    parser.add_argument("--dry-run", action="store_true",
                        help="Test generators without sending events to HEC")
    
    args = parser.parse_args()
    
    if args.list:
        print(f"Available products ({len(ALL_PRODUCTS)}):")
        for i, product in enumerate(sorted(ALL_PRODUCTS), 1):
            print(f"{i:3}. {product}")
        sys.exit(0)
    
    if args.subset:
        # Validate subset products
        invalid_products = [p for p in args.subset if p not in ALL_PRODUCTS]
        if invalid_products:
            print(f"❌ Invalid products: {invalid_products}")
            print(f"Use --list to see available products")
            sys.exit(1)
        
        test_subset(args.subset, args.count, args.dry_run)
    else:
        test_all_products(args.count, args.dry_run)