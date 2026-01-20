"""API endpoints for parser synchronization with destination SIEM"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
import logging

from app.services.parser_sync_service import get_parser_sync_service, ParserSyncService
from app.core.simple_auth import get_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


class ParserSyncRequest(BaseModel):
    """Request model for parser sync"""
    scenario_id: str = Field(..., description="Scenario identifier")
    config_api_url: str = Field(..., description="Config API URL (e.g., https://xdr.us1.sentinelone.net)")
    config_write_token: str = Field(..., description="Config API token for reading and writing parsers")
    sources: Optional[List[str]] = Field(None, description="Optional list of sources to sync (overrides scenario defaults)")


class ParserSyncResponse(BaseModel):
    """Response model for parser sync"""
    scenario_id: str
    sources_checked: int
    parsers_uploaded: int
    parsers_existing: int
    parsers_failed: int
    results: Dict[str, dict]


@router.post("/sync", response_model=ParserSyncResponse)
async def sync_parsers(
    request: ParserSyncRequest,
    auth_info: tuple = Depends(get_api_key)
):
    """
    Synchronize parsers for a scenario with the destination SIEM
    
    This endpoint:
    1. Determines which parsers are needed for the scenario
    2. Checks if each parser exists in the destination SIEM (using getFile API)
    3. Uploads missing parsers (using putFile API)
    
    Returns detailed status for each parser.
    """
    # Create service with the destination's config API URL
    service = ParserSyncService(config_api_url=request.config_api_url)
    
    # Get sources for the scenario or use provided sources
    if request.sources:
        sources = request.sources
    else:
        sources = service.get_scenario_sources(request.scenario_id)
    
    if not sources:
        logger.warning(f"No sources found for scenario: {request.scenario_id}")
        return ParserSyncResponse(
            scenario_id=request.scenario_id,
            sources_checked=0,
            parsers_uploaded=0,
            parsers_existing=0,
            parsers_failed=0,
            results={}
        )
    
    logger.info(f"Syncing parsers for scenario {request.scenario_id}: {sources}")
    
    # Perform parser sync
    results = service.ensure_parsers_for_sources(
        sources=sources,
        config_write_token=request.config_write_token
    )
    
    # Count results
    uploaded = sum(1 for r in results.values() if r.get('status') == 'uploaded')
    existing = sum(1 for r in results.values() if r.get('status') == 'exists')
    failed = sum(1 for r in results.values() if r.get('status') in ('failed', 'no_parser'))
    
    logger.info(
        f"Parser sync complete for {request.scenario_id}: "
        f"{existing} existing, {uploaded} uploaded, {failed} failed"
    )
    
    return ParserSyncResponse(
        scenario_id=request.scenario_id,
        sources_checked=len(sources),
        parsers_uploaded=uploaded,
        parsers_existing=existing,
        parsers_failed=failed,
        results=results
    )


@router.get("/sources/{scenario_id}")
async def get_scenario_sources(
    scenario_id: str,
    auth_info: tuple = Depends(get_api_key)
):
    """
    Get the list of sources (and their parsers) required for a scenario
    """
    service = get_parser_sync_service()
    sources = service.get_scenario_sources(scenario_id)
    
    result = []
    for source in sources:
        sourcetype = service.get_parser_sourcetype(source)
        result.append({
            "source": source,
            "sourcetype": sourcetype,
            "parser_path": service.get_parser_path_in_siem(sourcetype) if sourcetype else None
        })
    
    return {
        "scenario_id": scenario_id,
        "sources": result
    }


@router.post("/check")
async def check_parser_exists(
    parser_path: str,
    config_token: str,
    auth_info: tuple = Depends(get_api_key)
):
    """
    Check if a specific parser exists in the destination SIEM
    """
    service = get_parser_sync_service()
    exists, content = service.check_parser_exists(config_token, parser_path)
    
    return {
        "parser_path": parser_path,
        "exists": exists,
        "has_content": content is not None
    }
