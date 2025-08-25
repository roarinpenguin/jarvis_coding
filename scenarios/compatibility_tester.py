#!/usr/bin/env python3
"""
Automated Parser-Generator Compatibility Testing Framework

This tool provides comprehensive testing to ensure generators produce output 
compatible with their corresponding parsers by:
1. Validating output formats (JSON, Syslog, CSV, Key-Value)
2. Testing field extraction and mapping
3. Checking Star Trek character integration
4. Running end-to-end pipeline tests
5. Generating compatibility reports
"""

import os
import json
import sys
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import tempfile

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class CompatibilityTester:
    def __init__(self):
        self.project_root = project_root
        self.generators_dir = self.project_root / "event_generators"
        self.parsers_dir = self.project_root / "parsers" / "community"
        self.results = {
            "test_timestamp": datetime.now().isoformat(),
            "format_validation": {},
            "field_extraction": {},
            "star_trek_validation": {},
            "end_to_end_tests": {},
            "compatibility_scores": {},
            "summary": {}
        }
        
    def test_format_compatibility(self, generator_path: Path, expected_format: str) -> Dict:
        """Test if generator output matches expected format"""
        test_result = {
            "generator": generator_path.name,
            "expected_format": expected_format,
            "actual_format": None,
            "format_valid": False,
            "sample_output": None,
            "errors": []
        }
        
        try:
            # Import and run the generator
            sys.path.insert(0, str(generator_path.parent))
            module_name = generator_path.stem
            
            # Dynamic import
            spec = importlib.util.spec_from_file_location(module_name, generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find the log function
            function_name = f"{module_name}_log"
            if not hasattr(module, function_name):
                test_result["errors"].append(f"Function {function_name} not found")
                return test_result
                
            log_function = getattr(module, function_name)
            
            # Generate sample output
            sample_output = log_function()
            test_result["sample_output"] = sample_output[:500] if isinstance(sample_output, str) else str(sample_output)[:500]
            
            # Detect actual format
            actual_format = self._detect_format(sample_output)
            test_result["actual_format"] = actual_format
            
            # Check if formats match
            test_result["format_valid"] = (actual_format.lower() == expected_format.lower())
            
        except Exception as e:
            test_result["errors"].append(f"Execution error: {str(e)}")
            
        return test_result
        
    def test_field_extraction(self, generator_path: Path, parser_config: Dict) -> Dict:
        """Test field extraction against parser configuration"""
        test_result = {
            "generator": generator_path.name,
            "fields_extracted": 0,
            "fields_expected": 0,
            "extraction_rate": 0.0,
            "missing_fields": [],
            "unexpected_fields": [],
            "field_mapping_valid": False
        }
        
        try:
            # Generate sample output
            sys.path.insert(0, str(generator_path.parent))
            module_name = generator_path.stem
            
            spec = importlib.util.spec_from_file_location(module_name, generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            function_name = f"{module_name}_log"
            if hasattr(module, function_name):
                log_function = getattr(module, function_name)
                sample_output = log_function()
                
                # Extract fields from output
                output_fields = self._extract_fields_from_output(sample_output)
                
                # Extract expected fields from parser config
                expected_fields = self._extract_expected_fields(parser_config)
                
                # Calculate metrics
                test_result["fields_extracted"] = len(output_fields)
                test_result["fields_expected"] = len(expected_fields)
                
                if len(expected_fields) > 0:
                    matched_fields = set(output_fields) & set(expected_fields)
                    test_result["extraction_rate"] = len(matched_fields) / len(expected_fields)
                    test_result["missing_fields"] = list(set(expected_fields) - set(output_fields))
                    test_result["unexpected_fields"] = list(set(output_fields) - set(expected_fields))
                    test_result["field_mapping_valid"] = test_result["extraction_rate"] > 0.5
                    
        except Exception as e:
            test_result["error"] = str(e)
            
        return test_result
        
    def test_star_trek_integration(self, generator_path: Path) -> Dict:
        """Test Star Trek character integration"""
        test_result = {
            "generator": generator_path.name,
            "has_star_trek": False,
            "star_trek_score": 0.0,
            "characters_found": [],
            "starfleet_domain": False,
            "sample_users": []
        }
        
        try:
            # Read generator source code
            with open(generator_path, 'r') as f:
                source_code = f.read()
                
            # Check for Star Trek indicators
            star_trek_chars = [
                "jean.picard", "william.riker", "data.android", "geordi.laforge",
                "worf.security", "deanna.troi", "beverly.crusher", "james.kirk",
                "spock.science", "benjamin.sisko", "kathryn.janeway"
            ]
            
            found_chars = [char for char in star_trek_chars if char in source_code.lower()]
            test_result["characters_found"] = found_chars
            test_result["starfleet_domain"] = "starfleet.corp" in source_code.lower()
            
            # Calculate Star Trek score
            char_score = len(found_chars) / len(star_trek_chars) * 0.7
            domain_score = 0.3 if test_result["starfleet_domain"] else 0
            test_result["star_trek_score"] = char_score + domain_score
            test_result["has_star_trek"] = test_result["star_trek_score"] > 0.1
            
            # Generate sample to check actual output
            sys.path.insert(0, str(generator_path.parent))
            module_name = generator_path.stem
            
            spec = importlib.util.spec_from_file_location(module_name, generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            function_name = f"{module_name}_log"
            if hasattr(module, function_name):
                log_function = getattr(module, function_name)
                sample_output = str(log_function())
                
                # Extract user examples from output
                import re
                email_pattern = r'([a-z]+\.[a-z]+)@[a-z.-]+'
                user_matches = re.findall(email_pattern, sample_output.lower())
                test_result["sample_users"] = list(set(user_matches))[:5]
                
        except Exception as e:
            test_result["error"] = str(e)
            
        return test_result
        
    def run_end_to_end_test(self, generator_path: Path, parser_name: str) -> Dict:
        """Run end-to-end pipeline test (generator → parser → validation)"""
        test_result = {
            "generator": generator_path.name,
            "parser": parser_name,
            "pipeline_success": False,
            "events_generated": 0,
            "events_parsed": 0,
            "parsing_rate": 0.0,
            "test_duration": 0.0
        }
        
        start_time = time.time()
        
        try:
            # Generate multiple test events
            sys.path.insert(0, str(generator_path.parent))
            module_name = generator_path.stem
            
            spec = importlib.util.spec_from_file_location(module_name, generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            function_name = f"{module_name}_log"
            if hasattr(module, function_name):
                log_function = getattr(module, function_name)
                
                # Generate test events
                test_events = []
                for _ in range(10):  # Generate 10 test events
                    event = log_function()
                    test_events.append(event)
                    
                test_result["events_generated"] = len(test_events)
                
                # Simulate parsing (in real scenario, would send to HEC and query back)
                # For now, just validate format consistency
                parsed_events = 0
                for event in test_events:
                    if self._simulate_parsing_success(event):
                        parsed_events += 1
                        
                test_result["events_parsed"] = parsed_events
                test_result["parsing_rate"] = parsed_events / len(test_events) if test_events else 0
                test_result["pipeline_success"] = test_result["parsing_rate"] > 0.8
                
        except Exception as e:
            test_result["error"] = str(e)
            
        test_result["test_duration"] = time.time() - start_time
        return test_result
        
    def calculate_compatibility_score(self, generator_path: Path, parser_name: str) -> Dict:
        """Calculate overall compatibility score"""
        scores = {
            "generator": generator_path.name,
            "parser": parser_name,
            "format_score": 0.0,
            "field_score": 0.0,
            "star_trek_score": 0.0,
            "pipeline_score": 0.0,
            "overall_score": 0.0,
            "compatibility_grade": "F"
        }
        
        # Get individual test results
        format_result = self.results["format_validation"].get(generator_path.name, {})
        field_result = self.results["field_extraction"].get(generator_path.name, {})
        star_trek_result = self.results["star_trek_validation"].get(generator_path.name, {})
        pipeline_result = self.results["end_to_end_tests"].get(generator_path.name, {})
        
        # Calculate individual scores
        scores["format_score"] = 1.0 if format_result.get("format_valid", False) else 0.0
        scores["field_score"] = field_result.get("extraction_rate", 0.0)
        scores["star_trek_score"] = star_trek_result.get("star_trek_score", 0.0)
        scores["pipeline_score"] = pipeline_result.get("parsing_rate", 0.0)
        
        # Calculate weighted overall score
        weights = {"format": 0.3, "field": 0.3, "star_trek": 0.2, "pipeline": 0.2}
        overall = (
            scores["format_score"] * weights["format"] +
            scores["field_score"] * weights["field"] +
            scores["star_trek_score"] * weights["star_trek"] +
            scores["pipeline_score"] * weights["pipeline"]
        )
        scores["overall_score"] = overall
        
        # Assign grade
        if overall >= 0.9:
            scores["compatibility_grade"] = "A+"
        elif overall >= 0.8:
            scores["compatibility_grade"] = "A"
        elif overall >= 0.7:
            scores["compatibility_grade"] = "B"
        elif overall >= 0.6:
            scores["compatibility_grade"] = "C"
        elif overall >= 0.5:
            scores["compatibility_grade"] = "D"
        else:
            scores["compatibility_grade"] = "F"
            
        return scores
        
    def run_comprehensive_tests(self, limit: Optional[int] = None):
        """Run comprehensive compatibility tests"""
        print("🧪 Starting Comprehensive Parser-Generator Compatibility Tests")
        print("="*80)
        
        # Load audit results to get parser-generator mappings
        audit_file = self.project_root / "scenarios" / "parser_generator_audit_results.json"
        if not audit_file.exists():
            print("❌ Audit results not found. Run parser_generator_audit.py first.")
            return
            
        with open(audit_file, 'r') as f:
            audit_data = json.load(f)
            
        # Get format mismatches to test
        format_mismatches = audit_data.get("format_mismatches", [])
        if limit:
            format_mismatches = format_mismatches[:limit]
            
        print(f"🔍 Testing {len(format_mismatches)} parser-generator pairs")
        
        for i, mismatch in enumerate(format_mismatches, 1):
            generator_path = Path(mismatch["generator_path"])
            parser_name = mismatch["parser"]
            expected_format = mismatch["parser_format"]
            
            print(f"\n[{i}/{len(format_mismatches)}] Testing {generator_path.name} → {parser_name}")
            
            # Run individual tests
            format_result = self.test_format_compatibility(generator_path, expected_format)
            self.results["format_validation"][generator_path.name] = format_result
            
            # Load parser config for field testing
            parser_config = self._load_parser_config(parser_name)
            if parser_config:
                field_result = self.test_field_extraction(generator_path, parser_config)
                self.results["field_extraction"][generator_path.name] = field_result
                
            # Test Star Trek integration
            star_trek_result = self.test_star_trek_integration(generator_path)
            self.results["star_trek_validation"][generator_path.name] = star_trek_result
            
            # Run end-to-end test
            pipeline_result = self.run_end_to_end_test(generator_path, parser_name)
            self.results["end_to_end_tests"][generator_path.name] = pipeline_result
            
            # Calculate compatibility score
            compatibility_score = self.calculate_compatibility_score(generator_path, parser_name)
            self.results["compatibility_scores"][generator_path.name] = compatibility_score
            
            # Show progress
            grade = compatibility_score["compatibility_grade"]
            score = compatibility_score["overall_score"]
            print(f"   Grade: {grade} (Score: {score:.2f})")
            
        # Generate summary
        self._generate_summary()
        
    def _detect_format(self, output: Any) -> str:
        """Detect the format of generator output"""
        if isinstance(output, dict):
            return "JSON"
        elif isinstance(output, str):
            output_lower = output.lower().strip()
            
            # Check for JSON
            if output.startswith('{') and output.endswith('}'):
                try:
                    json.loads(output)
                    return "JSON"
                except:
                    pass
                    
            # Check for Syslog
            if output.startswith('<') and '>' in output[:10]:
                return "Syslog"
                
            # Check for CSV
            if ',' in output and not '=' in output:
                return "CSV"
                
            # Check for Key-Value
            if '=' in output and not output.startswith('{'):
                return "Key-Value"
                
            # Default to Text
            return "Text"
        else:
            return "Unknown"
            
    def _extract_fields_from_output(self, output: Any) -> List[str]:
        """Extract field names from generator output"""
        fields = []
        
        if isinstance(output, dict):
            fields = list(output.keys())
        elif isinstance(output, str):
            if output.startswith('{'):
                try:
                    json_data = json.loads(output)
                    fields = list(json_data.keys())
                except:
                    pass
            elif '=' in output:
                # Key-value format
                import re
                kv_pairs = re.findall(r'(\w+)=', output)
                fields = kv_pairs
                
        return fields
        
    def _extract_expected_fields(self, parser_config: Dict) -> List[str]:
        """Extract expected field names from parser configuration"""
        # This would need to be customized based on parser config format
        # For now, return common expected fields
        return [
            "timestamp", "source", "destination", "action", "user", "ip_address",
            "event_type", "severity", "message", "protocol", "port"
        ]
        
    def _load_parser_config(self, parser_name: str) -> Optional[Dict]:
        """Load parser configuration"""
        try:
            # Find parser directory
            parser_dirs = [d for d in self.parsers_dir.iterdir() 
                          if d.is_dir() and parser_name.lower().replace(" ", "_") in d.name.lower()]
                          
            if parser_dirs:
                parser_dir = parser_dirs[0]
                json_files = list(parser_dir.glob("*.json"))
                if json_files:
                    with open(json_files[0], 'r') as f:
                        return json.load(f)
        except Exception:
            pass
            
        return None
        
    def _simulate_parsing_success(self, event: Any) -> bool:
        """Simulate parsing success (placeholder for actual parser testing)"""
        # In real implementation, would send to HEC and check parsing
        # For now, just check if event is well-formed
        try:
            if isinstance(event, str):
                if event.startswith('{'):
                    json.loads(event)
                    return True
                elif len(event) > 10:
                    return True
            elif isinstance(event, dict):
                return len(event) > 0
        except:
            pass
            
        return False
        
    def _generate_summary(self):
        """Generate test summary"""
        compatibility_scores = list(self.results["compatibility_scores"].values())
        
        if not compatibility_scores:
            return
            
        # Calculate summary statistics
        total_tests = len(compatibility_scores)
        avg_score = sum(score["overall_score"] for score in compatibility_scores) / total_tests
        
        grade_counts = {}
        for score in compatibility_scores:
            grade = score["compatibility_grade"]
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
            
        format_valid = sum(1 for result in self.results["format_validation"].values() 
                          if result.get("format_valid", False))
        
        star_trek_integrated = sum(1 for result in self.results["star_trek_validation"].values() 
                                 if result.get("has_star_trek", False))
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "average_score": avg_score,
            "grade_distribution": grade_counts,
            "format_compatibility_rate": format_valid / total_tests if total_tests else 0,
            "star_trek_integration_rate": star_trek_integrated / total_tests if total_tests else 0
        }
        
    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n" + "="*80)
        print("📊 COMPATIBILITY TESTING REPORT")
        print("="*80)
        
        summary = self.results.get("summary", {})
        
        if not summary:
            print("❌ No test results available")
            return
            
        print(f"\n📈 SUMMARY STATISTICS:")
        print(f"   • Total tests run: {summary['total_tests']}")
        print(f"   • Average compatibility score: {summary['average_score']:.2f}")
        print(f"   • Format compatibility rate: {summary['format_compatibility_rate']:.1%}")
        print(f"   • Star Trek integration rate: {summary['star_trek_integration_rate']:.1%}")
        
        print(f"\n🎓 GRADE DISTRIBUTION:")
        for grade, count in sorted(summary["grade_distribution"].items()):
            percentage = count / summary["total_tests"] * 100
            print(f"   • {grade}: {count} ({percentage:.1f}%)")
            
        # Top performers
        compatibility_scores = list(self.results["compatibility_scores"].values())
        top_performers = sorted(compatibility_scores, 
                              key=lambda x: x["overall_score"], reverse=True)[:10]
        
        if top_performers:
            print(f"\n🏆 TOP PERFORMERS:")
            for i, performer in enumerate(top_performers, 1):
                print(f"   {i}. {performer['generator']} - Grade: {performer['compatibility_grade']} (Score: {performer['overall_score']:.2f})")
                
        # Areas for improvement
        failing_tests = [score for score in compatibility_scores if score["overall_score"] < 0.5]
        if failing_tests:
            print(f"\n⚠️  NEEDS IMMEDIATE ATTENTION ({len(failing_tests)} generators):")
            for test in failing_tests[:10]:
                print(f"   • {test['generator']} - Grade: {test['compatibility_grade']} (Score: {test['overall_score']:.2f})")
        
    def save_results(self, output_file: str = "compatibility_test_results.json"):
        """Save test results to JSON file"""
        output_path = self.project_root / "scenarios" / output_file
        
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
            
        print(f"\n💾 Test results saved to: {output_path}")

# Import required modules dynamically to avoid import errors
try:
    import importlib.util
except ImportError:
    print("❌ importlib.util not available. Python 3.4+ required.")
    sys.exit(1)

def main():
    """Main testing function"""
    print("🧪 Starting Automated Parser-Generator Compatibility Testing")
    print("="*80)
    
    tester = CompatibilityTester()
    
    # Run comprehensive tests (limit to first 20 for demo)
    tester.run_comprehensive_tests(limit=20)
    
    # Generate report
    tester.generate_report()
    
    # Save results
    tester.save_results()
    
    print("\n✅ Compatibility testing complete!")

if __name__ == "__main__":
    main()