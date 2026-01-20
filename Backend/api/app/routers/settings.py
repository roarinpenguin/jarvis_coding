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


class HiddenScenariosUpdate(BaseModel):
    """Request model for updating hidden scenarios"""
    hidden_scenarios: List[str]


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
