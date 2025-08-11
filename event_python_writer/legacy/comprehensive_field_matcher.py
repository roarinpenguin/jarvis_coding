#!/usr/bin/env python3
"""
Comprehensive Field Matcher
Tests all working generators against their parsers to analyze field extraction improvements.
"""

import json
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple, Any, Set
from datetime import datetime

class ComprehensiveFieldMatcher:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.parsers_dir = self.base_dir / "parsers" / "community"
        self.generators_dir = Path(__file__).parent
        
    def get_working_parsers(self) -> List[str]:
        """Get list of working parsers from our latest test results."""
        return [
            "abnormal_security_logs",
            "akamai_cdn", 
            "akamai_dns",
            "akamai_general",
            "akamai_sitedefender",
            "apache_http_logs",
            "armis_armis_logs",
            "aruba_clearpass_logs",
            "aws_elasticloadbalancer_logs",
            "aws_guardduty_logs",
            "aws_route53",
            "aws_vpc_dns_logs",
            "aws_vpcflow_logs",
            "aws_waf",
            "axway_sftp",
            "beyondtrust_passwordsafe_logs",
            "beyondtrust_privilegemgmtwindows_logs",
            "buildkite_ci_logs",
            "checkpoint_checkpoint_logs",
            "cisco_duo",
            "cisco_firewall",
            "cisco_firewall_threat_defense",
            "cisco_fmc_logs",
            "cisco_ios_logs",
            "cisco_ironport",
            "cisco_isa3000_logs",
            "cisco_ise_logs",
            "cisco_meraki",
            "cisco_meraki_flow_logs",
            "cisco_networks_logs",
            "cloudflare_general_logs",
            "cloudflare_waf_logs",
            "cohesity_backup",
            "corelight_conn_logs",
            "corelight_http_logs",
            "corelight_ssl_logs",
            "corelight_tunnel_logs",
            "crowdstrike_endpoint",
            "cyberark_conjur",
            "cyberark_pas_logs",
            "darktrace_darktrace_logs",
            "extrahop_extrahop_logs",
            "extreme_networks_logs",
            "f5_networks_logs",
            "f5_vpn",
            "forcepoint_forcepoint_logs",
            "fortinet_fortigate_fortimanager_logs",
            "github_audit",
            "google_cloud_dns_logs",
            "google_workspace_logs",
            "harness_ci",
            "hashicorp_hcp_vault_logs",
            "hypr_auth",
            "iis_w3c",
            "imperva_sonar",
            "imperva_waf_logs",
            "incapsula_incapsula_logs",
            "isc_bind",
            "isc_dhcp",
            "jamf_protect",
            "juniper_networks_logs",
            "linux_auth",
            "managedengine_ad_audit_plus",
            "manageengine_adauditplus_logs",
            "manageengine_general_logs",
            "manch_siem_logs",
            "microsoft_365_collaboration",
            "microsoft_365_defender",
            "microsoft_365_mgmt_api_logs",
            "microsoft_azure_ad_logs",
            "microsoft_eventhub_azure_signin_logs",
            "microsoft_eventhub_defender_email_logs",
            "microsoft_eventhub_defender_emailforcloud_logs",
            "microsoft_windows_eventlog",
            "mimecast_mimecast_logs",
            "netskope_logshipper_logs",
            "netskope_netskope_logs",
            "okta_ocsf_logs",
            "paloalto_alternate_logs",
            "paloalto_paloalto_logs",
            "paloalto_prismasase_logs",
            "pingfederate",
            "pingone_mfa",
            "pingprotect",
            "proofpoint_proofpoint_logs",
            "rsa_adaptive",
            "sap_logs",
            "securelink_logs",
            "singularityidentity_singularityidentity_logs",
            "tailscale_tailscale_logs",
            "teleport_logs",
            "ubiquiti_unifi_logs",
            "vectra_ai_logs",
            "veeam_backup",
            "vmware_vcenter_logs",
            "windows_dhcp_logs",
            "wiz_cloud",
            "zscaler_dns_firewall",
            "zscaler_firewall_logs"
        ]
    
    def find_matching_generator(self, parser_name: str) -> Path:
        """Find the corresponding event generator for a parser."""
        # Map parser names to generator names
        parser_to_generator_map = {
            "abnormal_security_logs": "abnormal_security",
            "akamai_cdn": "akamai_cdn",
            "akamai_dns": "akamai_dns", 
            "akamai_general": "akamai_general",
            "akamai_sitedefender": "akamai_sitedefender",
            "apache_http_logs": "apache_http",
            "armis_armis_logs": "armis",
            "aruba_clearpass_logs": "aruba_clearpass",
            "aws_elasticloadbalancer_logs": "aws_elb",
            "aws_guardduty_logs": "aws_guardduty",
            "aws_route53": "aws_route53",
            "aws_vpc_dns_logs": "aws_vpc_dns",
            "aws_vpcflow_logs": "aws_vpcflowlogs",
            "aws_waf": "aws_waf",
            "axway_sftp": "axway_sftp",
            "beyondtrust_passwordsafe_logs": "beyondtrust_passwordsafe",
            "beyondtrust_privilegemgmtwindows_logs": "beyondtrust_privilegemgmt_windows",
            "buildkite_ci_logs": "buildkite",
            "checkpoint_checkpoint_logs": "checkpoint",
            "cisco_duo": "cisco_duo",
            "cisco_firewall": "cisco_asa",
            "cisco_firewall_threat_defense": "cisco_asa",
            "cisco_fmc_logs": "cisco_fmc",
            "cisco_ios_logs": "cisco_ios",
            "cisco_ironport": "cisco_ironport",
            "cisco_isa3000_logs": "cisco_isa3000",
            "cisco_ise_logs": "cisco_ise",
            "cisco_meraki": "cisco_meraki",
            "cisco_meraki_flow_logs": "cisco_meraki",
            "cisco_networks_logs": "cisco_networks",
            "cloudflare_general_logs": "cloudflare_general",
            "cloudflare_waf_logs": "cloudflare_waf",
            "cohesity_backup": "cohesity_backup",
            "corelight_conn_logs": "corelight_conn",
            "corelight_http_logs": "corelight_http",
            "corelight_ssl_logs": "corelight_ssl",
            "corelight_tunnel_logs": "corelight_tunnel",
            "crowdstrike_endpoint": "crowdstrike_falcon",
            "cyberark_conjur": "cyberark_conjur",
            "cyberark_pas_logs": "cyberark_pas",
            "darktrace_darktrace_logs": "darktrace",
            "extrahop_extrahop_logs": "extrahop",
            "extreme_networks_logs": "extreme_networks",
            "f5_networks_logs": "f5_networks",
            "f5_vpn": "f5_vpn",
            "forcepoint_forcepoint_logs": "forcepoint_firewall",
            "fortinet_fortigate_fortimanager_logs": "fortinet_fortigate",
            "github_audit": "github_audit",
            "google_cloud_dns_logs": "google_cloud_dns",
            "google_workspace_logs": "google_workspace",
            "harness_ci": "harness_ci",
            "hashicorp_hcp_vault_logs": "hashicorp_vault",
            "hypr_auth": "hypr_auth",
            "iis_w3c": "iis_w3c",
            "imperva_sonar": "imperva_sonar",
            "imperva_waf_logs": "imperva_waf",
            "incapsula_incapsula_logs": "incapsula",
            "isc_bind": "isc_bind",
            "isc_dhcp": "isc_dhcp",
            "jamf_protect": "jamf_protect",
            "juniper_networks_logs": "juniper_networks",
            "linux_auth": "linux_auth",
            "managedengine_ad_audit_plus": "manageengine_ad_audit_plus",
            "manageengine_adauditplus_logs": "manageengine_ad_audit_plus",
            "manageengine_general_logs": "manageengine_general",
            "manch_siem_logs": "manch_siem",
            "microsoft_365_collaboration": "microsoft_365_collaboration",
            "microsoft_365_defender": "microsoft_365_defender",
            "microsoft_365_mgmt_api_logs": "microsoft_365_mgmt_api",
            "microsoft_azure_ad_logs": "microsoft_azuread",
            "microsoft_eventhub_azure_signin_logs": "microsoft_azure_ad_signin",
            "microsoft_eventhub_defender_email_logs": "microsoft_defender_email",
            "microsoft_eventhub_defender_emailforcloud_logs": "microsoft_defender_email",
            "microsoft_windows_eventlog": "microsoft_windows_eventlog",
            "mimecast_mimecast_logs": "mimecast",
            "netskope_logshipper_logs": "netskope",
            "netskope_netskope_logs": "netskope",
            "okta_ocsf_logs": "okta_authentication",
            "paloalto_alternate_logs": "paloalto_firewall",
            "paloalto_paloalto_logs": "paloalto_firewall",
            "paloalto_prismasase_logs": "paloalto_prismasase",
            "pingfederate": "pingfederate",
            "pingone_mfa": "pingone_mfa",
            "pingprotect": "pingprotect",
            "proofpoint_proofpoint_logs": "proofpoint",
            "rsa_adaptive": "rsa_adaptive",
            "sap_logs": "sap",
            "securelink_logs": "securelink",
            "singularityidentity_singularityidentity_logs": "sentinelone_identity",
            "tailscale_tailscale_logs": "tailscale",
            "teleport_logs": "teleport",
            "ubiquiti_unifi_logs": "ubiquiti_unifi",
            "vectra_ai_logs": "vectra_ai",
            "veeam_backup": "veeam_backup",
            "vmware_vcenter_logs": "vmware_vcenter",
            "windows_dhcp_logs": "windows_dhcp",
            "wiz_cloud": "wiz_cloud",
            "zscaler_dns_firewall": "zscaler_dns_firewall",
            "zscaler_firewall_logs": "zscaler_firewall"
        }
        
        generator_name = parser_to_generator_map.get(parser_name)
        if generator_name:
            generator_path = self.generators_dir / f"{generator_name}.py"
            if generator_path.exists():
                return generator_path
        return None
    
    def generate_sample_event(self, generator_path: Path) -> Dict:
        """Generate a sample event from the generator."""
        try:
            spec = importlib.util.spec_from_file_location("generator", generator_path)
            generator = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(generator)
            
            # Find the main log generation function
            generator_name = generator_path.stem
            function_name = f"{generator_name}_log"
            
            if hasattr(generator, function_name):
                result = getattr(generator, function_name)()
                return result if isinstance(result, dict) else {}
            else:
                # Try other common function patterns
                for func_name in dir(generator):
                    if func_name.endswith('_log') and callable(getattr(generator, func_name)):
                        result = getattr(generator, func_name)()
                        return result if isinstance(result, dict) else {}
                        
            return {}
            
        except Exception as e:
            return {}
    
    def load_parser(self, parser_name: str) -> Dict:
        """Load parser configuration from JSON file."""
        try:
            parser_path = self.parsers_dir / f"{parser_name}-latest"
            json_files = list(parser_path.glob("*.json"))
            if json_files:
                with open(json_files[0], 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            return {}
    
    def extract_parser_expected_fields(self, parser_config: Dict) -> Set[str]:
        """Extract all field names that the parser expects to find in events."""
        expected_fields = set()
        
        # Handle gron-based parsers
        if "formats" in parser_config:
            for fmt in parser_config["formats"]:
                if "rewrites" in fmt:
                    for rewrite in fmt["rewrites"]:
                        if "input" in rewrite:
                            field_name = rewrite["input"].replace("unmapped.", "")
                            expected_fields.add(field_name)
        
        return expected_fields
    
    def analyze_field_matching(self, parser_name: str) -> Dict:
        """Analyze field matching between parser and generator."""
        print(f"  🔍 Analyzing {parser_name}")
        
        result = {
            "parser_name": parser_name,
            "status": "unknown",
            "generator_fields": 0,
            "parser_expected_fields": 0,
            "matched_fields": 0,
            "missing_from_generator": [],
            "unused_generator_fields": [],
            "field_match_percentage": 0.0,
            "sample_event": {}
        }
        
        try:
            # Load parser config
            parser_config = self.load_parser(parser_name)
            if not parser_config:
                result["status"] = "no_parser"
                return result
            
            # Find generator
            generator_path = self.find_matching_generator(parser_name)
            if not generator_path:
                result["status"] = "no_generator"
                return result
            
            # Generate sample event
            sample_event = self.generate_sample_event(generator_path)
            if not sample_event:
                result["status"] = "no_sample"
                return result
            
            result["sample_event"] = sample_event
            result["generator_fields"] = len(sample_event)
            
            # Get parser expected fields
            expected_fields = self.extract_parser_expected_fields(parser_config)
            result["parser_expected_fields"] = len(expected_fields)
            
            # Analyze field matching
            generator_fields = set(sample_event.keys())
            
            matched_fields = generator_fields.intersection(expected_fields)
            missing_from_generator = expected_fields - generator_fields
            unused_generator_fields = generator_fields - expected_fields
            
            result["matched_fields"] = len(matched_fields)
            result["missing_from_generator"] = list(missing_from_generator)
            result["unused_generator_fields"] = list(unused_generator_fields)
            
            # Calculate field match percentage
            if expected_fields:
                result["field_match_percentage"] = (len(matched_fields) / len(expected_fields)) * 100
            else:
                result["field_match_percentage"] = 100.0 if not missing_from_generator else 0.0
            
            result["status"] = "success"
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
        
        return result
    
    def test_all_field_matching(self) -> Dict:
        """Test field matching for all working parsers."""
        print("🚀 Starting comprehensive field matching analysis...")
        
        working_parsers = self.get_working_parsers()
        print(f"📋 Testing field matching for {len(working_parsers)} parsers")
        
        results = {}
        successful_tests = 0
        total_match_percentage = 0.0
        perfect_matches = 0
        
        for i, parser_name in enumerate(working_parsers, 1):
            print(f"[{i}/{len(working_parsers)}]", end=" ")
            result = self.analyze_field_matching(parser_name)
            results[parser_name] = result
            
            if result["status"] == "success":
                successful_tests += 1
                total_match_percentage += result["field_match_percentage"]
                if result["field_match_percentage"] == 100.0:
                    perfect_matches += 1
                
                # Print summary
                match_pct = result["field_match_percentage"]
                if match_pct >= 90:
                    status_emoji = "✅"
                elif match_pct >= 70:
                    status_emoji = "⚠️"
                else:
                    status_emoji = "❌"
                
                print(f"    {status_emoji} {match_pct:.1f}% field match ({result['matched_fields']}/{result['parser_expected_fields']})")
            else:
                print(f"    ❌ {result['status']}")
        
        # Calculate overall statistics
        avg_match_percentage = total_match_percentage / successful_tests if successful_tests > 0 else 0
        
        print(f"\n✅ Field matching analysis complete!")
        print(f"📊 {successful_tests}/{len(working_parsers)} parsers analyzed successfully")
        print(f"🎯 {perfect_matches} parsers have 100% field matching")
        print(f"📈 Average field match percentage: {avg_match_percentage:.1f}%")
        
        return results
    
    def generate_field_matching_report(self, results: Dict) -> str:
        """Generate comprehensive field matching report."""
        report = "# Comprehensive Field Matching Report\n\n"
        report += f"**Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"**Parsers Tested**: {len(results)}\n\n"
        
        # Statistics
        successful = [r for r in results.values() if r["status"] == "success"]
        perfect_matches = [r for r in successful if r["field_match_percentage"] == 100.0]
        high_matches = [r for r in successful if 90 <= r["field_match_percentage"] < 100]
        medium_matches = [r for r in successful if 70 <= r["field_match_percentage"] < 90]
        low_matches = [r for r in successful if r["field_match_percentage"] < 70]
        
        total_match_pct = sum(r["field_match_percentage"] for r in successful)
        avg_match_pct = total_match_pct / len(successful) if successful else 0
        
        report += "## Summary Statistics\n\n"
        report += f"- **Total Parsers Analyzed**: {len(successful)}\n"
        report += f"- **Perfect Matches (100%)**: {len(perfect_matches)}\n"
        report += f"- **High Matches (90-99%)**: {len(high_matches)}\n"
        report += f"- **Medium Matches (70-89%)**: {len(medium_matches)}\n"
        report += f"- **Low Matches (<70%)**: {len(low_matches)}\n"
        report += f"- **Average Field Match**: {avg_match_pct:.1f}%\n\n"
        
        # Perfect matches
        report += f"## Perfect Field Matches ({len(perfect_matches)} parsers)\n\n"
        for result in sorted(perfect_matches, key=lambda x: x["parser_name"]):
            report += f"- **{result['parser_name']}**: {result['matched_fields']}/{result['parser_expected_fields']} fields ✅\n"
        
        # High matches
        report += f"\n## High Field Matches ({len(high_matches)} parsers)\n\n"
        for result in sorted(high_matches, key=lambda x: x["field_match_percentage"], reverse=True):
            report += f"- **{result['parser_name']}**: {result['field_match_percentage']:.1f}% ({result['matched_fields']}/{result['parser_expected_fields']})\n"
        
        # Problem parsers
        if low_matches:
            report += f"\n## Low Field Matches ({len(low_matches)} parsers)\n\n"
            for result in sorted(low_matches, key=lambda x: x["field_match_percentage"]):
                report += f"- **{result['parser_name']}**: {result['field_match_percentage']:.1f}% ({result['matched_fields']}/{result['parser_expected_fields']})\n"
                if result["missing_from_generator"]:
                    missing = result["missing_from_generator"][:5]  # Show first 5
                    report += f"  - Missing: {', '.join(missing)}\n"
        
        # Most commonly missing fields
        all_missing = {}
        for result in successful:
            for field in result["missing_from_generator"]:
                all_missing[field] = all_missing.get(field, 0) + 1
        
        if all_missing:
            top_missing = sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:15]
            report += "\n## Most Commonly Missing Fields\n\n"
            for field, count in top_missing:
                report += f"- **{field}**: Missing from {count} parsers\n"
        
        return report

if __name__ == "__main__":
    matcher = ComprehensiveFieldMatcher()
    results = matcher.test_all_field_matching()
    
    # Save results
    with open("comprehensive_field_matching_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Generate report
    report = matcher.generate_field_matching_report(results)
    with open("comprehensive_field_matching_report.md", "w") as f:
        f.write(report)
    
    print(f"\n📄 Results saved to comprehensive_field_matching_results.json")
    print(f"📄 Report saved to comprehensive_field_matching_report.md")