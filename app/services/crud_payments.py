import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import User, Payment
from app.schemas.requests import PaymentUpdateRequest
from app.schemas.responses import PaymentResponse
from typing import List


class PaymentCRUD:

    @staticmethod
    async def get_user_payments(db: AsyncSession, user: User) -> List[PaymentResponse]:
        try:
            payments = await db.execute(select(Payment).where(Payment.borrower_id == user["user_id"]))
            payments = payments.scalars().all()
            return [PaymentResponse.from_orm(payment) for payment in payments]
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error fetching payments")

    @staticmethod
    async def update_payment_status(db: AsyncSession, payment_id: int, status: str) -> PaymentResponse:
        try:
            payment = await db.scalar(select(Payment).where(Payment.payment_id == payment_id))
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")

            payment.status = status
            db.add(payment)
            await db.commit()
            await db.refresh(payment)

            return PaymentResponse.from_orm(payment)
        
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Error updating payment status")