#!/usr/bin/env python3
"""
SentinelOne Configuration Setup
Helps configure API credentials and test connectivity
"""
import os
import json
import requests
from urllib.parse import urljoin

def setup_credentials(service_account: bool = False):
    """Interactive setup of SentinelOne credentials
    
    Args:
        service_account: If True, use service account specific prompts
    """
    if service_account:
        print("SentinelOne Service Account Configuration Setup")
        print("=" * 50)
        print("ℹ️  Setting up automated service account for parser testing")
        print("📖 See SERVICE_ACCOUNT_SETUP.md for detailed instructions")
    else:
        print("SentinelOne API Configuration Setup")
        print("=" * 40)
    
    # Get current values
    current_url = os.getenv('S1_API_URL', '')
    current_api_token = os.getenv('S1_API_TOKEN', '')
    current_hec_token = os.getenv('S1_HEC_TOKEN', '')
    current_service_user_id = os.getenv('S1_SERVICE_USER_ID', '')
    current_account_id = os.getenv('S1_ACCOUNT_ID', '')
    current_site_id = os.getenv('S1_SITE_ID', '')
    
    # Console URL
    print(f"\n1. SentinelOne Console URL")
    print(f"   Current: {current_url or 'Not set'}")
    api_url = input("   Enter console URL (e.g., https://yourinstance.sentinelone.net): ").strip()
    if not api_url:
        api_url = current_url
    
    # API Token
    print(f"\n2. SentinelOne {'Service Account ' if service_account else ''}API Token")
    if service_account:
        print("   ⚠️  Use the API token generated for your service account")
        print("   📋 Required permissions: Viewer role + Data Visibility access")
    print(f"   Current: {'*' * min(len(current_api_token), 20) if current_api_token else 'Not set'}")
    api_token = input("   Enter API token: ").strip()
    if not api_token:
        api_token = current_api_token
    
    # HEC Token
    print(f"\n3. SentinelOne HEC Token")
    if service_account:
        print("   💡 Create a dedicated HEC endpoint for parser testing")
    print(f"   Current: {'*' * min(len(current_hec_token), 20) if current_hec_token else 'Not set'}")
    hec_token = input("   Enter HEC token: ").strip()
    if not hec_token:
        hec_token = current_hec_token
    
    # Service account specific fields
    service_user_id = None
    account_id = None
    site_id = None
    
    if service_account:
        print(f"\n4. Service Account User ID (Optional)")
        print(f"   📝 For tracking purposes in audit logs")
        print(f"   Current: {current_service_user_id or 'Not set'}")
        service_user_id = input("   Enter service user ID (press Enter to skip): ").strip()
        if not service_user_id:
            service_user_id = current_service_user_id
        
        print(f"\n5. Account ID (Optional)")
        print(f"   🔒 Scope operations to specific account")
        print(f"   Current: {current_account_id or 'Not set'}")
        account_id = input("   Enter account ID (press Enter to skip): ").strip()
        if not account_id:
            account_id = current_account_id
            
        print(f"\n6. Site ID (Optional)")
        print(f"   🏢 Scope operations to specific site")
        print(f"   Current: {current_site_id or 'Not set'}")
        site_id = input("   Enter site ID (press Enter to skip): ").strip()
        if not site_id:
            site_id = current_site_id
    
    return api_url, api_token, hec_token, service_user_id, account_id, site_id

def test_api_connectivity(api_url: str, api_token: str) -> bool:
    """Test SentinelOne API connectivity"""
    print("\nTesting API connectivity...")
    
    try:
        headers = {
            'Authorization': f'ApiToken {api_token}',
            'Content-Type': 'application/json'
        }
        
        # Test with a simple API call (get account info)
        test_url = urljoin(api_url, '/web/api/v2.1/accounts')
        response = requests.get(test_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API Connection successful!")
            
            # Show account info if available
            if 'data' in data and data['data']:
                account = data['data'][0]
                print(f"   Account: {account.get('name', 'Unknown')}")
                print(f"   ID: {account.get('id', 'Unknown')}")
            
            return True
        else:
            print(f"❌ API Connection failed: HTTP {response.status_code}")
            if response.text:
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data.get('message', response.text)}")
                except:
                    print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ API Connection failed: {e}")
        return False

def test_hec_connectivity(api_url: str, hec_token: str) -> bool:
    """Test SentinelOne HEC connectivity"""
    print("\nTesting HEC connectivity...")
    
    try:
        headers = {
            'Authorization': f'Splunk {hec_token}',
            'Content-Type': 'application/json'
        }
        
        # Test with a simple test event
        hec_url = urljoin(api_url, '/hec/event')
        test_event = {
            'event': {
                'message': 'Test event from parser validation tool',
                'test': True
            },
            'time': int(__import__('time').time()),
            'source': 'parser_validation_test',
            'sourcetype': 'json'
        }
        
        response = requests.post(hec_url, headers=headers, json=test_event, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ HEC Connection successful!")
            return True
        else:
            print(f"❌ HEC Connection failed: HTTP {response.status_code}")
            if response.text:
                print(f"   Response: {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ HEC Connection failed: {e}")
        return False

def save_config(api_url: str, api_token: str, hec_token: str, 
                service_user_id: str = None, account_id: str = None, site_id: str = None,
                service_account: bool = False):
    """Save configuration to environment file"""
    config_file = '.env.s1'
    
    config_content = f"""# SentinelOne {'Service Account ' if service_account else ''}API Configuration
# Generated on {datetime.now().isoformat()}

S1_API_URL={api_url}
S1_API_TOKEN={api_token}
S1_HEC_TOKEN={hec_token}
"""
    
    # Add service account specific variables if provided
    if service_user_id:
        config_content += f"S1_SERVICE_USER_ID={service_user_id}\n"
    if account_id:
        config_content += f"S1_ACCOUNT_ID={account_id}\n"
    if site_id:
        config_content += f"S1_SITE_ID={site_id}\n"
    
    if service_account:
        config_content += f"""
# Service Account Information
# - Use dedicated service account with minimal required permissions
# - Rotate tokens regularly (quarterly recommended)
# - Monitor usage through SentinelOne audit logs
"""
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"\n✅ Configuration saved to {config_file}")
    print("\nTo use these settings, run:")
    print(f"   source {config_file}")
    
    export_vars = ["S1_API_URL", "S1_API_TOKEN", "S1_HEC_TOKEN"]
    if service_user_id:
        export_vars.append("S1_SERVICE_USER_ID")
    if account_id:
        export_vars.append("S1_ACCOUNT_ID") 
    if site_id:
        export_vars.append("S1_SITE_ID")
        
    print(f"   export {' '.join(export_vars)}")

def load_existing_config():
    """Load existing configuration from .env.s1"""
    config_file = '.env.s1'
    
    if os.path.exists(config_file):
        print(f"Loading existing configuration from {config_file}...")
        
        config = {}
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    config[key] = value
        
        # Set environment variables
        for key, value in config.items():
            os.environ[key] = value
        
        return True
    
    return False

def main():
    """Main configuration setup"""
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description='SentinelOne API Configuration Setup')
    parser.add_argument('--test-only', action='store_true', help='Test existing configuration only')
    parser.add_argument('--load-config', action='store_true', help='Load from existing .env.s1 file')
    parser.add_argument('--service-account', action='store_true', help='Set up service account configuration')
    parser.add_argument('--validate-service-account', action='store_true', help='Validate service account permissions')
    
    args = parser.parse_args()
    
    if args.load_config:
        if load_existing_config():
            print("✅ Configuration loaded from .env.s1")
        else:
            print("❌ No .env.s1 file found")
        return
    
    if args.validate_service_account:
        # Validate existing service account
        try:
            from s1_dv_api_client import SentinelOneDVClient
            client = SentinelOneDVClient()
            validation = client.validate_service_account()
            
            print("🔍 Service Account Validation Results:")
            print("=" * 45)
            
            if validation['valid']:
                print("✅ Service account is properly configured!")
                print(f"   Account: {validation['account_info'].get('account_name', 'Unknown')}")
                print(f"   Permissions: {list(validation['permissions'].keys())}")
                print(f"   DV Access: {'✅' if validation['dv_access'] else '❌'}")
                print(f"   HEC Access: {'✅' if validation['hec_access'] else '❌'}")
            else:
                print("❌ Service account configuration issues:")
                for error in validation['errors']:
                    print(f"   • {error}")
                print("\n💡 Run with --service-account to reconfigure")
                
        except Exception as e:
            print(f"❌ Validation failed: {e}")
        return
    
    if args.test_only:
        # Test existing environment variables
        api_url = os.getenv('S1_API_URL')
        api_token = os.getenv('S1_API_TOKEN') 
        hec_token = os.getenv('S1_HEC_TOKEN')
        
        if not all([api_url, api_token, hec_token]):
            print("❌ Missing environment variables. Run without --test-only to configure.")
            return
        
        api_ok = test_api_connectivity(api_url, api_token)
        hec_ok = test_hec_connectivity(api_url, hec_token)
        
        if api_ok and hec_ok:
            print("\n✅ All connections successful! Ready for parser testing.")
        else:
            print("\n❌ Some connections failed. Check your configuration.")
        
        return
    
    # Interactive setup
    if args.service_account:
        print("🤖 Setting up service account for automated parser testing")
        print("📖 For detailed instructions, see SERVICE_ACCOUNT_SETUP.md\n")
    
    credentials = setup_credentials(service_account=args.service_account)
    api_url, api_token, hec_token = credentials[:3]
    service_user_id, account_id, site_id = credentials[3:] if len(credentials) > 3 else (None, None, None)
    
    if not all([api_url, api_token, hec_token]):
        print("❌ Configuration incomplete. Required fields: URL, API token, HEC token.")
        return
    
    # Test connectivity
    api_ok = test_api_connectivity(api_url, api_token)
    hec_ok = test_hec_connectivity(api_url, hec_token)
    
    if api_ok and hec_ok:
        save_config(api_url, api_token, hec_token, service_user_id, account_id, site_id, 
                   service_account=args.service_account)
        
        if args.service_account:
            print("\n🎉 Service account setup complete!")
            print("🔄 Next steps:")
            print("   1. Test service account: python s1_config_setup.py --validate-service-account")
            print("   2. Run parser tests: python comprehensive_parser_tester.py --fixed")
        else:
            print("\n🎉 Setup complete! You can now use the parser validation tools.")
    else:
        print("\n❌ Setup failed due to connectivity issues. Please check your credentials and try again.")

if __name__ == "__main__":
    main()