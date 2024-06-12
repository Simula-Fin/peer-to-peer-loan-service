from fastapi import APIRouter, Depends, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_session, get_current_user
from app.models import User

from app.schemas.requests import LoanRequest, LoanUpdateRequest
from app.schemas.responses import LoanResponse

from app.services.p2p import LoanCRUD
import json


router = APIRouter()

@router.get("/p2p")
def get_p2p(
    current_user = Depends(get_current_user),
):
    return current_user

@router.post("/loans", response_model=LoanResponse, description="Create a new loan", status_code=status.HTTP_201_CREATED)
async def create_loan(
    loan_in: LoanRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
) -> LoanResponse:
    print(current_user)
    print(loan_in)
    return await LoanCRUD.create_loan(db, loan_in, current_user)


@router.get("/loans", response_model=List[LoanResponse], description="List all loans", status_code=status.HTTP_200_OK)
async def list_loans(
    db: AsyncSession = Depends(get_session)
) -> List[LoanResponse]:
    return await LoanCRUD.list_loans(db)


@router.put("/loan/{loan_id}", response_model=LoanResponse, description="Update a loan", status_code=status.HTTP_200_OK)
async def update_loan(
    loan_id: int,
    loan_in: LoanUpdateRequest,
    db: AsyncSession = Depends(get_session)
) -> LoanResponse:
    return await LoanCRUD.update_loan(db, loan_id, loan_in)


@router.delete("/loan/{loan_id}", description="Delete a loan", status_code=status.HTTP_204_NO_CONTENT)
async def delete_loan(
    loan_id: int,
    db: AsyncSession = Depends(get_session)
):
    await LoanCRUD.delete_loan(db, loan_id)
    return {"message": "Loan deleted successfully"}