#!/usr/bin/env python3
"""
Comprehensive Parser Tester - End-to-end testing using SentinelOne DV API
Tests parser effectiveness by sending events and validating field extraction
"""
import json
import os
import sys
import importlib
import traceback
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s1_dv_api_client import SentinelOneDVClient, ParserTestResult

# Import the product mapping from hec_sender
try:
    from hec_sender import PROD_MAP, JSON_PRODUCTS
except ImportError:
    print("Warning: Could not import PROD_MAP from hec_sender")
    PROD_MAP = {}
    JSON_PRODUCTS = []

class ComprehensiveParserTester:
    """Comprehensive parser testing using SentinelOne DV API"""
    
    def __init__(self, dv_client: SentinelOneDVClient = None):
        """Initialize comprehensive parser tester
        
        Args:
            dv_client: SentinelOne DV API client instance
        """
        self.dv_client = dv_client or SentinelOneDVClient()
        self.test_results: Dict[str, ParserTestResult] = {}
        
        # Expected field mappings for different parser types
        self.expected_ocsf_fields = {
            'authentication': [
                'class_uid', 'class_name', 'activity_id', 'activity_name',
                'time', 'user.name', 'src_endpoint.ip', 'status'
            ],
            'network_activity': [
                'class_uid', 'class_name', 'time', 'src_endpoint.ip', 
                'dst_endpoint.ip', 'connection_info.protocol_name'
            ],
            'security_finding': [
                'class_uid', 'class_name', 'time', 'severity', 'message'
            ],
            'system_activity': [
                'class_uid', 'class_name', 'time', 'actor.user', 'activity_name'
            ]
        }
        
        # Parser type mapping - maps parser names to expected OCSF categories
        self.parser_types = {
            'pingfederate': 'authentication',
            'pingone_mfa': 'authentication', 
            'pingprotect': 'security_finding',
            'cisco_fmc': 'network_activity',
            'aws_waf': 'security_finding',
            'microsoft_365_defender': 'security_finding',
            'github_audit': 'system_activity',
            # Add more as needed
        }
    
    def generate_test_events(self, product_name: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate test events for a specific product
        
        Args:
            product_name: Product name (e.g., 'cisco_fmc', 'pingfederate')
            count: Number of events to generate
            
        Returns:
            List of generated events
        """
        if product_name not in PROD_MAP:
            raise ValueError(f"Unknown product: {product_name}. Available: {list(PROD_MAP.keys())[:10]}")
        
        module_name, func_name = PROD_MAP[product_name]
        
        try:
            # Import the generator module
            gen_module = importlib.import_module(module_name)
            generator_func = getattr(gen_module, func_name)
            
            events = []
            for _ in range(count):
                event = generator_func()
                
                # Handle different return types
                if isinstance(event, str):
                    # JSON string - parse it
                    if product_name in JSON_PRODUCTS:
                        event = json.loads(event)
                    else:
                        # Raw log string - wrap in structure for HEC
                        event = {
                            "raw_log": event, 
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "dataSource": {"name": product_name}
                        }
                elif isinstance(event, dict):
                    # Already a dict - ensure it has required fields
                    if 'timestamp' not in event:
                        event['timestamp'] = datetime.now(timezone.utc).isoformat()
                else:
                    raise ValueError(f"Unexpected event type from {product_name}: {type(event)}")
                
                events.append(event)
            
            return events
            
        except Exception as e:
            raise Exception(f"Failed to generate events for {product_name}: {e}")
    
    def get_expected_fields(self, parser_name: str) -> List[str]:
        """Get expected OCSF fields for a parser
        
        Args:
            parser_name: Name of the parser
            
        Returns:
            List of expected field names
        """
        parser_type = self.parser_types.get(parser_name, 'security_finding')
        return self.expected_ocsf_fields.get(parser_type, [])
    
    def test_single_parser(self, parser_name: str, count: int = 5, wait_time: int = 60) -> ParserTestResult:
        """Test a single parser end-to-end
        
        Args:
            parser_name: Parser name (should match product name)
            count: Number of test events
            wait_time: Wait time for processing
            
        Returns:
            ParserTestResult with test outcomes
        """
        print(f"\n{'='*80}")
        print(f"🧪 TESTING PARSER: {parser_name}")
        print(f"{'='*80}")
        
        try:
            # Generate test events
            print(f"1️⃣ Generating {count} test events...")
            events = self.generate_test_events(parser_name, count)
            print(f"   ✅ Generated {len(events)} events")
            
            # Show sample event structure
            if events:
                sample = events[0]
                print(f"   📋 Sample event has {len(sample)} fields:")
                for key in sorted(sample.keys())[:8]:
                    value = str(sample[key])[:40] + '...' if len(str(sample[key])) > 40 else sample[key]
                    print(f"      {key}: {value}")
                if len(sample) > 8:
                    print(f"      ... and {len(sample) - 8} more fields")
            
            # Get expected OCSF fields
            expected_fields = self.get_expected_fields(parser_name)
            print(f"   🎯 Expecting {len(expected_fields)} OCSF fields: {expected_fields[:5]}{'...' if len(expected_fields) > 5 else ''}")
            
            # Run end-to-end test via DV API
            print(f"2️⃣ Running end-to-end test...")
            result = self.dv_client.test_parser_end_to_end(
                parser_name=parser_name,
                test_events=events,
                expected_fields=expected_fields,
                wait_time=wait_time
            )
            
            # Store result
            self.test_results[parser_name] = result
            
            # Print immediate results
            print(f"3️⃣ Test Results:")
            if result.parsing_success:
                print(f"   ✅ SUCCESS - {result.events_found}/{result.events_sent} events parsed")
                print(f"   📊 Field coverage: {len(result.field_coverage)} fields extracted")
                
                # Show some key fields found
                if result.field_coverage:
                    consistent_fields = [k for k, v in result.field_coverage.items() if v.get('consistent', False)]
                    print(f"   🎯 Consistent fields ({len(consistent_fields)}): {consistent_fields[:5]}{'...' if len(consistent_fields) > 5 else ''}")
                    
            else:
                print(f"   ❌ FAILED - Issues detected:")
                if result.events_found == 0:
                    print(f"      🔍 No events found in DV (may indicate parsing failure)")
                if result.missing_fields:
                    print(f"      📋 Missing expected fields: {result.missing_fields[:5]}{'...' if len(result.missing_fields) > 5 else ''}")
                if result.errors:
                    for error in result.errors[:3]:
                        print(f"      ⚠️  {error}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            traceback.print_exc()
            
            # Create error result
            error_result = ParserTestResult(
                parser_name=parser_name,
                events_sent=0,
                events_found=0,
                parsing_success=False,
                field_coverage={},
                missing_fields=[],
                unexpected_fields=[],
                errors=[str(e)]
            )
            
            self.test_results[parser_name] = error_result
            return error_result
    
    def test_parser_group(self, group_name: str, parsers: List[str], 
                         count: int = 5, wait_time: int = 60) -> Dict[str, ParserTestResult]:
        """Test a group of related parsers
        
        Args:
            group_name: Name of the parser group
            parsers: List of parser names to test
            count: Number of test events per parser
            wait_time: Wait time between tests
            
        Returns:
            Dictionary mapping parser names to results
        """
        print(f"\n{'#'*100}")
        print(f"🧪 TESTING PARSER GROUP: {group_name}")
        print(f"📋 Parsers: {', '.join(parsers)}")
        print(f"{'#'*100}")
        
        group_results = {}
        
        for i, parser in enumerate(parsers):
            print(f"\n[{i+1}/{len(parsers)}] Testing {parser}...")
            result = self.test_single_parser(parser, count, wait_time)
            group_results[parser] = result
            
            # Brief pause between parsers to avoid overwhelming the system
            if i < len(parsers) - 1:
                print("   ⏳ Brief pause before next parser...")
                import time
                time.sleep(10)
        
        # Group summary
        successful = sum(1 for r in group_results.values() if r.parsing_success)
        print(f"\n{'='*50}")
        print(f"📊 {group_name} GROUP SUMMARY")
        print(f"   Success Rate: {successful}/{len(parsers)} ({100*successful/len(parsers):.1f}%)")
        print(f"   Total Events: {sum(r.events_sent for r in group_results.values())} sent, {sum(r.events_found for r in group_results.values())} found")
        print(f"{'='*50}")
        
        return group_results
    
    def test_ping_parsers(self, count: int = 5, wait_time: int = 60) -> Dict[str, ParserTestResult]:
        """Test all Ping Identity parsers"""
        ping_parsers = ['pingfederate', 'pingone_mfa', 'pingprotect']
        available = [p for p in ping_parsers if p in PROD_MAP]
        return self.test_parser_group("Ping Identity", available, count, wait_time)
    
    def test_cisco_parsers(self, count: int = 5, wait_time: int = 60) -> Dict[str, ParserTestResult]:
        """Test Cisco parsers"""
        cisco_parsers = [p for p in PROD_MAP.keys() if p.startswith('cisco_')]
        # Limit to first 5 for demo purposes
        return self.test_parser_group("Cisco", cisco_parsers[:5], count, wait_time)
    
    def test_aws_parsers(self, count: int = 5, wait_time: int = 60) -> Dict[str, ParserTestResult]:
        """Test AWS parsers"""
        aws_parsers = [p for p in PROD_MAP.keys() if p.startswith('aws_')]
        return self.test_parser_group("AWS", aws_parsers[:5], count, wait_time)
    
    def test_recently_fixed_parsers(self, count: int = 5, wait_time: int = 60) -> Dict[str, ParserTestResult]:
        """Test parsers that were recently fixed"""
        fixed_parsers = ['cisco_fmc', 'pingfederate', 'pingone_mfa', 'pingprotect']
        available = [p for p in fixed_parsers if p in PROD_MAP]
        return self.test_parser_group("Recently Fixed", available, count, wait_time)
    
    def validate_parser_configuration(self, parser_name: str) -> Dict[str, Any]:
        """Validate parser configuration against generator output
        
        Args:
            parser_name: Parser name to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Generate sample events
            events = self.generate_test_events(parser_name, 5)
            
            # Analyze field consistency
            all_fields = set()
            field_counts = {}
            
            for event in events:
                event_fields = self._extract_nested_fields(event)
                all_fields.update(event_fields)
                
                for field in event_fields:
                    field_counts[field] = field_counts.get(field, 0) + 1
            
            # Categorize fields
            consistent_fields = [f for f in all_fields if field_counts[f] == len(events)]
            optional_fields = [f for f in all_fields if field_counts[f] < len(events)]
            
            return {
                'success': True,
                'total_fields': len(all_fields),
                'consistent_fields': consistent_fields,
                'optional_fields': optional_fields,
                'field_consistency': {f: field_counts[f]/len(events) for f in all_fields}
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_nested_fields(self, obj: Any, prefix: str = '') -> List[str]:
        """Extract all nested field names from a nested dictionary"""
        fields = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_field = f"{prefix}.{key}" if prefix else key
                fields.append(current_field)
                
                if isinstance(value, (dict, list)):
                    fields.extend(self._extract_nested_fields(value, current_field))
        
        elif isinstance(obj, list) and obj:
            fields.extend(self._extract_nested_fields(obj[0], prefix))
        
        return fields
    
    def generate_comprehensive_report(self, output_file: str = None) -> str:
        """Generate comprehensive test report
        
        Args:
            output_file: Optional file to write report to
            
        Returns:
            Report content as string
        """
        if not self.test_results:
            return "No test results available. Run tests first."
        
        return self.dv_client.generate_test_report(self.test_results)


def main():
    """CLI interface for comprehensive parser testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Comprehensive SentinelOne Parser Testing')
    
    # Test selection
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('--parser', '-p', help='Test specific parser')
    test_group.add_argument('--ping', action='store_true', help='Test Ping Identity parsers')
    test_group.add_argument('--cisco', action='store_true', help='Test Cisco parsers (first 5)')
    test_group.add_argument('--aws', action='store_true', help='Test AWS parsers (first 5)')
    test_group.add_argument('--fixed', action='store_true', help='Test recently fixed parsers')
    test_group.add_argument('--validate', help='Validate specific parser configuration only')
    
    # Test parameters
    parser.add_argument('--count', '-c', type=int, default=3, help='Events per parser (default: 3)')
    parser.add_argument('--wait', '-w', type=int, default=90, help='Wait time in seconds (default: 90)')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--test-connection', action='store_true', help='Test API connectivity first')
    
    args = parser.parse_args()
    
    try:
        print("🚀 SentinelOne Comprehensive Parser Testing")
        print("=" * 60)
        
        # Initialize tester
        tester = ComprehensiveParserTester()
        
        if args.test_connection:
            print("🔗 Testing SentinelOne connectivity...")
            
            try:
                # Test DV API
                test_query = tester.dv_client.get_dv_events(
                    query='dataSource.name EXISTS',
                    limit=1
                )
                if test_query.status == 'SUCCESS':
                    print("✅ DV API: Connected and working")
                else:
                    print(f"⚠️  DV API: {test_query.status} - {test_query.errors}")
            except Exception as e:
                print(f"❌ DV API: {e}")
                
            print()
        
        # Validation mode
        if args.validate:
            print(f"🔍 Validating parser configuration: {args.validate}")
            validation = tester.validate_parser_configuration(args.validate)
            
            if validation['success']:
                print(f"✅ Parser validation successful")
                print(f"   Total fields: {validation['total_fields']}")
                print(f"   Consistent fields: {len(validation['consistent_fields'])}")
                print(f"   Optional fields: {len(validation['optional_fields'])}")
                
                if validation['optional_fields']:
                    print(f"   ⚠️  Optional fields: {validation['optional_fields'][:5]}{'...' if len(validation['optional_fields']) > 5 else ''}")
            else:
                print(f"❌ Parser validation failed: {validation['error']}")
            
            return
        
        # Run selected tests
        if args.parser:
            tester.test_single_parser(args.parser, args.count, args.wait)
        elif args.ping:
            tester.test_ping_parsers(args.count, args.wait)
        elif args.cisco:
            tester.test_cisco_parsers(args.count, args.wait)
        elif args.aws:
            tester.test_aws_parsers(args.count, args.wait)
        elif args.fixed:
            tester.test_recently_fixed_parsers(args.count, args.wait)
        else:
            # Default: test recently fixed parsers
            print("No specific test selected. Testing recently fixed parsers...")
            tester.test_recently_fixed_parsers(args.count, args.wait)
        
        # Generate comprehensive report
        if tester.test_results:
            report_file = args.output or f"parser_comprehensive_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            report = tester.generate_comprehensive_report(report_file)
            
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"\n📊 COMPREHENSIVE REPORT SAVED: {report_file}")
            
            # Print summary to console
            successful = sum(1 for r in tester.test_results.values() if r.parsing_success)
            total = len(tester.test_results)
            print(f"\n🎯 FINAL SUMMARY: {successful}/{total} parsers passed ({100*successful/total:.1f}%)")
    
    except KeyboardInterrupt:
        print("\n⏹️  Testing interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()