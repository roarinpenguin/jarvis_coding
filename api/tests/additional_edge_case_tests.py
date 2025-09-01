#!/usr/bin/env python3
"""
Additional Edge Case Tests for API QA Validation
Extended testing beyond the core comprehensive test suite
"""

import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class AdditionalEdgeCaseTests:
    """Additional edge case and stress tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.admin_key = "admin-test-key-123456789012345678901234"
        self.read_key = "read-test-key-1234567890123456789012345"
        self.headers = {"X-API-Key": self.admin_key, "Content-Type": "application/json"}
        
    def test_extremely_large_request_payload(self):
        """Test handling of extremely large request payloads"""
        print("Testing extremely large request payload...")
        
        # Create a very large payload
        large_data = {
            "count": 1,
            "format": "json",
            "star_trek_theme": True,
            "large_field": "x" * 10000  # 10KB of data
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/generators/crowdstrike_falcon/execute",
                headers=self.headers,
                json=large_data,
                timeout=30
            )
            
            # Should either handle it gracefully or return appropriate error
            if response.status_code in [200, 201, 413, 422]:  # 413 = Payload Too Large
                print(f"✅ Large payload handled appropriately: {response.status_code}")
                return True
            else:
                print(f"❌ Unexpected response to large payload: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Large payload test failed: {e}")
            return False
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters"""
        print("Testing Unicode and special characters...")
        
        special_chars = {
            "search": "🚀💫🖖 Jean-Luc Picard αβγ 中文 العربية русский",
            "category": "test'<>\"&",
            "vendor": "NULL\x00\r\n\t"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/generators",
                headers=self.headers,
                params=special_chars,
                timeout=30
            )
            
            if response.status_code in [200, 400, 422]:
                print("✅ Unicode/special chars handled appropriately")
                return True
            else:
                print(f"❌ Unexpected response to special chars: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Unicode test failed: {e}")
            return False
    
    def test_rapid_authentication_switching(self):
        """Test rapid switching between different API keys"""
        print("Testing rapid authentication key switching...")
        
        keys = [
            self.admin_key,
            self.read_key,
            "invalid-key-123",
            self.admin_key
        ]
        
        results = []
        for key in keys:
            headers = {"X-API-Key": key, "Content-Type": "application/json"}
            try:
                response = requests.get(
                    f"{self.base_url}/api/v1/generators",
                    headers=headers,
                    timeout=5
                )
                results.append(response.status_code)
            except Exception as e:
                results.append(0)
            time.sleep(0.1)  # Brief pause
        
        # Expected: [200, 200, 403, 200]
        expected = [200, 200, 403, 200]
        if results == expected:
            print("✅ Rapid auth switching handled correctly")
            return True
        else:
            print(f"❌ Unexpected auth pattern: expected {expected}, got {results}")
            return False
    
    def test_concurrent_different_operations(self):
        """Test concurrent different operations to check for race conditions"""
        print("Testing concurrent mixed operations...")
        
        def execute_generator():
            return requests.post(
                f"{self.base_url}/api/v1/generators/crowdstrike_falcon/execute",
                headers=self.headers,
                json={"count": 1, "format": "json"},
                timeout=30
            )
        
        def list_generators():
            return requests.get(
                f"{self.base_url}/api/v1/generators",
                headers=self.headers,
                timeout=30
            )
        
        def get_details():
            return requests.get(
                f"{self.base_url}/api/v1/generators/okta_authentication",
                headers=self.headers,
                timeout=30
            )
        
        operations = [execute_generator, list_generators, get_details] * 3
        
        try:
            with ThreadPoolExecutor(max_workers=9) as executor:
                futures = [executor.submit(op) for op in operations]
                responses = [future.result() for future in as_completed(futures)]
            
            success_count = sum(1 for r in responses if r.status_code == 200)
            
            if success_count >= 7:  # Allow some failures
                print(f"✅ Concurrent operations successful: {success_count}/9")
                return True
            else:
                print(f"❌ Too many concurrent operation failures: {success_count}/9")
                return False
                
        except Exception as e:
            print(f"❌ Concurrent operations test failed: {e}")
            return False
    
    def test_malformed_http_headers(self):
        """Test handling of malformed HTTP headers"""
        print("Testing malformed HTTP headers...")
        
        malformed_headers = {
            "X-API-Key": self.admin_key,
            "Content-Type": "application/json",
            "X-Custom\x00Header": "test",
            "X-Long-Header": "x" * 8192,  # Very long header
            "\x7f\x80\x81": "invalid"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/generators",
                headers=malformed_headers,
                timeout=30
            )
            
            # Should handle malformed headers gracefully
            if response.status_code in [200, 400, 413]:
                print("✅ Malformed headers handled appropriately")
                return True
            else:
                print(f"❌ Unexpected response to malformed headers: {response.status_code}")
                return False
                
        except Exception as e:
            # Requests library might reject malformed headers, which is acceptable
            print("✅ Malformed headers rejected by client (expected)")
            return True
    
    def test_deep_nesting_in_json(self):
        """Test deeply nested JSON structures"""
        print("Testing deeply nested JSON...")
        
        # Create deeply nested object
        nested = {"value": "test"}
        for i in range(50):  # 50 levels deep
            nested = {"level": i, "nested": nested}
        
        payload = {
            "count": 1,
            "format": "json",
            "deep_nested": nested
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/generators/crowdstrike_falcon/execute",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201, 400, 422, 413]:
                print("✅ Deep nesting handled appropriately")
                return True
            else:
                print(f"❌ Unexpected response to deep nesting: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Deep nesting test failed: {e}")
            return False
    
    def test_timeout_and_slow_requests(self):
        """Test timeout handling and slow request scenarios"""
        print("Testing timeout handling...")
        
        # Test with very short timeout
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/generators",
                headers=self.headers,
                timeout=0.001  # 1ms timeout - should fail
            )
            print("❌ Request should have timed out but didn't")
            return False
        except requests.exceptions.Timeout:
            print("✅ Short timeout handled correctly")
        except Exception as e:
            print(f"✅ Timeout or connection error handled: {type(e).__name__}")
        
        # Test normal request after timeout
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/generators",
                headers=self.headers,
                timeout=30
            )
            if response.status_code == 200:
                print("✅ Normal request works after timeout test")
                return True
            else:
                print(f"❌ Normal request failed after timeout: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Normal request after timeout failed: {e}")
            return False
    
    def run_all_additional_tests(self):
        """Run all additional edge case tests"""
        print("🧪 Running Additional Edge Case Tests")
        print("=" * 50)
        
        tests = [
            self.test_extremely_large_request_payload,
            self.test_unicode_and_special_characters,
            self.test_rapid_authentication_switching,
            self.test_concurrent_different_operations,
            self.test_malformed_http_headers,
            self.test_deep_nesting_in_json,
            self.test_timeout_and_slow_requests
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
                results.append(False)
            print()
        
        passed = sum(results)
        total = len(results)
        
        print(f"📊 Additional Edge Case Tests Summary:")
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        print(f"📈 Success Rate: {(passed/total)*100:.1f}%")
        
        return passed, total

if __name__ == "__main__":
    import subprocess
    import time
    import os
    
    # Start API server
    print("📡 Starting API server for edge case testing...")
    env = os.environ.copy()
    env.update({
        "DISABLE_AUTH": "false",
        "JARVIS_ADMIN_KEYS": "admin-test-key-123456789012345678901234",
        "JARVIS_WRITE_KEYS": "write-test-key-123456789012345678901234",
        "JARVIS_READ_KEYS": "read-test-key-1234567890123456789012345",
        "RATE_LIMIT_ADMIN": "1000",
        "RATE_LIMIT_WRITE": "500",
        "RATE_LIMIT_READ": "100"
    })
    
    api_dir = "/Users/nathanial.smalley/projects/jarvis_coding/api"
    server_process = subprocess.Popen(
        ["/opt/homebrew/bin/python3", "start_api.py"],
        cwd=api_dir,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Wait for server to start
    
    try:
        # Run additional tests
        tester = AdditionalEdgeCaseTests()
        passed, total = tester.run_all_additional_tests()
        
        if passed == total:
            print("\n🏆 All additional edge case tests passed!")
        else:
            print(f"\n⚠️  Some edge case tests failed: {passed}/{total}")
            
    finally:
        # Stop server
        server_process.terminate()
        server_process.wait(timeout=10)
        print("\n🛑 API server stopped")