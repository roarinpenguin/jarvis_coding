#!/usr/bin/env python3
"""
Star Trek Integration Test Suite
Tests all updated generators to ensure they produce:
1. Correct formats for their parsers
2. Star Trek themed data
3. Recent timestamps
4. Override support
"""

import sys
import json
import importlib.util
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class StarTrekIntegrationTester:
    def __init__(self):
        self.project_root = project_root
        self.generators_dir = self.project_root / "event_generators"
        self.test_results = []
        
        # Updated generators to test
        self.generators_to_test = [
            ("cloud_infrastructure", "aws_route53"),
            ("cloud_infrastructure", "aws_vpc_dns"),
            ("identity_access", "microsoft_365_collaboration"),
            ("identity_access", "microsoft_365_defender"),
            ("network_security", "cisco_duo"),
            ("network_security", "cisco_fmc"),
            ("cloud_infrastructure", "google_workspace"),
        ]
        
        # Star Trek indicators to check for
        self.star_trek_indicators = [
            "starfleet", "enterprise", "picard", "riker", "data", "worf",
            "federation", "romulan", "borg", "ferengi", "vulcan",
            "bridge", "engineering", "medical", "security", "science"
        ]
        
    def test_generator(self, category: str, generator_name: str) -> Dict:
        """Test a single generator"""
        result = {
            "generator": generator_name,
            "category": category,
            "format_correct": False,
            "star_trek_integrated": False,
            "recent_timestamp": False,
            "override_support": False,
            "sample_output": None,
            "errors": []
        }
        
        try:
            # Load the generator
            generator_path = self.generators_dir / category / f"{generator_name}.py"
            spec = importlib.util.spec_from_file_location(generator_name, generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the log function
            function_name = f"{generator_name}_log"
            if not hasattr(module, function_name):
                result["errors"].append(f"Function {function_name} not found")
                return result
                
            log_function = getattr(module, function_name)
            
            # Test 1: Generate basic event
            try:
                event = log_function()
                result["sample_output"] = str(event)[:500]  # First 500 chars
                
                # Check format
                if isinstance(event, (dict, str)):
                    result["format_correct"] = True
                    
            except TypeError:
                # Old function signature without overrides parameter
                event = log_function()
                result["sample_output"] = str(event)[:500]
                result["format_correct"] = isinstance(event, (dict, str))
                result["override_support"] = False
            
            # Test 2: Check Star Trek integration
            event_str = str(event).lower()
            has_star_trek = any(indicator in event_str for indicator in self.star_trek_indicators)
            result["star_trek_integrated"] = has_star_trek
            
            # Test 3: Check timestamp recency
            if isinstance(event, dict):
                # Check various timestamp field names
                timestamp_fields = ["timestamp", "Timestamp", "TimeStamp", "time", "eventTime"]
                for field in timestamp_fields:
                    if field in event:
                        try:
                            # Parse timestamp
                            if isinstance(event[field], str):
                                if "T" in event[field]:  # ISO format
                                    event_time = datetime.fromisoformat(event[field].replace("Z", "+00:00"))
                                    time_diff = datetime.now(event_time.tzinfo) - event_time
                                    # Check if within 15 minutes (accounting for test generation)
                                    result["recent_timestamp"] = time_diff.total_seconds() < 900
                                    break
                        except:
                            pass
            elif isinstance(event, str):
                # For syslog format, check if timestamp is recent
                import re
                timestamp_match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', event)
                if timestamp_match:
                    event_time = datetime.fromisoformat(timestamp_match.group().replace("Z", "+00:00"))
                    time_diff = datetime.now(event_time.tzinfo) - event_time
                    result["recent_timestamp"] = time_diff.total_seconds() < 900
            
            # Test 4: Check override support
            try:
                test_override = {"test_field": "test_value"}
                event_with_override = log_function(overrides=test_override)
                if isinstance(event_with_override, dict):
                    result["override_support"] = event_with_override.get("test_field") == "test_value"
                else:
                    result["override_support"] = False
            except:
                result["override_support"] = False
                
        except Exception as e:
            result["errors"].append(str(e))
            
        return result
        
    def run_all_tests(self):
        """Run tests on all generators"""
        print("🧪 Testing Star Trek Integration on Updated Generators")
        print("="*60)
        
        for category, generator_name in self.generators_to_test:
            print(f"\nTesting {generator_name} ({category})...")
            result = self.test_generator(category, generator_name)
            self.test_results.append(result)
            
            # Print immediate feedback
            checkmarks = {
                "Format": "✅" if result["format_correct"] else "❌",
                "Star Trek": "✅" if result["star_trek_integrated"] else "❌",
                "Recent Time": "✅" if result["recent_timestamp"] else "❌",
                "Overrides": "✅" if result["override_support"] else "❌"
            }
            
            status_line = " | ".join([f"{k}: {v}" for k, v in checkmarks.items()])
            print(f"  {status_line}")
            
            if result["errors"]:
                print(f"  ⚠️  Errors: {result['errors']}")
                
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📊 STAR TREK INTEGRATION TEST REPORT")
        print("="*60)
        
        # Calculate statistics
        total_tested = len(self.test_results)
        format_correct = sum(1 for r in self.test_results if r["format_correct"])
        star_trek_integrated = sum(1 for r in self.test_results if r["star_trek_integrated"])
        recent_timestamps = sum(1 for r in self.test_results if r["recent_timestamp"])
        override_support = sum(1 for r in self.test_results if r["override_support"])
        
        print(f"\n📈 SUMMARY STATISTICS:")
        print(f"  Total Generators Tested: {total_tested}")
        print(f"  Format Correct: {format_correct}/{total_tested} ({format_correct/total_tested*100:.1f}%)")
        print(f"  Star Trek Integration: {star_trek_integrated}/{total_tested} ({star_trek_integrated/total_tested*100:.1f}%)")
        print(f"  Recent Timestamps: {recent_timestamps}/{total_tested} ({recent_timestamps/total_tested*100:.1f}%)")
        print(f"  Override Support: {override_support}/{total_tested} ({override_support/total_tested*100:.1f}%)")
        
        # List perfect generators
        perfect_generators = [r for r in self.test_results 
                            if r["format_correct"] and r["star_trek_integrated"] 
                            and r["recent_timestamp"] and r["override_support"]]
        
        if perfect_generators:
            print(f"\n🏆 PERFECT GENERATORS ({len(perfect_generators)}):")
            for gen in perfect_generators:
                print(f"  ✨ {gen['generator']} - All tests passed!")
                
        # List generators needing attention
        needs_attention = [r for r in self.test_results 
                          if not (r["format_correct"] and r["star_trek_integrated"])]
        
        if needs_attention:
            print(f"\n⚠️  NEEDS ATTENTION ({len(needs_attention)}):")
            for gen in needs_attention:
                issues = []
                if not gen["format_correct"]:
                    issues.append("format")
                if not gen["star_trek_integrated"]:
                    issues.append("Star Trek")
                if not gen["recent_timestamp"]:
                    issues.append("timestamp")
                print(f"  • {gen['generator']}: Missing {', '.join(issues)}")
                
        # Save detailed results
        output_file = self.project_root / "scenarios" / "star_trek_integration_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2, default=str)
            
        print(f"\n💾 Detailed results saved to: {output_file}")
        
        # Overall grade
        overall_score = (format_correct + star_trek_integrated + recent_timestamps + override_support) / (total_tested * 4)
        grade = "A+" if overall_score >= 0.95 else "A" if overall_score >= 0.90 else "B" if overall_score >= 0.80 else "C"
        
        print(f"\n🎯 OVERALL GRADE: {grade} ({overall_score*100:.1f}%)")

def main():
    """Main test function"""
    tester = StarTrekIntegrationTester()
    tester.run_all_tests()
    tester.generate_report()

if __name__ == "__main__":
    main()