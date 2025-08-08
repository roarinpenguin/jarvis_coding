#!/usr/bin/env python3
"""
SentinelOne Data Visibility (DV) API Client for Parser Testing
Built from swagger 2.1 specification to test datasource delivery and parser validation
"""
import json
import os
import time
import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from urllib.parse import urljoin

@dataclass
class DVQueryResult:
    """Data Visibility query result"""
    query_id: str
    status: str
    total_results: int
    events: List[Dict[str, Any]]
    errors: List[str]
    metadata: Dict[str, Any]

@dataclass
class ParserTestResult:
    """Parser test result from DV API"""
    parser_name: str
    events_sent: int
    events_found: int
    parsing_success: bool
    field_coverage: Dict[str, Any]
    missing_fields: List[str]
    unexpected_fields: List[str]
    errors: List[str]

class SentinelOneDVClient:
    """SentinelOne Data Visibility API Client for parser testing with service account support"""
    
    def __init__(self, base_url: str = None, api_token: str = None, hec_token: str = None, 
                 service_user_id: str = None, site_id: str = None, account_id: str = None):
        """Initialize SentinelOne DV API client with service account authentication
        
        Args:
            base_url: SentinelOne console URL (e.g., https://example.sentinelone.net)
            api_token: Service account API token for management API
            hec_token: HEC token for event ingestion
            service_user_id: Service account user ID (optional, for tracking)
            site_id: Site ID to scope operations (optional)
            account_id: Account ID to scope operations (optional)
        """
        # Load configuration from environment variables
        self.base_url = base_url or os.getenv('S1_API_URL', '').rstrip('/')
        self.api_token = api_token or os.getenv('S1_API_TOKEN')
        self.hec_token = hec_token or os.getenv('S1_HEC_TOKEN')
        self.service_user_id = service_user_id or os.getenv('S1_SERVICE_USER_ID')
        self.site_id = site_id or os.getenv('S1_SITE_ID')
        self.account_id = account_id or os.getenv('S1_ACCOUNT_ID')
        
        # Validate required parameters
        if not self.base_url:
            raise ValueError("SentinelOne base URL required (S1_API_URL env var)")
        if not self.api_token:
            raise ValueError("SentinelOne service account API token required (S1_API_TOKEN env var)")
        if not self.hec_token:
            raise ValueError("SentinelOne HEC token required (S1_HEC_TOKEN env var)")
            
        # Configure HTTP session with service account authentication
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'ApiToken {self.api_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'SentinelOne-Parser-Tester/1.0'
        })
        
        # Add scope headers if provided
        if self.account_id:
            self.session.headers['Account-Id'] = self.account_id
        if self.site_id:
            self.session.headers['Site-Id'] = self.site_id
        
        # API endpoints based on swagger 2.1
        self.dv_endpoints = {
            'init_query': '/web/api/v2.1/dv/init-query',
            'query_status': '/web/api/v2.1/dv/query-status', 
            'events': '/web/api/v2.1/dv/events',
            'events_by_type': '/web/api/v2.1/dv/events/{event_type}',
            'events_pq': '/web/api/v2.1/dv/events/pq',
            'cancel_query': '/web/api/v2.1/dv/cancel-query',
            'process_state': '/web/api/v2.1/dv/process-state',
            'fetch_file': '/web/api/v2.1/dv/fetch-file'
        }
        
        # HEC endpoint
        self.hec_url = urljoin(self.base_url, '/hec/event')
        
        # Service account info (populated after validation)
        self.service_account_info = None
        
    def validate_service_account(self) -> Dict[str, Any]:
        """Validate service account permissions and capabilities
        
        Returns:
            Dictionary with validation results and account information
        """
        validation_results = {
            'valid': False,
            'account_info': {},
            'permissions': {},
            'dv_access': False,
            'hec_access': False,
            'errors': []
        }
        
        try:
            # Test basic API access
            accounts_response = self._make_request('GET', '/web/api/v2.1/accounts')
            if accounts_response.get('data'):
                account_info = accounts_response['data'][0] if accounts_response['data'] else {}
                validation_results['account_info'] = {
                    'account_name': account_info.get('name'),
                    'account_id': account_info.get('id'),
                    'account_state': account_info.get('state'),
                    'license_type': account_info.get('licenseType')
                }
                validation_results['permissions']['accounts'] = True
            else:
                validation_results['errors'].append('No account access or empty response')
                
        except Exception as e:
            validation_results['errors'].append(f'Account API access failed: {e}')
        
        try:
            # Test Data Visibility access
            test_query = self.init_dv_query('dataSource.name EXISTS', limit=1)
            validation_results['dv_access'] = bool(test_query)
            validation_results['permissions']['data_visibility'] = True
        except Exception as e:
            validation_results['errors'].append(f'Data Visibility access failed: {e}')
            
        try:
            # Test HEC access
            test_hec = self.send_hec_events([{
                'test': True, 
                'message': 'Service account validation test',
                'timestamp': datetime.now(timezone.utc).isoformat()
            }], source='service_account_test')
            
            validation_results['hec_access'] = test_hec['success_count'] > 0
            validation_results['permissions']['hec'] = True
        except Exception as e:
            validation_results['errors'].append(f'HEC access failed: {e}')
        
        # Check if service account has minimum required permissions
        validation_results['valid'] = (
            validation_results['permissions'].get('accounts', False) and
            validation_results['dv_access'] and
            validation_results['hec_access']
        )
        
        # Store for later reference
        self.service_account_info = validation_results
        
        return validation_results
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make authenticated API request"""
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed for {endpoint}: {e}")
    
    def send_hec_events(self, events: List[Dict[str, Any]], 
                       source: str = 'parser_test',
                       sourcetype: str = 'json') -> Dict[str, Any]:
        """Send events via HEC endpoint
        
        Args:
            events: List of event dictionaries to send
            source: Event source identifier
            sourcetype: Event sourcetype (json, syslog, etc.)
            
        Returns:
            Dictionary with send results
        """
        hec_session = requests.Session()
        hec_session.headers.update({
            'Authorization': f'Splunk {self.hec_token}',
            'Content-Type': 'application/json'
        })
        
        results = []
        for i, event in enumerate(events):
            hec_event = {
                'event': event,
                'time': int(time.time()),
                'source': source,
                'sourcetype': sourcetype,
                'index': 'main'  # Default index
            }
            
            try:
                response = hec_session.post(self.hec_url, json=hec_event, timeout=30)
                response.raise_for_status()
                results.append({
                    'success': True,
                    'event_index': i,
                    'response': response.json() if response.text else {}
                })
            except requests.exceptions.RequestException as e:
                results.append({
                    'success': False,
                    'event_index': i,
                    'error': str(e)
                })
        
        success_count = sum(1 for r in results if r['success'])
        return {
            'events_sent': len(events),
            'success_count': success_count,
            'failure_count': len(events) - success_count,
            'results': results
        }
    
    def init_dv_query(self, query: str, 
                     from_date: datetime = None,
                     to_date: datetime = None,
                     limit: int = 1000) -> str:
        """Initialize a Data Visibility query
        
        Args:
            query: DV query string (e.g., 'dataSource.name = "PingFederate"')
            from_date: Start time for query
            to_date: End time for query  
            limit: Maximum number of results
            
        Returns:
            Query ID for tracking the query
        """
        if not from_date:
            from_date = datetime.now(timezone.utc) - timedelta(hours=1)
        if not to_date:
            to_date = datetime.now(timezone.utc)
            
        payload = {
            'query': query,
            'fromDate': from_date.isoformat(),
            'toDate': to_date.isoformat(),
            'limit': limit
        }
        
        response = self._make_request('POST', self.dv_endpoints['init_query'], json=payload)
        
        if 'data' in response and 'queryId' in response['data']:
            return response['data']['queryId']
        else:
            raise Exception(f"Failed to init query: {response}")
    
    def get_query_status(self, query_id: str) -> Dict[str, Any]:
        """Get status of a DV query
        
        Args:
            query_id: Query ID from init_dv_query
            
        Returns:
            Query status information
        """
        params = {'queryId': query_id}
        return self._make_request('GET', self.dv_endpoints['query_status'], params=params)
    
    def get_dv_events(self, query_id: str = None,
                     query: str = None,
                     from_date: datetime = None, 
                     to_date: datetime = None,
                     limit: int = 1000) -> DVQueryResult:
        """Get events from Data Visibility
        
        Args:
            query_id: Existing query ID, or None to create new query
            query: DV query string (required if query_id is None)
            from_date: Start time for query
            to_date: End time for query
            limit: Maximum number of results
            
        Returns:
            DVQueryResult with events and metadata
        """
        if not query_id:
            if not query:
                raise ValueError("Either query_id or query must be provided")
            query_id = self.init_dv_query(query, from_date, to_date, limit)
        
        # Poll query status until complete
        max_attempts = 30
        attempt = 0
        
        while attempt < max_attempts:
            status_response = self.get_query_status(query_id)
            
            if status_response.get('data', {}).get('responseState') == 'FINISHED':
                break
            elif status_response.get('data', {}).get('responseState') == 'FAILED':
                return DVQueryResult(
                    query_id=query_id,
                    status='FAILED',
                    total_results=0,
                    events=[],
                    errors=[f"Query failed: {status_response}"],
                    metadata=status_response
                )
            
            time.sleep(2)
            attempt += 1
        
        if attempt >= max_attempts:
            return DVQueryResult(
                query_id=query_id,
                status='TIMEOUT',
                total_results=0,
                events=[],
                errors=['Query timed out'],
                metadata={}
            )
        
        # Fetch events
        params = {'queryId': query_id}
        events_response = self._make_request('GET', self.dv_endpoints['events'], params=params)
        
        events = events_response.get('data', [])
        total_results = len(events)
        
        return DVQueryResult(
            query_id=query_id,
            status='SUCCESS',
            total_results=total_results,
            events=events,
            errors=[],
            metadata=events_response
        )
    
    def search_events_by_datasource(self, datasource_name: str,
                                   from_date: datetime = None,
                                   to_date: datetime = None,
                                   limit: int = 100) -> DVQueryResult:
        """Search for events by datasource name
        
        Args:
            datasource_name: Name of the datasource (e.g., 'PingFederate')
            from_date: Start time for search
            to_date: End time for search
            limit: Maximum results
            
        Returns:
            DVQueryResult with matching events
        """
        query = f'dataSource.name = "{datasource_name}"'
        return self.get_dv_events(query=query, from_date=from_date, to_date=to_date, limit=limit)
    
    def search_events_by_vendor(self, vendor_name: str,
                               from_date: datetime = None,
                               to_date: datetime = None,
                               limit: int = 100) -> DVQueryResult:
        """Search for events by vendor name
        
        Args:
            vendor_name: Name of the vendor (e.g., 'Ping Identity')
            from_date: Start time for search
            to_date: End time for search
            limit: Maximum results
            
        Returns:
            DVQueryResult with matching events
        """
        query = f'dataSource.vendor = "{vendor_name}"'
        return self.get_dv_events(query=query, from_date=from_date, to_date=to_date, limit=limit)
    
    def test_parser_end_to_end(self, parser_name: str,
                              test_events: List[Dict[str, Any]],
                              expected_fields: List[str] = None,
                              wait_time: int = 60) -> ParserTestResult:
        """Test a parser end-to-end with sample events
        
        Args:
            parser_name: Name of the parser to test
            test_events: Sample events to send and verify
            expected_fields: List of fields that should be present in parsed events
            wait_time: Time to wait for events to be processed
            
        Returns:
            ParserTestResult with comprehensive test results
        """
        print(f"🧪 Testing parser: {parser_name}")
        print(f"   Sending {len(test_events)} events...")
        
        # Send events via HEC
        send_result = self.send_hec_events(test_events, source=parser_name)
        
        if send_result['success_count'] == 0:
            return ParserTestResult(
                parser_name=parser_name,
                events_sent=len(test_events),
                events_found=0,
                parsing_success=False,
                field_coverage={},
                missing_fields=[],
                unexpected_fields=[],
                errors=[f"Failed to send events: {send_result}"]
            )
        
        print(f"   ✅ Sent {send_result['success_count']} events successfully")
        print(f"   ⏳ Waiting {wait_time}s for processing...")
        time.sleep(wait_time)
        
        # Search for processed events
        search_result = self.search_events_by_datasource(
            parser_name, 
            from_date=datetime.now(timezone.utc) - timedelta(minutes=30)
        )
        
        if search_result.status != 'SUCCESS':
            return ParserTestResult(
                parser_name=parser_name,
                events_sent=len(test_events),
                events_found=0,
                parsing_success=False,
                field_coverage={},
                missing_fields=[],
                unexpected_fields=[],
                errors=[f"Search failed: {search_result.errors}"]
            )
        
        events_found = len(search_result.events)
        print(f"   📊 Found {events_found} processed events")
        
        # Analyze field coverage
        field_analysis = self._analyze_field_coverage(
            search_result.events, 
            expected_fields or []
        )
        
        parsing_success = events_found > 0 and len(field_analysis['missing_fields']) == 0
        
        return ParserTestResult(
            parser_name=parser_name,
            events_sent=len(test_events),
            events_found=events_found,
            parsing_success=parsing_success,
            field_coverage=field_analysis['field_coverage'],
            missing_fields=field_analysis['missing_fields'],
            unexpected_fields=field_analysis['unexpected_fields'],
            errors=search_result.errors
        )
    
    def _analyze_field_coverage(self, events: List[Dict[str, Any]], 
                              expected_fields: List[str]) -> Dict[str, Any]:
        """Analyze field coverage in parsed events
        
        Args:
            events: List of parsed events from DV
            expected_fields: Fields that should be present
            
        Returns:
            Dictionary with field analysis results
        """
        if not events:
            return {
                'field_coverage': {},
                'missing_fields': expected_fields,
                'unexpected_fields': []
            }
        
        # Collect all fields present in events
        all_fields = set()
        field_counts = {}
        
        for event in events:
            event_fields = self._extract_nested_fields(event)
            all_fields.update(event_fields)
            
            for field in event_fields:
                field_counts[field] = field_counts.get(field, 0) + 1
        
        # Calculate field coverage
        field_coverage = {}
        for field in all_fields:
            coverage_percent = (field_counts[field] / len(events)) * 100
            field_coverage[field] = {
                'count': field_counts[field],
                'coverage_percent': coverage_percent,
                'consistent': coverage_percent == 100.0
            }
        
        # Find missing and unexpected fields
        expected_set = set(expected_fields)
        found_set = set(all_fields)
        
        missing_fields = list(expected_set - found_set)
        unexpected_fields = list(found_set - expected_set) if expected_fields else []
        
        return {
            'field_coverage': field_coverage,
            'missing_fields': missing_fields,
            'unexpected_fields': unexpected_fields[:20]  # Limit to first 20
        }
    
    def _extract_nested_fields(self, obj: Any, prefix: str = '') -> List[str]:
        """Extract all nested field names from a nested dictionary
        
        Args:
            obj: Dictionary or other object to extract fields from
            prefix: Current field prefix for nested fields
            
        Returns:
            List of field names (with dot notation for nested fields)
        """
        fields = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_field = f"{prefix}.{key}" if prefix else key
                fields.append(current_field)
                
                # Recursively extract nested fields
                if isinstance(value, (dict, list)):
                    fields.extend(self._extract_nested_fields(value, current_field))
        
        elif isinstance(obj, list) and obj:
            # For lists, analyze the first item
            fields.extend(self._extract_nested_fields(obj[0], prefix))
        
        return fields
    
    def batch_test_parsers(self, parser_tests: Dict[str, Dict[str, Any]], 
                          wait_time: int = 60) -> Dict[str, ParserTestResult]:
        """Test multiple parsers in batch
        
        Args:
            parser_tests: Dict mapping parser names to test configurations:
                {
                    'parser_name': {
                        'events': [...],
                        'expected_fields': [...]
                    }
                }
            wait_time: Wait time between tests
            
        Returns:
            Dictionary mapping parser names to test results
        """
        results = {}
        
        for parser_name, test_config in parser_tests.items():
            try:
                result = self.test_parser_end_to_end(
                    parser_name=parser_name,
                    test_events=test_config.get('events', []),
                    expected_fields=test_config.get('expected_fields', []),
                    wait_time=wait_time
                )
                results[parser_name] = result
                
                # Brief pause between tests
                time.sleep(5)
                
            except Exception as e:
                results[parser_name] = ParserTestResult(
                    parser_name=parser_name,
                    events_sent=0,
                    events_found=0,
                    parsing_success=False,
                    field_coverage={},
                    missing_fields=[],
                    unexpected_fields=[],
                    errors=[f"Test failed: {e}"]
                )
        
        return results
    
    def generate_test_report(self, results: Dict[str, ParserTestResult]) -> str:
        """Generate comprehensive test report
        
        Args:
            results: Dictionary of parser test results
            
        Returns:
            Formatted test report
        """
        report_lines = [
            "# SentinelOne Parser End-to-End Test Report",
            "",
            f"**Generated:** {datetime.now(timezone.utc).isoformat()}",
            f"**Parsers Tested:** {len(results)}",
            ""
        ]
        
        # Summary statistics
        successful = sum(1 for r in results.values() if r.parsing_success)
        total_events_sent = sum(r.events_sent for r in results.values())
        total_events_found = sum(r.events_found for r in results.values())
        
        report_lines.extend([
            "## Summary",
            "",
            f"- **Success Rate:** {successful}/{len(results)} ({100*successful/len(results):.1f}%)",
            f"- **Total Events Sent:** {total_events_sent}",
            f"- **Total Events Found:** {total_events_found}",
            f"- **End-to-End Success Rate:** {100*total_events_found/total_events_sent:.1f}%" if total_events_sent > 0 else "- **End-to-End Success Rate:** N/A",
            ""
        ])
        
        # Results table
        report_lines.extend([
            "## Test Results",
            "",
            "| Parser | Status | Events Sent | Events Found | Success Rate | Field Coverage |",
            "|--------|--------|-------------|--------------|--------------|----------------|"
        ])
        
        for parser_name, result in sorted(results.items()):
            status = "✅ PASS" if result.parsing_success else "❌ FAIL"
            success_rate = f"{100*result.events_found/result.events_sent:.1f}%" if result.events_sent > 0 else "N/A"
            field_count = len(result.field_coverage)
            
            report_lines.append(
                f"| {parser_name} | {status} | {result.events_sent} | {result.events_found} | {success_rate} | {field_count} fields |"
            )
        
        # Detailed analysis for failed parsers
        failed_parsers = {name: result for name, result in results.items() if not result.parsing_success}
        
        if failed_parsers:
            report_lines.extend([
                "",
                "## Failed Parsers Analysis",
                ""
            ])
            
            for parser_name, result in failed_parsers.items():
                report_lines.extend([
                    f"### {parser_name}",
                    ""
                ])
                
                if result.errors:
                    report_lines.append("**Errors:**")
                    for error in result.errors:
                        report_lines.append(f"- {error}")
                    report_lines.append("")
                
                if result.missing_fields:
                    report_lines.append("**Missing Expected Fields:**")
                    for field in result.missing_fields:
                        report_lines.append(f"- {field}")
                    report_lines.append("")
        
        return "\n".join(report_lines)


def main():
    """CLI interface for DV parser testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='SentinelOne DV Parser Testing Tool')
    parser.add_argument('--test-connection', action='store_true', help='Test API connectivity')
    parser.add_argument('--search', '-s', help='Search for events by datasource name')
    parser.add_argument('--query', '-q', help='Custom DV query')
    parser.add_argument('--parser', '-p', help='Test specific parser')
    parser.add_argument('--wait-time', '-w', type=int, default=60, help='Wait time for processing (default: 60s)')
    parser.add_argument('--limit', '-l', type=int, default=100, help='Result limit (default: 100)')
    parser.add_argument('--output', '-o', help='Output report file')
    
    args = parser.parse_args()
    
    try:
        client = SentinelOneDVClient()
        
        if args.test_connection:
            print("🔗 Testing SentinelOne API connectivity...")
            
            # Test basic API connection
            try:
                accounts_response = client._make_request('GET', '/web/api/v2.1/accounts')
                print("✅ Management API: Connected")
                
                if accounts_response.get('data'):
                    account = accounts_response['data'][0]
                    print(f"   Account: {account.get('name', 'Unknown')}")
            except Exception as e:
                print(f"❌ Management API: {e}")
            
            # Test HEC connectivity  
            try:
                test_result = client.send_hec_events([
                    {'test': True, 'message': 'API connectivity test'}
                ], source='api_test')
                
                if test_result['success_count'] > 0:
                    print("✅ HEC Endpoint: Connected")
                else:
                    print(f"❌ HEC Endpoint: {test_result}")
            except Exception as e:
                print(f"❌ HEC Endpoint: {e}")
        
        elif args.search:
            print(f"🔍 Searching for events from datasource: {args.search}")
            result = client.search_events_by_datasource(args.search, limit=args.limit)
            
            print(f"Status: {result.status}")
            print(f"Events found: {result.total_results}")
            
            if result.events:
                print("\nSample event fields:")
                sample_fields = client._extract_nested_fields(result.events[0])
                for field in sorted(sample_fields)[:20]:
                    print(f"  - {field}")
                if len(sample_fields) > 20:
                    print(f"  ... and {len(sample_fields) - 20} more fields")
        
        elif args.query:
            print(f"🔍 Executing DV query: {args.query}")
            result = client.get_dv_events(query=args.query, limit=args.limit)
            
            print(f"Status: {result.status}")
            print(f"Events found: {result.total_results}")
            
            if result.events:
                print("\nSample event:")
                print(json.dumps(result.events[0], indent=2)[:500] + "...")
        
        elif args.parser:
            print(f"🧪 Testing parser: {args.parser}")
            print("Note: Implement specific parser test logic based on your generator modules")
        
        else:
            print("No action specified. Use --help for options.")
            print("\nQuick start:")
            print("  python s1_dv_api_client.py --test-connection")
            print("  python s1_dv_api_client.py --search 'PingFederate'")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())