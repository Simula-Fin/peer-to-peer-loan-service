import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select, and_
from sqlalchemy.orm import selectinload, joinedload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import Investment, Investor, Loan, User, Payment, Borrower
from app.schemas.requests import PaymentUpdateRequest
from app.schemas.responses import InvestmentResponse, LoanResponsePersonalizated, PaymentResponse, PaymentResponseDetailed, UserResponse
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
        
    @staticmethod
    async def get_investor_pending_payments(db: AsyncSession) -> list[PaymentResponseDetailed]:
        try:
            stmt = (
                select(Payment, Loan, Investment, Investor, User)
                .join(Loan, Payment.loan_id == Loan.loan_id)
                .join(Borrower, Payment.borrower_id == Borrower.borrower_id)
                .join(Investment, Loan.loan_id == Investment.loan_id)
                .join(Investor, Investment.investor_id == Investor.investor_id)
                .join(User, Investor.user_id == User.user_id)
                .options(
                    selectinload(Payment.loan)
                    .selectinload(Loan.investments)
                    .selectinload(Investment.investor)
                    .selectinload(Investor.user)
                )
                .where(
                    Payment.status == "payed",
                    Payment.status_payment_investor == "pending"
                )
            )

            result = await db.execute(stmt)
            payments = result.all()

            return [
                PaymentResponseDetailed(
                    payment_id=payment.Payment.payment_id,
                    loan_id=payment.Payment.loan_id,
                    borrower_id=payment.Payment.borrower_id,
                    installment_number=payment.Payment.installment_number,
                    amount=payment.Payment.amount,
                    due_date=payment.Payment.due_date,
                    status=payment.Payment.status,
                    status_payment_investor=payment.Payment.status_payment_investor,
                    investor_profit=payment.Payment.investor_profit,
                    loan=LoanResponsePersonalizated(
                        loan_id=payment.Loan.loan_id,
                        borrower_id=payment.Loan.borrower_id,
                        amount=payment.Loan.amount,
                        interest_rate=payment.Loan.interest_rate,
                        duration=payment.Loan.duration,
                        status=payment.Loan.status,
                        goals=payment.Loan.goals,
                        risk_score=30,
                        investor_profit=payment.Loan.investor_profit,
                        user=UserResponse(
                            user_id=payment.User.user_id,
                            name=payment.User.name,
                            email=payment.User.email,
                            cpf=payment.User.cpf
                        )
                    ),
                    investment=InvestmentResponse(
                        investment_id=payment.Investment.investment_id,
                        loan_id=payment.Investment.loan_id,
                        amount=payment.Investment.amount,
                        investor_id=payment.Investment.investor_id,
                        investor=UserResponse(
                            user_id=payment.Investor.user_id,
                            name=payment.Investor.user.name,
                            email=payment.Investor.user.email,
                            cpf=payment.Investor.user.cpf
                        )
                    )
                )
                for payment in payments
            ]

        except SQLAlchemyError as e:
            print(e)
            raise HTTPException(status_code=500, detail="Database error occurred")

        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Error fetching investor pending payments")    