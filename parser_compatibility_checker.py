#!/usr/bin/env python3
"""
Parser Compatibility Checker
Validates generator output formats against their corresponding parser expectations.
"""
import os
import sys
import json
import re
import importlib
import glob
from typing import Dict, List, Tuple, Any, Optional

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.ENDC}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.ENDC}")

# Generator to parser mappings
GENERATOR_PARSER_MAP = {
    "apache_http": "apache_http_logs-latest",
    "armis": "armis_armis_logs-latest", 
    "aruba_clearpass": "aruba_clearpass_logs-latest",
    "aws_cloudtrail": "aws_vpcflow_logs-latest",  # Need to check which AWS parser
    "aws_elb": "aws_elasticloadbalancer_logs-latest",
    "aws_guardduty": "aws_guardduty_logs-latest",
    "aws_vpcflowlogs": "aws_vpcflow_logs-latest",
    "beyondtrust_passwordsafe": "beyondtrust_passwordsafe_logs-latest",
    "checkpoint": "checkpoint_checkpoint_logs-latest",
    "cisco_asa": "cisco_firewall-latest",
    "cisco_meraki": "cisco_meraki-latest",
    "cisco_umbrella": "cisco_ios_logs-latest",  # Need to verify
    "cloudflare_waf": "cloudflare_inc_waf-lastest",
    "corelight_conn": "corelight_conn_logs-latest",
    "corelight_http": "corelight_http_logs-latest", 
    "corelight_ssl": "corelight_ssl_logs-latest",
    "corelight_tunnel": "corelight_tunnel_logs-latest",
    "crowdstrike_falcon": "crowdstrike_endpoint-latest",
    "cyberark_pas": "cyberark_pas_logs-latest",
    "darktrace": "darktrace_darktrace_logs-latest",
    "extrahop": "extrahop_extrahop_logs-latest",
    "fortinet_fortigate": "fortinet_fortigate_fortimanager_logs-latest",
    "hashicorp_vault": "hashicorp_hcp_vault_logs-latest",
    "microsoft_365_mgmt_api": "microsoft_365_mgmt_api_logs-latest",
    "microsoft_azure_ad_signin": "microsoft_eventhub_azure_signin_logs-latest",
    "microsoft_azuread": "microsoft_azure_ad_logs-latest",
    "microsoft_defender_email": "microsoft_eventhub_defender_email_logs-latest",
    "mimecast": "mimecast_mimecast_logs-latest",
    "netskope": "netskope_netskope_logs-latest",
    "okta_authentication": "okta_ocsf_logs-latest",
    "paloalto_firewall": "paloalto_alternate_logs-latest",
    "proofpoint": "proofpoint_proofpoint_logs-latest",
    "tailscale": "tailscale_tailscale_logs-latest",
    "vectra_ai": "vectra_ai_logs-latest",
    "vmware_vcenter": "vmware_vcenter_logs-latest",
    "zscaler": None  # No parser found
}

def load_parser_config(parser_name: str) -> Optional[Dict]:
    """Load parser configuration from JSON file."""
    parser_path = f"../parsers/community/{parser_name}"
    
    if not os.path.exists(parser_path):
        return None
    
    # Look for JSON configuration files
    config_files = glob.glob(f"{parser_path}/*.json")
    if not config_files:
        return None
    
    try:
        with open(config_files[0], 'r') as f:
            content = f.read()
            # Remove JavaScript-style comments
            content = re.sub(r'//.*', '', content)
            content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # Try to parse as JSON (might need cleanup)
            # This is a simplified parser - real parsing would be more complex
            return {"raw_content": content, "file": config_files[0]}
    except Exception as e:
        return {"error": str(e), "file": config_files[0]}

def extract_parser_formats(parser_config: Dict) -> List[str]:
    """Extract expected formats from parser configuration."""
    if "error" in parser_config:
        return []
    
    content = parser_config.get("raw_content", "")
    
    # Extract format patterns using regex
    format_patterns = []
    
    # Look for format: "..." patterns
    format_matches = re.findall(r'format:\s*"([^"]+)"', content)
    format_patterns.extend(format_matches)
    
    # Look for format patterns in different styles
    alt_matches = re.findall(r'"format":\s*"([^"]+)"', content)
    format_patterns.extend(alt_matches)
    
    return format_patterns

def analyze_generator_output(generator_name: str) -> Dict[str, Any]:
    """Analyze generator output format and characteristics."""
    try:
        module = importlib.import_module(generator_name)
        
        # Find the main log generation function
        log_func_name = None
        for attr_name in dir(module):
            if attr_name.endswith("_log") and callable(getattr(module, attr_name)):
                log_func_name = attr_name
                break
        
        if not log_func_name:
            return {"error": "No log function found"}
        
        log_func = getattr(module, log_func_name)
        
        # Generate multiple samples to analyze patterns
        samples = []
        for _ in range(3):
            try:
                output = log_func()
                samples.append(output)
            except Exception as e:
                samples.append(f"ERROR: {e}")
        
        # Analyze format characteristics
        analysis = {
            "samples": samples,
            "sample_count": len([s for s in samples if not s.startswith("ERROR")]),
            "formats": [],
            "characteristics": {}
        }
        
        if analysis["sample_count"] > 0:
            valid_sample = next(s for s in samples if not s.startswith("ERROR"))
            
            # Determine format type
            if valid_sample.strip().startswith('{'):
                analysis["characteristics"]["type"] = "JSON"
                try:
                    json.loads(valid_sample)
                    analysis["characteristics"]["valid_json"] = True
                except:
                    analysis["characteristics"]["valid_json"] = False
            elif valid_sample.startswith('<') and '>' in valid_sample[:20]:
                analysis["characteristics"]["type"] = "Syslog"
                # Extract syslog components
                syslog_match = re.match(r'<(\d+)>(.+)', valid_sample)
                if syslog_match:
                    analysis["characteristics"]["priority"] = syslog_match.group(1)
                    analysis["characteristics"]["message"] = syslog_match.group(2)[:100]
            elif '=' in valid_sample and '"' in valid_sample:
                analysis["characteristics"]["type"] = "Key-Value"
            elif ',' in valid_sample and not valid_sample.startswith('{'):
                analysis["characteristics"]["type"] = "CSV"
            else:
                analysis["characteristics"]["type"] = "Text/Other"
            
            analysis["characteristics"]["length"] = len(valid_sample)
            analysis["characteristics"]["preview"] = valid_sample[:150]
        
        return analysis
        
    except Exception as e:
        return {"error": f"Failed to analyze generator: {str(e)}"}

def check_format_compatibility(generator_output: Dict, parser_formats: List[str]) -> Dict[str, Any]:
    """Check if generator output matches parser format expectations."""
    if "error" in generator_output or not parser_formats:
        return {"compatible": False, "reason": "Missing data for comparison"}
    
    if generator_output["sample_count"] == 0:
        return {"compatible": False, "reason": "No valid generator samples"}
    
    sample = generator_output["samples"][0]
    gen_type = generator_output["characteristics"].get("type", "Unknown")
    
    compatibility = {
        "compatible": False,
        "confidence": "low",
        "issues": [],
        "matches": []
    }
    
    # Check against each parser format
    for fmt in parser_formats:
        if "parse=json" in fmt.lower() or "parse=dottedescapedjson" in fmt.lower():
            if gen_type == "JSON":
                compatibility["matches"].append(f"JSON format match: {fmt[:50]}...")
                compatibility["compatible"] = True
                compatibility["confidence"] = "high"
        elif "parse=gron" in fmt.lower():
            if gen_type == "JSON":
                compatibility["matches"].append(f"GRON/JSON format match: {fmt[:50]}...")
                compatibility["compatible"] = True
                compatibility["confidence"] = "medium"
        elif "$" in fmt and "=" in fmt:
            # Key-value or field extraction pattern
            if gen_type in ["Key-Value", "Syslog", "Text/Other"]:
                compatibility["matches"].append(f"Field extraction pattern: {fmt[:50]}...")
                compatibility["compatible"] = True
                compatibility["confidence"] = "medium"
        elif "," in fmt:
            # CSV-like format
            if gen_type == "CSV":
                compatibility["matches"].append(f"CSV format match: {fmt[:50]}...")
                compatibility["compatible"] = True
                compatibility["confidence"] = "high"
    
    # Check for specific issues
    if gen_type == "JSON" and not any("json" in fmt.lower() for fmt in parser_formats):
        compatibility["issues"].append("Generator produces JSON but parser expects text format")
    
    if gen_type in ["Syslog", "Text/Other"] and any("json" in fmt.lower() for fmt in parser_formats):
        compatibility["issues"].append("Generator produces text but parser expects JSON")
    
    return compatibility

def main():
    """Main compatibility checker."""
    print_header("Parser Compatibility Checker")
    
    results = {}
    total_generators = 0
    compatible_count = 0
    high_confidence_count = 0
    issues_found = []
    
    print("🔍 Checking generator-parser compatibility...")
    print()
    
    for generator_name, parser_name in GENERATOR_PARSER_MAP.items():
        total_generators += 1
        print(f"📋 Checking {generator_name}...")
        
        if parser_name is None:
            print_warning(f"  No parser found for {generator_name}")
            results[generator_name] = {
                "status": "no_parser",
                "parser": None,
                "compatible": False
            }
            continue
        
        # Load parser configuration
        parser_config = load_parser_config(parser_name)
        if not parser_config:
            print_error(f"  Could not load parser config for {parser_name}")
            results[generator_name] = {
                "status": "parser_error",
                "parser": parser_name,
                "compatible": False
            }
            continue
        
        if "error" in parser_config:
            print_error(f"  Parser config error: {parser_config['error']}")
            results[generator_name] = {
                "status": "parser_error", 
                "parser": parser_name,
                "error": parser_config["error"],
                "compatible": False
            }
            continue
        
        # Extract parser format expectations
        parser_formats = extract_parser_formats(parser_config)
        print_info(f"  Found {len(parser_formats)} parser format patterns")
        
        # Analyze generator output
        generator_output = analyze_generator_output(generator_name)
        if "error" in generator_output:
            print_error(f"  Generator error: {generator_output['error']}")
            results[generator_name] = {
                "status": "generator_error",
                "parser": parser_name,
                "error": generator_output["error"],
                "compatible": False
            }
            continue
        
        gen_type = generator_output["characteristics"].get("type", "Unknown")
        print_info(f"  Generator produces: {gen_type} format")
        
        # Check compatibility
        compatibility = check_format_compatibility(generator_output, parser_formats)
        
        if compatibility["compatible"]:
            if compatibility["confidence"] == "high":
                print_success(f"  High confidence match ({gen_type})")
                high_confidence_count += 1
            else:
                print_success(f"  Probable match ({gen_type}) - {compatibility['confidence']} confidence")
            compatible_count += 1
            
            if compatibility["matches"]:
                for match in compatibility["matches"][:2]:  # Show first 2 matches
                    print(f"    • {match}")
        else:
            print_error(f"  Format mismatch detected")
            issues_found.append({
                "generator": generator_name,
                "parser": parser_name,
                "generator_type": gen_type,
                "issues": compatibility["issues"]
            })
        
        if compatibility["issues"]:
            for issue in compatibility["issues"]:
                print_warning(f"    ⚠ {issue}")
        
        results[generator_name] = {
            "status": "analyzed",
            "parser": parser_name,
            "compatible": compatibility["compatible"],
            "confidence": compatibility["confidence"],
            "generator_type": gen_type,
            "issues": compatibility["issues"],
            "matches": compatibility["matches"]
        }
        
        print()
    
    # Summary
    print_header("Compatibility Summary")
    print(f"🧮 Total generators checked: {total_generators}")
    print(f"✅ Compatible generators: {compatible_count}")
    print(f"🎯 High confidence matches: {high_confidence_count}")
    print(f"⚠️  Issues found: {len(issues_found)}")
    print(f"📊 Compatibility rate: {(compatible_count/total_generators*100):.1f}%")
    
    if issues_found:
        print("\n🚨 Generators Needing Attention:")
        for issue in issues_found:
            print(f"  • {issue['generator']} → {issue['parser']}")
            print(f"    Type: {issue['generator_type']}")
            for problem in issue['issues']:
                print(f"    Issue: {problem}")
            print()
    
    # Save detailed report
    report = {
        "summary": {
            "total_generators": total_generators,
            "compatible_count": compatible_count,
            "high_confidence_count": high_confidence_count,
            "issues_count": len(issues_found),
            "compatibility_rate": compatible_count/total_generators*100
        },
        "results": results,
        "issues": issues_found
    }
    
    with open("parser_compatibility_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print_info("Detailed report saved to: parser_compatibility_report.json")
    
    # Exit with error code if issues found
    if len(issues_found) > 0:
        print(f"\n{Colors.RED}⚠️  Found {len(issues_found)} compatibility issues that need fixing!{Colors.ENDC}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}🎉 All generators appear compatible with their parsers!{Colors.ENDC}")

if __name__ == "__main__":
    main()