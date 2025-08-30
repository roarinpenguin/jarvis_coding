#!/usr/bin/env python3
"""
Test authentication for Jarvis Coding API
"""
import requests
import sys
import os

API_BASE = "http://localhost:8000"

def test_no_auth():
    """Test requests without authentication"""
    print("\n🧪 Testing without authentication...")
    
    # Try to access protected endpoint
    response = requests.get(f"{API_BASE}/api/v1/generators")
    
    if response.status_code == 403:
        print("   ✅ Correctly rejected - authentication required")
        return True
    elif response.status_code == 200:
        print("   ⚠️  Authentication might be disabled")
        return True
    else:
        print(f"   ❌ Unexpected status: {response.status_code}")
        return False


def test_invalid_auth():
    """Test with invalid API key"""
    print("\n🧪 Testing with invalid API key...")
    
    headers = {"X-API-Key": "invalid-key-12345"}
    response = requests.get(f"{API_BASE}/api/v1/generators", headers=headers)
    
    if response.status_code == 403:
        print("   ✅ Correctly rejected invalid key")
        return True
    else:
        print(f"   ❌ Should reject invalid key, got: {response.status_code}")
        return False


def test_valid_auth_header(api_key):
    """Test with valid API key in header"""
    print("\n🧪 Testing with valid API key (header)...")
    
    headers = {"X-API-Key": api_key}
    response = requests.get(f"{API_BASE}/api/v1/generators?per_page=1", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Authenticated successfully")
        print(f"   ✅ Found {data['data']['total']} generators")
        return True
    else:
        print(f"   ❌ Authentication failed: {response.status_code}")
        return False


def test_valid_auth_query(api_key):
    """Test with valid API key in query parameter"""
    print("\n🧪 Testing with valid API key (query param)...")
    
    response = requests.get(f"{API_BASE}/api/v1/generators?api_key={api_key}&per_page=1")
    
    if response.status_code == 200:
        print("   ✅ Query parameter authentication works")
        return True
    else:
        print(f"   ❌ Query auth failed: {response.status_code}")
        return False


def test_read_access(api_key):
    """Test read-only operations"""
    print("\n🧪 Testing read access...")
    
    headers = {"X-API-Key": api_key}
    
    # Test various read endpoints
    endpoints = [
        "/api/v1/generators",
        "/api/v1/generators/categories",
        "/api/v1/health"
    ]
    
    for endpoint in endpoints:
        response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
        if response.status_code == 200:
            print(f"   ✅ Can read {endpoint}")
        else:
            print(f"   ❌ Cannot read {endpoint}: {response.status_code}")
            return False
    
    return True


def test_write_access(api_key, should_succeed=True):
    """Test write operations"""
    print(f"\n🧪 Testing write access (should {'succeed' if should_succeed else 'fail'})...")
    
    headers = {"X-API-Key": api_key}
    
    # Try to execute a generator
    response = requests.post(
        f"{API_BASE}/api/v1/generators/crowdstrike_falcon/execute",
        headers=headers,
        json={"count": 1}
    )
    
    if should_succeed:
        if response.status_code == 200:
            print("   ✅ Write access granted")
            return True
        else:
            print(f"   ❌ Write access denied: {response.status_code}")
            return False
    else:
        if response.status_code == 403:
            print("   ✅ Write access correctly denied")
            return True
        else:
            print(f"   ❌ Should deny write access, got: {response.status_code}")
            return False


def test_rate_limiting(api_key, limit=10):
    """Test rate limiting"""
    print(f"\n🧪 Testing rate limiting (making {limit + 5} requests)...")
    
    headers = {"X-API-Key": api_key}
    rate_limited = False
    
    for i in range(limit + 5):
        response = requests.get(f"{API_BASE}/api/v1/generators/categories", headers=headers)
        
        if response.status_code == 429:
            print(f"   ✅ Rate limited after {i} requests")
            rate_limited = True
            break
        elif response.status_code != 200:
            print(f"   ❌ Unexpected error: {response.status_code}")
            return False
    
    if not rate_limited:
        print(f"   ⚠️  Rate limiting might be disabled or limit is > {limit + 5}")
    
    return True


def main():
    """Run authentication tests"""
    print("=" * 50)
    print("🔐 Jarvis Coding API Authentication Tests")
    print("=" * 50)
    
    # Check if auth is disabled
    check_response = requests.get(f"{API_BASE}/")
    if check_response.status_code != 200:
        print("❌ API is not running. Start it with: python start_api.py")
        sys.exit(1)
    
    # Get API key from environment or use default
    admin_key = os.getenv("JARVIS_ADMIN_KEYS", "development-key-change-in-production")
    read_key = os.getenv("JARVIS_READ_KEYS", admin_key)  # Use admin key if no read key
    
    print(f"\nUsing API keys from environment variables")
    print(f"Admin key prefix: {admin_key[:8]}...")
    
    # Check if auth is enabled
    response = requests.get(f"{API_BASE}/api/v1/generators")
    auth_enabled = response.status_code == 403
    
    if not auth_enabled:
        print("\n⚠️  WARNING: Authentication appears to be DISABLED!")
        print("   Set DISABLE_AUTH=false to enable authentication")
        print("\n   Running limited tests...")
        
        # Test that endpoints work without auth
        test_valid_auth_header("")  # Empty key should work if auth disabled
    else:
        print("\n✅ Authentication is ENABLED")
        
        # Run all tests
        tests_passed = 0
        tests_total = 0
        
        # Test 1: No auth
        tests_total += 1
        if test_no_auth():
            tests_passed += 1
        
        # Test 2: Invalid auth
        tests_total += 1
        if test_invalid_auth():
            tests_passed += 1
        
        # Test 3: Valid auth (header)
        tests_total += 1
        if test_valid_auth_header(admin_key):
            tests_passed += 1
        
        # Test 4: Valid auth (query)
        tests_total += 1
        if test_valid_auth_query(admin_key):
            tests_passed += 1
        
        # Test 5: Read access
        tests_total += 1
        if test_read_access(admin_key):
            tests_passed += 1
        
        # Test 6: Write access (admin should have it)
        tests_total += 1
        if test_write_access(admin_key, should_succeed=True):
            tests_passed += 1
        
        # Test 7: Write access with read-only key (if different from admin)
        if read_key != admin_key:
            tests_total += 1
            if test_write_access(read_key, should_succeed=False):
                tests_passed += 1
        
        # Test 8: Rate limiting (optional, may be high for admin)
        # Commenting out as admin typically has high limits
        # tests_total += 1
        # if test_rate_limiting(admin_key, limit=100):
        #     tests_passed += 1
        
        print("\n" + "=" * 50)
        print(f"📊 Results: {tests_passed}/{tests_total} tests passed")
        
        if tests_passed == tests_total:
            print("✅ All authentication tests passed!")
            return 0
        else:
            print(f"❌ {tests_total - tests_passed} tests failed")
            return 1
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Is it running?")
        print("   Start with: python start_api.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)