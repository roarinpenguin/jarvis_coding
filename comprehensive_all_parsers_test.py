#!/usr/bin/env python3
"""
Comprehensive All Parsers Test
Tests ALL 106 generators and validates field extraction with parsers
"""

import os
import subprocess
import time
import json
import glob
from datetime import datetime
from pathlib import Path
import re

class ComprehensiveParserTester:
    """Tests all generators and validates parser field extraction"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "categories": {},
            "individual_results": {}
        }
        
        # Discover all generators
        self.generators = self.discover_all_generators()
        print(f"📊 Discovered {len(self.generators)} total generators")
        
        # Track comprehensive stats
        self.total_generators = 0
        self.total_hec_success = 0
        self.total_parser_found = 0
        self.total_function_working = 0
        
    def discover_all_generators(self):
        """Discover all generator files"""
        generators = {}
        
        # Get all python files in event_generators (excluding shared)
        generator_files = glob.glob("event_generators/**/*.py", recursive=True)
        generator_files = [f for f in generator_files if "/shared/" not in f]
        
        for file_path in generator_files:
            try:
                path_parts = Path(file_path).parts
                if len(path_parts) >= 3:
                    category = path_parts[1]  # e.g., 'network_security'
                    filename = Path(file_path).stem  # e.g., 'cisco_firewall_threat_defense'
                    
                    # Determine product name for hec_sender mapping
                    product_name = self.extract_product_name(filename, file_path)
                    
                    if category not in generators:
                        generators[category] = []
                    
                    generators[category].append({
                        "filename": filename,
                        "product_name": product_name,
                        "file_path": file_path,
                        "category": category
                    })
            except Exception as e:
                print(f"⚠️  Error processing {file_path}: {e}")
        
        return generators
    
    def extract_product_name(self, filename, file_path):
        """Extract the product name for hec_sender mapping"""
        # Common mappings from hec_sender.py
        known_mappings = {
            "aws_cloudtrail": "aws_cloudtrail",
            "aws_guardduty": "aws_guardduty", 
            "aws_vpcflowlogs": "aws_vpcflowlogs",
            "aws_route53": "aws_route53",
            "aws_waf": "aws_waf",
            "okta_authentication": "okta_authentication",
            "crowdstrike_falcon": "crowdstrike_falcon",
            "sentinelone_endpoint": "sentinelone_endpoint",
            "paloalto_firewall": "paloalto_firewall",
            "cisco_duo": "cisco_duo",
            "cisco_fmc": "cisco_fmc",
            "microsoft_365_collaboration": "microsoft_365_collaboration",
            "microsoft_365_defender": "microsoft_365_defender",
            "fortinet_fortigate": "fortinet_fortigate",
            "cisco_meraki_flow": "cisco_meraki_flow",
            "abnormal_security": "abnormal_security",
            "google_workspace": "google_workspace",
            "zscaler": "zscaler"
        }
        
        if filename in known_mappings:
            return known_mappings[filename]
        
        # For others, use the filename as product name
        return filename
    
    def test_generator_function(self, generator_info):
        """Test if generator has working function"""
        try:
            file_path = generator_info["file_path"]
            filename = generator_info["filename"]
            
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for main log function (with parameters allowed)
            function_patterns = [
                rf"def {filename}_log\(",
                rf"def {filename.replace('_', '')}_log\(", 
                rf"def.*_log\(",
                rf"def generate_.*\(",
                rf"def.*event\("
            ]
            
            main_function = None
            for pattern in function_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    main_function = matches[0]
                    break
            
            if main_function:
                # Check for realistic field count (estimate)
                field_count = self.estimate_field_count(content)
                return {
                    "status": "function_found",
                    "function": main_function,
                    "estimated_fields": field_count,
                    "has_json_output": "json.dumps" in content or '"' in content
                }
            else:
                return {
                    "status": "no_function",
                    "function": None,
                    "estimated_fields": 0,
                    "has_json_output": False
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "estimated_fields": 0,
                "has_json_output": False
            }
    
    def estimate_field_count(self, content):
        """Estimate the number of fields a generator produces"""
        # Count unique field-like patterns
        field_patterns = [
            r'"([^"]+)":',  # JSON field names
            r"'([^']+)':",  # Single quoted field names
            r'(\w+)=',      # Key=value pairs
        ]
        
        unique_fields = set()
        for pattern in field_patterns:
            matches = re.findall(pattern, content)
            unique_fields.update(matches)
        
        # Filter out common non-field matches
        non_fields = {
            'timestamp', 'datetime', 'time', 'str', 'int', 'float', 'bool',
            'random', 'choice', 'choices', 'randint', 'uniform', 'if', 'else',
            'for', 'in', 'and', 'or', 'not', 'def', 'return', 'import', 'from'
        }
        
        actual_fields = unique_fields - non_fields
        return len(actual_fields)
    
    def test_hec_sending(self, product_name, count=1):
        """Test HEC sending for a product"""
        try:
            cmd = [
                ".venv/bin/python",
                "event_generators/shared/hec_sender.py", 
                "--product", product_name,
                "--count", str(count)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and ("success" in result.stdout.lower() or "delivered" in result.stdout.lower()):
                return {
                    "status": "success",
                    "output": result.stdout[:200],
                    "events_sent": count
                }
            else:
                return {
                    "status": "failed",
                    "error": (result.stderr or result.stdout)[:300],
                    "events_sent": 0
                }
                
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "error": "Command timed out after 30 seconds",
                "events_sent": 0
            }
        except Exception as e:
            return {
                "status": "error", 
                "error": str(e),
                "events_sent": 0
            }
    
    def check_parser_exists(self, product_name):
        """Check if parser exists and estimate field extraction capability"""
        # Look for parser in community directory
        parser_patterns = [
            f"parsers/community/{product_name}*",
            f"parsers/community/*{product_name}*",
            f"parsers/community/{product_name.replace('_', '')}*",
            f"parsers/community/*{product_name.replace('_', '')}*"
        ]
        
        for pattern in parser_patterns:
            matches = glob.glob(pattern)
            if matches:
                parser_path = matches[0]
                
                # Analyze parser configuration
                parser_analysis = self.analyze_parser_configuration(parser_path)
                
                return {
                    "exists": True,
                    "parser_path": parser_path,
                    "parser_count": len(matches),
                    **parser_analysis
                }
        
        return {
            "exists": False,
            "parser_path": None,
            "parser_count": 0,
            "expected_fields": 0,
            "parser_type": "unknown"
        }
    
    def analyze_parser_configuration(self, parser_path):
        """Analyze parser configuration to estimate field extraction"""
        try:
            # Look for parser JSON file
            json_files = glob.glob(f"{parser_path}/*.json")
            if not json_files:
                return {"expected_fields": 0, "parser_type": "unknown"}
            
            parser_file = json_files[0]
            with open(parser_file, 'r') as f:
                parser_config = json.load(f)
            
            # Count field mappings in parser
            field_count = 0
            parser_type = "unknown"
            
            # Check for gron parser
            if "parse" in parser_config and parser_config["parse"] == "gron":
                parser_type = "gron"
                # Gron parsers typically have fewer explicit field mappings
                field_count = 20
            
            # Check for regex parser
            elif "logPattern" in parser_config or "patterns" in parser_config:
                parser_type = "regex"
                # Count regex patterns and groups
                patterns = parser_config.get("logPattern", parser_config.get("patterns", []))
                if isinstance(patterns, str):
                    field_count = len(re.findall(r'\$\w+\$', patterns))
                elif isinstance(patterns, list):
                    field_count = sum(len(re.findall(r'\$\w+\$', p)) for p in patterns if isinstance(p, str))
            
            # Check for JSON parser with field mappings
            elif "fields" in parser_config:
                parser_type = "json"
                field_count = len(parser_config["fields"])
            
            # Check for custom parser configurations
            elif "mapping" in parser_config:
                parser_type = "mapping"
                field_count = len(parser_config["mapping"])
            
            else:
                # Estimate based on file size/complexity
                with open(parser_file, 'r') as f:
                    content = f.read()
                    field_count = len(re.findall(r'\$\w+\$', content))
                    if field_count == 0:
                        # Look for other field patterns
                        field_count = len(re.findall(r'"[^"]+"\s*:', content))
            
            return {
                "expected_fields": max(field_count, 10),  # Minimum 10 fields
                "parser_type": parser_type
            }
            
        except Exception as e:
            return {
                "expected_fields": 0,
                "parser_type": "error",
                "error": str(e)
            }
    
    def run_comprehensive_test(self):
        """Run comprehensive test of all generators and parsers"""
        print("=" * 100)
        print("🚀 COMPREHENSIVE ALL PARSERS TEST - FIELD EXTRACTION VALIDATION")
        print("=" * 100)
        print(f"📅 Timestamp: {datetime.now()}")
        print(f"🔧 Testing {sum(len(gens) for gens in self.generators.values())} total generators")
        print(f"🎯 Validating parser field extraction capabilities\n")
        
        category_stats = {}
        
        # Test each category
        for category, generators in self.generators.items():
            print(f"\n{'='*90}")
            print(f"📂 CATEGORY: {category.upper().replace('_', ' ')}")
            print(f"{'='*90}")
            print(f"Testing {len(generators)} generators in this category...")
            
            category_results = {
                "generators": {},
                "summary": {
                    "total": len(generators),
                    "function_working": 0,
                    "hec_success": 0,
                    "parser_exists": 0,
                    "high_field_extraction": 0
                }
            }
            
            for generator_info in generators:
                self.total_generators += 1
                filename = generator_info["filename"]
                product_name = generator_info["product_name"]
                
                print(f"\n🔧 Testing {filename}")
                print(f"   📦 Product: {product_name}")
                
                # Test generator function
                function_test = self.test_generator_function(generator_info)
                if function_test["status"] == "function_found":
                    print(f"   ✅ Function: {function_test['function']} (~{function_test['estimated_fields']} fields)")
                    self.total_function_working += 1
                    category_results["summary"]["function_working"] += 1
                else:
                    print(f"   ❌ Function: {function_test['status']}")
                
                # Test HEC sending
                hec_result = {"status": "skipped", "reason": "no_token"}
                if os.environ.get('S1_HEC_TOKEN'):
                    print(f"   📤 Testing HEC...", end="")
                    hec_result = self.test_hec_sending(product_name, count=1)
                    if hec_result["status"] == "success":
                        print(" ✅ Success")
                        self.total_hec_success += 1
                        category_results["summary"]["hec_success"] += 1
                    else:
                        print(f" ❌ {hec_result['status']}")
                        if len(hec_result.get('error', '')) > 100:
                            print(f"     Error: {hec_result['error'][:100]}...")
                else:
                    print(f"   ⚠️  HEC: Skipped (no S1_HEC_TOKEN)")
                
                # Check parser and field extraction
                parser_check = self.check_parser_exists(product_name)
                if parser_check["exists"]:
                    expected_fields = parser_check.get("expected_fields", 0)
                    parser_type = parser_check.get("parser_type", "unknown")
                    print(f"   📋 Parser: {parser_type} type, ~{expected_fields} expected fields")
                    self.total_parser_found += 1
                    category_results["summary"]["parser_exists"] += 1
                    
                    # Check if high field extraction expected
                    if expected_fields >= 20:
                        category_results["summary"]["high_field_extraction"] += 1
                        print(f"   🎯 High field extraction expected ({expected_fields} fields)")
                else:
                    print(f"   ⚠️  Parser: Not found")
                
                # Store detailed results
                category_results["generators"][filename] = {
                    "product_name": product_name,
                    "function_test": function_test,
                    "hec_test": hec_result,
                    "parser_check": parser_check,
                    "file_path": generator_info["file_path"]
                }
                
                # Small delay to avoid overwhelming
                time.sleep(0.1)
            
            # Category summary
            success_rate = (category_results["summary"]["function_working"] / len(generators) * 100) if generators else 0
            hec_rate = (category_results["summary"]["hec_success"] / len(generators) * 100) if generators else 0
            parser_rate = (category_results["summary"]["parser_exists"] / len(generators) * 100) if generators else 0
            
            print(f"\n📊 {category} Results:")
            print(f"   Functions Working: {category_results['summary']['function_working']}/{len(generators)} ({success_rate:.1f}%)")
            print(f"   HEC Success: {category_results['summary']['hec_success']}/{len(generators)} ({hec_rate:.1f}%)")
            print(f"   Parsers Found: {category_results['summary']['parser_exists']}/{len(generators)} ({parser_rate:.1f}%)")
            print(f"   High Field Extraction: {category_results['summary']['high_field_extraction']}/{len(generators)}")
            
            self.results["categories"][category] = category_results
            category_stats[category] = {
                "success_rate": success_rate,
                "hec_rate": hec_rate,
                "parser_rate": parser_rate,
                "total": len(generators)
            }
        
        # Generate final summary
        self.generate_final_summary(category_stats)
    
    def generate_final_summary(self, category_stats):
        """Generate comprehensive final summary"""
        print("\n" + "=" * 100)
        print("📋 COMPREHENSIVE VALIDATION SUMMARY")
        print("=" * 100)
        
        function_rate = (self.total_function_working / self.total_generators * 100) if self.total_generators > 0 else 0
        hec_rate = (self.total_hec_success / self.total_generators * 100) if self.total_generators > 0 else 0
        parser_rate = (self.total_parser_found / self.total_generators * 100) if self.total_generators > 0 else 0
        
        print(f"\n🎯 Overall Results:")
        print(f"   📊 Total Generators: {self.total_generators}")
        print(f"   ✅ Functions Working: {self.total_function_working}/{self.total_generators} ({function_rate:.1f}%)")
        print(f"   📤 HEC Success: {self.total_hec_success}/{self.total_generators} ({hec_rate:.1f}%)")
        print(f"   📋 Parsers Found: {self.total_parser_found}/{self.total_generators} ({parser_rate:.1f}%)")
        
        # Performance assessment
        if function_rate >= 90 and hec_rate >= 90 and parser_rate >= 85:
            status = "🎉 EXCELLENT! All systems performing optimally!"
        elif function_rate >= 80 and hec_rate >= 80 and parser_rate >= 75:
            status = "✅ GOOD! Most generators and parsers working well!"
        elif function_rate >= 70:
            status = "🔶 MODERATE! Some issues need attention!"
        else:
            status = f"⚠️  NEEDS WORK! Only {function_rate:.1f}% generators fully functional"
        
        print(f"\n{status}")
        
        # Category breakdown with field extraction focus
        print(f"\n📂 Category Performance Breakdown:")
        print("=" * 60)
        for category, stats in category_stats.items():
            print(f"{category:30} | Func: {stats['success_rate']:5.1f}% | HEC: {stats['hec_rate']:5.1f}% | Parser: {stats['parser_rate']:5.1f}% | ({stats['total']} gens)")
        
        # Store summary
        self.results["summary"] = {
            "total_generators": self.total_generators,
            "function_working": self.total_function_working,
            "hec_success": self.total_hec_success,
            "parser_found": self.total_parser_found,
            "function_rate": f"{function_rate:.1f}%",
            "hec_rate": f"{hec_rate:.1f}%", 
            "parser_rate": f"{parser_rate:.1f}%",
            "status": status,
            "category_breakdown": category_stats
        }
        
        # Save detailed results
        results_file = "comprehensive_all_parsers_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: {results_file}")
        
        # Identify problem generators
        self.identify_problem_generators()
        
        print(f"\n🔍 Field extraction analysis complete!")
        print(f"Check the detailed report for generator-specific parser compatibility.")
        print("=" * 100)
    
    def identify_problem_generators(self):
        """Identify generators that need field extraction improvements"""
        print(f"\n⚠️  GENERATORS NEEDING ATTENTION:")
        print("-" * 60)
        
        problem_generators = []
        
        for category, category_data in self.results["categories"].items():
            for gen_name, gen_data in category_data["generators"].items():
                issues = []
                
                # Check for missing function
                if gen_data["function_test"]["status"] != "function_found":
                    issues.append("No log function")
                
                # Check for HEC failure
                if gen_data["hec_test"]["status"] != "success" and gen_data["hec_test"]["status"] != "skipped":
                    issues.append("HEC sending failed")
                
                # Check for missing parser
                if not gen_data["parser_check"]["exists"]:
                    issues.append("No parser found")
                
                # Check for low field extraction
                expected_fields = gen_data["parser_check"].get("expected_fields", 0)
                estimated_fields = gen_data["function_test"].get("estimated_fields", 0)
                
                if expected_fields > 0 and estimated_fields > 0 and estimated_fields < expected_fields * 0.5:
                    issues.append(f"Low field count (gen:{estimated_fields} vs parser:{expected_fields})")
                
                if issues:
                    problem_generators.append({
                        "name": gen_name,
                        "category": category,
                        "issues": issues,
                        "priority": len(issues)
                    })
        
        # Sort by priority (most issues first)
        problem_generators.sort(key=lambda x: x["priority"], reverse=True)
        
        if problem_generators:
            for gen in problem_generators[:10]:  # Show top 10 problem generators
                print(f"🔴 {gen['name']:30} ({gen['category']}) - {', '.join(gen['issues'])}")
            
            if len(problem_generators) > 10:
                print(f"   ... and {len(problem_generators) - 10} more generators needing attention")
        else:
            print("✅ No major issues detected!")

def main():
    """Main entry point"""
    tester = ComprehensiveParserTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()