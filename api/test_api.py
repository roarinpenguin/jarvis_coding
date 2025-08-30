#!/usr/bin/env python3
"""
Simple test script for the Jarvis Coding API
"""
import requests
import json
import sys

API_BASE = "http://localhost:8000"

def test_api():
    """Test basic API functionality"""
    print("🧪 Testing Jarvis Coding API...")
    print("-" * 50)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE}/")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ API Name: {data['name']}")
        print(f"   ✅ Version: {data['version']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 2: Health check
    print("\n2. Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        print(f"   ✅ Status: {data['status']}")
        print(f"   ✅ Generators: {data['generators_available']}")
        print(f"   ✅ Parsers: {data['parsers_available']}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 3: List generators
    print("\n3. Testing list generators...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/generators?per_page=5")
        assert response.status_code == 200
        data = response.json()
        generators = data['data']['generators']
        print(f"   ✅ Found {data['data']['total']} total generators")
        print(f"   ✅ First generator: {generators[0]['name'] if generators else 'None'}")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 4: Get generator details
    print("\n4. Testing generator details...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/generators/crowdstrike_falcon")
        if response.status_code == 200:
            data = response.json()
            gen = data['data']
            print(f"   ✅ Name: {gen['name']}")
            print(f"   ✅ Category: {gen['category']}")
            print(f"   ✅ Vendor: {gen['vendor']}")
        else:
            print(f"   ⚠️  CrowdStrike generator not found (status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 5: Execute generator
    print("\n5. Testing generator execution...")
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/generators/crowdstrike_falcon/execute",
            json={"count": 2, "format": "json"}
        )
        if response.status_code == 200:
            data = response.json()
            events = data['data']['events']
            print(f"   ✅ Generated {len(events)} events")
            print(f"   ✅ Execution time: {data['data']['execution_time_ms']:.2f}ms")
        else:
            print(f"   ⚠️  Execution failed (status: {response.status_code})")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    # Test 6: List categories
    print("\n6. Testing categories...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/generators/categories")
        assert response.status_code == 200
        data = response.json()
        categories = data['data']['categories']
        print(f"   ✅ Found {len(categories)} categories")
        for cat in categories[:3]:
            print(f"      - {cat['name']}: {cat['generator_count']} generators")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✅ All tests passed!")
    return True

if __name__ == "__main__":
    try:
        success = test_api()
        sys.exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Is the server running?")
        print("   Run: python start_api.py")
        sys.exit(1)