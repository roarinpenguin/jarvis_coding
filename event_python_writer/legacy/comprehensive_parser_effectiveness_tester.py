#!/usr/bin/env python3
"""
Comprehensive Parser Effectiveness Tester
Combines field matching, generator testing, and parser configuration analysis
without requiring SDL API access
"""

import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Set, Any
from datetime import datetime
import traceback

class ComprehensiveParserEffectivenessTester:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.parsers_dir = self.base_dir / "parsers" / "community"
        self.generators_dir = Path(__file__).parent
        self.results = {}
        
    def get_all_parsers(self) -> List[str]:
        """Get all parser directories."""
        parsers = []
        for parser_path in self.parsers_dir.glob("*-latest"):
            if parser_path.is_dir():
                parser_name = parser_path.name.replace("-latest", "")
                parsers.append(parser_name)
        return sorted(parsers)
    
    def find_matching_generator(self, parser_name: str) -> Path:
        """Find the corresponding event generator for a parser."""
        # Direct mapping first
        generator_path = self.generators_dir / f"{parser_name}.py"
        if generator_path.exists():
            return generator_path
            
        # Try without _logs suffix
        if parser_name.endswith("_logs"):
            base_name = parser_name[:-5]
            generator_path = self.generators_dir / f"{base_name}.py"
            if generator_path.exists():
                return generator_path
        
        # Try common variations
        variations = [
            parser_name.replace("_", ""),
            parser_name.replace("_logs", ""),
            parser_name.replace("_", "_") if "_" in parser_name else parser_name + "_logs"
        ]
        
        for variation in variations:
            generator_path = self.generators_dir / f"{variation}.py"
            if generator_path.exists():
                return generator_path
                
        return None
    
    def test_generator(self, generator_path: Path) -> Dict:
        """Test if generator works and analyze output."""
        try:
            spec = importlib.util.spec_from_file_location("generator", generator_path)
            generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generator)
            
            # Find the main log generation function
            generator_name = generator_path.stem
            function_name = f"{generator_name}_log"
            
            if not hasattr(generator, function_name):
                return {"status": "no_function", "function_name": function_name}
            
            # Test function
            log_function = getattr(generator, function_name)
            event = log_function()
            
            if not isinstance(event, dict):
                return {
                    "status": "invalid_output", 
                    "output_type": type(event).__name__,
                    "output": str(event)[:200]
                }
            
            return {
                "status": "success",
                "event_fields": list(event.keys()),
                "field_count": len(event.keys()),
                "sample_event": {k: str(v)[:100] for k, v in list(event.items())[:5]}
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def load_parser_config(self, parser_name: str) -> Dict:
        """Load parser configuration."""
        try:
            parser_path = self.parsers_dir / f"{parser_name}-latest"
            json_files = list(parser_path.glob("*.json"))
            if json_files:
                with open(json_files[0], 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_parser_config(self, parser_config: Dict) -> Dict:
        """Analyze parser configuration for field extraction capabilities."""
        analysis = {
            "has_formats": "formats" in parser_config,
            "format_count": 0,
            "rewrite_count": 0,
            "expected_fields": set(),
            "ocsf_compliant": False,
            "status": "unknown"
        }
        
        if "formats" not in parser_config:
            analysis["status"] = "no_formats"
            return analysis
            
        try:
            formats = parser_config["formats"]
            analysis["format_count"] = len(formats)
            
            total_rewrites = 0
            for fmt in formats:
                if "rewrites" in fmt:
                    rewrites = fmt["rewrites"]
                    total_rewrites += len(rewrites)
                    
                    for rewrite in rewrites:
                        if "output" in rewrite:
                            analysis["expected_fields"].add(rewrite["output"])
            
            analysis["rewrite_count"] = total_rewrites
            analysis["expected_field_count"] = len(analysis["expected_fields"])
            
            # Check OCSF compliance indicators
            expected_fields_list = list(analysis["expected_fields"])
            ocsf_indicators = [
                "class_uid", "activity_id", "category_uid", "severity_id",
                "time", "start_time", "end_time", "actor", "src_endpoint", 
                "dst_endpoint", "observables"
            ]
            
            ocsf_matches = sum(1 for field in expected_fields_list 
                             if any(indicator in field.lower() for indicator in ocsf_indicators))
            analysis["ocsf_compliant"] = ocsf_matches >= 3
            analysis["ocsf_field_count"] = ocsf_matches
            
            analysis["status"] = "success"
            
        except Exception as e:
            analysis["status"] = "error"
            analysis["error"] = str(e)
            
        # Convert set to list for JSON serialization
        analysis["expected_fields"] = list(analysis["expected_fields"])
        return analysis
    
    def calculate_field_match_percentage(self, generator_fields: List[str], 
                                       expected_fields: List[str]) -> Dict:
        """Calculate field matching percentage between generator and parser."""
        if not expected_fields:
            return {
                "match_percentage": 0.0,
                "matched_fields": [],
                "missing_fields": [],
                "extra_fields": generator_fields
            }
            
        if not generator_fields:
            return {
                "match_percentage": 0.0,
                "matched_fields": [],
                "missing_fields": expected_fields,
                "extra_fields": []
            }
        
        generator_set = set(generator_fields)
        expected_set = set(expected_fields)
        
        matched = generator_set.intersection(expected_set)
        missing = expected_set - generator_set
        extra = generator_set - expected_set
        
        match_percentage = (len(matched) / len(expected_set)) * 100
        
        return {
            "match_percentage": round(match_percentage, 1),
            "matched_fields": list(matched),
            "missing_fields": list(missing),
            "extra_fields": list(extra),
            "generator_field_count": len(generator_fields),
            "expected_field_count": len(expected_fields)
        }
    
    def assess_parser_effectiveness(self, parser_name: str) -> Dict:
        """Comprehensive effectiveness assessment for a single parser."""
        print(f"🔍 Assessing: {parser_name}")
        
        assessment = {
            "parser_name": parser_name,
            "timestamp": datetime.now().isoformat(),
            "generator": {"status": "not_found"},
            "parser_config": {"status": "not_found"},
            "field_matching": {"status": "no_data"},
            "effectiveness_score": 0.0,
            "recommendations": []
        }
        
        # 1. Test Generator
        generator_path = self.find_matching_generator(parser_name)
        if generator_path:
            assessment["generator"] = self.test_generator(generator_path)
            assessment["generator"]["path"] = str(generator_path)
        else:
            assessment["recommendations"].append("Create missing event generator")
        
        # 2. Analyze Parser Config
        parser_config = self.load_parser_config(parser_name)
        if parser_config and "error" not in parser_config:
            assessment["parser_config"] = self.analyze_parser_config(parser_config)
        else:
            assessment["recommendations"].append("Fix parser configuration")
        
        # 3. Field Matching Analysis
        if (assessment["generator"]["status"] == "success" and 
            assessment["parser_config"]["status"] == "success"):
            
            generator_fields = assessment["generator"]["event_fields"]
            expected_fields = assessment["parser_config"]["expected_fields"]
            
            assessment["field_matching"] = self.calculate_field_match_percentage(
                generator_fields, expected_fields
            )
            assessment["field_matching"]["status"] = "success"
        
        # 4. Calculate Effectiveness Score (0-100)
        score_components = []
        
        # Generator working (25 points)
        if assessment["generator"]["status"] == "success":
            score_components.append(25)
        
        # Parser config valid (25 points) 
        if assessment["parser_config"]["status"] == "success":
            score_components.append(25)
        
        # Field matching (50 points based on percentage)
        if assessment["field_matching"]["status"] == "success":
            match_score = (assessment["field_matching"]["match_percentage"] / 100) * 50
            score_components.append(match_score)
        
        assessment["effectiveness_score"] = round(sum(score_components), 1)
        
        # 5. Generate Recommendations
        if assessment["field_matching"]["status"] == "success":
            match_pct = assessment["field_matching"]["match_percentage"]
            if match_pct < 50:
                assessment["recommendations"].append(
                    f"Low field matching ({match_pct}%) - review parser field mappings"
                )
            elif match_pct < 80:
                assessment["recommendations"].append(
                    f"Medium field matching ({match_pct}%) - optimize field extractions"
                )
        
        if assessment["parser_config"]["status"] == "success":
            if not assessment["parser_config"]["ocsf_compliant"]:
                assessment["recommendations"].append("Enhance OCSF compliance")
        
        return assessment
    
    def test_all_parsers(self) -> Dict:
        """Test all parsers comprehensively."""
        print("🚀 Starting comprehensive parser effectiveness testing...\n")
        
        all_parsers = self.get_all_parsers()
        print(f"📋 Found {len(all_parsers)} parsers to test\n")
        
        results = {}
        
        # Stats tracking
        working_generators = 0
        valid_configs = 0
        high_effectiveness = 0
        medium_effectiveness = 0
        
        for i, parser_name in enumerate(all_parsers, 1):
            print(f"[{i:3d}/{len(all_parsers)}] ", end="")
            
            assessment = self.assess_parser_effectiveness(parser_name)
            results[parser_name] = assessment
            
            # Update stats
            if assessment["generator"]["status"] == "success":
                working_generators += 1
                
            if assessment["parser_config"]["status"] == "success":
                valid_configs += 1
                
            score = assessment["effectiveness_score"]
            if score >= 80:
                high_effectiveness += 1
                print(" ✅")
            elif score >= 60:
                medium_effectiveness += 1 
                print(" ⚠️")
            else:
                print(" ❌")
        
        # Summary statistics
        summary = {
            "total_parsers": len(all_parsers),
            "working_generators": working_generators,
            "valid_configs": valid_configs,
            "high_effectiveness": high_effectiveness,
            "medium_effectiveness": medium_effectiveness,
            "low_effectiveness": len(all_parsers) - high_effectiveness - medium_effectiveness,
            "avg_effectiveness": round(
                sum(r["effectiveness_score"] for r in results.values()) / len(results), 1
            ) if results else 0
        }
        
        print(f"\n✅ Assessment complete!")
        print(f"📊 {working_generators}/{len(all_parsers)} working generators")
        print(f"📋 {valid_configs}/{len(all_parsers)} valid configurations")
        print(f"🎯 {high_effectiveness} high effectiveness parsers (≥80%)")
        print(f"⚠️ {medium_effectiveness} medium effectiveness parsers (60-79%)")
        print(f"📈 Average effectiveness: {summary['avg_effectiveness']}%")
        
        return {
            "summary": summary,
            "results": results,
            "test_timestamp": datetime.now().isoformat()
        }
    
    def generate_effectiveness_report(self, results: Dict) -> str:
        """Generate comprehensive effectiveness report."""
        summary = results["summary"]
        assessments = results["results"]
        
        report = "# Comprehensive Parser Effectiveness Report\n\n"
        report += f"**Test Date**: {results['test_timestamp']}\n"
        report += f"**Parsers Tested**: {summary['total_parsers']}\n\n"
        
        # Executive Summary
        report += "## Executive Summary\n\n"
        report += f"- **Working Generators**: {summary['working_generators']}/{summary['total_parsers']} ({(summary['working_generators']/summary['total_parsers']*100):.1f}%)\n"
        report += f"- **Valid Configurations**: {summary['valid_configs']}/{summary['total_parsers']} ({(summary['valid_configs']/summary['total_parsers']*100):.1f}%)\n"
        report += f"- **High Effectiveness** (≥80%): {summary['high_effectiveness']}\n"
        report += f"- **Medium Effectiveness** (60-79%): {summary['medium_effectiveness']}\n"
        report += f"- **Low Effectiveness** (<60%): {summary['low_effectiveness']}\n"
        report += f"- **Average Effectiveness Score**: {summary['avg_effectiveness']}%\n\n"
        
        # High Effectiveness Parsers
        high_eff = [a for a in assessments.values() if a["effectiveness_score"] >= 80]
        high_eff.sort(key=lambda x: x["effectiveness_score"], reverse=True)
        
        if high_eff:
            report += f"## High Effectiveness Parsers ({len(high_eff)} parsers)\n\n"
            report += "| Parser | Score | Field Match % | OCSF | Recommendations |\n"
            report += "|--------|-------|---------------|------|----------------|\n"
            
            for assessment in high_eff:
                name = assessment["parser_name"]
                score = assessment["effectiveness_score"]
                
                field_match = "N/A"
                if assessment["field_matching"]["status"] == "success":
                    field_match = f"{assessment['field_matching']['match_percentage']}%"
                
                ocsf = "❌"
                if (assessment["parser_config"]["status"] == "success" and 
                    assessment["parser_config"]["ocsf_compliant"]):
                    ocsf = "✅"
                
                recommendations = "; ".join(assessment["recommendations"][:2]) or "None"
                
                report += f"| {name} | {score}% | {field_match} | {ocsf} | {recommendations} |\n"
        
        # Top Issues
        report += "\n## Most Common Issues\n\n"
        issue_counts = {}
        for assessment in assessments.values():
            for rec in assessment["recommendations"]:
                issue_counts[rec] = issue_counts.get(rec, 0) + 1
        
        for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            report += f"- **{issue}**: {count} parsers\n"
        
        return report

if __name__ == "__main__":
    tester = ComprehensiveParserEffectivenessTester()
    results = tester.test_all_parsers()
    
    # Save results
    with open("comprehensive_parser_effectiveness.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = tester.generate_effectiveness_report(results)
    with open("comprehensive_parser_effectiveness_report.md", "w") as f:
        f.write(report)
    
    print(f"\n📄 Results saved to comprehensive_parser_effectiveness.json")
    print(f"📄 Report saved to comprehensive_parser_effectiveness_report.md")