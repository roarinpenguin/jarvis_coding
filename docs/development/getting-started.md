# Getting Started with Jarvis Coding

Welcome! This guide will get you up and running with the Jarvis Coding security event generation platform in under 5 minutes.

## 🎯 Quick Start (TL;DR)

```bash
# Clone the repository
git clone https://github.com/natesmalley/jarvis_coding.git
cd jarvis_coding

# Set up Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r event_generators/shared/requirements.txt

# Test a generator
python event_generators/endpoint_security/crowdstrike_falcon.py

# Send events to SentinelOne
export S1_HEC_TOKEN="your-token-here"
python event_generators/shared/hec_sender.py --product crowdstrike_falcon --count 5
```

## 📋 Prerequisites

- **Python 3.8+** installed
- **Git** for version control
- **SentinelOne HEC token** (optional, for sending events)
- **Text editor** (VS Code recommended)

## 🔧 Detailed Setup

### 1. Clone the Repository

```bash
git clone https://github.com/natesmalley/jarvis_coding.git
cd jarvis_coding
```

### 2. Create Python Virtual Environment

Always use a virtual environment to avoid dependency conflicts:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate

# You should see (.venv) in your terminal prompt
```

### 3. Install Dependencies

```bash
pip install -r event_generators/shared/requirements.txt
```

This installs:
- `requests` - For HTTP API calls
- Standard library dependencies

### 4. Set Environment Variables (Optional)

For sending events to SentinelOne:

```bash
# HEC Token for event ingestion
export S1_HEC_TOKEN="1FUC88b9Z4BaHtQxwIXwYGpMGEMv7UQ1JjPHEkERjDEe2U7_AS67SJJRpbIqk78h7"

# SDL API Token for validation (optional)
export S1_SDL_API_TOKEN="your-read-api-token"
```

**Tip**: Add these to your `.bashrc` or `.zshrc` for persistence.

### 5. Verify Installation

Test that everything works:

```bash
# Test a generator
python event_generators/network_security/fortinet_fortigate.py

# You should see JSON output with Star Trek themed events
```

## 🚀 Your First Generator Run

### Running a Single Generator

```bash
# Navigate to any category
cd event_generators/endpoint_security

# Run a generator directly
python crowdstrike_falcon.py

# Output: JSON events with Star Trek characters
```

### Using the HEC Sender

The HEC sender is the central tool for sending events:

```bash
# Send 10 CrowdStrike events
python event_generators/shared/hec_sender.py \
  --product crowdstrike_falcon \
  --count 10

# Use a marketplace parser for better field extraction
python event_generators/shared/hec_sender.py \
  --marketplace-parser marketplace-fortinetfortigate-latest \
  --count 5
```

### Available Generator Categories

```bash
# Cloud Infrastructure (AWS, GCP, Azure)
python event_generators/cloud_infrastructure/aws_cloudtrail.py

# Network Security (Firewalls, NDR)
python event_generators/network_security/cisco_firewall_threat_defense.py

# Endpoint Security (EDR, AV)
python event_generators/endpoint_security/sentinelone_endpoint.py

# Identity & Access (IAM, SSO)
python event_generators/identity_access/okta_authentication.py

# Email Security
python event_generators/email_security/proofpoint.py

# Web Security (WAF, Proxy)
python event_generators/web_security/cloudflare_waf.py

# Infrastructure (Backup, DevOps)
python event_generators/infrastructure/github_audit.py
```

## 🧪 Testing Your Setup

### Run Comprehensive Tests

```bash
# Test all generators
python testing/comprehensive_generator_test.py

# Validate parsers
python testing/validation/final_parser_validation.py
```

### Create a Test Scenario

```bash
# Generate a quick attack scenario
python scenarios/quick_scenario.py
```

## 📊 Understanding the Output

### Generator Output Format

All generators produce events with:
- **Star Trek themed data** (jean.picard@starfleet.corp)
- **Recent timestamps** (last 10 minutes)
- **Realistic field values**
- **Format appropriate for parser** (JSON, Syslog, CSV, KeyValue)

Example output:
```json
{
  "timestamp": "2025-01-29T10:45:32Z",
  "user": "jean.picard@starfleet.corp",
  "source_ip": "10.0.0.50",
  "action": "login_success",
  "device": "ENTERPRISE-BRIDGE-01"
}
```

## 🎭 Star Trek Theme

All test data uses Star Trek characters and systems:
- **Users**: jean.picard, worf.security, data.android, jordy.laforge
- **Domain**: starfleet.corp
- **Devices**: ENTERPRISE-BRIDGE-01, ENTERPRISE-SECURITY-01
- **IPs**: 10.0.0.x range for internal

## 🔍 Common Tasks

### List All Available Generators

```bash
# See all generators
ls -la event_generators/*/*.py | grep -v __pycache__ | wc -l
# Output: 100+ generators
```

### Send Events to Different Parsers

```bash
# Community parser
python event_generators/shared/hec_sender.py --product aws_cloudtrail --count 5

# Marketplace parser (better field extraction)
python event_generators/shared/hec_sender.py \
  --marketplace-parser marketplace-awscloudtrail-latest \
  --count 5
```

### Generate Bulk Events

```bash
# Send events from multiple generators
for product in crowdstrike_falcon fortinet_fortigate okta_authentication; do
  python event_generators/shared/hec_sender.py --product $product --count 10
done
```

## 🐛 Troubleshooting

### Issue: Module Not Found

```bash
# Error: ModuleNotFoundError
# Solution: Ensure virtual environment is activated
source .venv/bin/activate
```

### Issue: HEC Token Invalid

```bash
# Error: 401 Unauthorized
# Solution: Check your S1_HEC_TOKEN environment variable
echo $S1_HEC_TOKEN
```

### Issue: Generator Fails

```bash
# Error: Generator error
# Solution: Check the generator directly
python -c "from event_generators.endpoint_security.crowdstrike_falcon import crowdstrike_log; print(crowdstrike_log())"
```

## 📚 Next Steps

Now that you're set up:

1. **[Create a Generator](../generators/generator-tutorial.md)** - Build your own event generator
2. **[Develop a Parser](../parsers/parser-tutorial.md)** - Create custom parsers
3. **[Run Scenarios](../user-guide/scenarios.md)** - Simulate attack campaigns
4. **[Contribute Code](contributing.md)** - Submit improvements

## 🤝 Getting Help

- Check [Troubleshooting Guide](../user-guide/troubleshooting.md)
- Open an [Issue](https://github.com/natesmalley/jarvis_coding/issues)
- Review [Architecture Docs](../architecture/current_state_analysis.md)

## ✅ Setup Complete!

You're now ready to:
- Generate security events from 100+ products
- Send events to SentinelOne for parsing
- Create custom generators and scenarios
- Contribute to the project

**Next**: Learn to [create your own generator](../generators/generator-tutorial.md) →