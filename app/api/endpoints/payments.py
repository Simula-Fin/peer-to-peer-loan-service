from fastapi import APIRouter, Depends, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.deps import get_session, get_current_user
from app.models import User

from app.schemas.requests import PaymentUpdateRequest
from app.schemas.responses import PaymentResponse

from app.services.crud_payments import PaymentCRUD

router = APIRouter()

@router.get("/payments", response_model=List[PaymentResponse], description="List all payments of the current user")
async def list_user_payments(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await PaymentCRUD.get_user_payments(db, current_user)

@router.patch("/payments/{payment_id}", response_model=PaymentResponse, description="Update the status of a payment")
async def update_payment_status(
    payment_id: int,
    payment_update: PaymentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_session)
):
    return await PaymentCRUD.update_payment_status(db, payment_id, payment_update.status)