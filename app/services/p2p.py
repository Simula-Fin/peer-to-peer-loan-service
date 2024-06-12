from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import Loan, Borrower, User
from app.schemas.requests import LoanRequest, LoanUpdateRequest
from app.schemas.responses import LoanResponse
from typing import List

class LoanCRUD:
    
    @staticmethod
    async def create_loan(db: AsyncSession, loan_in: LoanRequest, user: User) -> LoanResponse:
        try:
            borrower = await db.scalar(select(Borrower).where(Borrower.user_id == user["user_id"]))
            if not borrower:
                raise HTTPException(status_code=404, detail="Borrower not found")
            
            print(borrower)
            
            loan = Loan(
                borrower_id=borrower.borrower_id,
                amount=loan_in.amount,
                interest_rate=loan_in.interest_rate,
                duration=loan_in.duration,
                status="pending",
                goals=loan_in.goals
            )
            db.add(loan)
            await db.commit()
            await db.refresh(loan)
            
            return LoanResponse(
                loan_id=loan.loan_id,
                borrower_id=loan.borrower_id,
                amount=loan.amount,
                interest_rate=loan.interest_rate,
                duration=loan.duration,
                status=loan.status,
                goals=loan.goals
            )
        
        except SQLAlchemyError as e:
            print(e)
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Error creating loan")
        
    @staticmethod
    async def list_loans(db: AsyncSession) -> List[LoanResponse]:
        try:
            result = await db.execute(select(Loan))
            loans = result.scalars().all()
            return [LoanResponse(
                loan_id=loan.loan_id,
                borrower_id=loan.borrower_id,
                amount=loan.amount,
                interest_rate=loan.interest_rate,
                duration=loan.duration,
                status=loan.status,
                goals=loan.goals
            ) for loan in loans]
        
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="Error retrieving loans")
        
    @staticmethod
    async def delete_loan(db: AsyncSession, loan_id: int) -> None:
        try:
            result = await db.execute(select(Loan).where(Loan.loan_id == loan_id))
            loan = result.scalar_one_or_none()

            if not loan:
                raise HTTPException(status_code=404, detail="Loan not found")
            
            await db.delete(loan)
            await db.commit()
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error deleting loan")    
        

    @staticmethod
    async def update_loan(db: AsyncSession, loan_id: int, loan_in: LoanUpdateRequest) -> LoanResponse:
        try:
            result = await db.execute(select(Loan).where(Loan.loan_id == loan_id))
            loan = result.scalar_one_or_none()

            if not loan:
                raise HTTPException(status_code=404, detail="Loan not found")
            
            loan.amount = loan_in.amount
            loan.interest_rate = loan_in.interest_rate
            loan.duration = loan_in.duration
            loan.status = loan_in.status
            loan.goals = loan_in.goals

            await db.commit()
            await db.refresh(loan)

            return LoanResponse(
                loan_id=loan.loan_id,
                borrower_id=loan.borrower_id,
                amount=loan.amount,
                interest_rate=loan.interest_rate,
                duration=loan.duration,
                status=loan.status,
                goals=loan.goals
            )
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error updating loan")    