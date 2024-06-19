from fastapi import APIRouter, Depends, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_session, get_current_user, admin_required
from app.models import User

from app.schemas.requests import PaymentUpdateRequest
from app.schemas.responses import PaymentResponse, PaymentResponseDetailed

from app.services.crud_payments import PaymentCRUD

router = APIRouter()

@router.get("/payments/user/borrower", response_model=List[PaymentResponse], description="List all payments of the current user borrower")
async def list_user_payments_borrower(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await PaymentCRUD.get_user_payments_borrower(db, current_user)

@router.get("/payments/user/investor", response_model=List[PaymentResponse], description="List all payments of the current user investor")
async def list_user_payments_investor(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await PaymentCRUD.get_user_payments_investor(db, current_user)

@router.patch("/payments/{payment_id}", response_model=PaymentResponse, description="Update the status of a payment")
async def update_payment_status(
    payment_id: int,
    payment_update: PaymentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await PaymentCRUD.update_payment_status(db, payment_id, payment_update.status)

@router.patch("/payments/investor/{payment_id}", response_model=PaymentResponse, description="Update the status of a payment investor")
async def update_payment_investor_status(
    payment_id: int,
    payment_update: PaymentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await PaymentCRUD.update_payment_investor_status(db, payment_id, payment_update.status)


@router.get("/payments/pending-payments", response_model=list[PaymentResponseDetailed])
async def get_investor_pending_payments(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(admin_required)
):
    return await PaymentCRUD.get_investor_pending_payments(db)