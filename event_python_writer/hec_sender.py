#!/usr/bin/env python3
"""Send logs from vendor_product generators to SentinelOne AI SIEM (Splunk‑HEC) one‑by‑one."""
import argparse, json, os, time, random, requests, importlib

# Map product → (module_name, generator function names)
PROD_MAP = {
    "fortinet_fortigate": (
        "fortinet_fortigate",
        ["local_log", "forward_log", "rest_api_log", "vpn_log", "virus_log"],
    ),
    "zscaler": (
        "zscaler",
        ["zscaler_log"],
    ),
    "aws_cloudtrail": (
        "aws_cloudtrail",
        ["cloudtrail_log"],
    ),
    "aws_vpcflowlogs": (
        "aws_vpcflowlogs",
        ["vpcflow_log"],
    ),
    "aws_guardduty": (
        "aws_guardduty",
        ["guardduty_log"],
    ),
    "aws_elb": (
        "aws_elb",
        ["aws_elb_log"],
    ),
    "microsoft_azuread": (
        "microsoft_azuread",
        ["azuread_log"],
    ),
    "okta_authentication": (
        "okta_authentication",
        ["okta_authentication_log"],
    ),
    "cisco_asa": (
        "cisco_asa",
        ["asa_log"],
    ),
    "cisco_umbrella": (
        "cisco_umbrella",
        ["umbrella_dns_log"],
    ),
    "cisco_meraki": (
        "cisco_meraki",
        ["cisco_meraki_log"],
    ),
    "crowdstrike_falcon": (
        "crowdstrike_falcon",
        ["crowdstrike_log"],
    ),
    "cyberark_pas": (
        "cyberark_pas",
        ["cyberark_pas_log"],
    ),
    "darktrace": (
        "darktrace",
        ["darktrace_log"],
    ),
    "proofpoint": (
        "proofpoint",
        ["proofpoint_log"],
    ),
    "microsoft_365_mgmt_api": (
        "microsoft_365_mgmt_api",
        ["microsoft_365_mgmt_api_log"],
    ),
    "netskope": (
        "netskope",
        ["netskope_log"],
    ),
    "mimecast": (
        "mimecast",
        ["mimecast_log"],
    ),
    "microsoft_azure_ad_signin": (
        "microsoft_azure_ad_signin",
        ["microsoft_azure_ad_signin_log"],
    ),
    "microsoft_defender_email": (
        "microsoft_defender_email",
        ["microsoft_defender_email_log"],
    ),
    "beyondtrust_passwordsafe": (
        "beyondtrust_passwordsafe",
        ["beyondtrust_passwordsafe_log"],
    ),
    "hashicorp_vault": (
        "hashicorp_vault",
        ["hashicorp_vault_log"],
    ),
    "corelight_conn": (
        "corelight_conn",
        ["corelight_conn_log"],
    ),
    "corelight_http": (
        "corelight_http",
        ["corelight_http_log"],
    ),
    "corelight_ssl": (
        "corelight_ssl",
        ["corelight_ssl_log"],
    ),
    "corelight_tunnel": (
        "corelight_tunnel",
        ["corelight_tunnel_log"],
    ),
    "vectra_ai": (
        "vectra_ai",
        ["vectra_ai_log"],
    ),
    "tailscale": (
        "tailscale",
        ["tailscale_log"],
    ),
    "extrahop": (
        "extrahop",
        ["extrahop_log"],
    ),
    "armis": (
        "armis",
        ["armis_log"],
    ),
    "sentinelone_endpoint": (
        "sentinelone_endpoint",
        ["sentinelone_endpoint_log"],
    ),
    "sentinelone_identity": (
        "sentinelone_identity",
        ["sentinelone_identity_log"],
    ),
    "apache_http": (
        "apache_http",
        ["apache_http_log"],
    ),
    "abnormal_security": (
        "abnormal_security",
        ["abnormal_security_log"],
    ),
    "buildkite": (
        "buildkite",
        ["buildkite_log"],
    ),
    "teleport": (
        "teleport",
        ["teleport_log"],
    ),
    "cisco_ise": (
        "cisco_ise",
        ["cisco_ise_log"],
    ),
    "google_workspace": (
        "google_workspace",
        ["google_workspace_log"],
    ),
    "aws_vpc_dns": (
        "aws_vpc_dns",
        ["aws_vpc_dns_log"],
    ),
    "cisco_networks": (
        "cisco_networks",
        ["cisco_networks_log"],
    ),
    "cloudflare_general": (
        "cloudflare_general",
        ["cloudflare_general_log"],
    ),
    "extreme_networks": (
        "extreme_networks",
        ["extreme_networks_log"],
    ),
    "f5_networks": (
        "f5_networks",
        ["f5_networks_log"],
    ),
    "google_cloud_dns": (
        "google_cloud_dns",
        ["google_cloud_dns_log"],
    ),
    "imperva_waf": (
        "imperva_waf",
        ["imperva_waf_log"],
    ),
    "juniper_networks": (
        "juniper_networks",
        ["juniper_networks_log"],
    ),
    "ubiquiti_unifi": (
        "ubiquiti_unifi",
        ["ubiquiti_unifi_log"],
    ),
    "zscaler_firewall": (
        "zscaler_firewall",
        ["zscaler_firewall_log"],
    ),
    "cisco_fmc": (
        "cisco_fmc",
        ["cisco_fmc_log"],
    ),
    "cisco_ios": (
        "cisco_ios",
        ["cisco_ios_log"],
    ),
    "cisco_isa3000": (
        "cisco_isa3000",
        ["cisco_isa3000_log"],
    ),
    "incapsula": (
        "incapsula",
        ["incapsula_log"],
    ),
    "manageengine_general": (
        "manageengine_general",
        ["manageengine_general_log"],
    ),
    "manch_siem": (
        "manch_siem",
        ["manch_siem_log"],
    ),
    "microsoft_windows_eventlog": (
        "microsoft_windows_eventlog",
        ["microsoft_windows_eventlog_log"],
    ),
    "paloalto_prismasase": (
        "paloalto_prismasase",
        ["paloalto_prismasase_log"],
    ),
    "sap": (
        "sap",
        ["sap_log"],
    ),
    "securelink": (
        "securelink",
        ["securelink_log"],
    ),
    "aws_waf": (
        "aws_waf",
        ["aws_waf_log"],
    ),
    "aws_route53": (
        "aws_route53",
        ["aws_route53_log"],
    ),
    "cisco_ironport": (
        "cisco_ironport",
        ["cisco_ironport_log"],
    ),
    "cyberark_conjur": (
        "cyberark_conjur",
        ["cyberark_conjur_log"],
    ),
    "iis_w3c": (
        "iis_w3c",
        ["iis_w3c_log"],
    ),
    "linux_auth": (
        "linux_auth",
        ["linux_auth_log"],
    ),
    "microsoft_365_collaboration": (
        "microsoft_365_collaboration",
        ["microsoft_365_collaboration_log"],
    ),
    "microsoft_365_defender": (
        "microsoft_365_defender",
        ["microsoft_365_defender_log"],
    ),
    "pingfederate": (
        "pingfederate",
        ["pingfederate_log"],
    ),
    "zscaler_dns_firewall": (
        "zscaler_dns_firewall",
        ["zscaler_dns_firewall_log"],
    ),
    "akamai_cdn": (
        "akamai_cdn",
        ["akamai_cdn_log"],
    ),
    "akamai_dns": (
        "akamai_dns",
        ["akamai_dns_log"],
    ),
    "akamai_general": (
        "akamai_general",
        ["akamai_general_log"],
    ),
    "akamai_sitedefender": (
        "akamai_sitedefender",
        ["akamai_sitedefender_log"],
    ),
    "axway_sftp": (
        "axway_sftp",
        ["axway_sftp_log"],
    ),
    "cisco_duo": (
        "cisco_duo",
        ["cisco_duo_log"],
    ),
    "cohesity_backup": (
        "cohesity_backup",
        ["cohesity_backup_log"],
    ),
    "f5_vpn": (
        "f5_vpn",
        ["f5_vpn_log"],
    ),
    "github_audit": (
        "github_audit",
        ["github_audit_log"],
    ),
    "harness_ci": (
        "harness_ci",
        ["harness_ci_log"],
    ),
    "hypr_auth": (
        "hypr_auth",
        ["hypr_auth_log"],
    ),
    "imperva_sonar": (
        "imperva_sonar",
        ["imperva_sonar_log"],
    ),
    "isc_bind": (
        "isc_bind",
        ["isc_bind_log"],
    ),
    "isc_dhcp": (
        "isc_dhcp",
        ["isc_dhcp_log"],
    ),
    "jamf_protect": (
        "jamf_protect",
        ["jamf_protect_log"],
    ),
    "pingone_mfa": (
        "pingone_mfa",
        ["pingone_mfa_log"],
    ),
    "pingprotect": (
        "pingprotect",
        ["pingprotect_log"],
    ),
    "rsa_adaptive": (
        "rsa_adaptive",
        ["rsa_adaptive_log"],
    ),
    "veeam_backup": (
        "veeam_backup",
        ["veeam_backup_log"],
    ),
    "wiz_cloud": (
        "wiz_cloud",
        ["wiz_cloud_log"],
    ),
}
# I need to move this down below sourcetype_map so
#HEC_URL = os.getenv(
#    "S1_HEC_URL",
#   "https://ingest.us1.sentinelone.net/services/collector/raw?sourcetype=$sourcetype_map,
#)
HEC_TOKEN = os.getenv("S1_HEC_TOKEN")
if not HEC_TOKEN:
    raise RuntimeError("export S1_HEC_TOKEN=… first")

HEADERS = {
    "Authorization": f"Bearer {HEC_TOKEN}",
}

SOURCETYPE_MAP = {
    "fortinet_fortigate": "marketplace-fortinetfortigate-latest",
    "zscaler": "marketplace-zscalerinternetaccess-latest",
    "aws_cloudtrail": "marketplace-awscloudtrail-latest",
    "aws_vpcflowlogs": "marketplace-awsvpcflowlogs-latest",
    "aws_guardduty": "community-awsguarddutylogs-latest",
    "aws_elb": "json",
    "microsoft_azuread": "azuread",
    "okta_authentication": "json",
    "cisco_asa": "CommCiscoASA",
    "cisco_umbrella": "community-ciscoumbrella-latest",
    "cisco_meraki": "CommCiscoMeraki",
    "crowdstrike_falcon": "CommCrowdstrikeEP",
    "cyberark_pas": "json",
    "darktrace": "json",
    "proofpoint": "json",
    "microsoft_365_mgmt_api": "json",
    "netskope": "json",
    "mimecast": "json",
    "microsoft_azure_ad_signin": "json",
    "microsoft_defender_email": "json",
    "beyondtrust_passwordsafe": "json",
    "hashicorp_vault": "json",
    "corelight_conn": "json",
    "corelight_http": "json",
    "corelight_ssl": "json",
    "corelight_tunnel": "json",
    "vectra_ai": "syslog",
    "tailscale": "json",
    "extrahop": "json",
    "armis": "armis_syslog",
    "sentinelone_endpoint": "json",
    "sentinelone_identity": "json",
    "apache_http": "community-apachehttplogs-latest",
    "abnormal_security": "community-abnormalsecurityemailsecurity-latest",
    "buildkite": "community-buildkiteaudit-latest",
    "teleport": "community-teleportaccessproxy-latest",
    "cisco_ise": "community-ciscoidentityservicesengine-latest",
    "google_workspace": "community-googleworkspaceaudit-latest",
    "aws_vpc_dns": "community-awsvpcdns-latest",
    "cisco_networks": "community-cisconetworks-latest",
    "cloudflare_general": "community-cloudflaregeneral-latest",
    "extreme_networks": "community-extremenetworks-latest",
    "f5_networks": "community-f5networks-latest",
    "google_cloud_dns": "community-googleclouddns-latest",
    "imperva_waf": "community-impervawaf-latest",
    "juniper_networks": "community-junipernetworks-latest",
    "ubiquiti_unifi": "community-ubiquitiunifi-latest",
    "zscaler_firewall": "community-zscalerfirewall-latest",
    "cisco_fmc": "community-ciscofmc-latest",
    "cisco_ios": "community-ciscoios-latest",
    "cisco_isa3000": "community-ciscoisa3000-latest",
    "incapsula": "community-incapsula-latest",
    "manageengine_general": "community-manageenginegeneral-latest",
    "manch_siem": "community-manchsiem-latest",
    "microsoft_windows_eventlog": "community-microsoftwindowseventlog-latest",
    "paloalto_prismasase": "community-paloaltoprismasase-latest",
    "sap": "community-sap-latest",
    "securelink": "community-securelink-latest",
    "aws_waf": "community-awswaf-latest",
    "aws_route53": "community-awsroute53-latest",
    "cisco_ironport": "community-ciscoironport-latest",
    "cyberark_conjur": "community-cyberarkconjur-latest",
    "iis_w3c": "community-iisw3c-latest",
    "linux_auth": "community-linuxauth-latest",
    "microsoft_365_collaboration": "community-microsoft365collaboration-latest",
    "microsoft_365_defender": "community-microsoft365defender-latest",
    "pingfederate": "community-pingfederate-latest",
    "zscaler_dns_firewall": "community-zscalerdnsfirewall-latest",
    "akamai_cdn": "community-akamaicdn-latest",
    "akamai_dns": "community-akamaidns-latest",
    "akamai_general": "community-akamaigeneral-latest",
    "akamai_sitedefender": "community-akamaisitedefender-latest",
    "axway_sftp": "community-axwaysftp-latest",
    "cisco_duo": "community-ciscoduo-latest",
    "cohesity_backup": "community-cohesitybackup-latest",
    "f5_vpn": "community-f5vpn-latest",
    "github_audit": "community-githubaudit-latest",
    "harness_ci": "community-harnessci-latest",
    "hypr_auth": "community-hyprauth-latest",
    "imperva_sonar": "community-impervasonar-latest",
    "isc_bind": "community-iscbind-latest",
    "isc_dhcp": "community-iscdhcp-latest",
    "jamf_protect": "community-jamfprotect-latest",
    "pingone_mfa": "community-pingonemfa-latest",
    "pingprotect": "community-pingprotect-latest",
    "rsa_adaptive": "community-rsaadaptive-latest",
    "veeam_backup": "community-veeambackup-latest",
    "wiz_cloud": "community-wizcloud-latest",
}

# Generators that already emit structured JSON events; these must be sent to /event
JSON_PRODUCTS = {
    "aws_cloudtrail",
    "microsoft_azuread",
    "okta_authentication",
    "crowdstrike_falcon",
    "cyberark_pas",
    "darktrace",
    "proofpoint",
    "microsoft_365_mgmt_api",
    "netskope",
    "mimecast",
    "microsoft_azure_ad_signin",
    "microsoft_defender_email",
    "beyondtrust_passwordsafe",
    "hashicorp_vault",
    "aws_elb",
    "corelight_conn",
    "corelight_http",
    "corelight_ssl",
    "corelight_tunnel",
    "tailscale",
    "extrahop",
    "sentinelone_endpoint",
    "sentinelone_identity",
    "abnormal_security",
    "buildkite", 
    "teleport",
    "cisco_ise",
    "google_workspace",
    "aws_vpc_dns",
    "cisco_networks",
    "cloudflare_general",
    "extreme_networks",
    "f5_networks",
    "google_cloud_dns",
    "imperva_waf",
    "juniper_networks",
    "ubiquiti_unifi",
    "zscaler_firewall",
    "cisco_fmc",
    "cisco_ios",
    "cisco_isa3000",
    "incapsula",
    "manageengine_general",
    "manch_siem",
    "microsoft_windows_eventlog",
    "paloalto_prismasase",
    "sap",
    "securelink",
    "aws_waf",
    "aws_route53",
    "cisco_ironport",
    "cyberark_conjur",
    "iis_w3c",
    "linux_auth",
    "microsoft_365_collaboration",
    "microsoft_365_defender",
    "pingfederate",
    "zscaler_dns_firewall",
    "akamai_cdn",
    "akamai_dns",
    "akamai_general",
    "akamai_sitedefender",
    "axway_sftp",
    "cisco_duo",
    "cohesity_backup",
    "f5_vpn",
    "github_audit",
    "harness_ci",
    "hypr_auth",
    "imperva_sonar",
    "isc_bind",
    "isc_dhcp",
    "jamf_protect",
    "pingone_mfa",
    "pingprotect",
    "rsa_adaptive",
    "veeam_backup",
    "wiz_cloud",
}

def _envelope(line: str, product: str, attr_fields: dict) -> str:
    return json.dumps(
        {
            "time": round(time.time()),
            "event": line,
            "sourcetype": SOURCETYPE_MAP[product],
            "fields": attr_fields,
        },
        ensure_ascii=False,
        separators=(',', ':')
    )

def send_one(line: str, product: str, attr_fields: dict):
    """
    Route JSON‑structured products to the /event endpoint and all
    raw / CSV / syslog products to the /raw endpoint.
    """
    raw_base   = os.getenv("S1_HEC_RAW_URL_BASE",   "https://ingest.us1.sentinelone.net/services/collector/raw")
    event_base = os.getenv("S1_HEC_EVENT_URL_BASE", "https://ingest.us1.sentinelone.net/services/collector/event")

    if product in JSON_PRODUCTS:
        # ── JSON payload → /event ─────────────────────────
        url = event_base
        payload = _envelope(line, product, attr_fields)  # JSON envelope
        headers = {**HEADERS, "Content-Type": "application/json"}
    else:
        # ── Raw payload → /raw ───────────────────────────
        url = f"{raw_base}?sourcetype={SOURCETYPE_MAP[product]}"
        payload = line  # plain CSV/syslog/raw string
        headers = {**HEADERS, "Content-Type": "text/plain"}

    resp = requests.post(url, headers=headers, data=payload, timeout=10)
    resp.raise_for_status()
    try:
        return resp.json()
    except ValueError:
        return {"status": "OK", "code": resp.status_code}

def send_many_with_spacing(lines, product: str, attr_fields: dict,
                           min_delay=0.020, max_delay=60.0):
    """Send events individually with random delay between each."""
    results = []
    for idx, line in enumerate(lines, 1):
        results.append(send_one(line, product, attr_fields))
        if idx != len(lines):
            time.sleep(random.uniform(min_delay, max_delay))
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate & send security events from various vendors (one‑by‑one) to S1"
    )
    parser.add_argument("-n", "--count", type=int, default=1,
                        help="How many events to send (default 1)")
    parser.add_argument("--min-delay", type=float, default=0.020,
                        help="Minimum delay between events in seconds (default 0.02)")
    parser.add_argument("--max-delay", type=float, default=60.0,
                        help="Maximum delay between events in seconds (default 60)")
    parser.add_argument(
        "--product",
        choices=[
            "fortinet_fortigate",
            "zscaler",
            "aws_cloudtrail",
            "aws_vpcflowlogs",
            "aws_guardduty",
            "aws_elb",
            "microsoft_azuread",
            "okta_authentication",
            "cisco_asa",
            "cisco_umbrella",
            "cisco_meraki",
            "crowdstrike_falcon",
            "cyberark_pas",
            "darktrace",
            "proofpoint",
            "microsoft_365_mgmt_api",
            "netskope",
            "mimecast",
            "microsoft_azure_ad_signin",
            "microsoft_defender_email",
            "beyondtrust_passwordsafe",
            "hashicorp_vault",
            "corelight_conn",
            "corelight_http",
            "corelight_ssl",
            "corelight_tunnel",
            "vectra_ai",
            "tailscale",
            "extrahop",
            "armis",
            "sentinelone_endpoint",
            "sentinelone_identity",
            "apache_http",
            "abnormal_security",
            "buildkite",
            "teleport",
            "cisco_ise",
            "google_workspace",
            "aws_vpc_dns",
            "cisco_networks",
            "cloudflare_general",
            "extreme_networks",
            "f5_networks",
            "google_cloud_dns",
            "imperva_waf",
            "juniper_networks",
            "ubiquiti_unifi",
            "zscaler_firewall",
            "cisco_fmc",
            "cisco_ios",
            "cisco_isa3000",
            "incapsula",
            "manageengine_general",
            "manch_siem",
            "microsoft_windows_eventlog",
            "paloalto_prismasase",
            "sap",
            "securelink",
            "aws_waf",
            "aws_route53",
            "cisco_ironport",
            "cyberark_conjur",
            "iis_w3c",
            "linux_auth",
            "microsoft_365_collaboration",
            "microsoft_365_defender",
            "pingfederate",
            "zscaler_dns_firewall",
            "akamai_cdn",
            "akamai_dns",
            "akamai_general",
            "akamai_sitedefender",
            "axway_sftp",
            "cisco_duo",
            "cohesity_backup",
            "f5_vpn",
            "github_audit",
            "harness_ci",
            "hypr_auth",
            "imperva_sonar",
            "isc_bind",
            "isc_dhcp",
            "jamf_protect",
            "pingone_mfa",
            "pingprotect",
            "rsa_adaptive",
            "veeam_backup",
            "wiz_cloud",
        ],
        default="fortinet_fortigate",
        help="Which log generator to use (default: fortinet_fortigate)",
    )
    args = parser.parse_args()

    mod_name, func_names = PROD_MAP[args.product]
    gen_mod = importlib.import_module(mod_name)
    attr_fields = getattr(gen_mod, "ATTR_FIELDS")
    generators = [getattr(gen_mod, fn) for fn in func_names]

    events = [generators[i % len(generators)]() for i in range(args.count)]

    if args.count == 1:
        print("HEC response:", send_one(events[0], args.product, attr_fields))
    else:
        print(f"Sending {args.count} events one-by-one "
              f"(spacing {args.min_delay}s – {args.max_delay}s)…")
        print("Responses:", send_many_with_spacing(
            events, args.product, attr_fields, args.min_delay, args.max_delay
        ))