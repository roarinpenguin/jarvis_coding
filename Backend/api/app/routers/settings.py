"""API endpoints for application settings"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import logging

from app.services.destination_service import get_session
from app.models.settings import Setting
from app.core.simple_auth import get_api_key

logger = logging.getLogger(__name__)

router = APIRouter()


DEFAULT_PARSER_REPOSITORIES = [
    "https://github.com/Sentinel-One/ai-siem/tree/main/parsers",
    "https://github.com/natesmalley/jarvis_coding/tree/main/Backend/parsers",
]


class HiddenScenariosUpdate(BaseModel):
    """Request model for updating hidden scenarios"""
    hidden_scenarios: List[str]


class ParserRepositoriesUpdate(BaseModel):
    """Request model for updating parser GitHub repositories"""
    repositories: List[str]  # Up to 3 GitHub repo URLs
    github_token: Optional[str] = None  # Optional GitHub PAT for private repos


@router.get("/hidden-scenarios")
async def get_hidden_scenarios(
    session: AsyncSession = Depends(get_session),
    auth_info: tuple = Depends(get_api_key)
):
    """Get list of hidden scenario IDs"""
    result = await session.execute(
        select(Setting).where(Setting.key == "hidden_scenarios")
    )
    setting = result.scalar_one_or_none()
    
    if setting and setting.value:
        try:
            return {"hidden_scenarios": json.loads(setting.value)}
        except json.JSONDecodeError:
            return {"hidden_scenarios": []}
    
    return {"hidden_scenarios": []}


@router.put("/hidden-scenarios")
async def update_hidden_scenarios(
    update: HiddenScenariosUpdate,
    session: AsyncSession = Depends(get_session),
    auth_info: tuple = Depends(get_api_key)
):
    """Update list of hidden scenario IDs"""
    result = await session.execute(
        select(Setting).where(Setting.key == "hidden_scenarios")
    )
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = json.dumps(update.hidden_scenarios)
    else:
        setting = Setting(
            key="hidden_scenarios",
            value=json.dumps(update.hidden_scenarios)
        )
        session.add(setting)
    
    await session.commit()
    logger.info(f"Updated hidden scenarios: {update.hidden_scenarios}")
    
    return {"hidden_scenarios": update.hidden_scenarios}


@router.get("/parser-repositories")
async def get_parser_repositories(
    session: AsyncSession = Depends(get_session),
    auth_info: tuple = Depends(get_api_key)
):
    """Get list of GitHub parser repository URLs and token"""
    result = await session.execute(
        select(Setting).where(Setting.key == "parser_repositories")
    )
    setting = result.scalar_one_or_none()
    
    repos = []
    if setting and setting.value:
        try:
            repos = json.loads(setting.value)
        except json.JSONDecodeError:
            pass

    if not repos:
        repos = DEFAULT_PARSER_REPOSITORIES
    
    # Get GitHub token
    token_result = await session.execute(
        select(Setting).where(Setting.key == "github_token")
    )
    token_setting = token_result.scalar_one_or_none()
    github_token = token_setting.value if token_setting else None
    
    return {"repositories": repos, "github_token": github_token}


@router.put("/parser-repositories")
async def update_parser_repositories(
    update: ParserRepositoriesUpdate,
    session: AsyncSession = Depends(get_session),
    auth_info: tuple = Depends(get_api_key)
):
    """Update list of GitHub parser repository URLs (max 3) and token"""
    # Limit to 3 repositories
    repos = update.repositories[:3]
    
    # Validate URLs (basic check)
    valid_repos = []
    for repo in repos:
        repo = repo.strip()
        if repo and ("github.com" in repo or repo.startswith("https://")):
            valid_repos.append(repo)
    
    # Update repositories
    result = await session.execute(
        select(Setting).where(Setting.key == "parser_repositories")
    )
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = json.dumps(valid_repos)
    else:
        setting = Setting(
            key="parser_repositories",
            value=json.dumps(valid_repos)
        )
        session.add(setting)
    
    # Update GitHub token if provided
    if update.github_token is not None:
        token_result = await session.execute(
            select(Setting).where(Setting.key == "github_token")
        )
        token_setting = token_result.scalar_one_or_none()
        
        if token_setting:
            token_setting.value = update.github_token
        else:
            token_setting = Setting(
                key="github_token",
                value=update.github_token
            )
            session.add(token_setting)
    
    await session.commit()
    logger.info(f"Updated parser repositories: {valid_repos}")
    
    return {"repositories": valid_repos, "github_token": update.github_token}
