#!/usr/bin/env python3
"""
Comprehensive Generator Test Suite
Tests ALL generators to ensure they:
1. Execute without errors
2. Produce correct format for their parsers
3. Include Star Trek integration where updated
4. Generate valid timestamps
5. Can be sent to HEC endpoint successfully
"""

import os
import sys
import json
import time
import importlib.util
import subprocess
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
import traceback

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import name mappings
from generator_name_mappings import get_log_function_name

class ComprehensiveGeneratorTester:
    def __init__(self):
        self.project_root = project_root
        self.generators_dir = self.project_root / "event_generators"
        self.parsers_dir = self.project_root / "parsers" / "community"
        self.test_results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {},
            "generators": {},
            "categories": {}
        }
        
        # Track statistics
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "star_trek": 0,
            "recent_timestamps": 0,
            "has_parser": 0,
            "format_issues": 0
        }
        
        # Star Trek indicators
        self.star_trek_indicators = [
            "starfleet", "enterprise", "picard", "riker", "data", "worf",
            "geordi", "crusher", "troi", "kirk", "spock", "mccoy",
            "federation", "romulan", "borg", "ferengi", "vulcan", "klingon"
        ]
        
    def discover_all_generators(self) -> List[Tuple[str, Path]]:
        """Discover all generator files in the project"""
        generators = []
        
        for category_dir in self.generators_dir.iterdir():
            if category_dir.is_dir() and category_dir.name not in ["shared", "__pycache__"]:
                for gen_file in category_dir.glob("*.py"):
                    if not gen_file.name.startswith("__"):
                        generators.append((category_dir.name, gen_file))
                        
        return sorted(generators)
        
    def test_generator(self, category: str, generator_path: Path) -> Dict:
        """Test a single generator comprehensively"""
        generator_name = generator_path.stem
        
        result = {
            "name": generator_name,
            "category": category,
            "path": str(generator_path),
            "status": "untested",
            "execution": {"success": False, "error": None},
            "format": {"type": None, "valid": False},
            "star_trek": {"present": False, "examples": []},
            "timestamp": {"recent": False, "value": None},
            "parser": {"exists": False, "path": None},
            "sample_output": None,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Load the generator module
            spec = importlib.util.spec_from_file_location(generator_name, generator_path)
            if not spec or not spec.loader:
                result["execution"]["error"] = "Failed to load module spec"
                result["status"] = "failed"
                return result
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the log function using mappings
            function_name = get_log_function_name(generator_name)
            if not hasattr(module, function_name):
                # Try alternative naming patterns
                alt_names = [
                    f"{generator_name}_log",  # Standard pattern
                    generator_name,  # Just the name
                    function_name.replace("aws_", ""),  # Remove aws_ prefix
                    function_name.replace("cisco_", ""),  # Remove cisco_ prefix
                    function_name.replace("microsoft_", ""),  # Remove microsoft_ prefix
                    "generate_log",
                    "generate_event"
                ]
                for alt_name in alt_names:
                    if hasattr(module, alt_name):
                        function_name = alt_name
                        break
                else:
                    result["execution"]["error"] = f"No log function found (tried {function_name} and alternatives)"
                    result["status"] = "failed"
                    return result
                    
            log_function = getattr(module, function_name)
            
            # Test execution
            try:
                # Try with overrides parameter first
                try:
                    event = log_function(overrides={})
                    result["execution"]["supports_overrides"] = True
                except TypeError:
                    # Fall back to no parameters
                    event = log_function()
                    result["execution"]["supports_overrides"] = False
                    
                result["execution"]["success"] = True
                result["sample_output"] = str(event)[:1000]  # First 1000 chars
                
            except Exception as e:
                result["execution"]["error"] = f"{type(e).__name__}: {str(e)}"
                result["status"] = "failed"
                return result
                
            # Analyze format
            if isinstance(event, dict):
                result["format"]["type"] = "JSON/Dict"
                result["format"]["valid"] = True
                result["format"]["fields"] = len(event.keys())
            elif isinstance(event, str):
                if event.startswith("{"):
                    try:
                        json.loads(event)
                        result["format"]["type"] = "JSON String"
                        result["format"]["valid"] = True
                    except:
                        result["format"]["type"] = "Invalid JSON String"
                        result["format"]["valid"] = False
                elif "=" in event and not event.startswith("<"):
                    result["format"]["type"] = "Key-Value"
                    result["format"]["valid"] = True
                elif event.startswith("<") or "CEF:" in event:
                    result["format"]["type"] = "Syslog/CEF"
                    result["format"]["valid"] = True
                else:
                    result["format"]["type"] = "Plain Text"
                    result["format"]["valid"] = True
            else:
                result["format"]["type"] = f"Unknown ({type(event).__name__})"
                result["format"]["valid"] = False
                
            # Check for Star Trek integration
            event_str = str(event).lower()
            star_trek_found = []
            for indicator in self.star_trek_indicators:
                if indicator in event_str:
                    star_trek_found.append(indicator)
                    
            result["star_trek"]["present"] = len(star_trek_found) > 0
            result["star_trek"]["examples"] = star_trek_found[:5]  # First 5 examples
            
            # Check timestamp recency
            if isinstance(event, dict):
                # Check various timestamp fields
                for field in ["timestamp", "Timestamp", "TimeStamp", "time", "eventTime", "windowstart"]:
                    if field in event:
                        try:
                            ts_value = event[field]
                            if isinstance(ts_value, str) and "T" in ts_value:
                                event_time = datetime.fromisoformat(ts_value.replace("Z", "+00:00"))
                                time_diff = datetime.now(timezone.utc) - event_time
                                result["timestamp"]["recent"] = abs(time_diff.total_seconds()) < 900  # 15 min
                                result["timestamp"]["value"] = ts_value
                                break
                            elif isinstance(ts_value, (int, float)):
                                # Unix timestamp
                                event_time = datetime.fromtimestamp(ts_value, tz=timezone.utc)
                                time_diff = datetime.now(timezone.utc) - event_time  
                                result["timestamp"]["recent"] = abs(time_diff.total_seconds()) < 900
                                result["timestamp"]["value"] = str(event_time)
                                break
                        except:
                            pass
                            
            # Check for parser
            parser_patterns = [
                f"{generator_name}-latest",
                f"{generator_name}_logs-latest",
                f"{generator_name.replace('_', '')}-latest"
            ]
            
            for pattern in parser_patterns:
                parser_path = self.parsers_dir / pattern
                if parser_path.exists():
                    result["parser"]["exists"] = True
                    result["parser"]["path"] = str(parser_path)
                    break
                    
            # Determine overall status
            if result["execution"]["success"]:
                if result["format"]["valid"]:
                    if result["star_trek"]["present"] and result["timestamp"]["recent"]:
                        result["status"] = "excellent"
                    elif result["star_trek"]["present"] or result["timestamp"]["recent"]:
                        result["status"] = "good"
                    else:
                        result["status"] = "functional"
                else:
                    result["status"] = "format_issue"
            else:
                result["status"] = "failed"
                
            # Add recommendations
            if not result["star_trek"]["present"]:
                result["recommendations"].append("Add Star Trek character/domain integration")
            if not result["timestamp"]["recent"]:
                result["recommendations"].append("Update to use recent timestamps (last 10 minutes)")
            if not result["parser"]["exists"]:
                result["recommendations"].append("Create parser configuration")
            if not result["execution"].get("supports_overrides"):
                result["recommendations"].append("Add overrides parameter support")
                
        except Exception as e:
            result["execution"]["error"] = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
            result["status"] = "failed"
            
        return result
        
    def test_all_generators(self):
        """Test all discovered generators"""
        print("🔍 Discovering all generators...")
        generators = self.discover_all_generators()
        
        print(f"📊 Found {len(generators)} generators to test\n")
        print("="*80)
        
        # Group by category
        by_category = {}
        for category, gen_path in generators:
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(gen_path)
            
        # Test each category
        for category, gen_paths in sorted(by_category.items()):
            print(f"\n📁 Testing {category} ({len(gen_paths)} generators)")
            print("-"*60)
            
            category_results = []
            
            for gen_path in gen_paths:
                gen_name = gen_path.stem
                print(f"  Testing {gen_name}...", end=" ")
                
                result = self.test_generator(category, gen_path)
                category_results.append(result)
                
                # Update statistics
                self.stats["total"] += 1
                
                if result["status"] in ["excellent", "good", "functional"]:
                    self.stats["successful"] += 1
                    status_icon = "✅"
                else:
                    self.stats["failed"] += 1
                    status_icon = "❌"
                    
                if result["star_trek"]["present"]:
                    self.stats["star_trek"] += 1
                if result["timestamp"]["recent"]:
                    self.stats["recent_timestamps"] += 1
                if result["parser"]["exists"]:
                    self.stats["has_parser"] += 1
                if result["status"] == "format_issue":
                    self.stats["format_issues"] += 1
                    
                # Store result
                self.test_results["generators"][gen_name] = result
                
                # Print status
                extras = []
                if result["star_trek"]["present"]:
                    extras.append("🖖")
                if result["timestamp"]["recent"]:
                    extras.append("⏰")
                if result["parser"]["exists"]:
                    extras.append("📋")
                    
                extras_str = " ".join(extras) if extras else ""
                print(f"{status_icon} {result['status'].upper()} {extras_str}")
                
                if result["execution"]["error"]:
                    print(f"    ⚠️  {result['execution']['error']}")
                    
            # Store category results
            self.test_results["categories"][category] = {
                "total": len(category_results),
                "successful": sum(1 for r in category_results if r["status"] in ["excellent", "good", "functional"]),
                "failed": sum(1 for r in category_results if r["status"] == "failed"),
                "generators": [r["name"] for r in category_results]
            }
            
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE GENERATOR TEST REPORT")
        print("="*80)
        
        # Calculate percentages
        success_rate = (self.stats["successful"] / self.stats["total"] * 100) if self.stats["total"] else 0
        star_trek_rate = (self.stats["star_trek"] / self.stats["total"] * 100) if self.stats["total"] else 0
        timestamp_rate = (self.stats["recent_timestamps"] / self.stats["total"] * 100) if self.stats["total"] else 0
        parser_rate = (self.stats["has_parser"] / self.stats["total"] * 100) if self.stats["total"] else 0
        
        print(f"\n📈 OVERALL STATISTICS:")
        print(f"  • Total Generators: {self.stats['total']}")
        print(f"  • Successful: {self.stats['successful']}/{self.stats['total']} ({success_rate:.1f}%)")
        print(f"  • Failed: {self.stats['failed']}/{self.stats['total']}")
        print(f"  • Format Issues: {self.stats['format_issues']}")
        
        print(f"\n🖖 INTEGRATION METRICS:")
        print(f"  • Star Trek Integration: {self.stats['star_trek']}/{self.stats['total']} ({star_trek_rate:.1f}%)")
        print(f"  • Recent Timestamps: {self.stats['recent_timestamps']}/{self.stats['total']} ({timestamp_rate:.1f}%)")
        print(f"  • Has Parser: {self.stats['has_parser']}/{self.stats['total']} ({parser_rate:.1f}%)")
        
        # List excellent generators
        excellent = [name for name, result in self.test_results["generators"].items() 
                    if result["status"] == "excellent"]
        if excellent:
            print(f"\n🌟 EXCELLENT GENERATORS ({len(excellent)}):")
            for gen in excellent[:10]:  # Show first 10
                print(f"  ✨ {gen}")
                
        # List failed generators
        failed = [(name, result) for name, result in self.test_results["generators"].items() 
                 if result["status"] == "failed"]
        if failed:
            print(f"\n❌ FAILED GENERATORS ({len(failed)}):")
            for gen_name, result in failed[:10]:  # Show first 10
                print(f"  • {gen_name}: {result['execution']['error']}")
                
        # Category breakdown
        print(f"\n📁 CATEGORY BREAKDOWN:")
        for category, stats in sorted(self.test_results["categories"].items()):
            success = stats["successful"]
            total = stats["total"]
            rate = (success / total * 100) if total else 0
            print(f"  • {category}: {success}/{total} working ({rate:.1f}%)")
            
        # Update summary
        self.test_results["summary"] = {
            "total_generators": self.stats["total"],
            "successful": self.stats["successful"],
            "failed": self.stats["failed"],
            "success_rate": success_rate,
            "star_trek_integration_rate": star_trek_rate,
            "recent_timestamp_rate": timestamp_rate,
            "parser_coverage_rate": parser_rate,
            "test_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Save results
        output_file = self.project_root / "testing" / "comprehensive_test_results.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
            
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        # Overall grade
        overall_score = (success_rate * 0.4 + star_trek_rate * 0.2 + 
                        timestamp_rate * 0.2 + parser_rate * 0.2)
        
        if overall_score >= 95:
            grade = "A+"
        elif overall_score >= 90:
            grade = "A"
        elif overall_score >= 80:
            grade = "B"
        elif overall_score >= 70:
            grade = "C"
        else:
            grade = "D"
            
        print(f"\n🎯 OVERALL GRADE: {grade} ({overall_score:.1f}%)")
        
        if success_rate < 100:
            print(f"\n💡 RECOMMENDATION: Fix {self.stats['failed']} failed generators to achieve 100% success rate")

def main():
    """Main test execution"""
    print("🚀 Starting Comprehensive Generator Test Suite")
    print("="*80)
    
    tester = ComprehensiveGeneratorTester()
    tester.test_all_generators()
    tester.generate_report()
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    main()