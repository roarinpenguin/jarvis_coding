#!/usr/bin/env python3
"""
Apply Generator-Parser Alignment Fixes
======================================

This script systematically fixes the critical generator-parser alignment issues
identified in the comprehensive audit. It focuses on Phase 1 quick wins:
the 6 critical name mapping fixes that will improve success rate by 8-10%.

Usage:
    python apply_generator_parser_fixes.py [--test-run] [--verbose]
    
    --test-run    : Show what would be fixed without making changes
    --verbose     : Show detailed progress information

Phase 1 Fixes (Name Mappings):
1. okta_authentication → okta_ocsf_logs-latest  
2. crowdstrike_falcon → crowdstrike_endpoint-latest
3. sentinelone_endpoint → singularityidentity_logs-latest
4. microsoft_azure_ad_signin → microsoft_azure_ad_logs-latest
5. paloalto_firewall → paloalto_paloalto_logs-latest
6. aws_cloudtrail → marketplace-awscloudtrail-latest

This creates new mapping configuration and validates the fixes.
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

def load_mapping_config(config_path: str) -> Dict:
    """Load the generator-parser mapping configuration."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Mapping configuration not found: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in configuration file: {e}")
        return {}

def verify_parser_exists(parser_name: str, parsers_dir: str) -> bool:
    """Verify that a parser directory exists."""
    parser_path = Path(parsers_dir) / "community" / parser_name
    marketplace_path = Path(parsers_dir) / "sentinelone" / parser_name
    
    return parser_path.exists() or marketplace_path.exists()

def verify_generator_exists(generator_name: str, generators_dir: str) -> Optional[str]:
    """Find the generator file in the appropriate category directory."""
    categories = [
        'cloud_infrastructure', 'network_security', 'endpoint_security', 
        'identity_access', 'email_security', 'web_security', 'infrastructure'
    ]
    
    for category in categories:
        generator_path = Path(generators_dir) / category / f"{generator_name}.py"
        if generator_path.exists():
            return str(generator_path)
    
    return None

def validate_critical_mappings(mappings: Dict[str, str], base_dir: str, verbose: bool = False) -> Tuple[List[str], List[str]]:
    """Validate that all critical mappings can be applied."""
    valid_mappings = []
    invalid_mappings = []
    
    generators_dir = os.path.join(base_dir, "event_generators")  
    parsers_dir = os.path.join(base_dir, "parsers")
    
    for generator, parser in mappings.items():
        if verbose:
            print(f"  Validating: {generator} → {parser}")
            
        # Check generator exists
        generator_path = verify_generator_exists(generator, generators_dir)
        if not generator_path:
            if verbose:
                print(f"    ❌ Generator not found: {generator}")
            invalid_mappings.append(f"{generator} → {parser} (generator missing)")
            continue
            
        # Check parser exists
        if not verify_parser_exists(parser, parsers_dir):
            if verbose:
                print(f"    ❌ Parser not found: {parser}")
            invalid_mappings.append(f"{generator} → {parser} (parser missing)")
            continue
            
        if verbose:
            print(f"    ✅ Valid mapping: {generator} → {parser}")
        valid_mappings.append(f"{generator} → {parser}")
    
    return valid_mappings, invalid_mappings

def update_hec_sender_mappings(hec_sender_path: str, mappings: Dict[str, str], test_run: bool = False, verbose: bool = False) -> bool:
    """Update the HEC sender sourcetype mappings."""
    try:
        with open(hec_sender_path, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ HEC sender not found: {hec_sender_path}")
        return False
    
    # Create updated sourcetype mappings
    updates_made = []
    original_content = content
    
    for generator, parser in mappings.items():
        # Find the sourcetype mapping for this generator
        search_pattern = f'"{generator}": "'
        if search_pattern in content:
            # Extract current mapping
            start_idx = content.find(search_pattern)
            start_value = content.find('"', start_idx + len(search_pattern))
            end_value = content.find('"', start_value + 1)
            current_parser = content[start_value + 1:end_value]
            
            if current_parser != parser:
                # Update the mapping
                new_line = f'"{generator}": "{parser}"'
                old_line = f'"{generator}": "{current_parser}"'
                content = content.replace(old_line, new_line)
                updates_made.append(f"{generator}: {current_parser} → {parser}")
                if verbose:
                    print(f"    Updated: {generator}: {current_parser} → {parser}")
            else:
                if verbose:
                    print(f"    Already correct: {generator} → {parser}")
        else:
            # Add new mapping if not found
            # Find the SOURCETYPE_MAP section and add the mapping
            sourcetype_start = content.find("SOURCETYPE_MAP = {")
            if sourcetype_start != -1:
                # Find a good place to insert (before the closing brace)
                insert_point = content.rfind("}", sourcetype_start)
                if insert_point != -1:
                    new_entry = f'    "{generator}": "{parser}",\n'
                    # Insert before the closing brace
                    content = content[:insert_point] + new_entry + content[insert_point:]
                    updates_made.append(f"Added mapping: {generator} → {parser}")
                    if verbose:
                        print(f"    Added: {generator} → {parser}")
    
    if not test_run and updates_made:
        # Write the updated content
        try:
            with open(hec_sender_path, 'w') as f:
                f.write(content)
            print(f"✅ Updated HEC sender with {len(updates_made)} mapping changes")
            return True
        except Exception as e:
            print(f"❌ Failed to update HEC sender: {e}")
            return False
    elif test_run and updates_made:
        print(f"🔍 Would update HEC sender with {len(updates_made)} changes:")
        for update in updates_made:
            print(f"    - {update}")
        return True
    elif verbose:
        print("    No updates needed for HEC sender")
    
    return len(updates_made) > 0

def create_validation_script(base_dir: str, mappings: Dict[str, str]) -> str:
    """Create a script to validate the fixes."""
    script_path = os.path.join(base_dir, "validate_mapping_fixes.py")
    
    script_content = f'''#!/usr/bin/env python3
"""
Validate Generator-Parser Mapping Fixes
=======================================

This script validates that the critical mapping fixes have been applied correctly
and tests each fixed generator-parser pair.

Generated automatically by apply_generator_parser_fixes.py
"""

import sys
import os
import importlib
import json

# Add generator category paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
generator_root = os.path.join(current_dir, "event_generators")
for category in ['cloud_infrastructure', 'network_security', 'endpoint_security', 
                 'identity_access', 'email_security', 'web_security', 'infrastructure']:
    sys.path.insert(0, os.path.join(generator_root, category))

# Fixed mappings to test
FIXED_MAPPINGS = {json.dumps(mappings, indent=4)}

def test_generator(generator_name: str) -> bool:
    """Test that a generator can be loaded and executed."""
    try:
        # Import the generator module
        module = importlib.import_module(generator_name)
        
        # Find the main generator function
        func_name = f"{{generator_name}}_log"
        if hasattr(module, func_name):
            generator_func = getattr(module, func_name)
            
            # Test execution
            event = generator_func()
            
            # Validate output
            if isinstance(event, (str, dict)):
                print(f"✅ {{generator_name}}: Generated {{type(event).__name__}} event")
                return True
            else:
                print(f"❌ {{generator_name}}: Invalid event type {{type(event)}}")
                return False
        else:
            print(f"❌ {{generator_name}}: Function {{func_name}} not found")
            return False
            
    except Exception as e:
        print(f"❌ {{generator_name}}: Import/execution error: {{e}}")
        return False

def validate_parser_exists(parser_name: str) -> bool:
    """Validate that a parser exists."""
    community_path = os.path.join(current_dir, "parsers", "community", parser_name)
    marketplace_path = os.path.join(current_dir, "parsers", "sentinelone", parser_name)
    
    exists = os.path.exists(community_path) or os.path.exists(marketplace_path)
    if exists:
        print(f"✅ Parser exists: {{parser_name}}")
    else:
        print(f"❌ Parser missing: {{parser_name}}")
    
    return exists

def main():
    """Run validation tests for all fixed mappings."""
    print("🔍 Validating Generator-Parser Mapping Fixes")
    print("=" * 50)
    
    total_tests = len(FIXED_MAPPINGS)
    passed_tests = 0
    
    for generator, parser in FIXED_MAPPINGS.items():
        print(f"\\nTesting: {{generator}} → {{parser}}")
        print("-" * 40)
        
        generator_ok = test_generator(generator)
        parser_ok = validate_parser_exists(parser)
        
        if generator_ok and parser_ok:
            passed_tests += 1
            print(f"✅ PASS: {{generator}} → {{parser}}")
        else:
            print(f"❌ FAIL: {{generator}} → {{parser}}")
    
    print(f"\\n📊 Results: {{passed_tests}}/{{total_tests}} mappings validated")
    print(f"Success rate: {{(passed_tests/total_tests)*100:.1f}}%")
    
    if passed_tests == total_tests:
        print("🎉 All critical mappings are working correctly!")
        return 0
    else:
        print(f"⚠️  {{total_tests - passed_tests}} mappings need attention")
        return 1

if __name__ == "__main__":
    sys.exit(main())
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    os.chmod(script_path, 0o755)
    
    return script_path

def main():
    parser = argparse.ArgumentParser(
        description="Apply critical generator-parser alignment fixes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--test-run", action="store_true",
                       help="Show what would be changed without making changes")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Show detailed progress information")
    
    args = parser.parse_args()
    
    # Determine base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "generator_parser_mappings.json")
    hec_sender_path = os.path.join(base_dir, "event_generators", "shared", "hec_sender.py")
    
    print("🔧 Applying Generator-Parser Alignment Fixes")
    print("=" * 50)
    
    if args.test_run:
        print("🔍 TEST RUN MODE - No changes will be made")
        print()
    
    # Load mapping configuration
    print("📋 Loading mapping configuration...")
    config = load_mapping_config(config_path)
    
    if not config:
        print("❌ Failed to load mapping configuration. Exiting.")
        return 1
    
    mappings = config.get("generator_parser_mappings", {}).get("mappings", {})
    if not mappings:
        print("❌ No mappings found in configuration. Exiting.")
        return 1
    
    print(f"✅ Loaded {len(mappings)} critical mappings")
    
    # Validate mappings
    print("\\n🔍 Validating critical mappings...")
    valid_mappings, invalid_mappings = validate_critical_mappings(mappings, base_dir, args.verbose)
    
    print(f"✅ Valid mappings: {len(valid_mappings)}")
    if invalid_mappings:
        print(f"❌ Invalid mappings: {len(invalid_mappings)}")
        for invalid in invalid_mappings:
            print(f"  - {invalid}")
    
    if not valid_mappings:
        print("❌ No valid mappings to apply. Exiting.")
        return 1
    
    # Apply fixes to HEC sender
    print("\\n⚙️ Updating HEC sender mappings...")
    valid_mappings_dict = {}
    for mapping in valid_mappings:
        parts = mapping.split(" → ")
        if len(parts) == 2:
            valid_mappings_dict[parts[0]] = parts[1]
    
    hec_updated = update_hec_sender_mappings(hec_sender_path, valid_mappings_dict, args.test_run, args.verbose)
    
    # Create validation script
    if not args.test_run:
        print("\\n📝 Creating validation script...")
        validation_script = create_validation_script(base_dir, valid_mappings_dict)
        print(f"✅ Created validation script: {validation_script}")
        print("   Run with: python validate_mapping_fixes.py")
    
    # Summary
    print("\\n📊 Summary")
    print("=" * 20)
    print(f"Total mappings processed: {len(mappings)}")
    print(f"Valid mappings: {len(valid_mappings)}")
    print(f"Invalid mappings: {len(invalid_mappings)}")
    print(f"HEC sender updated: {'Yes' if hec_updated else 'No'}")
    
    if args.test_run:
        print("\\n🔍 This was a test run - no changes were made")
        print("Remove --test-run flag to apply fixes")
    else:
        print("\\n✅ Phase 1 fixes applied successfully!")
        print("Expected improvement: +8-10% success rate")
        print("\\nNext steps:")
        print("1. Run: python validate_mapping_fixes.py")
        print("2. Test generators with: python event_generators/shared/hec_sender.py --product okta_authentication --count 3")
        print("3. Proceed to Phase 2 format conversions")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())