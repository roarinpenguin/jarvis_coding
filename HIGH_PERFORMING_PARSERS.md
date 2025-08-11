# High-Performing Parser Reference Guide

This document lists the **21 highest-performing parsers** validated through comprehensive SDL API analysis. These parsers demonstrate excellent OCSF compliance and field extraction capabilities, making them ideal reference examples for parser development.

## Perfect OCSF Compliance (100% scores)

These 11 parsers achieve perfect OCSF compliance with comprehensive field extraction:

### `fortinet_fortigate` → marketplace-fortinetfortigate-latest
- **Field Count**: 193 extracted fields
- **OCSF Score**: 100% 
- **Strengths**: Comprehensive FortiGate firewall log parsing with full metadata extraction

### `okta_authentication` → json
- **Field Count**: 271 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Complete Okta authentication event parsing with user context

### `cyberark_pas` → json
- **Field Count**: 221 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Full CyberArk Privileged Access Security audit log parsing

### `corelight_conn` → json
- **Field Count**: 289 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Comprehensive Corelight network connection metadata

### `corelight_http` → json
- **Field Count**: 271 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Complete HTTP traffic analysis with request/response details

### `buildkite` → community-buildkiteaudit-latest
- **Field Count**: 122 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Full CI/CD pipeline audit event parsing

### `cisco_fmc` → community-ciscofmc-latest
- **Field Count**: 124 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Cisco Firepower Management Center security event parsing

### `aws_waf` → community-awswaf-latest
- **Field Count**: 113 extracted fields
- **OCSF Score**: 100%
- **Strengths**: AWS Web Application Firewall security event analysis

### `aws_route53` → community-awsroute53-latest
- **Field Count**: 89 extracted fields
- **OCSF Score**: 100%
- **Strengths**: AWS Route 53 DNS query log parsing with threat intelligence

### `cisco_ironport` → community-ciscoironport-latest
- **Field Count**: 88 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Cisco Email Security Appliance comprehensive parsing

### `cisco_duo` → community-ciscoduo-latest
- **Field Count**: 138 extracted fields
- **OCSF Score**: 100%
- **Strengths**: Complete Cisco Duo MFA authentication event analysis

## Strong OCSF Compliance (60-80% scores)

These 10 parsers show strong OCSF compliance with effective field extraction:

### `zscaler` → marketplace-zscalerinternetaccess-latest
- **Field Count**: 119 extracted fields
- **OCSF Score**: 60%
- **Strengths**: Zscaler proxy traffic analysis

### `cisco_meraki` → CommCiscoMeraki
- **Field Count**: 115 extracted fields
- **OCSF Score**: 80%
- **Strengths**: Cisco Meraki network device event parsing

### `crowdstrike_falcon` → CommCrowdstrikeEP
- **Field Count**: 135 extracted fields
- **OCSF Score**: 80%
- **Strengths**: CrowdStrike Falcon endpoint detection and response

### `aws_vpc_dns` → community-awsvpcdns-latest
- **Field Count**: 123 extracted fields
- **OCSF Score**: 60%
- **Strengths**: AWS VPC DNS query analysis

### `cloudflare_general` → community-cloudflaregeneral-latest
- **Field Count**: 135 extracted fields
- **OCSF Score**: 60%
- **Strengths**: Cloudflare security and performance event parsing

### `google_cloud_dns` → community-googleclouddns-latest
- **Field Count**: 132 extracted fields
- **OCSF Score**: 60%
- **Strengths**: Google Cloud DNS query log analysis

### `incapsula` → community-incapsula-latest
- **Field Count**: 92 extracted fields
- **OCSF Score**: 80%
- **Strengths**: Imperva Incapsula WAF security event parsing

### `pingone_mfa` → community-pingonemfa-latest
- **Field Count**: 98 extracted fields
- **OCSF Score**: 60%
- **Strengths**: PingOne MFA authentication event analysis

### `pingprotect` → community-pingprotect-latest
- **Field Count**: 96 extracted fields
- **OCSF Score**: 60%
- **Strengths**: PingProtect fraud detection event parsing

### `aws_elasticloadbalancer` → community-awselasticloadbalancer-latest
- **Field Count**: 99 extracted fields
- **OCSF Score**: 60%
- **Strengths**: AWS Elastic Load Balancer access log parsing

## Key Success Patterns

Analysis of these high-performing parsers reveals several common success patterns:

### 1. **Comprehensive Field Mapping**
- Average of 88-289 extracted fields per parser
- Complete metadata preservation from original events
- Proper OCSF field normalization

### 2. **Strong OCSF Compliance**
- Consistent use of standard OCSF field naming conventions
- Proper activity classification and severity mapping
- Observable extraction (IPs, domains, users, files)

### 3. **Robust Parser Architecture**
- JSON-based configuration for flexibility
- Comprehensive regex and field extraction rules
- Proper error handling and edge case management

### 4. **Production Validation**
- All parsers successfully process real event traffic
- Consistent field extraction across event variations
- Scalable performance under load

## Usage as Reference Examples

When developing new parsers or improving existing ones, use these high-performing parsers as reference templates:

1. **Study field mapping patterns** from similar product categories
2. **Adopt OCSF compliance practices** demonstrated in these parsers
3. **Implement comprehensive field extraction** following these examples
4. **Test against real traffic** using the validation framework

## Validation Command

To validate any of these parsers or test new implementations:

```bash
# Run comprehensive validation
python final_parser_validation.py

# Test specific parser events
export S1_HEC_TOKEN="your_token"
python event_python_writer/hec_sender.py --product <parser_name> --count 5
```

These 21 parsers represent the gold standard for security event parsing in the SentinelOne AI SIEM platform and serve as the foundation for scaling to additional security products.