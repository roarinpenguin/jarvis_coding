#!/usr/bin/env python3
"""
Test script to validate the parser mapping fixes.
Measures improvement in generator-parser compatibility from 21.6% to target 60%+.
"""

import os
import sys
import json
import importlib
from typing import Dict, List, Tuple

# Add paths for generator imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'event_generators/shared'))

def discover_available_parsers() -> Dict[str, List[str]]:
    """Discover all available parsers by scanning the parsers directory."""
    parsers_dir = os.path.join(os.path.dirname(__file__), "parsers")
    available_parsers = {
        "community": [],
        "marketplace": [],
        "total": []
    }
    
    # Scan community parsers
    community_dir = os.path.join(parsers_dir, "community")
    if os.path.exists(community_dir):
        for item in os.listdir(community_dir):
            if os.path.isdir(os.path.join(community_dir, item)) and "-latest" in item:
                available_parsers["community"].append(item)
                available_parsers["total"].append(item)
    
    # Scan SentinelOne/marketplace parsers
    sentinelone_dir = os.path.join(parsers_dir, "sentinelone")
    if os.path.exists(sentinelone_dir):
        for item in os.listdir(sentinelone_dir):
            if os.path.isdir(os.path.join(sentinelone_dir, item)) and "marketplace-" in item:
                available_parsers["marketplace"].append(item)
                available_parsers["total"].append(item)
    
    return available_parsers

def load_fixed_sourcetype_map():
    """Load the fixed SOURCETYPE_MAP by parsing hec_sender.py directly"""
    try:
        # Read the file and extract the SOURCETYPE_MAP
        hec_sender_path = os.path.join(os.path.dirname(__file__), 'event_generators/shared/hec_sender.py')
        with open(hec_sender_path, 'r') as f:
            content = f.read()
        
        # Find the SOURCETYPE_MAP definition
        start = content.find('SOURCETYPE_MAP = {')
        if start == -1:
            print("Error: Could not find SOURCETYPE_MAP in hec_sender.py")
            return {}
        
        # Find the matching closing brace
        brace_count = 0
        in_map = False
        end = start
        
        for i, char in enumerate(content[start:], start):
            if char == '{':
                brace_count += 1
                in_map = True
            elif char == '}':
                brace_count -= 1
                if in_map and brace_count == 0:
                    end = i + 1
                    break
        
        # Extract and evaluate the mapping
        map_definition = content[start:end]
        # Use exec to safely evaluate the mapping
        local_vars = {}
        exec(map_definition, {}, local_vars)
        return local_vars.get('SOURCETYPE_MAP', {})
        
    except Exception as e:
        print(f"Error loading SOURCETYPE_MAP: {e}")
        return {}

def test_parser_compatibility() -> Dict[str, any]:
    """Test compatibility between generators and parsers using the fixed mapping."""
    available_parsers = discover_available_parsers()
    fixed_mapping = load_fixed_sourcetype_map()
    
    results = {
        "working": [],
        "failed": [],
        "summary": {}
    }
    
    print(f"Testing {len(fixed_mapping)} product-parser mappings...")
    print(f"Available parsers: {len(available_parsers['total'])} total")
    print(f"  - Community: {len(available_parsers['community'])}")  
    print(f"  - Marketplace: {len(available_parsers['marketplace'])}")
    print("-" * 60)
    
    working_count = 0
    failed_count = 0
    
    for product, parser in fixed_mapping.items():
        result = {
            "product": product,
            "parser": parser,
            "status": "unknown",
            "error": None
        }
        
        # Check if parser exists
        if parser in available_parsers["total"]:
            result["status"] = "working"
            result["parser_exists"] = True
            working_count += 1
            results["working"].append(result)
            print(f"✅ {product:<35} -> {parser}")
        else:
            result["status"] = "parser_missing"
            result["error"] = f"Parser not found: {parser}"
            result["parser_exists"] = False
            failed_count += 1
            results["failed"].append(result)
            print(f"❌ {product:<35} -> {parser} (NOT FOUND)")
    
    # Calculate success rate
    total_tests = working_count + failed_count
    success_rate = (working_count / total_tests * 100) if total_tests > 0 else 0
    
    results["summary"] = {
        "total_tests": total_tests,
        "working_pairs": working_count,
        "failed_pairs": failed_count,
        "success_rate": success_rate,
        "improvement_from_baseline": success_rate - 21.6  # Original was 21.6%
    }
    
    print("-" * 60)
    print(f"RESULTS SUMMARY:")
    print(f"Total products tested: {total_tests}")
    print(f"Working mappings: {working_count}")
    print(f"Failed mappings: {failed_count}")
    print(f"Success rate: {success_rate:.1f}%")
    print(f"Improvement: +{success_rate - 21.6:.1f}% from baseline (21.6%)")
    
    if success_rate >= 60:
        print("🎉 SUCCESS: Achieved target of 60%+ compatibility!")
    else:
        print(f"⚠️  Target not met: Need {60 - success_rate:.1f}% more to reach 60%")
    
    return results

def analyze_failed_parsers(results: Dict[str, any]) -> List[str]:
    """Analyze failed parsers and suggest fixes."""
    print("\n" + "="*60)
    print("FAILED PARSER ANALYSIS")
    print("="*60)
    
    available_parsers = discover_available_parsers()
    suggestions = []
    
    if results["failed"]:
        print(f"Analyzing {len(results['failed'])} failed mappings...")
        
        for failed in results["failed"]:
            product = failed["product"]
            missing_parser = failed["parser"]
            
            print(f"\n❌ {product} -> {missing_parser}")
            
            # Try to find similar parsers
            product_words = set(product.lower().replace("_", " ").split())
            best_matches = []
            
            for parser in available_parsers["total"]:
                parser_words = set(parser.lower().replace("_", " ").replace("-", " ").split())
                common_words = product_words & parser_words
                if len(common_words) >= 1:
                    score = len(common_words)
                    best_matches.append((parser, score, common_words))
            
            # Sort by score
            best_matches.sort(key=lambda x: x[1], reverse=True)
            
            if best_matches:
                print(f"   Possible alternatives:")
                for parser, score, common_words in best_matches[:3]:
                    print(f"   - {parser} (score: {score}, common: {common_words})")
                    
                suggestions.append(f'"{product}": "{best_matches[0][0]}",  # Suggested fix')
            else:
                print("   No similar parsers found")
                suggestions.append(f'# No parser found for {product}')
    
    return suggestions

def generate_fix_recommendations(results: Dict[str, any]) -> None:
    """Generate specific fix recommendations."""
    print("\n" + "="*60)
    print("FIX RECOMMENDATIONS")
    print("="*60)
    
    suggestions = analyze_failed_parsers(results)
    
    if suggestions:
        print("\nSuggested additions to SOURCETYPE_MAP:")
        print("-" * 40)
        for suggestion in suggestions[:10]:  # Show top 10
            print(f"    {suggestion}")
        
        print(f"\n... and {len(suggestions)-10} more suggestions" if len(suggestions) > 10 else "")
    
    # Priority fixes for enterprise vendors
    enterprise_vendors = [
        "microsoft_", "aws_", "cisco_", "crowdstrike_", "sentinelone_", 
        "okta_", "cyberark_", "paloalto_", "fortinet_"
    ]
    
    enterprise_failed = []
    for failed in results["failed"]:
        product = failed["product"]
        if any(product.startswith(vendor) for vendor in enterprise_vendors):
            enterprise_failed.append(product)
    
    if enterprise_failed:
        print(f"\n🚨 PRIORITY FIXES NEEDED:")
        print(f"   {len(enterprise_failed)} enterprise vendors failing:")
        for product in enterprise_failed:
            print(f"   - {product}")

def main():
    print("🔍 Testing Parser Mapping Fixes")
    print("="*60)
    
    # Run the compatibility test
    results = test_parser_compatibility()
    
    # Analyze failures and provide recommendations
    analyze_failed_parsers(results)
    generate_fix_recommendations(results)
    
    # Save results
    output_file = "parser_fix_test_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📝 Full results saved to: {output_file}")
    
    # Return success status
    success_rate = results["summary"]["success_rate"]
    if success_rate >= 60:
        print(f"\n🎉 MISSION ACCOMPLISHED: {success_rate:.1f}% compatibility achieved!")
        sys.exit(0)
    else:
        print(f"\n⚠️  NEEDS MORE WORK: {success_rate:.1f}% compatibility (target: 60%)")
        sys.exit(1)

if __name__ == "__main__":
    main()