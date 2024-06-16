import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload, joinedload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import Investment, Investor, Loan, User, Payment, Borrower
from app.schemas.requests import PaymentUpdateRequest
from app.schemas.responses import PaymentResponse
from typing import List


class PaymentCRUD:

    @staticmethod
    async def get_user_payments(db: AsyncSession, user: User) -> List[PaymentResponse]:
        try:
            result = await db.execute(
                select(User)
                .options(
                    selectinload(User.investor),
                    selectinload(User.borrower)
                )
                .filter_by(user_id=user["user_id"])
            )
            user = result.scalars().first()
            
            if user is None:
                return []

            query = select(Payment).options(joinedload(Payment.loan))

            if user.investor:
                query = query.join(Loan).join(Investment).where(Investment.investor_id == user.investor.investor_id)
            elif user.borrower:
                query = query.where(Payment.borrower_id == user.borrower.borrower_id)

            payments_result = await db.execute(query)
            payments = payments_result.scalars().all()
            
            return [PaymentResponse.from_orm(payment) for payment in payments]
            
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Error fetching payments")
        
    @staticmethod
    async def get_user_payments_borrower(db: AsyncSession, user: User) -> List[PaymentResponse]:
        try:
            result = await db.execute(
                select(User).options(selectinload(User.borrower)).filter_by(user_id=user["user_id"])
            )
            user = result.scalars().first()
            
            if user is None or user.borrower is None:
                return []

            query = (
                select(Payment)
                .where(Payment.borrower_id == user.borrower.borrower_id)
                .options(joinedload(Payment.loan))
            )

            payments_result = await db.execute(query)
            payments = payments_result.scalars().all()
            
            return [PaymentResponse.from_orm(payment) for payment in payments]
            
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Error fetching payments")


    @staticmethod
    async def get_user_payments_investor(db: AsyncSession, user: User) -> List[PaymentResponse]:
        try:
            result = await db.execute(
                select(User).options(selectinload(User.investor)).filter_by(user_id=user["user_id"])
            )
            user = result.scalars().first()
            
            if user is None or user.investor is None:
                return []

            query = (
                select(Payment)
                .join(Loan)
                .join(Investment)
                .options(joinedload(Payment.loan))
                .where(Investment.investor_id == user.investor.investor_id)
            )

            payments_result = await db.execute(query)
            payments = payments_result.scalars().all()
            
            return [PaymentResponse.from_orm(payment) for payment in payments]
            
        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            print(e)
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

    @staticmethod
    async def update_payment_investor_status(db: AsyncSession, payment_id: int, status: str) -> PaymentResponse:
        try:
            payment = await db.scalar(select(Payment).where(Payment.payment_id == payment_id))
            if not payment:
                raise HTTPException(status_code=404, detail="Payment not found")

            payment.status_payment_investor = status
            db.add(payment)
            await db.commit()
            await db.refresh(payment)

            return PaymentResponse.from_orm(payment)
        
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Error updating payment investor status")