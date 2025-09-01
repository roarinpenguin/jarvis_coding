#!/usr/bin/env python3
"""
Comprehensive API Test Suite for Jarvis Coding API
QA Testing Framework with Authentication, Functional, and Integration Testing

This test suite provides comprehensive validation of:
- Authentication and authorization
- All API endpoints functionality
- Input validation and error handling
- Performance and load testing
- Security testing
- Integration testing between services
"""

import asyncio
import json
import time
import sys
import os
import requests
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
from pathlib import Path
import subprocess
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import string

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    category: str
    passed: bool
    duration_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict] = None
    status_code: Optional[int] = None
    response_data: Optional[Dict] = None


@dataclass
class TestReport:
    """Comprehensive test report"""
    start_time: datetime
    end_time: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    categories: Dict[str, Dict]
    results: List[TestResult]
    issues: List[Dict]
    recommendations: List[str]
    performance_metrics: Dict[str, Any]


class APITestFramework:
    """Comprehensive API Testing Framework"""
    
    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url
        
        # Test API keys for different roles
        self.test_keys = {
            "admin": "admin-test-key-123456789012345678901234",
            "write": "write-test-key-123456789012345678901234", 
            "read": "read-test-key-1234567890123456789012345",
            "invalid": "invalid-key-123456789012345678901234"
        }
        
        # Use admin key as default for functional tests
        self.api_key = api_key or self.test_keys["admin"]
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}
        self.results: List[TestResult] = []
        self.server_process: Optional[subprocess.Popen] = None
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for test framework"""
        logger = logging.getLogger("api_test_framework")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def start_api_server(self) -> bool:
        """Start the API server for testing"""
        try:
            # Set environment variables for testing
            env = os.environ.copy()
            env.update({
                "DISABLE_AUTH": "false",
                "JARVIS_ADMIN_KEYS": self.test_keys["admin"],
                "JARVIS_WRITE_KEYS": self.test_keys["write"],
                "JARVIS_READ_KEYS": self.test_keys["read"],
                "RATE_LIMIT_ADMIN": "1000",
                "RATE_LIMIT_WRITE": "500", 
                "RATE_LIMIT_READ": "100"
            })
            
            api_dir = Path(__file__).parent.parent
            self.logger.info(f"Starting API server from {api_dir}")
            
            # Use the virtual environment Python executable
            project_root = api_dir.parent
            venv_python = project_root / ".venv" / "bin" / "python"
            python_executable = str(venv_python) if venv_python.exists() else "/opt/homebrew/bin/python3"
            
            # Start server in background
            self.server_process = subprocess.Popen(
                [python_executable, "start_api.py"],
                cwd=api_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for server to start
            await asyncio.sleep(3)
            
            # Test server is responding
            try:
                response = requests.get(f"{self.base_url}/", timeout=5)
                if response.status_code == 200:
                    self.logger.info("API server started successfully")
                    return True
            except requests.RequestException:
                pass
            
            self.logger.error("Failed to start API server")
            return False
            
        except Exception as e:
            self.logger.error(f"Error starting API server: {e}")
            return False
    
    def stop_api_server(self):
        """Stop the API server"""
        if self.server_process:
            self.logger.info("Stopping API server")
            self.server_process.terminate()
            self.server_process.wait(timeout=10)
            self.server_process = None
    
    def _execute_test(self, test_func, test_name: str, category: str) -> TestResult:
        """Execute a single test and return result"""
        start_time = time.time()
        
        try:
            result = test_func()
            duration_ms = (time.time() - start_time) * 1000
            
            if isinstance(result, dict) and result.get("passed", False):
                return TestResult(
                    test_name=test_name,
                    category=category,
                    passed=True,
                    duration_ms=duration_ms,
                    details=result.get("details"),
                    status_code=result.get("status_code"),
                    response_data=result.get("response_data")
                )
            else:
                return TestResult(
                    test_name=test_name,
                    category=category,
                    passed=False,
                    duration_ms=duration_ms,
                    error_message=result.get("error") if isinstance(result, dict) else str(result),
                    details=result.get("details") if isinstance(result, dict) else None
                )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return TestResult(
                test_name=test_name,
                category=category,
                passed=False,
                duration_ms=duration_ms,
                error_message=str(e)
            )
    
    def _make_request(self, method: str, endpoint: str, headers: Dict = None, 
                     data: Dict = None, params: Dict = None) -> Dict:
        """Make HTTP request and return standardized response"""
        try:
            url = f"{self.base_url}{endpoint}"
            request_headers = headers or self.headers
            
            if method.upper() == "GET":
                response = requests.get(url, headers=request_headers, params=params, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=request_headers, json=data, params=params, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=request_headers, json=data, params=params, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=request_headers, params=params, timeout=30)
            else:
                return {"passed": False, "error": f"Unsupported method: {method}"}
            
            return {
                "passed": True,
                "status_code": response.status_code,
                "response_data": response.json() if response.content else {},
                "headers": dict(response.headers)
            }
            
        except requests.RequestException as e:
            return {"passed": False, "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"passed": False, "error": f"Unexpected error: {str(e)}"}

    # ============================================================================
    # AUTHENTICATION AND AUTHORIZATION TESTS
    # ============================================================================
    
    def test_no_auth_required_endpoints(self) -> Dict:
        """Test endpoints that don't require authentication"""
        # Root endpoint
        result = self._make_request("GET", "/")
        if not result["passed"]:
            return result
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Root endpoint returned {result['status_code']}"}
        
        # Health endpoint
        result = self._make_request("GET", "/api/v1/health")
        if not result["passed"]:
            return result
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Health endpoint returned {result['status_code']}"}
        
        return {"passed": True, "details": "Public endpoints accessible"}
    
    def test_missing_api_key(self) -> Dict:
        """Test requests without API key are rejected"""
        no_auth_headers = {"Content-Type": "application/json"}
        result = self._make_request("GET", "/api/v1/generators", headers=no_auth_headers)
        
        if result["status_code"] != 403:
            return {"passed": False, "error": f"Expected 403, got {result['status_code']}"}
        
        return {"passed": True, "details": "Missing API key properly rejected"}
    
    def test_invalid_api_key(self) -> Dict:
        """Test requests with invalid API key are rejected"""
        invalid_headers = {"X-API-Key": self.test_keys["invalid"], "Content-Type": "application/json"}
        result = self._make_request("GET", "/api/v1/generators", headers=invalid_headers)
        
        if result["status_code"] != 403:
            return {"passed": False, "error": f"Expected 403, got {result['status_code']}"}
        
        return {"passed": True, "details": "Invalid API key properly rejected"}
    
    def test_role_based_access_read(self) -> Dict:
        """Test read-only role can access read endpoints"""
        read_headers = {"X-API-Key": self.test_keys["read"], "Content-Type": "application/json"}
        result = self._make_request("GET", "/api/v1/generators", headers=read_headers)
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Read role denied access: {result['status_code']}"}
        
        return {"passed": True, "details": "Read role has proper access"}
    
    def test_role_based_access_write_denied(self) -> Dict:
        """Test read-only role cannot access write endpoints"""
        read_headers = {"X-API-Key": self.test_keys["read"], "Content-Type": "application/json"}
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute", 
                                   headers=read_headers, data={"count": 1})
        
        if result["status_code"] != 403:
            return {"passed": False, "error": f"Read role allowed write access: {result['status_code']}"}
        
        return {"passed": True, "details": "Read role properly denied write access"}
    
    def test_role_based_access_write_allowed(self) -> Dict:
        """Test write role can access write endpoints"""
        write_headers = {"X-API-Key": self.test_keys["write"], "Content-Type": "application/json"}
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute",
                                   headers=write_headers, data={"count": 1, "format": "json"})
        
        if result["status_code"] not in [200, 201]:
            return {"passed": False, "error": f"Write role denied access: {result['status_code']}"}
        
        return {"passed": True, "details": "Write role has proper access"}
    
    def test_admin_access(self) -> Dict:
        """Test admin role has full access"""
        admin_headers = {"X-API-Key": self.test_keys["admin"], "Content-Type": "application/json"}
        
        # Test read access
        result = self._make_request("GET", "/api/v1/generators", headers=admin_headers)
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Admin denied read access: {result['status_code']}"}
        
        # Test write access
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute",
                                   headers=admin_headers, data={"count": 1, "format": "json"})
        if result["status_code"] not in [200, 201]:
            return {"passed": False, "error": f"Admin denied write access: {result['status_code']}"}
        
        return {"passed": True, "details": "Admin role has full access"}

    # ============================================================================
    # FUNCTIONAL ENDPOINT TESTS
    # ============================================================================
    
    def test_list_generators(self) -> Dict:
        """Test listing all generators"""
        result = self._make_request("GET", "/api/v1/generators")
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Status code: {result['status_code']}"}
        
        data = result["response_data"]
        if not data.get("success"):
            return {"passed": False, "error": "Response not successful"}
        
        if "generators" not in data.get("data", {}):
            return {"passed": False, "error": "No generators in response"}
        
        generators = data["data"]["generators"]
        if not isinstance(generators, list) or len(generators) == 0:
            return {"passed": False, "error": "No generators found"}
        
        return {"passed": True, "details": f"Found {len(generators)} generators"}
    
    def test_list_generators_with_filters(self) -> Dict:
        """Test generator listing with filters"""
        # Test category filter
        result = self._make_request("GET", "/api/v1/generators", params={"category": "endpoint_security"})
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Category filter failed: {result['status_code']}"}
        
        # Test search filter
        result = self._make_request("GET", "/api/v1/generators", params={"search": "crowdstrike"})
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Search filter failed: {result['status_code']}"}
        
        return {"passed": True, "details": "Filters working correctly"}
    
    def test_get_generator_details(self) -> Dict:
        """Test getting details for a specific generator"""
        result = self._make_request("GET", "/api/v1/generators/crowdstrike_falcon")
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Status code: {result['status_code']}"}
        
        data = result["response_data"]
        if not data.get("success"):
            return {"passed": False, "error": "Response not successful"}
        
        generator_data = data.get("data", {})
        required_fields = ["name", "category", "vendor"]
        
        for field in required_fields:
            if field not in generator_data:
                return {"passed": False, "error": f"Missing field: {field}"}
        
        return {"passed": True, "details": "Generator details complete"}
    
    def test_get_nonexistent_generator(self) -> Dict:
        """Test getting details for non-existent generator"""
        result = self._make_request("GET", "/api/v1/generators/nonexistent_generator")
        
        if result["status_code"] != 404:
            return {"passed": False, "error": f"Expected 404, got {result['status_code']}"}
        
        return {"passed": True, "details": "Non-existent generator properly returns 404"}
    
    def test_execute_generator(self) -> Dict:
        """Test executing a generator"""
        data = {"count": 3, "format": "json", "star_trek_theme": True}
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute", data=data)
        
        if result["status_code"] not in [200, 201]:
            return {"passed": False, "error": f"Status code: {result['status_code']}"}
        
        response_data = result["response_data"]
        if not response_data.get("success"):
            return {"passed": False, "error": "Execution not successful"}
        
        exec_data = response_data.get("data", {})
        if exec_data.get("count", 0) != 3:
            return {"passed": False, "error": f"Expected 3 events, got {exec_data.get('count')}"}
        
        if not exec_data.get("events"):
            return {"passed": False, "error": "No events returned"}
        
        return {"passed": True, "details": f"Generated {exec_data.get('count')} events in {exec_data.get('execution_time_ms', 0):.2f}ms"}
    
    def test_batch_execute_generators(self) -> Dict:
        """Test batch execution of multiple generators"""
        batch_data = {
            "executions": [
                {"generator_id": "crowdstrike_falcon", "count": 2, "format": "json"},
                {"generator_id": "okta_authentication", "count": 1, "format": "json"}
            ]
        }
        
        result = self._make_request("POST", "/api/v1/generators/batch/execute", data=batch_data)
        
        if result["status_code"] not in [200, 201]:
            return {"passed": False, "error": f"Status code: {result['status_code']}"}
        
        response_data = result["response_data"]
        if not response_data.get("success"):
            return {"passed": False, "error": "Batch execution not successful"}
        
        batch_result = response_data.get("data", {})
        executions = batch_result.get("executions", [])
        
        if len(executions) != 2:
            return {"passed": False, "error": f"Expected 2 executions, got {len(executions)}"}
        
        return {"passed": True, "details": f"Batch executed {len(executions)} generators"}
    
    def test_generator_validation(self) -> Dict:
        """Test generator validation endpoint"""
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/validate", 
                                   params={"sample_size": 3})
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Status code: {result['status_code']}"}
        
        data = result["response_data"]
        if not data.get("success"):
            return {"passed": False, "error": "Validation not successful"}
        
        return {"passed": True, "details": "Generator validation working"}
    
    def test_generator_schema(self) -> Dict:
        """Test generator schema endpoint"""
        result = self._make_request("GET", "/api/v1/generators/crowdstrike_falcon/schema")
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Status code: {result['status_code']}"}
        
        data = result["response_data"]
        if not data.get("success"):
            return {"passed": False, "error": "Schema request not successful"}
        
        schema_data = data.get("data", {})
        if "schema" not in schema_data:
            return {"passed": False, "error": "No schema in response"}
        
        return {"passed": True, "details": "Schema endpoint working"}
    
    def test_list_categories(self) -> Dict:
        """Test listing generator categories"""
        result = self._make_request("GET", "/api/v1/generators/categories")
        
        if result["status_code"] != 200:
            return {"passed": False, "error": f"Status code: {result['status_code']}"}
        
        data = result["response_data"]
        if not data.get("success"):
            return {"passed": False, "error": "Categories request not successful"}
        
        categories = data.get("data", {}).get("categories", [])
        if not categories:
            return {"passed": False, "error": "No categories found"}
        
        return {"passed": True, "details": f"Found {len(categories)} categories"}

    # ============================================================================
    # INPUT VALIDATION AND ERROR HANDLING TESTS
    # ============================================================================
    
    def test_invalid_json_payload(self) -> Dict:
        """Test handling of invalid JSON payloads"""
        headers = self.headers.copy()
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/generators/crowdstrike_falcon/execute",
                headers=headers,
                data="invalid json{",  # Malformed JSON
                timeout=30
            )
            
            if response.status_code not in [400, 422]:
                return {"passed": False, "error": f"Expected 400/422, got {response.status_code}"}
            
            return {"passed": True, "details": "Invalid JSON properly rejected"}
        
        except Exception as e:
            return {"passed": False, "error": f"Request failed: {str(e)}"}
    
    def test_missing_required_fields(self) -> Dict:
        """Test validation of missing required fields"""
        # Missing count field
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute", 
                                   data={"format": "json"})
        
        if result["status_code"] not in [400, 422]:
            return {"passed": False, "error": f"Missing field not caught: {result['status_code']}"}
        
        return {"passed": True, "details": "Missing required fields properly validated"}
    
    def test_invalid_field_values(self) -> Dict:
        """Test validation of invalid field values"""
        # Invalid count (negative)
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute",
                                   data={"count": -1, "format": "json"})
        
        if result["status_code"] not in [400, 422]:
            return {"passed": False, "error": f"Invalid count not caught: {result['status_code']}"}
        
        # Invalid format
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute",
                                   data={"count": 1, "format": "invalid_format"})
        
        if result["status_code"] not in [400, 422]:
            return {"passed": False, "error": f"Invalid format not caught: {result['status_code']}"}
        
        return {"passed": True, "details": "Invalid field values properly validated"}
    
    def test_boundary_values(self) -> Dict:
        """Test boundary value validation"""
        # Test maximum count (assuming 100 is limit)
        result = self._make_request("POST", "/api/v1/generators/crowdstrike_falcon/execute",
                                   data={"count": 1000, "format": "json"})
        
        # Should either succeed or return proper validation error
        if result["status_code"] not in [200, 201, 400, 422]:
            return {"passed": False, "error": f"Unexpected status for boundary test: {result['status_code']}"}
        
        return {"passed": True, "details": "Boundary values handled appropriately"}

    # ============================================================================
    # PERFORMANCE TESTS
    # ============================================================================
    
    def test_response_time(self) -> Dict:
        """Test API response times are reasonable"""
        start_time = time.time()
        result = self._make_request("GET", "/api/v1/generators")
        duration_ms = (time.time() - start_time) * 1000
        
        if not result["passed"]:
            return result
        
        if duration_ms > 5000:  # 5 second threshold
            return {"passed": False, "error": f"Response time too slow: {duration_ms:.2f}ms"}
        
        return {"passed": True, "details": f"Response time: {duration_ms:.2f}ms"}
    
    def test_concurrent_requests(self) -> Dict:
        """Test handling of concurrent requests"""
        def make_concurrent_request():
            return self._make_request("GET", "/api/v1/generators")
        
        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_concurrent_request) for _ in range(10)]
                results = [future.result() for future in as_completed(futures)]
            
            successful_requests = sum(1 for r in results if r["passed"] and r["status_code"] == 200)
            
            if successful_requests < 8:  # Allow for some failures
                return {"passed": False, "error": f"Only {successful_requests}/10 concurrent requests succeeded"}
            
            return {"passed": True, "details": f"{successful_requests}/10 concurrent requests succeeded"}
        
        except Exception as e:
            return {"passed": False, "error": f"Concurrent test failed: {str(e)}"}

    # ============================================================================
    # SECURITY TESTS
    # ============================================================================
    
    def test_sql_injection_attempts(self) -> Dict:
        """Test protection against SQL injection"""
        # Test SQL injection in query parameters
        malicious_params = {
            "search": "'; DROP TABLE generators; --",
            "category": "1' OR '1'='1",
            "vendor": "test'; SELECT * FROM users; --"
        }
        
        result = self._make_request("GET", "/api/v1/generators", params=malicious_params)
        
        # Should not cause server error
        if result["status_code"] == 500:
            return {"passed": False, "error": "SQL injection may have caused server error"}
        
        return {"passed": True, "details": "SQL injection attempts handled safely"}
    
    def test_xss_attempts(self) -> Dict:
        """Test protection against XSS"""
        xss_payload = "<script>alert('xss')</script>"
        
        result = self._make_request("GET", "/api/v1/generators", params={"search": xss_payload})
        
        if result["passed"] and result["status_code"] == 200:
            # Check if XSS payload is properly escaped in response
            response_text = str(result["response_data"])
            if "<script>" in response_text:
                return {"passed": False, "error": "XSS payload not properly escaped"}
        
        return {"passed": True, "details": "XSS attempts handled safely"}
    
    def test_rate_limiting(self) -> Dict:
        """Test rate limiting functionality"""
        # Use read-only key with low rate limit
        read_headers = {"X-API-Key": self.test_keys["read"], "Content-Type": "application/json"}
        
        # Make many rapid requests
        rate_limited = False
        for i in range(150):  # Exceed typical rate limit
            result = self._make_request("GET", "/api/v1/generators", headers=read_headers)
            if result["status_code"] == 429:  # Too Many Requests
                rate_limited = True
                break
            time.sleep(0.01)  # Small delay
        
        if not rate_limited:
            return {"passed": False, "error": "Rate limiting not working"}
        
        return {"passed": True, "details": "Rate limiting is functional"}

    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    def test_end_to_end_workflow(self) -> Dict:
        """Test complete end-to-end workflow"""
        # 1. List generators
        result = self._make_request("GET", "/api/v1/generators")
        if not result["passed"] or result["status_code"] != 200:
            return {"passed": False, "error": "Failed to list generators"}
        
        generators = result["response_data"]["data"]["generators"]
        if not generators:
            return {"passed": False, "error": "No generators available"}
        
        # 2. Get generator details
        generator_id = generators[0]["id"]
        result = self._make_request("GET", f"/api/v1/generators/{generator_id}")
        if not result["passed"] or result["status_code"] != 200:
            return {"passed": False, "error": "Failed to get generator details"}
        
        # 3. Execute generator
        result = self._make_request("POST", f"/api/v1/generators/{generator_id}/execute",
                                   data={"count": 2, "format": "json"})
        if not result["passed"] or result["status_code"] not in [200, 201]:
            return {"passed": False, "error": "Failed to execute generator"}
        
        # 4. Validate generator
        result = self._make_request("POST", f"/api/v1/generators/{generator_id}/validate")
        if not result["passed"] or result["status_code"] != 200:
            return {"passed": False, "error": "Failed to validate generator"}
        
        return {"passed": True, "details": "End-to-end workflow completed successfully"}

    # ============================================================================
    # TEST EXECUTION AND REPORTING
    # ============================================================================
    
    async def run_all_tests(self) -> TestReport:
        """Run all test categories"""
        self.logger.info("Starting comprehensive API test suite")
        start_time = datetime.now()
        
        # Define test categories and their tests
        test_categories = {
            "authentication": [
                ("No Auth Required Endpoints", self.test_no_auth_required_endpoints),
                ("Missing API Key", self.test_missing_api_key),
                ("Invalid API Key", self.test_invalid_api_key),
                ("Role Based Access - Read", self.test_role_based_access_read),
                ("Role Based Access - Write Denied", self.test_role_based_access_write_denied),
                ("Role Based Access - Write Allowed", self.test_role_based_access_write_allowed),
                ("Admin Access", self.test_admin_access),
            ],
            "functional": [
                ("List Generators", self.test_list_generators),
                ("List Generators with Filters", self.test_list_generators_with_filters),
                ("Get Generator Details", self.test_get_generator_details),
                ("Get Nonexistent Generator", self.test_get_nonexistent_generator),
                ("Execute Generator", self.test_execute_generator),
                ("Batch Execute Generators", self.test_batch_execute_generators),
                ("Generator Validation", self.test_generator_validation),
                ("Generator Schema", self.test_generator_schema),
                ("List Categories", self.test_list_categories),
            ],
            "validation": [
                ("Invalid JSON Payload", self.test_invalid_json_payload),
                ("Missing Required Fields", self.test_missing_required_fields),
                ("Invalid Field Values", self.test_invalid_field_values),
                ("Boundary Values", self.test_boundary_values),
            ],
            "performance": [
                ("Response Time", self.test_response_time),
                ("Concurrent Requests", self.test_concurrent_requests),
            ],
            "security": [
                ("SQL Injection Attempts", self.test_sql_injection_attempts),
                ("XSS Attempts", self.test_xss_attempts),
                ("Rate Limiting", self.test_rate_limiting),
            ],
            "integration": [
                ("End-to-End Workflow", self.test_end_to_end_workflow),
            ]
        }
        
        # Execute all tests
        for category, tests in test_categories.items():
            self.logger.info(f"Running {category.upper()} tests")
            
            for test_name, test_func in tests:
                self.logger.info(f"  Running: {test_name}")
                result = self._execute_test(test_func, test_name, category)
                self.results.append(result)
                
                if result.passed:
                    self.logger.info(f"    ✅ PASSED ({result.duration_ms:.2f}ms)")
                else:
                    self.logger.error(f"    ❌ FAILED: {result.error_message}")
        
        end_time = datetime.now()
        
        # Generate report
        return self._generate_report(start_time, end_time)
    
    def _generate_report(self, start_time: datetime, end_time: datetime) -> TestReport:
        """Generate comprehensive test report"""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        # Categorize results
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {"passed": 0, "failed": 0, "total": 0}
            
            categories[result.category]["total"] += 1
            if result.passed:
                categories[result.category]["passed"] += 1
            else:
                categories[result.category]["failed"] += 1
        
        # Identify issues
        issues = []
        for result in self.results:
            if not result.passed:
                issues.append({
                    "test": result.test_name,
                    "category": result.category,
                    "error": result.error_message,
                    "severity": self._classify_issue_severity(result)
                })
        
        # Generate recommendations
        recommendations = self._generate_recommendations(categories, issues)
        
        # Performance metrics
        avg_response_time = sum(r.duration_ms for r in self.results) / len(self.results)
        performance_metrics = {
            "average_response_time_ms": avg_response_time,
            "slowest_test": max(self.results, key=lambda x: x.duration_ms),
            "fastest_test": min(self.results, key=lambda x: x.duration_ms)
        }
        
        return TestReport(
            start_time=start_time,
            end_time=end_time,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            categories=categories,
            results=self.results,
            issues=issues,
            recommendations=recommendations,
            performance_metrics=performance_metrics
        )
    
    def _classify_issue_severity(self, result: TestResult) -> str:
        """Classify issue severity based on test type and failure"""
        if result.category == "security":
            return "HIGH"
        elif result.category == "authentication":
            return "HIGH"
        elif result.category == "functional" and "execute" in result.test_name.lower():
            return "MEDIUM"
        elif result.category == "performance":
            return "MEDIUM"
        else:
            return "LOW"
    
    def _generate_recommendations(self, categories: Dict, issues: List) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        # Check for high-severity issues
        high_severity_issues = [i for i in issues if i["severity"] == "HIGH"]
        if high_severity_issues:
            recommendations.append(
                f"🔴 CRITICAL: {len(high_severity_issues)} high-severity issues found. "
                "Address authentication and security issues immediately."
            )
        
        # Check category-specific issues
        for category, stats in categories.items():
            if stats["failed"] > 0:
                failure_rate = (stats["failed"] / stats["total"]) * 100
                if failure_rate > 50:
                    recommendations.append(
                        f"📊 {category.upper()} category has {failure_rate:.1f}% failure rate. "
                        "Requires immediate attention."
                    )
        
        # Performance recommendations
        perf_issues = [i for i in issues if i["category"] == "performance"]
        if perf_issues:
            recommendations.append(
                "⚡ Performance issues detected. Consider optimizing response times "
                "and implementing better caching strategies."
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ No critical issues found. API is functioning well.")
        
        recommendations.extend([
            "📝 Consider implementing automated testing in CI/CD pipeline",
            "📊 Set up monitoring and alerting for production API",
            "🔍 Implement structured logging for better debugging",
            "📈 Consider implementing API versioning strategy"
        ])
        
        return recommendations


async def main():
    """Main test execution"""
    print("🚀 Jarvis Coding API - Comprehensive Test Suite")
    print("=" * 60)
    
    # Initialize test framework
    test_framework = APITestFramework()
    
    try:
        # Start API server
        print("📡 Starting API server...")
        server_started = await test_framework.start_api_server()
        
        if not server_started:
            print("❌ Failed to start API server")
            return
        
        print("✅ API server started successfully")
        print()
        
        # Run comprehensive test suite
        report = await test_framework.run_all_tests()
        
        # Display results
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"🕐 Duration: {report.end_time - report.start_time}")
        print(f"📝 Total Tests: {report.total_tests}")
        print(f"✅ Passed: {report.passed_tests}")
        print(f"❌ Failed: {report.failed_tests}")
        print(f"📈 Success Rate: {(report.passed_tests/report.total_tests)*100:.1f}%")
        
        print("\n📋 RESULTS BY CATEGORY:")
        for category, stats in report.categories.items():
            success_rate = (stats["passed"] / stats["total"]) * 100
            status = "✅" if success_rate == 100 else "⚠️" if success_rate >= 75 else "❌"
            print(f"  {status} {category.upper()}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        if report.issues:
            print(f"\n🔍 CRITICAL ISSUES FOUND ({len(report.issues)}):")
            for issue in report.issues[:5]:  # Show top 5 issues
                severity_emoji = "🔴" if issue["severity"] == "HIGH" else "🟡" if issue["severity"] == "MEDIUM" else "🔵"
                print(f"  {severity_emoji} {issue['test']} ({issue['category']})")
                print(f"     {issue['error']}")
        
        print(f"\n⚡ PERFORMANCE METRICS:")
        print(f"  Average Response Time: {report.performance_metrics['average_response_time_ms']:.2f}ms")
        print(f"  Slowest Test: {report.performance_metrics['slowest_test'].test_name} ({report.performance_metrics['slowest_test'].duration_ms:.2f}ms)")
        print(f"  Fastest Test: {report.performance_metrics['fastest_test'].test_name} ({report.performance_metrics['fastest_test'].duration_ms:.2f}ms)")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations[:5], 1):
            print(f"  {i}. {rec}")
        
        # Save detailed report
        report_file = Path(__file__).parent / "comprehensive_test_report.json"
        with open(report_file, 'w') as f:
            # Convert dataclasses to dict for JSON serialization
            report_dict = {
                "start_time": report.start_time.isoformat(),
                "end_time": report.end_time.isoformat(),
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "categories": report.categories,
                "results": [asdict(r) for r in report.results],
                "issues": report.issues,
                "recommendations": report.recommendations,
                "performance_metrics": {
                    "average_response_time_ms": report.performance_metrics["average_response_time_ms"],
                    "slowest_test": asdict(report.performance_metrics["slowest_test"]),
                    "fastest_test": asdict(report.performance_metrics["fastest_test"])
                }
            }
            json.dump(report_dict, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Final assessment
        overall_success_rate = (report.passed_tests / report.total_tests) * 100
        print(f"\n🎯 OVERALL ASSESSMENT:")
        
        if overall_success_rate >= 95:
            print("🏆 EXCELLENT: API is highly robust and production-ready")
        elif overall_success_rate >= 85:
            print("👍 GOOD: API is mostly functional with minor issues")
        elif overall_success_rate >= 70:
            print("⚠️  NEEDS IMPROVEMENT: Several issues require attention")
        else:
            print("🚨 CRITICAL: Significant issues found, not production-ready")
    
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop API server
        test_framework.stop_api_server()
        print("\n🛑 API server stopped")


if __name__ == "__main__":
    asyncio.run(main())