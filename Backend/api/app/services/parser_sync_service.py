"""
Parser Sync Service - Check and upload parsers to destination AI SIEM

Uses the SentinelOne/Scalyr Configuration API:
- getFile: Check if a parser exists in the destination account
- putFile: Upload a parser to the destination account

API Documentation: https://app.scalyr.com/help/api#getFile
"""
import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import requests

logger = logging.getLogger(__name__)

# Mapping from generator/source names to parser sourcetypes
# This maps scenario sources to their corresponding parser directory names
SCENARIO_SOURCE_TO_PARSER = {
    # Identity & Access
    "okta_authentication": "okta_authentication-latest",
    "microsoft_azuread": "microsoft_azuread-latest",
    "microsoft_azure_ad_signin": "microsoft_azure_ad_signin-latest",
    
    # Microsoft 365
    "microsoft_365_collaboration": "microsoft_365_collaboration-latest",
    "microsoft_365_mgmt_api": "microsoft_365_mgmt_api_logs-latest",
    "microsoft_365_defender": "microsoft_365_defender-latest",
    
    # Endpoint Security
    "crowdstrike_falcon": "crowdstrike_falcon-latest",
    "sentinelone_endpoint": "sentinelone_endpoint-latest",
    
    # Email Security
    "proofpoint": "proofpoint_proofpoint_logs-latest",
    "mimecast": "mimecast_mimecast_logs-latest",
    
    # Cloud Infrastructure
    "aws_cloudtrail": "aws_cloudtrail-latest",
    "aws_guardduty": "aws_guardduty_logs-latest",
    "netskope": "netskope_netskope_logs-latest",
    
    # Network Security
    "darktrace": "darktrace_darktrace_logs-latest",
    "paloalto_firewall": "paloalto_firewall-latest",
    "fortinet_fortigate": "fortinet_fortigate_candidate_logs-latest",
    "zscaler": "zscaler_logs-latest",
    
    # Privileged Access
    "cyberark_pas": "cyberark_pas_logs-latest",
    "beyondtrust_passwordsafe": "beyondtrust_passwordsafe_logs-latest",
    "hashicorp_vault": "hashicorp_vault-latest",
}


class ParserSyncService:
    """Service to check and upload parsers to destination AI SIEM"""
    
    def __init__(self, parsers_dir: Optional[str] = None, config_api_url: Optional[str] = None):
        """
        Initialize the parser sync service
        
        Args:
            parsers_dir: Path to the local parsers directory
            config_api_url: Config API URL for the destination (e.g., https://xdr.us1.sentinelone.net)
        """
        if parsers_dir:
            self.parsers_dir = Path(parsers_dir)
        else:
            # Default to Backend/parsers relative to this file
            self.parsers_dir = Path(__file__).parent.parent.parent.parent / "parsers"
        
        # API base URL - use provided URL, or fall back to environment variable
        if config_api_url:
            self.api_base_url = config_api_url.rstrip('/') + "/api"
        else:
            self.api_base_url = os.getenv("S1_CONFIG_API_URL", "https://app.scalyr.com/api")
    
    def get_parser_sourcetype(self, source: str) -> Optional[str]:
        """
        Get the parser sourcetype for a given scenario source
        
        Args:
            source: The scenario source name (e.g., 'okta_authentication')
            
        Returns:
            The parser sourcetype or None if not found
        """
        return SCENARIO_SOURCE_TO_PARSER.get(source)
    
    def get_parser_path_in_siem(self, sourcetype: str) -> str:
        """
        Get the parser file path in the SIEM configuration
        
        Args:
            sourcetype: The parser sourcetype (e.g., 'okta_authentication-latest')
            
        Returns:
            The parser path in SIEM (e.g., '/logParsers/okta_authentication-latest')
        """
        return f"/logParsers/{sourcetype}"
    
    def load_local_parser(self, sourcetype: str) -> Optional[str]:
        """
        Load parser content from local parsers directory
        
        Args:
            sourcetype: The parser sourcetype (e.g., 'okta_authentication-latest')
            
        Returns:
            The parser JSON content as string, or None if not found
        """
        # Try community directory first
        parser_dirs = [
            self.parsers_dir / "community" / sourcetype,
            self.parsers_dir / "community_new" / sourcetype,
            self.parsers_dir / "sentinelone" / sourcetype,
        ]
        
        for parser_dir in parser_dirs:
            if parser_dir.exists():
                # Look for parser.json or any .json file
                parser_file = parser_dir / "parser.json"
                if parser_file.exists():
                    try:
                        return parser_file.read_text()
                    except Exception as e:
                        logger.error(f"Error reading parser file {parser_file}: {e}")
                        continue
                
                # Try any .json file in the directory
                json_files = list(parser_dir.glob("*.json"))
                if json_files:
                    try:
                        return json_files[0].read_text()
                    except Exception as e:
                        logger.error(f"Error reading parser file {json_files[0]}: {e}")
                        continue
        
        logger.warning(f"Parser not found locally: {sourcetype}")
        return None
    
    def check_parser_exists(
        self,
        config_read_token: str,
        parser_path: str,
        timeout: int = 30
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if a parser exists in the destination SIEM using getFile API
        
        Args:
            config_read_token: The config read API token
            parser_path: The parser path in SIEM (e.g., '/parsers/okta_authentication-latest')
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (exists: bool, content: Optional[str])
        """
        try:
            url = f"{self.api_base_url}/getFile"
            payload = {
                "token": config_read_token,
                "path": parser_path
            }
            
            logger.info(f"Checking if parser exists: {parser_path}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                # Scalyr API returns status: "success" if file exists
                if result.get("status") == "success":
                    content = result.get("content")
                    logger.info(f"Parser exists: {parser_path}")
                    return True, content
                else:
                    # File doesn't exist
                    logger.info(f"Parser does not exist: {parser_path}")
                    return False, None
            elif response.status_code == 404:
                logger.info(f"Parser does not exist: {parser_path}")
                return False, None
            else:
                logger.warning(
                    f"Unexpected response checking parser {parser_path}: "
                    f"{response.status_code} - {response.text}"
                )
                return False, None
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout checking parser: {parser_path}")
            return False, None
        except Exception as e:
            logger.error(f"Error checking parser {parser_path}: {e}")
            return False, None
    
    def upload_parser(
        self,
        config_write_token: str,
        parser_path: str,
        content: str,
        timeout: int = 30
    ) -> bool:
        """
        Upload a parser to the destination SIEM using putFile API
        
        Args:
            config_write_token: The config write API token
            parser_path: The parser path in SIEM (e.g., '/parsers/okta_authentication-latest')
            content: The parser JSON content
            timeout: Request timeout in seconds
            
        Returns:
            True if upload succeeded, False otherwise
        """
        try:
            url = f"{self.api_base_url}/putFile"
            payload = {
                "token": config_write_token,
                "path": parser_path,
                "content": content
            }
            
            logger.info(f"Uploading parser: {parser_path}")
            
            response = requests.post(
                url,
                json=payload,
                timeout=timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    logger.info(f"Parser uploaded successfully: {parser_path}")
                    return True
                else:
                    logger.error(
                        f"Failed to upload parser {parser_path}: {result.get('message', 'Unknown error')}"
                    )
                    return False
            else:
                logger.error(
                    f"Failed to upload parser {parser_path}: "
                    f"{response.status_code} - {response.text}"
                )
                return False
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout uploading parser: {parser_path}")
            return False
        except Exception as e:
            logger.error(f"Error uploading parser {parser_path}: {e}")
            return False
    
    def ensure_parsers_for_sources(
        self,
        sources: List[str],
        config_read_token: str,
        config_write_token: str
    ) -> Dict[str, dict]:
        """
        Ensure all required parsers exist in the destination SIEM
        
        Args:
            sources: List of scenario sources (e.g., ['okta_authentication', 'microsoft_azuread'])
            config_read_token: The config read API token
            config_write_token: The config write API token
            
        Returns:
            Dict with status for each source:
            {
                'okta_authentication': {
                    'status': 'exists' | 'uploaded' | 'failed' | 'no_parser',
                    'sourcetype': str,
                    'message': str
                }
            }
        """
        results = {}
        
        for source in sources:
            sourcetype = self.get_parser_sourcetype(source)
            
            if not sourcetype:
                results[source] = {
                    "status": "no_parser",
                    "sourcetype": None,
                    "message": f"No parser mapping found for source: {source}"
                }
                continue
            
            parser_path = self.get_parser_path_in_siem(sourcetype)
            
            # Check if parser exists
            exists, _ = self.check_parser_exists(config_read_token, parser_path)
            
            if exists:
                results[source] = {
                    "status": "exists",
                    "sourcetype": sourcetype,
                    "message": f"Parser already exists: {parser_path}"
                }
                continue
            
            # Parser doesn't exist, try to upload it
            local_content = self.load_local_parser(sourcetype)
            
            if not local_content:
                results[source] = {
                    "status": "failed",
                    "sourcetype": sourcetype,
                    "message": f"Parser not found locally: {sourcetype}"
                }
                continue
            
            # Upload the parser
            success = self.upload_parser(config_write_token, parser_path, local_content)
            
            if success:
                results[source] = {
                    "status": "uploaded",
                    "sourcetype": sourcetype,
                    "message": f"Parser uploaded successfully: {parser_path}"
                }
            else:
                results[source] = {
                    "status": "failed",
                    "sourcetype": sourcetype,
                    "message": f"Failed to upload parser: {parser_path}"
                }
        
        return results
    
    def get_scenario_sources(self, scenario_id: str) -> List[str]:
        """
        Get the list of sources used by a scenario
        
        Args:
            scenario_id: The scenario identifier
            
        Returns:
            List of source names used by the scenario
        """
        # Mapping of scenarios to their sources
        scenario_sources = {
            "finance_mfa_fatigue_scenario": [
                "okta_authentication",
                "microsoft_azuread",
                "microsoft_365_collaboration"
            ],
            "insider_cloud_download_exfiltration": [
                "okta_authentication",
                "microsoft_365_collaboration",
                "crowdstrike_falcon"
            ],
            "enterprise_attack_scenario": [
                "proofpoint",
                "microsoft_azuread",
                "microsoft_365_collaboration",
                "crowdstrike_falcon",
                "darktrace",
                "netskope"
            ],
            "showcase_attack_scenario": [
                "mimecast",
                "microsoft_azuread",
                "crowdstrike_falcon",
                "darktrace",
                "netskope",
                "cyberark_pas"
            ]
        }
        
        return scenario_sources.get(scenario_id, [])


# Singleton instance for use across the application
_parser_sync_service: Optional[ParserSyncService] = None


def get_parser_sync_service() -> ParserSyncService:
    """Get or create the parser sync service singleton"""
    global _parser_sync_service
    if _parser_sync_service is None:
        _parser_sync_service = ParserSyncService()
    return _parser_sync_service
