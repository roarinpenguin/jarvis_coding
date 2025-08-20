#!/usr/bin/env python3
"""
Test HEC Connection and SSL/TLS Issues
======================================
This script helps diagnose and fix SSL connection issues with SentinelOne HEC endpoint.
"""

import os
import sys
import json
import requests
import ssl
import socket
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings for testing
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def test_basic_connection():
    """Test basic network connectivity"""
    print("🔍 Testing basic network connectivity...")
    
    host = "ingest.us1.sentinelone.net"
    port = 443
    
    try:
        # Test DNS resolution
        ip = socket.gethostbyname(host)
        print(f"✅ DNS resolution successful: {host} -> {ip}")
        
        # Test socket connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()
        
        if result == 0:
            print(f"✅ Socket connection successful to {host}:{port}")
            return True
        else:
            print(f"❌ Socket connection failed to {host}:{port}")
            return False
            
    except socket.gaierror:
        print(f"❌ DNS resolution failed for {host}")
        return False
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def test_ssl_connection():
    """Test SSL/TLS connection"""
    print("\n🔒 Testing SSL/TLS connection...")
    
    host = "ingest.us1.sentinelone.net"
    port = 443
    
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"✅ SSL connection successful")
                print(f"   Protocol: {ssock.version()}")
                print(f"   Cipher: {ssock.cipher()}")
                return True
    except ssl.SSLError as e:
        print(f"❌ SSL Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def test_hec_with_different_methods():
    """Test HEC connection with various configurations"""
    print("\n🚀 Testing HEC connection methods...")
    
    token = os.environ.get('S1_HEC_TOKEN', '')
    if not token:
        print("❌ S1_HEC_TOKEN not set")
        return
    
    base_url = "https://ingest.us1.sentinelone.net"
    test_event = {
        "event": {
            "message": "Connection test",
            "source": "test_script",
            "sourcetype": "test"
        },
        "time": 1234567890
    }
    
    headers = {
        "Authorization": f"Splunk {token}",
        "Content-Type": "application/json"
    }
    
    # Method 1: Standard HTTPS
    print("\n1️⃣ Testing standard HTTPS...")
    try:
        response = requests.post(
            f"{base_url}/services/collector/event",
            headers=headers,
            json=test_event,
            timeout=10
        )
        print(f"✅ Standard HTTPS: Status {response.status_code}")
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 2: With SSL verification disabled (for testing only)
    print("\n2️⃣ Testing with SSL verification disabled...")
    try:
        response = requests.post(
            f"{base_url}/services/collector/event",
            headers=headers,
            json=test_event,
            timeout=10,
            verify=False
        )
        print(f"✅ No SSL verify: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Method 3: With custom SSL context
    print("\n3️⃣ Testing with custom SSL context...")
    try:
        session = requests.Session()
        session.headers.update(headers)
        
        # Try with TLS 1.2
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.ssl_ import create_urllib3_context
        
        class TLSAdapter(HTTPAdapter):
            def init_poolmanager(self, *args, **kwargs):
                ctx = create_urllib3_context()
                ctx.set_ciphers('DEFAULT@SECLEVEL=1')
                kwargs['ssl_context'] = ctx
                return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)
        
        session.mount('https://', TLSAdapter())
        response = session.post(
            f"{base_url}/services/collector/event",
            json=test_event,
            timeout=10
        )
        print(f"✅ Custom SSL: Status {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def test_alternative_endpoints():
    """Test alternative HEC endpoints"""
    print("\n🌐 Testing alternative endpoints...")
    
    token = os.environ.get('S1_HEC_TOKEN', '')
    if not token:
        print("❌ S1_HEC_TOKEN not set")
        return
    
    # Alternative endpoints to try
    endpoints = [
        "https://ingest.us1.sentinelone.net",
        "https://ingest.usea1.sentinelone.net",
        "https://ingest.sentinelone.net"
    ]
    
    test_event = {
        "event": {"message": "Endpoint test"},
        "time": 1234567890
    }
    
    headers = {
        "Authorization": f"Splunk {token}",
        "Content-Type": "application/json"
    }
    
    for endpoint in endpoints:
        print(f"\nTesting: {endpoint}")
        try:
            response = requests.post(
                f"{endpoint}/services/collector/event",
                headers=headers,
                json=test_event,
                timeout=5,
                verify=False
            )
            print(f"  ✅ Response: {response.status_code}")
        except Exception as e:
            print(f"  ❌ Failed: {str(e)[:100]}")

def main():
    print("🔧 SentinelOne HEC Connection Diagnostic Tool")
    print("=" * 60)
    
    # Run all tests
    test_basic_connection()
    test_ssl_connection()
    test_hec_with_different_methods()
    test_alternative_endpoints()
    
    print("\n" + "=" * 60)
    print("📋 RECOMMENDATIONS:")
    print("1. If SSL errors persist, try using verify=False temporarily")
    print("2. Check if you're behind a corporate proxy/firewall")
    print("3. Try using curl with -k flag to bypass SSL verification")
    print("4. Consider saving events to file and using batch upload later")
    print("5. Contact SentinelOne support if the issue persists")

if __name__ == "__main__":
    main()