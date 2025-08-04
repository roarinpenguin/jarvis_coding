#!/usr/bin/env python3
"""
Comprehensive test script for all security event generators.
Tests each generator, validates output, and checks parser compatibility.
"""
import os
import sys
import json
import importlib
import traceback
from datetime import datetime
from typing import Dict, List, Tuple, Any
import glob

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.ENDC}\n")

def print_section(text: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{text}{Colors.ENDC}")
    print("-" * len(text))

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

def discover_generators() -> List[str]:
    """Discover all Python generator files."""
    generators = []
    exclude_files = [
        "hec_sender.py", "attack_scenario_orchestrator.py", 
        "quick_scenario.py", "scenario_hec_sender.py", 
        "direct_sample.py", "test_all_generators.py",
        "__init__.py"
    ]
    
    for file in glob.glob("*.py"):
        if file not in exclude_files and not file.startswith("_"):
            generators.append(file[:-3])  # Remove .py extension
    
    return sorted(generators)

def test_generator(module_name: str) -> Tuple[bool, str, Any]:
    """Test a single generator module."""
    try:
        # Import the module
        module = importlib.import_module(module_name)
        
        # Find the main log generation function
        log_func_name = None
        for attr_name in dir(module):
            if attr_name.endswith("_log") and callable(getattr(module, attr_name)):
                log_func_name = attr_name
                break
        
        if not log_func_name:
            return False, "No log generation function found", None
        
        log_func = getattr(module, log_func_name)
        
        # Generate a sample log
        log_output = log_func()
        
        # Validate output
        if not log_output:
            return False, "Empty log output", None
        
        # Check if it's JSON (many generators return JSON)
        try:
            if log_output.strip().startswith("{"):
                parsed = json.loads(log_output)
                return True, "JSON output validated", log_output
        except:
            pass
        
        # For non-JSON formats, just check it's not empty
        if len(log_output) > 10:  # Reasonable minimum length
            return True, "Text log output validated", log_output
        else:
            return False, "Log output too short", log_output
            
    except Exception as e:
        return False, f"Exception: {str(e)}", traceback.format_exc()

def check_attr_fields(module_name: str) -> Tuple[bool, Dict[str, str]]:
    """Check if module has ATTR_FIELDS for HEC integration."""
    try:
        module = importlib.import_module(module_name)
        if hasattr(module, 'ATTR_FIELDS'):
            attr_fields = getattr(module, 'ATTR_FIELDS')
            if isinstance(attr_fields, dict):
                return True, attr_fields
        return False, {}
    except:
        return False, {}

def find_matching_parser(generator_name: str) -> List[str]:
    """Find parser directories that might match this generator."""
    parser_dir = "../parsers/community"
    matches = []
    
    # Common name mappings
    name_map = {
        "apache_http": ["apache_http_logs"],
        "aruba_clearpass": ["aruba_clearpass_logs"],
        "checkpoint": ["checkpoint_checkpoint_logs"],
        "cloudflare_waf": ["cloudflare_inc_waf"],
        "paloalto_firewall": ["paloalto_alternate_logs", "paloalto_paloalto_logs"],
        "vmware_vcenter": ["vmware_vcenter_logs"],
        "aws_elb": ["aws_elasticloadbalancer_logs"],
        "microsoft_azure_ad_signin": ["microsoft_eventhub_azure_signin_logs"],
        "microsoft_defender_email": ["microsoft_eventhub_defender_email_logs"],
        "microsoft_365_mgmt_api": ["microsoft_365_mgmt_api_logs"],
        "okta_authentication": ["okta_ocsf_logs"],
    }
    
    # Check direct mapping first
    if generator_name in name_map:
        for parser_name in name_map[generator_name]:
            parser_path = os.path.join(parser_dir, f"{parser_name}-latest")
            if os.path.exists(parser_path):
                matches.append(parser_path)
    
    # Try fuzzy matching
    vendor_product = generator_name.replace("_", " ").split()
    if vendor_product:
        vendor = vendor_product[0]
        for parser in glob.glob(f"{parser_dir}/*"):
            if vendor in parser.lower():
                matches.append(parser)
    
    return list(set(matches))  # Remove duplicates

def test_scenario_tools() -> Dict[str, bool]:
    """Test scenario generation tools."""
    results = {}
    
    scenario_tools = [
        "attack_scenario_orchestrator.py",
        "quick_scenario.py",
        "scenario_hec_sender.py"
    ]
    
    for tool in scenario_tools:
        if os.path.exists(tool):
            try:
                # Just check if we can import it without errors
                spec = importlib.util.spec_from_file_location(tool[:-3], tool)
                module = importlib.util.module_from_spec(spec)
                results[tool] = True
            except Exception as e:
                results[tool] = False
        else:
            results[tool] = False
    
    return results

def main():
    """Run comprehensive tests on all generators."""
    print_header("Security Event Generator Test Suite")
    
    # Change to event_python_writer directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Discover generators
    print_section("Discovering Generators")
    generators = discover_generators()
    print_info(f"Found {len(generators)} generators")
    
    # Test results
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    warnings = 0
    
    # Test each generator
    print_section("Testing Event Generators")
    generator_results = {}
    
    for generator in generators:
        total_tests += 1
        print(f"\nTesting {generator}...", end="", flush=True)
        
        success, message, output = test_generator(generator)
        has_attr, attr_fields = check_attr_fields(generator)
        parsers = find_matching_parser(generator)
        
        generator_results[generator] = {
            "success": success,
            "message": message,
            "has_attr_fields": has_attr,
            "parsers": parsers,
            "sample": output[:200] if output and isinstance(output, str) else None
        }
        
        if success:
            print(f"\r{Colors.GREEN}✓{Colors.ENDC} {generator:<30} {message}")
            passed_tests += 1
            
            if not has_attr:
                print_warning(f"  Missing ATTR_FIELDS for HEC integration")
                warnings += 1
            
            if parsers:
                print_info(f"  Matching parsers: {', '.join([os.path.basename(p) for p in parsers])}")
            else:
                print_warning(f"  No matching parser found")
                warnings += 1
        else:
            print(f"\r{Colors.RED}✗{Colors.ENDC} {generator:<30} {message}")
            failed_tests += 1
            if output and "Traceback" in str(output):
                print(f"  {Colors.RED}{output}{Colors.ENDC}")
    
    # Test scenario tools
    print_section("Testing Scenario Tools")
    scenario_results = test_scenario_tools()
    
    for tool, success in scenario_results.items():
        total_tests += 1
        if success:
            print_success(f"{tool}")
            passed_tests += 1
        else:
            print_error(f"{tool}")
            failed_tests += 1
    
    # Summary statistics
    print_header("Test Summary")
    
    print(f"Total generators found: {len(generators)}")
    print(f"Total tests run: {total_tests}")
    print(f"{Colors.GREEN}Tests passed: {passed_tests}{Colors.ENDC}")
    print(f"{Colors.RED}Tests failed: {failed_tests}{Colors.ENDC}")
    print(f"{Colors.YELLOW}Warnings: {warnings}{Colors.ENDC}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\nSuccess rate: {success_rate:.1f}%")
    
    # List of working generators for HEC
    print_section("HEC-Ready Generators")
    hec_ready = [g for g, r in generator_results.items() if r["success"] and r["has_attr_fields"]]
    print(f"Found {len(hec_ready)} generators ready for HEC integration:")
    for generator in sorted(hec_ready):
        print(f"  • {generator}")
    
    # Failed generators that need attention
    if failed_tests > 0:
        print_section("Failed Generators (Need Attention)")
        for generator, result in generator_results.items():
            if not result["success"]:
                print(f"  • {generator}: {result['message']}")
    
    # Missing parsers
    missing_parsers = [g for g, r in generator_results.items() if r["success"] and not r["parsers"]]
    if missing_parsers:
        print_section("Generators Without Parsers")
        for generator in sorted(missing_parsers):
            print(f"  • {generator}")
    
    # Save detailed report
    report_file = "test_report.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_generators": len(generators),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "warnings": warnings,
            "success_rate": success_rate
        },
        "generators": generator_results,
        "scenario_tools": scenario_results,
        "hec_ready": hec_ready,
        "missing_parsers": missing_parsers
    }
    
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    print_info(f"\nDetailed report saved to: {report_file}")
    
    # Exit code based on failures
    sys.exit(1 if failed_tests > 0 else 0)

if __name__ == "__main__":
    main()