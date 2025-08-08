# SentinelOne Service Account Setup Guide

This guide explains how to set up a service account for automated parser testing with SentinelOne.

## Overview

Service accounts provide secure, programmatic access to SentinelOne APIs without requiring individual user credentials. For parser testing, we need:

1. **Management API Access** - Query Data Visibility, manage parsers
2. **HEC (HTTP Event Collector) Access** - Send test events for parsing
3. **Appropriate Permissions** - Read accounts, execute queries, send data

## Step 1: Create Service Account

### In SentinelOne Management Console:

1. **Navigate to Settings**
   - Go to **Settings** > **Users**
   - Click **Actions** > **Create Service User**

2. **Configure Service User**
   - **Name**: `Parser Testing Service Account`
   - **Email**: `parser-testing@yourcompany.com` (use your domain)
   - **Description**: `Automated service account for parser testing and validation`

3. **Set Permissions**
   - **Role**: `Viewer` (minimum required)
   - **Scope**: 
     - Account level for multi-tenant testing
     - Site level for single-site testing
   - **Additional Permissions**:
     - ✅ **Data Visibility**: Read access
     - ✅ **Deep Visibility**: Query execution
     - ✅ **Settings**: Read access (for parser management)

4. **Generate API Token**
   - Click **Generate API Token**
   - **Copy and securely store** the API token
   - ⚠️ **This token will only be shown once**

## Step 2: Configure HEC Token

### For Event Ingestion:

1. **Navigate to Data Sources**
   - Go to **Settings** > **Data Sources**
   - Click **Add Data Source** > **HTTP Event Collector (HEC)**

2. **Configure HEC Collector**
   - **Name**: `Parser Testing HEC`
   - **Description**: `HEC endpoint for parser testing events`
   - **Index**: `main` (or dedicated testing index)
   - **Sourcetype**: `json`

3. **Generate HEC Token**
   - Click **Generate Token**
   - **Copy and securely store** the HEC token
   - Note the **HEC URL** (usually `/hec/event`)

## Step 3: Environment Configuration

### Option 1: Environment Variables

Create a `.env.s1` file:

```bash
# SentinelOne Service Account Configuration
S1_API_URL=https://your-instance.sentinelone.net
S1_API_TOKEN=your-service-account-api-token-here
S1_HEC_TOKEN=your-hec-token-here
S1_SERVICE_USER_ID=service-user-id-optional
S1_ACCOUNT_ID=account-id-optional
S1_SITE_ID=site-id-optional
```

Load the environment:
```bash
source .env.s1
export S1_API_URL S1_API_TOKEN S1_HEC_TOKEN S1_SERVICE_USER_ID S1_ACCOUNT_ID S1_SITE_ID
```

### Option 2: Configuration Script

Use the provided configuration script:
```bash
python s1_config_setup.py --service-account
```

## Step 4: Validate Setup

### Test Service Account Permissions:

```python
from s1_dv_api_client import SentinelOneDVClient

# Initialize client with service account
client = SentinelOneDVClient()

# Validate permissions
validation = client.validate_service_account()

if validation['valid']:
    print("✅ Service account setup successful!")
    print(f"Account: {validation['account_info']['account_name']}")
    print(f"Permissions: {list(validation['permissions'].keys())}")
else:
    print("❌ Service account setup issues:")
    for error in validation['errors']:
        print(f"  - {error}")
```

### CLI Validation:

```bash
python s1_dv_api_client.py --test-connection
```

## Required Permissions Summary

| Component | Permission | Scope | Purpose |
|-----------|------------|-------|---------|
| **Management API** | Viewer | Account/Site | Read account info, sites |
| **Data Visibility** | DV Read | Account/Site | Query parsed events |
| **Deep Visibility** | Query Execute | Account/Site | Run DV queries |
| **HEC** | Data Input | Global | Send test events |

## Security Best Practices

### API Token Management:
- ✅ Store tokens in environment variables or secure vault
- ✅ Use separate tokens for different environments (dev/test/prod)
- ✅ Rotate tokens regularly (quarterly recommended)
- ❌ Never commit tokens to version control
- ❌ Don't use personal user accounts for automation

### Access Control:
- ✅ Use minimal required permissions
- ✅ Scope access to specific accounts/sites when possible
- ✅ Monitor service account usage through audit logs
- ✅ Disable unused service accounts

### Network Security:
- ✅ Restrict API access to specific IP ranges if possible
- ✅ Use HTTPS only (never HTTP)
- ✅ Implement proper certificate validation

## Troubleshooting

### Common Issues:

1. **403 Forbidden Errors**
   ```
   Error: API request failed: 403 Forbidden
   ```
   **Solution**: Check service account permissions, ensure DV access is enabled

2. **401 Unauthorized Errors**
   ```
   Error: API request failed: 401 Unauthorized  
   ```
   **Solution**: Verify API token is correct and not expired

3. **HEC Connection Issues**
   ```
   Error: HEC access failed: Connection refused
   ```
   **Solution**: Verify HEC token and endpoint URL, check firewall rules

4. **Data Visibility Access Denied**
   ```
   Error: Data Visibility access failed: Permission denied
   ```
   **Solution**: Enable Deep Visibility permissions for service account

### Validation Commands:

```bash
# Test basic connectivity
curl -H "Authorization: ApiToken YOUR_TOKEN" \
     "https://your-instance.sentinelone.net/web/api/v2.1/accounts"

# Test HEC endpoint
curl -H "Authorization: Splunk YOUR_HEC_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"event":{"test":true},"time":1234567890,"source":"test"}' \
     "https://your-instance.sentinelone.net/hec/event"

# Test DV query
python -c "
from s1_dv_api_client import SentinelOneDVClient
client = SentinelOneDVClient()
result = client.get_dv_events(query='dataSource.name EXISTS', limit=1)
print(f'DV Query Status: {result.status}')
"
```

## Integration with Parser Testing

Once the service account is configured, you can run comprehensive parser tests:

```bash
# Test recently fixed parsers
python comprehensive_parser_tester.py --fixed

# Test specific parser group  
python comprehensive_parser_tester.py --ping

# Test with custom parameters
python comprehensive_parser_tester.py --parser pingfederate --count 5 --wait 90
```

The service account will automatically:
1. Send test events via HEC
2. Query Data Visibility for parsed results
3. Validate field mappings and parser effectiveness
4. Generate comprehensive reports

## Support and Maintenance

### Regular Tasks:
- Monitor service account usage in SentinelOne audit logs
- Review and rotate API tokens quarterly
- Update permissions as needed for new parser types
- Test connectivity after SentinelOne updates

### Monitoring:
- Set up alerts for service account authentication failures
- Monitor parser test success rates
- Track API rate limits and usage patterns

For additional support, consult:
- SentinelOne API Documentation
- SentinelOne Support Portal
- Your SentinelOne Customer Success Manager