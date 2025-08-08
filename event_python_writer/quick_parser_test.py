#!/usr/bin/env python3
"""
Quick Parser Test - Simple validation of recently fixed parsers
Tests ping parsers and cisco_fmc without requiring full S1 API setup
"""
import json
import sys
import os
from typing import Dict, List, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_generator(product_name: str, count: int = 3) -> Dict[str, Any]:
    """Test a generator and return analysis"""
    try:
        # Import the generator
        if product_name == 'pingfederate':
            from pingfederate import pingfederate_log as generator
        elif product_name == 'pingone_mfa':
            from pingone_mfa import pingone_mfa_log as generator
        elif product_name == 'pingprotect':
            from pingprotect import pingprotect_log as generator
        elif product_name == 'cisco_fmc':
            from cisco_fmc import cisco_fmc_log as generator
        else:
            return {'error': f'Unknown product: {product_name}'}
        
        # Generate test events
        events = []
        field_variations = {}
        
        for i in range(count):
            event = generator()
            
            # Handle string vs dict returns
            if isinstance(event, str):
                try:
                    event = json.loads(event)
                except json.JSONDecodeError:
                    return {'error': f'Generated invalid JSON: {event[:100]}...'}
            
            events.append(event)
            
            # Track field variations
            event_fields = set(event.keys())
            if i == 0:
                field_variations['common'] = event_fields
            else:
                field_variations['common'] = field_variations['common'].intersection(event_fields)
                
        # Analyze field consistency
        all_fields = set()
        for event in events:
            all_fields.update(event.keys())
        
        optional_fields = all_fields - field_variations['common']
        
        return {
            'success': True,
            'events_generated': len(events),
            'common_fields': sorted(field_variations['common']),
            'optional_fields': sorted(optional_fields),
            'sample_event': events[0] if events else {},
            'field_analysis': {
                'total_fields': len(all_fields),
                'consistent_fields': len(field_variations['common']),
                'optional_fields': len(optional_fields)
            }
        }
        
    except Exception as e:
        return {'error': f'Generator failed: {e}'}

def validate_parser_fields(product_name: str, generator_result: Dict[str, Any]) -> Dict[str, Any]:
    """Validate parser field mappings against generator output"""
    if not generator_result.get('success'):
        return {'error': 'Cannot validate - generator failed'}
    
    try:
        # Load parser configuration
        if product_name == 'cisco_fmc':
            parser_file = f"../parsers/community/cisco_fmc_logs-latest/cisco_fmc.json"
        else:
            parser_file = f"../parsers/community/{product_name}-latest/{product_name}.json"
        
        if not os.path.exists(parser_file):
            return {'error': f'Parser file not found: {parser_file}'}
        
        with open(parser_file, 'r') as f:
            parser_config = json.load(f)
        
        # Extract field mappings from parser
        mapped_fields = []
        if 'mappings' in parser_config:
            for mapping in parser_config['mappings'].get('mappings', []):
                for transform in mapping.get('transformations', []):
                    if 'rename' in transform:
                        from_field = transform['rename']['from'].replace('unmapped.', '')
                        mapped_fields.append(from_field)
        
        # Check for problematic mappings
        common_fields = set(generator_result['common_fields'])
        optional_fields = set(generator_result['optional_fields'])
        mapped_fields_set = set(mapped_fields)
        
        # Find issues
        missing_mappings = mapped_fields_set - (common_fields | optional_fields)
        optional_mapped = mapped_fields_set.intersection(optional_fields)
        
        validation_result = {
            'success': len(missing_mappings) == 0 and len(optional_mapped) == 0,
            'parser_maps': len(mapped_fields),
            'generator_fields': len(common_fields) + len(optional_fields),
            'missing_fields': sorted(missing_mappings),
            'optional_field_mappings': sorted(optional_mapped),
            'safe_mappings': sorted(mapped_fields_set.intersection(common_fields))
        }
        
        # Add recommendations
        if missing_mappings:
            validation_result['issues'] = validation_result.get('issues', [])
            validation_result['issues'].append(f"Parser maps {len(missing_mappings)} non-existent fields")
        
        if optional_mapped:
            validation_result['issues'] = validation_result.get('issues', [])
            validation_result['issues'].append(f"Parser maps {len(optional_mapped)} optional fields (may cause parsing failures)")
        
        return validation_result
        
    except Exception as e:
        return {'error': f'Parser validation failed: {e}'}

def test_product(product_name: str, count: int = 5) -> None:
    """Test a single product comprehensively"""
    print(f"\n{'='*60}")
    print(f"Testing: {product_name}")
    print(f"{'='*60}")
    
    # Test generator
    print(f"📊 Testing generator ({count} events)...")
    gen_result = test_generator(product_name, count)
    
    if gen_result.get('error'):
        print(f"❌ Generator Error: {gen_result['error']}")
        return
    
    print(f"✅ Generator: {gen_result['events_generated']} events")
    print(f"   Common fields: {gen_result['field_analysis']['consistent_fields']}")
    print(f"   Optional fields: {gen_result['field_analysis']['optional_fields']}")
    
    if gen_result['optional_fields']:
        print(f"   ⚠️  Optional fields detected: {', '.join(gen_result['optional_fields'][:5])}")
    
    # Test parser validation
    print(f"🔍 Validating parser configuration...")
    parser_result = validate_parser_fields(product_name, gen_result)
    
    if parser_result.get('error'):
        print(f"❌ Parser Validation Error: {parser_result['error']}")
        return
    
    if parser_result['success']:
        print(f"✅ Parser: {parser_result['parser_maps']} safe field mappings")
    else:
        print(f"❌ Parser Issues Found:")
        for issue in parser_result.get('issues', []):
            print(f"   - {issue}")
        
        if parser_result.get('missing_fields'):
            print(f"   Missing fields: {', '.join(parser_result['missing_fields'])}")
        
        if parser_result.get('optional_field_mappings'):
            print(f"   Optional field mappings: {', '.join(parser_result['optional_field_mappings'])}")
    
    # Show sample event
    if gen_result.get('sample_event'):
        print(f"\n📄 Sample Event:")
        sample = gen_result['sample_event']
        for key in sorted(sample.keys())[:10]:  # Show first 10 fields
            value = str(sample[key])[:50] + '...' if len(str(sample[key])) > 50 else sample[key]
            print(f"   {key}: {value}")
        
        if len(sample) > 10:
            print(f"   ... and {len(sample) - 10} more fields")

def main():
    """Main test function"""
    print("Quick Parser Test - Recently Fixed Parsers")
    print("=" * 60)
    
    # Test the recently fixed parsers
    test_products = ['pingfederate', 'pingone_mfa', 'pingprotect', 'cisco_fmc']
    
    results = {}
    
    for product in test_products:
        test_product(product)
        
    print(f"\n{'*'*60}")
    print("SUMMARY")
    print(f"{'*'*60}")
    print(f"Tested {len(test_products)} parsers")
    print("\nNext Steps:")
    print("1. Configure SentinelOne API credentials:")
    print("   python s1_config_setup.py")
    print("2. Run full validation:")
    print("   python parser_validator.py --problematic")
    print("3. Test specific parser:")
    print("   python parser_validator.py --parser pingfederate")

if __name__ == "__main__":
    main()