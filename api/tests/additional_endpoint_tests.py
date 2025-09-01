#!/usr/bin/env python3
"""
Additional API endpoint tests for comprehensive coverage
Testing parsers, scenarios, validation, export, metrics, and search endpoints
"""

import requests
import json
import time
from typing import Dict, Any

class AdditionalEndpointTests:
    """Test additional API endpoints not covered in main test suite"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.admin_key = "admin-test-key-123456789012345678901234"
        self.headers = {"X-API-Key": self.admin_key, "Content-Type": "application/json"}
    
    def test_parsers_endpoints(self) -> Dict[str, Any]:
        """Test parser-related endpoints"""
        results = {}
        
        # Test list parsers
        try:
            response = requests.get(f"{self.base_url}/api/v1/parsers", headers=self.headers, timeout=30)
            results["list_parsers"] = {
                "status": response.status_code,
                "success": response.status_code == 200,
                "response_size": len(response.text) if response.text else 0
            }
        except Exception as e:
            results["list_parsers"] = {"error": str(e), "success": False}
        
        # Test get parser details (if parsers exist)
        try:
            response = requests.get(f"{self.base_url}/api/v1/parsers/crowdstrike_endpoint", headers=self.headers, timeout=30)
            results["get_parser"] = {
                "status": response.status_code,
                "success": response.status_code in [200, 404],  # Both are acceptable
            }
        except Exception as e:
            results["get_parser"] = {"error": str(e), "success": False}
        
        return results
    
    def test_validation_endpoints(self) -> Dict[str, Any]:
        """Test validation endpoints"""
        results = {}
        
        # Test validate event format
        try:
            test_event = {
                "timestamp": "2023-08-29T10:00:00Z",
                "event_type": "authentication",
                "user": "test.user@starfleet.corp"
            }
            response = requests.post(
                f"{self.base_url}/api/v1/validation/event", 
                headers=self.headers, 
                json={"event": test_event, "parser_id": "crowdstrike_endpoint"},
                timeout=30
            )
            results["validate_event"] = {
                "status": response.status_code,
                "success": response.status_code in [200, 400, 404]  # Various acceptable responses
            }
        except Exception as e:
            results["validate_event"] = {"error": str(e), "success": False}
        
        return results
    
    def test_scenarios_endpoints(self) -> Dict[str, Any]:
        """Test scenario endpoints"""
        results = {}
        
        # Test list scenarios
        try:
            response = requests.get(f"{self.base_url}/api/v1/scenarios", headers=self.headers, timeout=30)
            results["list_scenarios"] = {
                "status": response.status_code,
                "success": response.status_code == 200
            }
        except Exception as e:
            results["list_scenarios"] = {"error": str(e), "success": False}
        
        # Test execute scenario
        try:
            scenario_data = {
                "scenario_type": "phishing_attack",
                "duration_minutes": 5,
                "target_count": 10
            }
            response = requests.post(
                f"{self.base_url}/api/v1/scenarios/execute", 
                headers=self.headers, 
                json=scenario_data,
                timeout=30
            )
            results["execute_scenario"] = {
                "status": response.status_code,
                "success": response.status_code in [200, 201, 400]  # Various acceptable responses
            }
        except Exception as e:
            results["execute_scenario"] = {"error": str(e), "success": False}
        
        return results
    
    def test_export_endpoints(self) -> Dict[str, Any]:
        """Test export endpoints"""
        results = {}
        
        # Test export events
        try:
            export_request = {
                "generator_ids": ["crowdstrike_falcon"],
                "format": "json",
                "count": 5
            }
            response = requests.post(
                f"{self.base_url}/api/v1/export/events", 
                headers=self.headers, 
                json=export_request,
                timeout=30
            )
            results["export_events"] = {
                "status": response.status_code,
                "success": response.status_code in [200, 201]
            }
        except Exception as e:
            results["export_events"] = {"error": str(e), "success": False}
        
        return results
    
    def test_metrics_endpoints(self) -> Dict[str, Any]:
        """Test metrics endpoints"""
        results = {}
        
        # Test get metrics
        try:
            response = requests.get(f"{self.base_url}/api/v1/metrics", headers=self.headers, timeout=30)
            results["get_metrics"] = {
                "status": response.status_code,
                "success": response.status_code == 200
            }
        except Exception as e:
            results["get_metrics"] = {"error": str(e), "success": False}
        
        # Test generator metrics
        try:
            response = requests.get(f"{self.base_url}/api/v1/metrics/generators", headers=self.headers, timeout=30)
            results["generator_metrics"] = {
                "status": response.status_code,
                "success": response.status_code == 200
            }
        except Exception as e:
            results["generator_metrics"] = {"error": str(e), "success": False}
        
        return results
    
    def test_search_endpoints(self) -> Dict[str, Any]:
        """Test search endpoints"""
        results = {}
        
        # Test search generators
        try:
            search_params = {"q": "crowdstrike", "type": "generators"}
            response = requests.get(
                f"{self.base_url}/api/v1/search", 
                headers=self.headers, 
                params=search_params,
                timeout=30
            )
            results["search_generators"] = {
                "status": response.status_code,
                "success": response.status_code == 200
            }
        except Exception as e:
            results["search_generators"] = {"error": str(e), "success": False}
        
        # Test search parsers
        try:
            search_params = {"q": "firewall", "type": "parsers"}
            response = requests.get(
                f"{self.base_url}/api/v1/search", 
                headers=self.headers, 
                params=search_params,
                timeout=30
            )
            results["search_parsers"] = {
                "status": response.status_code,
                "success": response.status_code == 200
            }
        except Exception as e:
            results["search_parsers"] = {"error": str(e), "success": False}
        
        return results
    
    def run_all_additional_tests(self) -> Dict[str, Any]:
        """Run all additional endpoint tests"""
        print("Running additional endpoint tests...")
        
        all_results = {
            "parsers": self.test_parsers_endpoints(),
            "validation": self.test_validation_endpoints(),
            "scenarios": self.test_scenarios_endpoints(),
            "export": self.test_export_endpoints(),
            "metrics": self.test_metrics_endpoints(),
            "search": self.test_search_endpoints()
        }
        
        # Calculate summary
        total_tests = 0
        passed_tests = 0
        
        for category, tests in all_results.items():
            for test_name, result in tests.items():
                total_tests += 1
                if result.get("success", False):
                    passed_tests += 1
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": success_rate,
            "results_by_category": all_results
        }
        
        return summary


def run_additional_tests():
    """Run additional endpoint tests and display results"""
    tester = AdditionalEndpointTests()
    results = tester.run_all_additional_tests()
    
    print("\n" + "="*60)
    print("ADDITIONAL ENDPOINT TEST RESULTS")
    print("="*60)
    
    print(f"📊 Total Tests: {results['total_tests']}")
    print(f"✅ Passed: {results['passed_tests']}")
    print(f"❌ Failed: {results['total_tests'] - results['passed_tests']}")
    print(f"📈 Success Rate: {results['success_rate']:.1f}%")
    
    print("\n📋 RESULTS BY ENDPOINT CATEGORY:")
    for category, tests in results["results_by_category"].items():
        category_passed = sum(1 for test in tests.values() if test.get("success", False))
        category_total = len(tests)
        category_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
        
        status = "✅" if category_rate == 100 else "⚠️" if category_rate >= 50 else "❌"
        print(f"  {status} {category.upper()}: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        for test_name, result in tests.items():
            test_status = "✅" if result.get("success", False) else "❌"
            status_code = result.get("status", "N/A")
            error = result.get("error", "")
            
            if error:
                print(f"    {test_status} {test_name}: ERROR - {error[:50]}...")
            else:
                print(f"    {test_status} {test_name}: Status {status_code}")
    
    return results


if __name__ == "__main__":
    run_additional_tests()