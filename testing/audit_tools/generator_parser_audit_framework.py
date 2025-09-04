#!/usr/bin/env python3
"""
Generator-Parser Audit Framework
================================

Comprehensive audit tool to analyze generator-parser alignment for the Jarvis Coding platform.
Identifies format mismatches, missing parsers, field alignment issues, and prioritizes fixes.

Author: Senior Security Data Engineer
Date: September 2025
"""

import os
import json
import re
import ast
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import subprocess

@dataclass
class GeneratorInfo:
    """Information about a generator"""
    name: str
    path: str
    category: str
    output_format: str  # json, syslog, csv, key_value
    sample_output: Optional[Dict] = None
    function_name: str = ""
    has_star_trek: bool = False
    has_recent_timestamps: bool = False
    enterprise_tier: str = "unknown"  # tier1, tier2, tier3, unknown
    issues: List[str] = field(default_factory=list)

@dataclass
class ParserInfo:
    """Information about a parser"""
    name: str
    path: str
    parser_type: str  # community, sentinelone, marketplace
    expected_format: str  # json, syslog, csv, key_value
    fields_extracted: List[str] = field(default_factory=list)
    ocsf_compliance: float = 0.0
    has_metadata: bool = False
    issues: List[str] = field(default_factory=list)

@dataclass
class AlignmentIssue:
    """Represents a generator-parser alignment issue"""
    generator: str
    parser: str
    issue_type: str  # missing_parser, format_mismatch, field_mismatch, timestamp_issue
    severity: str  # critical, high, medium, low
    description: str
    recommended_fix: str
    complexity: str  # simple, medium, complex
    business_impact: str  # high, medium, low

class GeneratorParserAuditor:
    """Main auditor class for generator-parser alignment analysis"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.generators_path = self.base_path / "event_generators"
        self.parsers_path = self.base_path / "parsers"
        
        # Enterprise vendor tiers for prioritization
        self.enterprise_tiers = {
            "tier1": ["aws", "microsoft", "cisco", "paloalto", "fortinet", "okta"],
            "tier2": ["crowdstrike", "sentinelone", "checkpoint", "zscaler", "proofpoint", "mimecast"],
            "tier3": ["corelight", "extrahop", "vectra", "darktrace", "jamf", "armis"]
        }
        
        self.generators: Dict[str, GeneratorInfo] = {}
        self.parsers: Dict[str, ParserInfo] = {}
        self.alignment_issues: List[AlignmentIssue] = []
        
    def determine_enterprise_tier(self, name: str) -> str:
        """Determine enterprise tier based on vendor name"""
        name_lower = name.lower()
        for tier, vendors in self.enterprise_tiers.items():
            for vendor in vendors:
                if vendor in name_lower:
                    return tier
        return "unknown"
    
    def detect_output_format(self, generator_path: str) -> str:
        """Analyze generator code to determine output format"""
        try:
            with open(generator_path, 'r') as f:
                content = f.read()
            
            # Look for format indicators
            if 'syslog' in content.lower() or '<priority>' in content:
                return "syslog"
            elif 'csv' in content.lower() or '.join(' in content:
                return "csv"
            elif 'key=' in content or 'value=' in content:
                return "key_value"
            else:
                return "json"  # default assumption
                
        except Exception as e:
            print(f"Error analyzing {generator_path}: {e}")
            return "unknown"
    
    def extract_parser_format(self, parser_path: str) -> str:
        """Extract expected input format from parser configuration"""
        try:
            with open(parser_path, 'r') as f:
                parser_data = json.load(f)
            
            # Look for format indicators in parser
            if 'syslog' in str(parser_data).lower():
                return "syslog"
            elif 'csv' in str(parser_data).lower():
                return "csv"
            elif 'key_value' in str(parser_data).lower() or 'keyvalue' in str(parser_data).lower():
                return "key_value"
            else:
                return "json"  # default assumption
                
        except Exception as e:
            print(f"Error analyzing parser {parser_path}: {e}")
            return "unknown"
    
    def check_star_trek_integration(self, content: str) -> bool:
        """Check if generator has Star Trek theme integration"""
        star_trek_indicators = [
            'picard', 'enterprise', 'starfleet', 'federation', 'klingon',
            'romulan', 'vulcan', 'borg', 'warp', 'trek'
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in star_trek_indicators)
    
    def check_recent_timestamps(self, content: str) -> bool:
        """Check if generator uses recent timestamps (last 10 minutes)"""
        recent_indicators = [
            'timedelta', 'minutes=', 'now()', 'datetime.now',
            'recent', 'last.*minutes'
        ]
        return any(re.search(indicator, content, re.IGNORECASE) for indicator in recent_indicators)
    
    def scan_generators(self) -> None:
        """Scan all generators and extract information"""
        print("Scanning generators...")
        
        for category_path in self.generators_path.iterdir():
            if not category_path.is_dir() or category_path.name == "shared":
                continue
                
            category = category_path.name
            for gen_file in category_path.glob("*.py"):
                if gen_file.name.startswith("__"):
                    continue
                
                generator_name = gen_file.stem
                
                try:
                    # Read generator content
                    with open(gen_file, 'r') as f:
                        content = f.read()
                    
                    # Extract information
                    output_format = self.detect_output_format(str(gen_file))
                    has_star_trek = self.check_star_trek_integration(content)
                    has_recent_timestamps = self.check_recent_timestamps(content)
                    enterprise_tier = self.determine_enterprise_tier(generator_name)
                    
                    # Find function name
                    function_match = re.search(r'def (\w+).*log.*\(', content)
                    function_name = function_match.group(1) if function_match else f"{generator_name}_log"
                    
                    generator_info = GeneratorInfo(
                        name=generator_name,
                        path=str(gen_file),
                        category=category,
                        output_format=output_format,
                        function_name=function_name,
                        has_star_trek=has_star_trek,
                        has_recent_timestamps=has_recent_timestamps,
                        enterprise_tier=enterprise_tier
                    )
                    
                    self.generators[generator_name] = generator_info
                    
                except Exception as e:
                    print(f"Error processing generator {gen_file}: {e}")
    
    def scan_parsers(self) -> None:
        """Scan all parsers and extract information"""
        print("Scanning parsers...")
        
        for parser_type in ["community", "sentinelone"]:
            parser_type_path = self.parsers_path / parser_type
            if not parser_type_path.exists():
                continue
                
            for parser_dir in parser_type_path.iterdir():
                if not parser_dir.is_dir():
                    continue
                
                # Find parser JSON files
                json_files = list(parser_dir.glob("*.json"))
                if not json_files:
                    continue
                
                parser_name = parser_dir.name.replace("-latest", "")
                parser_file = json_files[0]  # Use first JSON file
                
                try:
                    expected_format = self.extract_parser_format(str(parser_file))
                    
                    # Check for metadata
                    has_metadata = (parser_dir / "metadata.yaml").exists()
                    
                    parser_info = ParserInfo(
                        name=parser_name,
                        path=str(parser_file),
                        parser_type=parser_type,
                        expected_format=expected_format,
                        has_metadata=has_metadata
                    )
                    
                    self.parsers[parser_name] = parser_info
                    
                except Exception as e:
                    print(f"Error processing parser {parser_dir}: {e}")
    
    def find_generator_parser_matches(self) -> Dict[str, List[str]]:
        """Find potential matches between generators and parsers"""
        matches = defaultdict(list)
        
        for gen_name in self.generators.keys():
            # Direct name match
            for parser_name in self.parsers.keys():
                if self.names_match(gen_name, parser_name):
                    matches[gen_name].append(parser_name)
        
        return dict(matches)
    
    def names_match(self, gen_name: str, parser_name: str) -> bool:
        """Check if generator and parser names indicate they should work together"""
        # Normalize names for comparison
        gen_normalized = gen_name.lower().replace("_", "").replace("-", "")
        parser_normalized = parser_name.lower().replace("_", "").replace("-", "")
        
        # Direct match
        if gen_normalized == parser_normalized:
            return True
        
        # Vendor + product match
        gen_parts = gen_name.split("_")
        parser_parts = parser_name.split("_")
        
        if len(gen_parts) >= 2 and len(parser_parts) >= 2:
            if gen_parts[0] == parser_parts[0] and gen_parts[1] in parser_parts[1]:
                return True
        
        # Partial matches for known patterns
        if "cisco" in gen_name and "cisco" in parser_name:
            return True
        if "aws" in gen_name and "aws" in parser_name:
            return True
        if "microsoft" in gen_name and "microsoft" in parser_name:
            return True
        
        return False
    
    def analyze_alignment(self) -> None:
        """Analyze generator-parser alignment and identify issues"""
        print("Analyzing generator-parser alignment...")
        
        matches = self.find_generator_parser_matches()
        
        # Check for missing parsers
        for gen_name, generator in self.generators.items():
            if gen_name not in matches:
                issue = AlignmentIssue(
                    generator=gen_name,
                    parser="MISSING",
                    issue_type="missing_parser",
                    severity="critical" if generator.enterprise_tier == "tier1" else "high",
                    description=f"No parser found for generator {gen_name}",
                    recommended_fix=f"Create or identify existing parser for {gen_name}",
                    complexity="medium",
                    business_impact="high" if generator.enterprise_tier == "tier1" else "medium"
                )
                self.alignment_issues.append(issue)
        
        # Check format mismatches
        for gen_name, parser_names in matches.items():
            generator = self.generators[gen_name]
            
            for parser_name in parser_names:
                parser = self.parsers[parser_name]
                
                if generator.output_format != parser.expected_format:
                    issue = AlignmentIssue(
                        generator=gen_name,
                        parser=parser_name,
                        issue_type="format_mismatch",
                        severity="high",
                        description=f"Format mismatch: generator produces {generator.output_format}, parser expects {parser.expected_format}",
                        recommended_fix=f"Update generator to produce {parser.expected_format} format",
                        complexity="medium",
                        business_impact="high" if generator.enterprise_tier == "tier1" else "medium"
                    )
                    self.alignment_issues.append(issue)
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        print("Generating audit report...")
        
        # Count statistics
        total_generators = len(self.generators)
        total_parsers = len(self.parsers)
        
        # Generator statistics by category
        category_stats = defaultdict(lambda: {"count": 0, "star_trek": 0, "recent_timestamps": 0})
        for gen in self.generators.values():
            category_stats[gen.category]["count"] += 1
            if gen.has_star_trek:
                category_stats[gen.category]["star_trek"] += 1
            if gen.has_recent_timestamps:
                category_stats[gen.category]["recent_timestamps"] += 1
        
        # Issue statistics
        issue_stats = defaultdict(int)
        for issue in self.alignment_issues:
            issue_stats[issue.issue_type] += 1
            issue_stats[f"severity_{issue.severity}"] += 1
        
        # Enterprise tier breakdown
        tier_stats = defaultdict(int)
        for gen in self.generators.values():
            tier_stats[gen.enterprise_tier] += 1
        
        # Top priority fixes (Tier 1 vendors with critical/high severity)
        top_priority = [
            issue for issue in self.alignment_issues
            if self.generators[issue.generator].enterprise_tier == "tier1"
            and issue.severity in ["critical", "high"]
        ]
        
        report = {
            "audit_summary": {
                "total_generators": total_generators,
                "total_parsers": total_parsers,
                "total_alignment_issues": len(self.alignment_issues),
                "generators_with_parsers": sum(1 for g in self.generators if g in self.find_generator_parser_matches()),
                "generators_without_parsers": sum(1 for g in self.generators if g not in self.find_generator_parser_matches())
            },
            "category_breakdown": dict(category_stats),
            "enterprise_tier_stats": dict(tier_stats),
            "issue_statistics": dict(issue_stats),
            "top_priority_fixes": [
                {
                    "generator": issue.generator,
                    "parser": issue.parser,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommended_fix": issue.recommended_fix,
                    "business_impact": issue.business_impact,
                    "enterprise_tier": self.generators[issue.generator].enterprise_tier
                }
                for issue in top_priority[:15]  # Top 15 priority fixes
            ],
            "all_alignment_issues": [
                {
                    "generator": issue.generator,
                    "parser": issue.parser,
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommended_fix": issue.recommended_fix,
                    "complexity": issue.complexity,
                    "business_impact": issue.business_impact
                }
                for issue in self.alignment_issues
            ],
            "generator_details": {
                name: {
                    "path": gen.path,
                    "category": gen.category,
                    "output_format": gen.output_format,
                    "has_star_trek": gen.has_star_trek,
                    "has_recent_timestamps": gen.has_recent_timestamps,
                    "enterprise_tier": gen.enterprise_tier,
                    "function_name": gen.function_name
                }
                for name, gen in self.generators.items()
            },
            "parser_details": {
                name: {
                    "path": parser.path,
                    "parser_type": parser.parser_type,
                    "expected_format": parser.expected_format,
                    "has_metadata": parser.has_metadata
                }
                for name, parser in self.parsers.items()
            }
        }
        
        return report
    
    def run_audit(self) -> Dict[str, Any]:
        """Run complete audit process"""
        print("Starting comprehensive generator-parser audit...")
        
        self.scan_generators()
        self.scan_parsers()
        self.analyze_alignment()
        
        return self.generate_report()

def main():
    """Main execution function"""
    base_path = "/Users/nathanial.smalley/projects/jarvis_coding"
    
    auditor = GeneratorParserAuditor(base_path)
    report = auditor.run_audit()
    
    # Save report
    report_path = Path(base_path) / "generator_parser_audit_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print(f"\n{'='*60}")
    print("GENERATOR-PARSER AUDIT SUMMARY")
    print(f"{'='*60}")
    print(f"Total Generators: {report['audit_summary']['total_generators']}")
    print(f"Total Parsers: {report['audit_summary']['total_parsers']}")
    print(f"Generators with Parsers: {report['audit_summary']['generators_with_parsers']}")
    print(f"Generators without Parsers: {report['audit_summary']['generators_without_parsers']}")
    print(f"Total Alignment Issues: {report['audit_summary']['total_alignment_issues']}")
    
    print(f"\nTop Priority Fixes (Tier 1 Vendors):")
    for i, fix in enumerate(report['top_priority_fixes'][:10], 1):
        print(f"{i:2d}. {fix['generator']} -> {fix['issue_type']} ({fix['severity']})")
    
    print(f"\nIssue Breakdown:")
    for issue_type, count in report['issue_statistics'].items():
        if not issue_type.startswith('severity_'):
            print(f"  {issue_type}: {count}")
    
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    main()