#!/usr/bin/env python3
"""
Comprehensive Generator-Parser Alignment Audit
Analyzes all 106+ generators against their parsers to identify alignment issues
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import importlib.util

class GeneratorParserAuditor:
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.generators_path = self.base_path / "event_generators"
        self.parsers_path = self.base_path / "parsers"
        self.audit_results = {
            "audit_timestamp": datetime.now().isoformat(),
            "total_generators": 0,
            "total_parsers": 0,
            "alignment_issues": [],
            "critical_issues": [],
            "high_priority_issues": [],
            "medium_priority_issues": [],
            "low_priority_issues": [],
            "no_parser_found": [],
            "format_mismatches": [],
            "field_mismatches": [],
            "working_pairs": [],
            "enterprise_priority": []
        }
        
        # Enterprise vendors (high priority)
        self.enterprise_vendors = [
            'aws', 'azure', 'microsoft', 'cisco', 'paloalto', 'fortinet', 
            'checkpoint', 'crowdstrike', 'sentinelone', 'okta', 'zscaler',
            'google', 'vmware', 'cyberark', 'proofpoint', 'mimecast'
        ]

    def load_generator(self, generator_path: Path) -> Optional[Dict[str, Any]]:
        """Load and analyze a generator file"""
        try:
            spec = importlib.util.spec_from_file_location("generator", generator_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Try to find the main function (usually ends with _log())
            generator_functions = []
            for attr_name in dir(module):
                if callable(getattr(module, attr_name)) and attr_name.endswith('_log'):
                    generator_functions.append(attr_name)
            
            if not generator_functions:
                return None
                
            # Use the first generator function found
            generator_func = getattr(module, generator_functions[0])
            sample_event = generator_func()
            
            return {
                'file_path': str(generator_path),
                'function_name': generator_functions[0],
                'sample_event': sample_event,
                'event_format': self.detect_format(sample_event)
            }
        except Exception as e:
            return {
                'file_path': str(generator_path),
                'error': str(e),
                'event_format': 'ERROR'
            }

    def detect_format(self, event: Any) -> str:
        """Detect the format of the generated event"""
        if isinstance(event, dict):
            return "JSON"
        elif isinstance(event, str):
            # Check for different string formats
            if event.startswith('<') and '>' in event:
                return "SYSLOG"
            elif '=' in event and (',' in event or ' ' in event):
                return "KEY_VALUE"
            elif ',' in event and '\n' not in event:
                return "CSV"
            elif '\n' in event and '=' in event:
                return "MULTI_LINE_KEY_VALUE"
            else:
                return "RAW_STRING"
        else:
            return "UNKNOWN"

    def find_parser_for_generator(self, generator_name: str) -> List[Path]:
        """Find corresponding parsers for a generator"""
        parsers = []
        
        # Clean generator name for matching
        clean_name = generator_name.replace('_', '').lower()
        
        # Search in community parsers
        community_path = self.parsers_path / "community"
        if community_path.exists():
            for parser_dir in community_path.iterdir():
                if parser_dir.is_dir():
                    parser_name = parser_dir.name.replace('_', '').replace('-', '').lower()
                    if self.names_match(clean_name, parser_name):
                        json_files = list(parser_dir.glob("*.json"))
                        if json_files:
                            parsers.extend(json_files)
        
        # Search in SentinelOne marketplace parsers
        sentinelone_path = self.parsers_path / "sentinelone"
        if sentinelone_path.exists():
            for parser_dir in sentinelone_path.iterdir():
                if parser_dir.is_dir():
                    parser_name = parser_dir.name.replace('_', '').replace('-', '').lower()
                    if self.names_match(clean_name, parser_name):
                        json_files = list(parser_dir.glob("*.json"))
                        if json_files:
                            parsers.extend(json_files)
        
        return parsers

    def names_match(self, generator_name: str, parser_name: str) -> bool:
        """Check if generator and parser names match"""
        # Direct match
        if generator_name in parser_name or parser_name in generator_name:
            return True
        
        # Split and check components
        gen_parts = set(generator_name.split('_'))
        parser_parts = set(parser_name.split('_'))
        
        # Check for significant overlap
        overlap = gen_parts.intersection(parser_parts)
        return len(overlap) >= 2 or (len(overlap) >= 1 and len(gen_parts) <= 2)

    def analyze_parser(self, parser_path: Path) -> Dict[str, Any]:
        """Analyze a parser file"""
        try:
            with open(parser_path, 'r', encoding='utf-8') as f:
                parser_config = json.load(f)
            
            return {
                'file_path': str(parser_path),
                'config': parser_config,
                'expected_format': self.detect_parser_format(parser_config),
                'fields': self.extract_parser_fields(parser_config)
            }
        except Exception as e:
            return {
                'file_path': str(parser_path),
                'error': str(e)
            }

    def detect_parser_format(self, parser_config: Dict) -> str:
        """Detect expected input format from parser configuration"""
        if 'input' in parser_config:
            input_config = parser_config['input']
            if 'type' in input_config:
                return input_config['type'].upper()
        
        # Look for format indicators in the configuration
        config_str = json.dumps(parser_config).lower()
        if 'syslog' in config_str:
            return 'SYSLOG'
        elif 'json' in config_str:
            return 'JSON'
        elif 'csv' in config_str:
            return 'CSV'
        elif 'key' in config_str and 'value' in config_str:
            return 'KEY_VALUE'
        
        return 'UNKNOWN'

    def extract_parser_fields(self, parser_config: Dict) -> List[str]:
        """Extract expected fields from parser configuration"""
        fields = []
        
        def extract_fields_recursive(obj, prefix=''):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key in ['field', 'fields', 'map', 'mapping']:
                        if isinstance(value, str):
                            fields.append(f"{prefix}{value}")
                        elif isinstance(value, list):
                            fields.extend([f"{prefix}{v}" for v in value if isinstance(v, str)])
                    else:
                        extract_fields_recursive(value, f"{prefix}{key}.")
            elif isinstance(obj, list):
                for item in obj:
                    extract_fields_recursive(item, prefix)
        
        extract_fields_recursive(parser_config)
        return list(set(fields))

    def prioritize_issue(self, issue: Dict[str, Any]) -> str:
        """Prioritize issues based on severity and enterprise importance"""
        generator_name = issue['generator_name'].lower()
        
        # Check if enterprise vendor
        is_enterprise = any(vendor in generator_name for vendor in self.enterprise_vendors)
        
        # Critical: No parser exists for enterprise vendors
        if issue['issue_type'] == 'no_parser' and is_enterprise:
            return 'critical'
        
        # Critical: Format mismatch for enterprise vendors
        if issue['issue_type'] == 'format_mismatch' and is_enterprise:
            return 'critical'
        
        # High: Any format mismatch
        if issue['issue_type'] == 'format_mismatch':
            return 'high'
        
        # High: No parser for any vendor
        if issue['issue_type'] == 'no_parser':
            return 'high'
        
        # Medium: Field mismatches
        if issue['issue_type'] == 'field_mismatch':
            return 'medium'
        
        # Low: Other issues
        return 'low'

    def audit_all_generators(self):
        """Perform comprehensive audit of all generators"""
        print("🔍 Starting comprehensive generator-parser audit...")
        
        # Find all generator files
        generator_files = []
        for category_dir in self.generators_path.iterdir():
            if category_dir.is_dir() and category_dir.name != 'shared':
                generator_files.extend(list(category_dir.glob("*.py")))
        
        self.audit_results['total_generators'] = len(generator_files)
        print(f"📊 Found {len(generator_files)} generators to audit")
        
        # Analyze each generator
        for i, gen_file in enumerate(generator_files, 1):
            print(f"🔍 [{i:3d}/{len(generator_files)}] Analyzing {gen_file.name}...")
            
            generator_name = gen_file.stem
            generator_info = self.load_generator(gen_file)
            
            if not generator_info or 'error' in generator_info:
                issue = {
                    'generator_name': generator_name,
                    'generator_path': str(gen_file),
                    'issue_type': 'generator_error',
                    'description': f"Failed to load generator: {generator_info.get('error', 'Unknown error')}",
                    'severity': 'medium'
                }
                self.audit_results['alignment_issues'].append(issue)
                continue
            
            # Find corresponding parsers
            parser_paths = self.find_parser_for_generator(generator_name)
            
            if not parser_paths:
                issue = {
                    'generator_name': generator_name,
                    'generator_path': str(gen_file),
                    'issue_type': 'no_parser',
                    'description': f"No parser found for generator {generator_name}",
                    'generator_format': generator_info['event_format']
                }
                issue['severity'] = self.prioritize_issue(issue)
                self.audit_results['alignment_issues'].append(issue)
                self.audit_results['no_parser_found'].append(issue)
                continue
            
            # Analyze each parser match
            for parser_path in parser_paths:
                parser_info = self.analyze_parser(parser_path)
                
                if 'error' in parser_info:
                    continue
                
                # Check format alignment
                gen_format = generator_info['event_format']
                parser_format = parser_info['expected_format']
                
                if gen_format != parser_format and not self.formats_compatible(gen_format, parser_format):
                    issue = {
                        'generator_name': generator_name,
                        'generator_path': str(gen_file),
                        'parser_path': str(parser_path),
                        'issue_type': 'format_mismatch',
                        'description': f"Format mismatch: generator produces {gen_format}, parser expects {parser_format}",
                        'generator_format': gen_format,
                        'parser_format': parser_format
                    }
                    issue['severity'] = self.prioritize_issue(issue)
                    self.audit_results['alignment_issues'].append(issue)
                    self.audit_results['format_mismatches'].append(issue)
                else:
                    # Formats match - this is a working pair
                    working_pair = {
                        'generator_name': generator_name,
                        'generator_path': str(gen_file),
                        'parser_path': str(parser_path),
                        'generator_format': gen_format,
                        'parser_format': parser_format
                    }
                    self.audit_results['working_pairs'].append(working_pair)

    def formats_compatible(self, gen_format: str, parser_format: str) -> bool:
        """Check if generator and parser formats are compatible"""
        # Same format
        if gen_format == parser_format:
            return True
        
        # Compatible formats
        compatible_pairs = [
            ('JSON', 'UNKNOWN'),
            ('SYSLOG', 'UNKNOWN'),
            ('KEY_VALUE', 'MULTI_LINE_KEY_VALUE'),
            ('RAW_STRING', 'UNKNOWN')
        ]
        
        return (gen_format, parser_format) in compatible_pairs or (parser_format, gen_format) in compatible_pairs

    def categorize_issues(self):
        """Categorize issues by priority"""
        for issue in self.audit_results['alignment_issues']:
            severity = issue.get('severity', 'low')
            
            if severity == 'critical':
                self.audit_results['critical_issues'].append(issue)
            elif severity == 'high':
                self.audit_results['high_priority_issues'].append(issue)
            elif severity == 'medium':
                self.audit_results['medium_priority_issues'].append(issue)
            else:
                self.audit_results['low_priority_issues'].append(issue)
            
            # Track enterprise issues separately
            generator_name = issue['generator_name'].lower()
            if any(vendor in generator_name for vendor in self.enterprise_vendors):
                self.audit_results['enterprise_priority'].append(issue)

    def generate_report(self) -> str:
        """Generate comprehensive audit report"""
        total_issues = len(self.audit_results['alignment_issues'])
        total_generators = self.audit_results['total_generators']
        working_pairs = len(self.audit_results['working_pairs'])
        
        report = f"""
# 🔍 COMPREHENSIVE GENERATOR-PARSER ALIGNMENT AUDIT REPORT
**Generated:** {self.audit_results['audit_timestamp']}

## 📊 EXECUTIVE SUMMARY
- **Total Generators Analyzed:** {total_generators}
- **Working Generator-Parser Pairs:** {working_pairs}
- **Total Alignment Issues Found:** {total_issues}
- **Success Rate:** {(working_pairs / (working_pairs + total_issues) * 100):.1f}%

## 🚨 ISSUES BY SEVERITY

### CRITICAL ISSUES ({len(self.audit_results['critical_issues'])})
**Enterprise vendors with no parser or major format mismatch**
"""
        
        for issue in self.audit_results['critical_issues'][:10]:  # Top 10 critical
            report += f"- **{issue['generator_name']}**: {issue['description']}\n"
        
        if len(self.audit_results['critical_issues']) > 10:
            report += f"- ... and {len(self.audit_results['critical_issues']) - 10} more\n"
        
        report += f"""
### HIGH PRIORITY ISSUES ({len(self.audit_results['high_priority_issues'])})
**Format mismatches and missing parsers**
"""
        
        for issue in self.audit_results['high_priority_issues'][:10]:  # Top 10 high
            report += f"- **{issue['generator_name']}**: {issue['description']}\n"
        
        if len(self.audit_results['high_priority_issues']) > 10:
            report += f"- ... and {len(self.audit_results['high_priority_issues']) - 10} more\n"
        
        report += f"""
### MEDIUM PRIORITY ISSUES ({len(self.audit_results['medium_priority_issues'])})
### LOW PRIORITY ISSUES ({len(self.audit_results['low_priority_issues'])})

## 🎯 ENTERPRISE PRIORITY FIXES ({len(self.audit_results['enterprise_priority'])})
**Issues affecting enterprise vendors (AWS, Microsoft, Cisco, etc.)**
"""
        
        for issue in self.audit_results['enterprise_priority']:
            report += f"- **{issue['generator_name']}** ({issue['severity'].upper()}): {issue['description']}\n"
        
        report += f"""
## 📈 BREAKDOWN BY ISSUE TYPE
- **No Parser Found:** {len(self.audit_results['no_parser_found'])} generators
- **Format Mismatches:** {len(self.audit_results['format_mismatches'])} pairs
- **Field Mismatches:** {len(self.audit_results['field_mismatches'])} pairs

## ✅ TOP 10 SUCCESSFUL PAIRS
"""
        
        for pair in self.audit_results['working_pairs'][:10]:
            report += f"- **{pair['generator_name']}**: {pair['generator_format']} → Parser\n"
        
        report += f"""
## 🔧 RECOMMENDED FIX ORDER

### Phase 1: Critical Fixes ({len(self.audit_results['critical_issues'])})
Focus on enterprise vendors with no parsers or major format mismatches.

### Phase 2: High Priority Fixes ({len(self.audit_results['high_priority_issues'])})
Address format mismatches and missing parsers for all vendors.

### Phase 3: Medium Priority Fixes ({len(self.audit_results['medium_priority_issues'])})
Field alignment and optimization improvements.

## 📋 DETAILED ISSUES LIST
"""
        
        # Add detailed issue breakdown
        for issue in self.audit_results['alignment_issues'][:20]:  # Top 20 detailed
            report += f"""
### {issue['generator_name']} ({issue.get('severity', 'unknown').upper()})
- **Issue:** {issue['issue_type']}
- **Description:** {issue['description']}
- **Generator Path:** {issue['generator_path']}
"""
            if 'parser_path' in issue:
                report += f"- **Parser Path:** {issue['parser_path']}\n"
            if 'generator_format' in issue:
                report += f"- **Generator Format:** {issue['generator_format']}\n"
            if 'parser_format' in issue:
                report += f"- **Parser Format:** {issue['parser_format']}\n"
        
        return report

    def save_results(self, output_path: str):
        """Save audit results to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, default=str)

def main():
    """Main audit execution"""
    base_path = "/Users/nathanial.smalley/projects/jarvis_coding"
    
    print("🚀 JARVIS CODING - COMPREHENSIVE GENERATOR-PARSER AUDIT")
    print("=" * 60)
    
    auditor = GeneratorParserAuditor(base_path)
    
    # Perform comprehensive audit
    auditor.audit_all_generators()
    auditor.categorize_issues()
    
    # Generate and save report
    report = auditor.generate_report()
    print(report)
    
    # Save detailed results
    results_path = f"{base_path}/comprehensive_audit_results.json"
    auditor.save_results(results_path)
    
    print(f"\n📄 Detailed results saved to: {results_path}")
    print(f"🎯 Found {len(auditor.audit_results['critical_issues'])} critical issues")
    print(f"⚡ Found {len(auditor.audit_results['high_priority_issues'])} high priority issues")
    print(f"✅ Found {len(auditor.audit_results['working_pairs'])} working pairs")

if __name__ == "__main__":
    main()