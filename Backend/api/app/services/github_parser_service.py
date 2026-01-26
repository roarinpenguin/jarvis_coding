"""
GitHub Parser Service - Fetch parsers from GitHub repositories

This service fetches parser definitions from configured GitHub repositories
and provides fuzzy matching to detect similar parser names.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from difflib import SequenceMatcher
import requests

logger = logging.getLogger(__name__)

# Common suffixes to normalize when comparing parser names
PARSER_SUFFIXES = ['-latest', '-marketplace', '-community', '-custom', '-v2', '-v1', '_logs', '_log', '_candidate_logs']


class GitHubParserService:
    """Service to fetch and manage parsers from GitHub repositories"""
    
    def __init__(self):
        self.cache: Dict[str, Dict] = {}  # Cache parsed repo contents
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Jarvis-Parser-Sync'
        })
    
    def parse_github_url(self, url: str) -> Optional[Dict[str, str]]:
        """
        Parse a GitHub URL to extract owner, repo, and optional path
        
        Supports formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo/tree/branch/path
        - https://github.com/owner/repo/tree/main/parsers
        
        Returns:
            Dict with 'owner', 'repo', 'branch', 'path' or None if invalid
        """
        patterns = [
            # Full path with tree
            r'https?://github\.com/([^/]+)/([^/]+)/tree/([^/]+)(?:/(.+))?',
            # Basic repo URL
            r'https?://github\.com/([^/]+)/([^/]+)/?$',
        ]
        
        for pattern in patterns:
            match = re.match(pattern, url.strip())
            if match:
                groups = match.groups()
                if len(groups) == 4:
                    return {
                        'owner': groups[0],
                        'repo': groups[1],
                        'branch': groups[2],
                        'path': groups[3] or ''
                    }
                else:
                    return {
                        'owner': groups[0],
                        'repo': groups[1].rstrip('.git'),
                        'branch': 'main',
                        'path': ''
                    }
        
        logger.warning(f"Could not parse GitHub URL: {url}")
        return None
    
    def list_parsers_in_repo(
        self,
        repo_url: str,
        github_token: Optional[str] = None,
        max_depth: int = 2,
        return_meta: bool = False
    ):
        """
        List all parser directories in a GitHub repository, searching subdirectories
        
        Args:
            repo_url: GitHub repository URL
            github_token: Optional GitHub personal access token for private repos
            max_depth: Maximum depth to search for parser directories (default 2)
            
        Returns:
            List of dicts with 'name', 'path', 'download_url' for each parser
        """
        parsed = self.parse_github_url(repo_url)
        if not parsed:
            if return_meta:
                return {
                    "repo_url": repo_url,
                    "parsers": [],
                    "count": 0,
                    "rate_limited": False,
                    "warning": "Could not parse GitHub repository URL",
                    "status_code": None,
                }
            return []
        
        owner = parsed['owner']
        repo = parsed['repo']
        branch = parsed['branch']
        base_path = parsed['path']
        
        headers = dict(self.session.headers)
        if github_token:
            headers['Authorization'] = f'token {github_token}'
            logger.info(f"Using GitHub token for authentication (token length: {len(github_token)})")
        else:
            logger.warning("No GitHub token provided - may hit rate limits")
        
        meta = {
            "rate_limited": False,
            "warning": None,
            "status_code": None,
        }

        def fetch_directory(path: str, depth: int) -> List[Dict[str, str]]:
            """Recursively fetch parser directories"""
            if depth > max_depth:
                return []
            
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            if path:
                api_url += f"/{path}"
            api_url += f"?ref={branch}"
            
            try:
                response = self.session.get(api_url, headers=headers, timeout=30)
                
                if response.status_code != 200:
                    meta["status_code"] = response.status_code
                    body_preview = (response.text or "")[:200]
                    if response.status_code == 403 and "rate limit" in (response.text or "").lower():
                        meta["rate_limited"] = True
                        meta["warning"] = "GitHub API rate limit exceeded. Add a GitHub PAT to increase limits."
                    elif response.status_code == 401:
                        meta["warning"] = "GitHub API authentication failed (401). Check your GitHub PAT."
                    else:
                        meta["warning"] = f"GitHub API returned {response.status_code}."
                    logger.warning(f"GitHub API returned {response.status_code} for {api_url}: {response.text[:200]}")
                    return []
                
                contents = response.json()
                parsers = []
                
                for item in contents:
                    if item['type'] == 'dir':
                        name = item['name']
                        item_path = item['path']
                        
                        # Check if this looks like a parser directory (contains -latest, _logs, etc.)
                        # or is a category directory (community, sentinelone, etc.)
                        is_parser_dir = any(suffix in name.lower() for suffix in ['-latest', '_logs', '_log', '-marketplace', '-community'])
                        is_category_dir = name.lower() in ['community', 'sentinelone', 'custom', 'marketplace', 'community_new']
                        
                        if is_parser_dir:
                            # This looks like a parser directory
                            parsers.append({
                                'name': name,
                                'path': item_path,
                                'repo_url': repo_url,
                                'api_url': item['url']
                            })
                        elif is_category_dir:
                            # This is a category directory, search inside it
                            parsers.extend(fetch_directory(item_path, depth + 1))
                        else:
                            # Could be a parser without standard suffix, add it and also search inside
                            parsers.append({
                                'name': name,
                                'path': item_path,
                                'repo_url': repo_url,
                                'api_url': item['url']
                            })
                            # Also search inside in case it's a category
                            if depth < max_depth:
                                parsers.extend(fetch_directory(item_path, depth + 1))
                
                return parsers
                
            except Exception as e:
                logger.debug(f"Error fetching directory {path}: {e}")
                return []
        
        try:
            parsers = fetch_directory(base_path, 0)
            logger.info(f"Found {len(parsers)} parser directories in {repo_url}")
            if return_meta:
                warning = meta["warning"]
                if not parsers and not warning:
                    warning = "No parsers found in this repository path. If this is unexpected, add a GitHub PAT to avoid rate limits or verify the URL path/branch."
                return {
                    "repo_url": repo_url,
                    "parsers": parsers,
                    "count": len(parsers),
                    "rate_limited": meta["rate_limited"],
                    "warning": warning,
                    "status_code": meta["status_code"],
                }
            return parsers
            
        except Exception as e:
            logger.error(f"Error listing parsers in repo {repo_url}: {e}")
            if return_meta:
                return {
                    "repo_url": repo_url,
                    "parsers": [],
                    "count": 0,
                    "rate_limited": False,
                    "warning": "Error contacting GitHub. Add a GitHub PAT or try again.",
                    "status_code": None,
                }
            return []
    
    def fetch_parser_content(
        self,
        repo_url: str,
        parser_path: str,
        github_token: Optional[str] = None
    ) -> Optional[str]:
        """
        Fetch the actual parser content from a GitHub repository
        
        Args:
            repo_url: GitHub repository URL
            parser_path: Path to the parser directory within the repo
            github_token: Optional GitHub personal access token
            
        Returns:
            Parser content as string (JSON or conf), or None if not found
        """
        parsed = self.parse_github_url(repo_url)
        if not parsed:
            return None
        
        owner = parsed['owner']
        repo = parsed['repo']
        branch = parsed['branch']
        
        headers = dict(self.session.headers)
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        # List directory contents to find parser files
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{parser_path}?ref={branch}"
        
        try:
            response = self.session.get(api_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                logger.warning(f"Failed to fetch directory contents for {parser_path}: {response.status_code}")
                return None
            
            contents = response.json()
            
            # Look for parser files in priority order: .json first, then .conf
            parser_file = None
            for item in contents:
                if item['type'] == 'file':
                    name = item['name'].lower()
                    if name.endswith('.json'):
                        parser_file = item
                        break  # Prefer JSON
                    elif name.endswith('.conf') and not parser_file:
                        parser_file = item
            
            if parser_file:
                # Fetch raw content
                raw_url = parser_file.get('download_url')
                if raw_url:
                    raw_response = self.session.get(raw_url, headers=headers, timeout=30)
                    if raw_response.status_code == 200:
                        logger.info(f"Fetched parser content from {raw_url}")
                        return raw_response.text
            else:
                logger.warning(f"No parser file (.json or .conf) found in {parser_path}")
            
        except Exception as e:
            logger.error(f"Error fetching parser content from {parser_path}: {e}")
        
        return None
    
    def check_parser_has_content(
        self,
        repo_url: str,
        parser_path: str,
        github_token: Optional[str] = None
    ) -> bool:
        """
        Check if a parser directory has a valid parser file (.json or .conf)
        
        Args:
            repo_url: GitHub repository URL
            parser_path: Path to the parser directory
            github_token: Optional GitHub token
            
        Returns:
            True if the directory contains a parser file
        """
        parsed = self.parse_github_url(repo_url)
        if not parsed:
            return False
        
        owner = parsed['owner']
        repo = parsed['repo']
        branch = parsed['branch']
        
        headers = dict(self.session.headers)
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{parser_path}?ref={branch}"
        
        try:
            response = self.session.get(api_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                return False
            
            contents = response.json()
            
            for item in contents:
                if item['type'] == 'file':
                    name = item['name'].lower()
                    if name.endswith('.json') or name.endswith('.conf'):
                        return True
            
        except Exception:
            pass
        
        return False
    
    def normalize_parser_name(self, name: str) -> str:
        """
        Normalize a parser name for comparison by removing common suffixes
        
        Args:
            name: Parser name (e.g., 'aws_cloudtrail-latest', 'f5_networks_logs-latest')
            
        Returns:
            Normalized name (e.g., 'aws_cloudtrail', 'f5_networks')
        """
        normalized = name.lower()
        # Keep stripping suffixes until no more are found (handles compound suffixes)
        changed = True
        while changed:
            changed = False
            for suffix in PARSER_SUFFIXES:
                if normalized.endswith(suffix):
                    normalized = normalized[:-len(suffix)]
                    changed = True
                    break
        return normalized
    
    def calculate_similarity(self, name1: str, name2: str) -> float:
        """
        Calculate similarity ratio between two parser names
        
        Args:
            name1: First parser name
            name2: Second parser name
            
        Returns:
            Similarity ratio between 0 and 1
        """
        norm1 = self.normalize_parser_name(name1)
        norm2 = self.normalize_parser_name(name2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_similar_parsers(
        self,
        target_name: str,
        available_parsers: List[Dict[str, str]],
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find parsers with similar names to the target
        
        Args:
            target_name: The parser name we're looking for
            available_parsers: List of available parser dicts from GitHub repos
            threshold: Minimum similarity ratio to consider a match
            
        Returns:
            List of matching parsers with similarity scores, sorted by similarity
        """
        matches = []
        target_normalized = self.normalize_parser_name(target_name)
        
        for parser in available_parsers:
            parser_name = parser.get('name', '')
            similarity = self.calculate_similarity(target_name, parser_name)
            
            # Check for exact normalized match or high similarity
            parser_normalized = self.normalize_parser_name(parser_name)
            is_exact_normalized = target_normalized == parser_normalized
            
            if is_exact_normalized or similarity >= threshold:
                matches.append({
                    **parser,
                    'similarity': similarity,
                    'is_exact_normalized': is_exact_normalized
                })
        
        # Sort by exact match first, then by similarity
        matches.sort(key=lambda x: (-x['is_exact_normalized'], -x['similarity']))
        
        return matches
    
    def search_parser_in_repos(
        self,
        parser_name: str,
        repo_urls: List[str],
        github_token: Optional[str] = None,
        validate_content: bool = False
    ) -> List[Dict]:
        """
        Search for a parser across multiple GitHub repositories
        
        Args:
            parser_name: Name of the parser to find
            repo_urls: List of GitHub repository URLs to search
            github_token: Optional GitHub personal access token
            validate_content: If True, only return parsers that have valid content files
            
        Returns:
            List of matching parsers from all repos with similarity info
        """
        all_matches = []
        
        for repo_url in repo_urls:
            if not repo_url:
                continue
                
            parsers = self.list_parsers_in_repo(repo_url, github_token)
            matches = self.find_similar_parsers(parser_name, parsers)
            
            for match in matches:
                match['repo_url'] = repo_url
                
                # Optionally validate that parser directory has content
                if validate_content:
                    has_content = self.check_parser_has_content(
                        repo_url=repo_url,
                        parser_path=match.get('path', ''),
                        github_token=github_token
                    )
                    if not has_content:
                        logger.debug(f"Skipping {match.get('name')} - no parser file found")
                        continue
                    match['has_content'] = True
                
                all_matches.append(match)
        
        # Sort all matches by similarity
        all_matches.sort(key=lambda x: (-x.get('is_exact_normalized', False), -x.get('similarity', 0)))
        
        logger.info(f"Found {len(all_matches)} valid matches for parser '{parser_name}'")
        return all_matches


# Singleton instance
_github_parser_service: Optional[GitHubParserService] = None


def get_github_parser_service() -> GitHubParserService:
    """Get or create the GitHub parser service singleton"""
    global _github_parser_service
    if _github_parser_service is None:
        _github_parser_service = GitHubParserService()
    return _github_parser_service
