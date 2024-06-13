from fastapi import APIRouter, Depends, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_session, get_current_user
from app.models import User
from app.schemas.responses import ContractResponse

from app.services.crud_contracts import ContractCRUD


router = APIRouter()

@router.get("/contracts", response_model=List[ContractResponse], description="List all contracts")
async def list_all_contracts(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    return await ContractCRUD.get_all_contracts(db)

@router.get("/contracts/user", response_model=List[ContractResponse], description="List contracts of the current user")
async def list_user_contracts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await ContractCRUD.get_user_contracts(db, current_user)