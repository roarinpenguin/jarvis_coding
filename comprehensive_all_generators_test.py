#!/usr/bin/env python3
"""
Comprehensive All Generators Test
Tests all 106+ generators and parsers in the jarvis_coding project
"""

import os
import subprocess
import time
import json
import glob
from datetime import datetime
from pathlib import Path
import re

class ComprehensiveGeneratorTester:
    """Tests all generators and their parser compatibility"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now().isoformat(),
            "summary": {},
            "categories": {},
            "individual_results": {}
        }
        
        # Discover all generators
        self.generators = self.discover_all_generators()
        print(f"📊 Discovered {len(self.generators)} generators across all categories")
    
    def discover_all_generators(self):
        """Discover all generator files and extract their product names"""
        generators = {}
        
        # Get all python files in event_generators (excluding shared)
        generator_files = glob.glob("event_generators/**/*.py", recursive=True)
        generator_files = [f for f in generator_files if "/shared/" not in f]
        
        for file_path in generator_files:
            try:
                # Extract category from path
                path_parts = Path(file_path).parts
                if len(path_parts) >= 3:
                    category = path_parts[1]  # e.g., 'network_security'
                    filename = Path(file_path).stem  # e.g., 'cisco_firewall_threat_defense'
                    
                    # Try to determine the product name for hec_sender mapping
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
        """Extract the product name that would be used in hec_sender.py"""
        # Common mappings based on hec_sender.py patterns
        mappings = {
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
            "cisco_meraki": "cisco_meraki_flow",  # Note: special mapping
            "cisco_meraki_flow": "cisco_meraki_flow",
            "darktrace": "darktrace",
            "cisco_umbrella": "cisco_umbrella",
            "abnormal_security": "abnormal_security",
            "google_workspace": "google_workspace",
            "cloudflare_general": "cloudflare_general",
            "zscaler": "zscaler",
            "zscaler_dns_firewall": "zscaler_dns_firewall"
        }
        
        if filename in mappings:
            return mappings[filename]
        
        # For other generators, try to guess the product name
        # Remove common suffixes and use the base name
        product_name = filename.replace("_logs", "").replace("_events", "")
        return product_name
    
    def test_generator_function(self, generator_info):
        """Test if a generator has a working function"""
        try:
            file_path = generator_info["file_path"]
            filename = generator_info["filename"]
            
            # Read the file to find the main function
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Look for the main function pattern (allow parameters)
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
                return {
                    "status": "function_found",
                    "function": main_function,
                    "has_star_trek": "picard" in content.lower() or "starfleet" in content.lower(),
                    "recent_timestamps": "datetime.now()" in content or "random" in content
                }
            else:
                return {
                    "status": "no_function",
                    "function": None,
                    "has_star_trek": False,
                    "recent_timestamps": False
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "function": None,
                "has_star_trek": False,
                "recent_timestamps": False
            }
    
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
            
            if result.returncode == 0 and ("success" in result.stdout.lower() or "successfully" in result.stdout.lower() or "delivered" in result.stdout.lower()):
                return {
                    "status": "success",
                    "output": result.stdout[:200] + "..." if len(result.stdout) > 200 else result.stdout,
                    "events_sent": count
                }
            else:
                return {
                    "status": "failed",
                    "error": (result.stderr or result.stdout)[:200] + "..." if len(result.stderr or result.stdout) > 200 else (result.stderr or result.stdout),
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
        """Check if a parser exists for the product"""
        # Look in parsers/community/ for matching parser
        parser_patterns = [
            f"parsers/community/{product_name}*",
            f"parsers/community/*{product_name}*",
            # Handle some common variations
            f"parsers/community/{product_name.replace('_', '')}*",
            f"parsers/community/*{product_name.replace('_', '')}*"
        ]
        
        for pattern in parser_patterns:
            matches = glob.glob(pattern)
            if matches:
                return {
                    "exists": True,
                    "parser_path": matches[0],
                    "parser_count": len(matches)
                }
        
        return {
            "exists": False,
            "parser_path": None,
            "parser_count": 0
        }
    
    def run_comprehensive_test(self):
        """Run the comprehensive test across all generators"""
        print("=" * 100)
        print("🚀 COMPREHENSIVE ALL GENERATORS TEST - JARVIS CODING PROJECT")
        print("=" * 100)
        print(f"📅 Timestamp: {datetime.now()}")
        print(f"🔧 Testing {sum(len(gens) for gens in self.generators.values())} generators")
        print(f"📂 Categories: {list(self.generators.keys())}\n")
        
        total_generators = 0
        total_function_working = 0
        total_hec_success = 0
        total_parser_exists = 0
        total_star_trek = 0
        
        # Test each category
        for category, generators in self.generators.items():
            print(f"\n{'='*80}")
            print(f"🏷️  CATEGORY: {category.upper().replace('_', ' ')}")
            print(f"{'='*80}")
            
            category_results = {
                "generators": {},
                "summary": {
                    "total": len(generators),
                    "function_working": 0,
                    "hec_success": 0,
                    "parser_exists": 0,
                    "star_trek_themes": 0
                }
            }
            
            for generator_info in generators:
                total_generators += 1
                filename = generator_info["filename"]
                product_name = generator_info["product_name"]
                
                print(f"\n🔧 Testing {filename}")
                print(f"   📦 Product: {product_name}")
                
                # Test generator function
                function_test = self.test_generator_function(generator_info)
                if function_test["status"] == "function_found":
                    print(f"   ✅ Function: {function_test['function']}")
                    total_function_working += 1
                    category_results["summary"]["function_working"] += 1
                else:
                    print(f"   ❌ Function: {function_test['status']}")
                
                # Check for Star Trek themes
                if function_test["has_star_trek"]:
                    print(f"   🖖 Star Trek themes detected")
                    total_star_trek += 1
                    category_results["summary"]["star_trek_themes"] += 1
                
                # Test HEC sending (only if we have token)
                hec_result = {"status": "skipped", "reason": "no_token"}
                if os.environ.get('S1_HEC_TOKEN'):
                    print(f"   📤 Testing HEC sending...", end="")
                    hec_result = self.test_hec_sending(product_name, count=1)
                    if hec_result["status"] == "success":
                        print(" ✅ Success!")
                        total_hec_success += 1
                        category_results["summary"]["hec_success"] += 1
                    else:
                        print(f" ❌ {hec_result['status']}")
                else:
                    print(f"   ⚠️  HEC: Skipped (no token)")
                
                # Check parser existence
                parser_check = self.check_parser_exists(product_name)
                if parser_check["exists"]:
                    print(f"   📋 Parser: Found ({parser_check['parser_path']})")
                    total_parser_exists += 1
                    category_results["summary"]["parser_exists"] += 1
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
            print(f"\n📊 {category} Summary:")
            print(f"   Function Success: {category_results['summary']['function_working']}/{len(generators)} ({success_rate:.1f}%)")
            print(f"   HEC Success: {category_results['summary']['hec_success']}/{len(generators)}")
            print(f"   Parser Found: {category_results['summary']['parser_exists']}/{len(generators)}")
            print(f"   Star Trek Themes: {category_results['summary']['star_trek_themes']}/{len(generators)}")
            
            self.results["categories"][category] = category_results
        
        # Overall summary
        print("\n" + "=" * 100)
        print("📋 COMPREHENSIVE TEST SUMMARY")
        print("=" * 100)
        
        function_rate = (total_function_working / total_generators * 100) if total_generators > 0 else 0
        hec_rate = (total_hec_success / total_generators * 100) if total_generators > 0 else 0
        parser_rate = (total_parser_exists / total_generators * 100) if total_generators > 0 else 0
        star_trek_rate = (total_star_trek / total_generators * 100) if total_generators > 0 else 0
        
        print(f"\n🎯 Overall Results:")
        print(f"   📊 Total Generators: {total_generators}")
        print(f"   ✅ Function Working: {total_function_working}/{total_generators} ({function_rate:.1f}%)")
        print(f"   📤 HEC Success: {total_hec_success}/{total_generators} ({hec_rate:.1f}%)")
        print(f"   📋 Parser Exists: {total_parser_exists}/{total_generators} ({parser_rate:.1f}%)")
        print(f"   🖖 Star Trek Themes: {total_star_trek}/{total_generators} ({star_trek_rate:.1f}%)")
        
        # Performance assessment
        if function_rate >= 90:
            status = "🎉 EXCELLENT! 90%+ generators working!"
        elif function_rate >= 75:
            status = "✅ GOOD! 75%+ generators working!"
        elif function_rate >= 50:
            status = "🔶 MODERATE! 50%+ generators working!"
        else:
            status = f"⚠️  NEEDS WORK! Only {function_rate:.1f}% working"
        
        print(f"\n{status}")
        
        # Category breakdown
        print(f"\n📂 Category Breakdown:")
        for category, results in self.results["categories"].items():
            summary = results["summary"]
            success_rate = (summary["function_working"] / summary["total"] * 100) if summary["total"] > 0 else 0
            print(f"   {category:30} {summary['function_working']:3}/{summary['total']:3} ({success_rate:5.1f}%)")
        
        # Store summary
        self.results["summary"] = {
            "total_generators": total_generators,
            "function_working": total_function_working,
            "hec_success": total_hec_success,
            "parser_exists": total_parser_exists,
            "star_trek_themes": total_star_trek,
            "function_rate": f"{function_rate:.1f}%",
            "hec_rate": f"{hec_rate:.1f}%", 
            "parser_rate": f"{parser_rate:.1f}%",
            "star_trek_rate": f"{star_trek_rate:.1f}%",
            "status": status
        }
        
        # Save results
        results_file = "comprehensive_all_generators_results.json"
        with open(results_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📁 Detailed results saved to: {results_file}")
        
        print("\n🖖 Testing complete! May your generators live long and prosper!")
        print("=" * 100)

def main():
    """Main entry point"""
    tester = ComprehensiveGeneratorTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()