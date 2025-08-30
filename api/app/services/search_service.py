"""
Search and filtering service for generators, parsers, and events
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from collections import defaultdict
import importlib.util

from app.core.config import settings


class SearchService:
    """Service for searching and filtering across the system"""
    
    def __init__(self):
        self.generators_path = settings.GENERATORS_PATH
        self.parsers_path = settings.PARSERS_PATH
        self.scenarios_path = settings.SCENARIOS_PATH
        self._cache = {}
        self._index_built = False
    
    async def build_search_index(self):
        """Build search index for faster queries"""
        if self._index_built:
            return
        
        self._cache["generators"] = await self._index_generators()
        self._cache["parsers"] = await self._index_parsers()
        self._cache["scenarios"] = await self._index_scenarios()
        self._index_built = True
    
    async def _index_generators(self) -> Dict[str, Any]:
        """Index all generators for searching"""
        index = {
            "by_category": defaultdict(list),
            "by_vendor": defaultdict(list),
            "by_product": defaultdict(list),
            "by_format": defaultdict(list),
            "all": []
        }
        
        categories = [
            "cloud_infrastructure",
            "network_security",
            "endpoint_security",
            "identity_access",
            "email_security",
            "web_security",
            "infrastructure"
        ]
        
        for category in categories:
            category_path = self.generators_path / category
            if not category_path.exists():
                continue
            
            for file_path in category_path.glob("*.py"):
                if file_path.name.startswith("__"):
                    continue
                
                generator_id = file_path.stem
                parts = generator_id.split("_", 1)
                vendor = parts[0] if parts else ""
                product = parts[1] if len(parts) > 1 else generator_id
                
                # Determine format from generator
                format_type = await self._detect_generator_format(file_path)
                
                generator_info = {
                    "id": generator_id,
                    "category": category,
                    "vendor": vendor,
                    "product": product,
                    "format": format_type,
                    "file_path": str(file_path),
                    "star_trek": await self._has_star_trek_theme(file_path)
                }
                
                index["by_category"][category].append(generator_info)
                index["by_vendor"][vendor].append(generator_info)
                index["by_product"][product].append(generator_info)
                index["by_format"][format_type].append(generator_info)
                index["all"].append(generator_info)
        
        return index
    
    async def _index_parsers(self) -> Dict[str, Any]:
        """Index all parsers for searching"""
        index = {
            "by_type": defaultdict(list),
            "by_vendor": defaultdict(list),
            "all": []
        }
        
        community_path = self.parsers_path / "community"
        if community_path.exists():
            for parser_dir in community_path.iterdir():
                if not parser_dir.is_dir():
                    continue
                
                parser_id = parser_dir.name
                if parser_id.endswith("-latest"):
                    parser_id = parser_id[:-7]
                
                parts = parser_id.split("_", 1)
                vendor = parts[0] if parts else ""
                
                # Read parser config
                config_file = parser_dir / "parser.json"
                parser_type = "community"
                fields_count = 0
                
                if config_file.exists():
                    try:
                        with open(config_file, 'r') as f:
                            config = json.load(f)
                            fields_count = len(config.get("fields", []))
                    except:
                        pass
                
                parser_info = {
                    "id": parser_id,
                    "type": parser_type,
                    "vendor": vendor,
                    "fields_count": fields_count,
                    "path": str(parser_dir)
                }
                
                index["by_type"][parser_type].append(parser_info)
                index["by_vendor"][vendor].append(parser_info)
                index["all"].append(parser_info)
        
        return index
    
    async def _index_scenarios(self) -> Dict[str, Any]:
        """Index all scenarios for searching"""
        index = {
            "by_category": defaultdict(list),
            "all": []
        }
        
        # Pre-defined scenarios
        scenarios = [
            {"id": "enterprise_attack", "category": "apt", "phases": 5},
            {"id": "quick_phishing", "category": "phishing", "phases": 3},
            {"id": "ransomware_sim", "category": "ransomware", "phases": 4},
            {"id": "insider_threat", "category": "insider", "phases": 6},
            {"id": "cloud_breach", "category": "cloud", "phases": 5}
        ]
        
        for scenario in scenarios:
            index["by_category"][scenario["category"]].append(scenario)
            index["all"].append(scenario)
        
        return index
    
    async def search_generators(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        vendor: Optional[str] = None,
        format: Optional[str] = None,
        star_trek: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Search generators with filters"""
        await self.build_search_index()
        
        results = self._cache["generators"]["all"].copy()
        
        # Apply filters
        if category:
            results = [g for g in results if g["category"] == category]
        
        if vendor:
            results = [g for g in results if g["vendor"].lower() == vendor.lower()]
        
        if format:
            results = [g for g in results if g["format"] == format]
        
        if star_trek is not None:
            results = [g for g in results if g["star_trek"] == star_trek]
        
        # Apply text search
        if query:
            query_lower = query.lower()
            results = [
                g for g in results
                if query_lower in g["id"].lower() or
                   query_lower in g["vendor"].lower() or
                   query_lower in g["product"].lower()
            ]
        
        return results
    
    async def search_parsers(
        self,
        query: Optional[str] = None,
        parser_type: Optional[str] = None,
        vendor: Optional[str] = None,
        min_fields: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search parsers with filters"""
        await self.build_search_index()
        
        results = self._cache["parsers"]["all"].copy()
        
        # Apply filters
        if parser_type:
            results = [p for p in results if p["type"] == parser_type]
        
        if vendor:
            results = [p for p in results if p["vendor"].lower() == vendor.lower()]
        
        if min_fields:
            results = [p for p in results if p["fields_count"] >= min_fields]
        
        # Apply text search
        if query:
            query_lower = query.lower()
            results = [
                p for p in results
                if query_lower in p["id"].lower() or
                   query_lower in p["vendor"].lower()
            ]
        
        return results
    
    async def search_scenarios(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_phases: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search scenarios with filters"""
        await self.build_search_index()
        
        results = self._cache["scenarios"]["all"].copy()
        
        # Apply filters
        if category:
            results = [s for s in results if s["category"] == category]
        
        if min_phases:
            results = [s for s in results if s.get("phases", 0) >= min_phases]
        
        # Apply text search
        if query:
            query_lower = query.lower()
            results = [
                s for s in results
                if query_lower in s["id"].lower() or
                   query_lower in s.get("category", "").lower()
            ]
        
        return results
    
    async def global_search(
        self,
        query: str,
        types: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all resource types"""
        if not types:
            types = ["generators", "parsers", "scenarios"]
        
        results = {}
        
        if "generators" in types:
            results["generators"] = await self.search_generators(query=query)
        
        if "parsers" in types:
            results["parsers"] = await self.search_parsers(query=query)
        
        if "scenarios" in types:
            results["scenarios"] = await self.search_scenarios(query=query)
        
        return results
    
    async def get_compatibility_matches(
        self,
        generator_id: Optional[str] = None,
        parser_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Find compatible generators and parsers"""
        await self.build_search_index()
        
        matches = {
            "generators": [],
            "parsers": [],
            "compatibility_score": 0
        }
        
        if generator_id:
            # Find matching parsers for generator
            generators = await self.search_generators(query=generator_id)
            if generators:
                generator = generators[0]
                vendor = generator["vendor"]
                product = generator["product"]
                
                # Search for parsers with same vendor/product
                parsers = await self.search_parsers(query=f"{vendor}_{product}")
                matches["parsers"] = parsers
                
                if parsers:
                    matches["compatibility_score"] = 100
        
        if parser_id:
            # Find matching generators for parser
            parsers = await self.search_parsers(query=parser_id)
            if parsers:
                parser = parsers[0]
                vendor = parser["vendor"]
                
                # Search for generators with same vendor
                generators = await self.search_generators(vendor=vendor)
                matches["generators"] = generators
                
                if generators:
                    matches["compatibility_score"] = 100
        
        return matches
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get search statistics"""
        await self.build_search_index()
        
        return {
            "generators": {
                "total": len(self._cache["generators"]["all"]),
                "by_category": {
                    cat: len(gens) 
                    for cat, gens in self._cache["generators"]["by_category"].items()
                },
                "by_format": {
                    fmt: len(gens)
                    for fmt, gens in self._cache["generators"]["by_format"].items()
                },
                "with_star_trek": len([
                    g for g in self._cache["generators"]["all"] 
                    if g.get("star_trek", False)
                ])
            },
            "parsers": {
                "total": len(self._cache["parsers"]["all"]),
                "by_type": {
                    typ: len(pars)
                    for typ, pars in self._cache["parsers"]["by_type"].items()
                },
                "avg_fields": sum(
                    p["fields_count"] for p in self._cache["parsers"]["all"]
                ) / len(self._cache["parsers"]["all"]) if self._cache["parsers"]["all"] else 0
            },
            "scenarios": {
                "total": len(self._cache["scenarios"]["all"]),
                "by_category": {
                    cat: len(scens)
                    for cat, scens in self._cache["scenarios"]["by_category"].items()
                }
            }
        }
    
    async def _detect_generator_format(self, file_path: Path) -> str:
        """Detect the output format of a generator"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
                if 'json.dumps' in content or 'return {' in content:
                    return "json"
                elif 'csv' in content.lower():
                    return "csv"
                elif 'syslog' in content.lower():
                    return "syslog"
                elif 'key=' in content or 'key-value' in content.lower():
                    return "keyvalue"
                else:
                    return "json"  # Default
        except:
            return "unknown"
    
    async def _has_star_trek_theme(self, file_path: Path) -> bool:
        """Check if generator has Star Trek theme"""
        try:
            with open(file_path, 'r') as f:
                content = f.read().lower()
                
                star_trek_indicators = [
                    "picard", "worf", "data", "laforge", "crusher",
                    "enterprise", "starfleet", "federation", "vulcan"
                ]
                
                return any(indicator in content for indicator in star_trek_indicators)
        except:
            return False
    
    async def get_recommendations(
        self,
        resource_type: str = "generator",
        based_on: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get recommendations based on usage or similarity"""
        await self.build_search_index()
        
        recommendations = []
        
        if resource_type == "generator" and based_on:
            # Find similar generators
            generators = await self.search_generators(query=based_on)
            if generators:
                source = generators[0]
                
                # Recommend generators from same category
                similar = await self.search_generators(
                    category=source["category"]
                )
                
                recommendations = [
                    g for g in similar 
                    if g["id"] != source["id"]
                ][:5]
        
        elif resource_type == "parser" and based_on:
            # Find similar parsers
            parsers = await self.search_parsers(query=based_on)
            if parsers:
                source = parsers[0]
                
                # Recommend parsers from same vendor
                similar = await self.search_parsers(
                    vendor=source["vendor"]
                )
                
                recommendations = [
                    p for p in similar
                    if p["id"] != source["id"]
                ][:5]
        
        else:
            # General recommendations
            if resource_type == "generator":
                # Recommend top generators with Star Trek theme
                all_gens = self._cache["generators"]["all"]
                recommendations = [
                    g for g in all_gens
                    if g.get("star_trek", False)
                ][:5]
            
            elif resource_type == "parser":
                # Recommend parsers with most fields
                all_pars = sorted(
                    self._cache["parsers"]["all"],
                    key=lambda x: x["fields_count"],
                    reverse=True
                )
                recommendations = all_pars[:5]
        
        return recommendations