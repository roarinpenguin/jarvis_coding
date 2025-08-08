#!/usr/bin/env python3
"""
Parser Validator - End-to-end testing for SentinelOne parsers
Integrates with existing generators to test all parsers systematically
"""
import json
import os
import sys
import importlib
import traceback
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s1_api_client import SentinelOneAPI, ParseResult

# Import the product mapping from hec_sender
try:
    from hec_sender import PROD_MAP, JSON_PRODUCTS
except ImportError:
    print("Warning: Could not import PROD_MAP from hec_sender")
    PROD_MAP = {}
    JSON_PRODUCTS = []

class ParserValidator:
    """Comprehensive parser validation using SentinelOne API"""
    
    def __init__(self, api_client: SentinelOneAPI = None):
        """Initialize parser validator
        
        Args:
            api_client: SentinelOne API client instance
        """
        self.api_client = api_client or SentinelOneAPI()
        self.results: Dict[str, ParseResult] = {}
        
    def generate_test_events(self, product_name: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate test events for a specific product
        
        Args:
            product_name: Product name (e.g., 'cisco_fmc', 'pingfederate')
            count: Number of events to generate
            
        Returns:
            List of generated events
        """
        if product_name not in PROD_MAP:
            raise ValueError(f"Unknown product: {product_name}")
        
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
                        # Raw log string - convert to dict
                        event = {"raw_log": event, "timestamp": datetime.now(timezone.utc).isoformat()}
                elif isinstance(event, dict):
                    # Already a dict
                    pass
                else:
                    raise ValueError(f"Unexpected event type: {type(event)}")
                
                events.append(event)
            
            return events
            
        except Exception as e:
            raise Exception(f"Failed to generate events for {product_name}: {e}")
    
    def test_parser(self, parser_name: str, count: int = 5, wait_time: int = 30) -> ParseResult:
        """Test a specific parser with generated events
        
        Args:
            parser_name: Parser name (should match product name)
            count: Number of test events
            wait_time: Wait time for processing
            
        Returns:
            ParseResult with test outcomes
        """
        print(f"\n{'='*60}")
        print(f"Testing Parser: {parser_name}")
        print(f"{'='*60}")
        
        try:
            # Generate test events
            print(f"Generating {count} test events...")
            events = self.generate_test_events(parser_name, count)
            print(f"✅ Generated {len(events)} events")
            
            # Show sample event
            if events:
                sample = events[0]
                print(f"Sample event fields: {list(sample.keys())}")
            
            # Test with SentinelOne API
            result = self.api_client.test_parser(parser_name, events, wait_time)
            
            # Store result
            self.results[parser_name] = result
            
            # Print immediate results
            if result.success:
                print(f"✅ PASS - {result.events_parsed}/{result.events_sent} events parsed successfully")
            else:
                print(f"❌ FAIL - {len(result.parse_errors)} error(s):")
                for error in result.parse_errors:
                    print(f"   - {error}")
            
            return result
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            traceback.print_exc()
            
            # Create error result
            error_result = ParseResult(
                success=False,
                parser_name=parser_name,
                events_sent=0,
                events_parsed=0,
                parse_errors=[str(e)],
                field_mappings={},
                raw_response={}
            )
            
            self.results[parser_name] = error_result
            return error_result
    
    def test_product_group(self, group_name: str, products: List[str], 
                          count: int = 5, wait_time: int = 30) -> Dict[str, ParseResult]:
        """Test a group of related products
        
        Args:
            group_name: Name of the product group
            products: List of product names to test
            count: Number of test events per product
            wait_time: Wait time between tests
            
        Returns:
            Dictionary mapping product names to results
        """
        print(f"\n{'#'*80}")
        print(f"Testing Product Group: {group_name}")
        print(f"Products: {', '.join(products)}")
        print(f"{'#'*80}")
        
        group_results = {}
        
        for product in products:
            result = self.test_parser(product, count, wait_time)
            group_results[product] = result
        
        # Group summary
        successful = sum(1 for r in group_results.values() if r.success)
        print(f"\n{group_name} Group Summary: {successful}/{len(products)} parsers passed")
        
        return group_results
    
    def test_all_ping_parsers(self, count: int = 5, wait_time: int = 30) -> Dict[str, ParseResult]:
        """Test all Ping Identity parsers"""
        ping_products = ['pingfederate', 'pingone_mfa', 'pingprotect']
        return self.test_product_group("Ping Identity", ping_products, count, wait_time)
    
    def test_all_cisco_parsers(self, count: int = 5, wait_time: int = 30) -> Dict[str, ParseResult]:
        """Test all Cisco parsers"""
        cisco_products = [p for p in PROD_MAP.keys() if p.startswith('cisco_')]
        return self.test_product_group("Cisco", cisco_products, count, wait_time)
    
    def test_all_aws_parsers(self, count: int = 5, wait_time: int = 30) -> Dict[str, ParseResult]:
        """Test all AWS parsers"""
        aws_products = [p for p in PROD_MAP.keys() if p.startswith('aws_')]
        return self.test_product_group("AWS", aws_products, count, wait_time)
    
    def test_all_microsoft_parsers(self, count: int = 5, wait_time: int = 30) -> Dict[str, ParseResult]:
        """Test all Microsoft parsers"""
        ms_products = [p for p in PROD_MAP.keys() if p.startswith('microsoft_')]
        return self.test_product_group("Microsoft", ms_products, count, wait_time)
    
    def test_problematic_parsers(self, count: int = 5, wait_time: int = 30) -> Dict[str, ParseResult]:
        """Test parsers that have had recent issues"""
        problematic = ['cisco_fmc', 'pingfederate', 'pingprotect', 'pingone_mfa']
        available = [p for p in problematic if p in PROD_MAP]
        return self.test_product_group("Recently Fixed", available, count, wait_time)
    
    def run_comprehensive_test(self, count: int = 3, wait_time: int = 20) -> Dict[str, ParseResult]:
        """Run comprehensive test of all parsers
        
        Args:
            count: Number of events per parser (reduced for comprehensive testing)
            wait_time: Wait time between tests
            
        Returns:
            Complete results dictionary
        """
        print(f"\n{'*'*80}")
        print("COMPREHENSIVE PARSER VALIDATION")
        print(f"Testing {len(PROD_MAP)} parsers with {count} events each")
        print(f"{'*'*80}")
        
        # Test in logical groups
        group_tests = [
            ("Ping Identity", ['pingfederate', 'pingone_mfa', 'pingprotect']),
            ("AWS Services", [p for p in PROD_MAP.keys() if p.startswith('aws_')][:5]),  # Limit for demo
            ("Cisco Products", [p for p in PROD_MAP.keys() if p.startswith('cisco_')][:5]),
            ("Microsoft Services", [p for p in PROD_MAP.keys() if p.startswith('microsoft_')][:5]),
            ("Other Security Tools", ['jamf_protect', 'veeam_backup', 'wiz_cloud'])
        ]
        
        for group_name, products in group_tests:
            available_products = [p for p in products if p in PROD_MAP]
            if available_products:
                self.test_product_group(group_name, available_products, count, wait_time)
        
        return self.results
    
    def generate_validation_report(self, output_file: str = None) -> str:
        """Generate comprehensive validation report
        
        Args:
            output_file: Optional file to write report to
            
        Returns:
            Report content as string
        """
        report_lines = []
        
        # Header
        report_lines.extend([
            "# SentinelOne Parser Validation Report",
            "",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Total Parsers Tested:** {len(self.results)}",
            ""
        ])
        
        # Summary statistics
        successful = sum(1 for r in self.results.values() if r.success)
        total_events_sent = sum(r.events_sent for r in self.results.values())
        total_events_parsed = sum(r.events_parsed for r in self.results.values())
        
        report_lines.extend([
            "## Summary",
            "",
            f"- **Success Rate:** {successful}/{len(self.results)} ({100*successful/len(self.results):.1f}%)",
            f"- **Total Events Sent:** {total_events_sent}",
            f"- **Total Events Parsed:** {total_events_parsed}",
            f"- **Overall Parse Rate:** {100*total_events_parsed/total_events_sent:.1f}%" if total_events_sent > 0 else "- **Overall Parse Rate:** N/A",
            ""
        ])
        
        # Results table
        report_lines.extend([
            "## Test Results",
            "",
            "| Parser | Status | Events Sent | Events Parsed | Parse Rate | Errors |",
            "|--------|--------|-------------|---------------|------------|--------|"
        ])
        
        for parser_name, result in sorted(self.results.items()):
            status = "✅ PASS" if result.success else "❌ FAIL"
            parse_rate = f"{100*result.events_parsed/result.events_sent:.1f}%" if result.events_sent > 0 else "N/A"
            error_count = len(result.parse_errors)
            
            report_lines.append(
                f"| {parser_name} | {status} | {result.events_sent} | {result.events_parsed} | {parse_rate} | {error_count} |"
            )
        
        # Detailed error analysis
        failed_parsers = {name: result for name, result in self.results.items() if not result.success}
        
        if failed_parsers:
            report_lines.extend([
                "",
                "## Failed Parsers",
                ""
            ])
            
            for parser_name, result in failed_parsers.items():
                report_lines.extend([
                    f"### {parser_name}",
                    ""
                ])
                
                if result.parse_errors:
                    report_lines.append("**Errors:**")
                    for error in result.parse_errors:
                        report_lines.append(f"- {error}")
                    report_lines.append("")
                
                if result.events_sent > 0 and result.events_parsed == 0:
                    report_lines.extend([
                        "**Diagnosis:** Complete parsing failure - no events were successfully parsed",
                        "**Recommended Actions:**",
                        "- Check parser JSON syntax and format configuration",
                        "- Verify field mappings match generator output",
                        "- Test with simplified field mappings",
                        ""
                    ])
                elif result.events_parsed < result.events_sent:
                    report_lines.extend([
                        "**Diagnosis:** Partial parsing failure - some events not parsed",
                        "**Recommended Actions:**",
                        "- Review optional field mappings",
                        "- Check for conditional field generation in generator",
                        ""
                    ])
        
        # Success stories
        successful_parsers = {name: result for name, result in self.results.items() if result.success}
        
        if successful_parsers:
            report_lines.extend([
                "## Successful Parsers",
                "",
                f"The following {len(successful_parsers)} parsers passed all tests:",
                ""
            ])
            
            for parser_name in sorted(successful_parsers.keys()):
                result = successful_parsers[parser_name]
                report_lines.append(f"- **{parser_name}**: {result.events_parsed}/{result.events_sent} events parsed successfully")
            
            report_lines.append("")
        
        # Recommendations
        report_lines.extend([
            "## Recommendations",
            "",
            "### For Failed Parsers:",
            "1. **Review field mappings** - Ensure parser only maps fields that are always present",
            "2. **Check optional fields** - Remove mappings for conditionally generated fields", 
            "3. **Validate JSON syntax** - Use `python -m json.tool parser.json` to check syntax",
            "4. **Test format configuration** - Verify `parse=gron` for JSON events",
            "",
            "### For Successful Parsers:",
            "1. **Monitor in production** - Watch for parsing issues with real data",
            "2. **Performance testing** - Test with higher event volumes",
            "3. **Field coverage** - Review if all important fields are being mapped",
            ""
        ])
        
        report_content = "\n".join(report_lines)
        
        # Write to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_content)
            print(f"\n📊 Report saved to: {output_file}")
        
        return report_content


def main():
    """CLI interface for parser validation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SentinelOne Parser Validation Tool')
    
    # Test selection
    test_group = parser.add_mutually_exclusive_group()
    test_group.add_argument('--parser', '-p', help='Test specific parser')
    test_group.add_argument('--ping', action='store_true', help='Test Ping Identity parsers')
    test_group.add_argument('--cisco', action='store_true', help='Test Cisco parsers')
    test_group.add_argument('--aws', action='store_true', help='Test AWS parsers')
    test_group.add_argument('--microsoft', action='store_true', help='Test Microsoft parsers')
    test_group.add_argument('--problematic', action='store_true', help='Test recently fixed parsers')
    test_group.add_argument('--comprehensive', action='store_true', help='Test all parsers')
    
    # Test parameters
    parser.add_argument('--count', '-c', type=int, default=5, help='Events per parser (default: 5)')
    parser.add_argument('--wait', '-w', type=int, default=30, help='Wait time in seconds (default: 30)')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--dry-run', action='store_true', help='Generate events without sending to S1')
    
    args = parser.parse_args()
    
    try:
        # Initialize validator
        if args.dry_run:
            print("DRY RUN MODE - Events will be generated but not sent to SentinelOne")
            # Create mock API client for dry run
            class MockAPI:
                def test_parser(self, name, events, wait):
                    return ParseResult(True, name, len(events), len(events), [], {}, {})
            validator = ParserValidator(MockAPI())
        else:
            validator = ParserValidator()
        
        # Run selected tests
        if args.parser:
            validator.test_parser(args.parser, args.count, args.wait)
        elif args.ping:
            validator.test_all_ping_parsers(args.count, args.wait)
        elif args.cisco:
            validator.test_all_cisco_parsers(args.count, args.wait)
        elif args.aws:
            validator.test_all_aws_parsers(args.count, args.wait)
        elif args.microsoft:
            validator.test_all_microsoft_parsers(args.count, args.wait)
        elif args.problematic:
            validator.test_problematic_parsers(args.count, args.wait)
        elif args.comprehensive:
            validator.run_comprehensive_test(args.count, args.wait)
        else:
            # Default: test problematic parsers
            print("No specific test selected. Testing recently fixed parsers...")
            validator.test_problematic_parsers(args.count, args.wait)
        
        # Generate report
        if validator.results:
            report_file = args.output or f"parser_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            validator.generate_validation_report(report_file)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()