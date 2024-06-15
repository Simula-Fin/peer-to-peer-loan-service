from fastapi import APIRouter, Depends, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_session, get_current_user
from app.models import User

from app.schemas.requests import InvestmentRequest
from app.schemas.responses import InvestmentResponse, InvestmentResponseDetailed, InvestmentResponsePersonalizated

from app.services.crud_investment import InvestmentCRUD

router = APIRouter()

@router.post("/investments", response_model=InvestmentResponse, description="Create a new investment", status_code=status.HTTP_201_CREATED)
async def create_investment(
    investment_in: InvestmentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> InvestmentResponse:
    return await InvestmentCRUD.create_investment(db, investment_in, current_user)


@router.get("/investments", response_model=List[InvestmentResponseDetailed], description="List all investments", status_code=status.HTTP_200_OK)
async def list_investments(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[InvestmentResponseDetailed]:
    return await InvestmentCRUD.list_investments(db)


@router.get("/investments/user", response_model=List[InvestmentResponsePersonalizated], description="List investments of a specific user", status_code=status.HTTP_200_OK)
async def list_user_investments(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> List[InvestmentResponsePersonalizated]:
    current_user_id = current_user["user_id"]
    return await InvestmentCRUD.list_user_investments(db, current_user_id)