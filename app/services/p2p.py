from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import Investment, Investor, Loan, Borrower, RiskProfile, User
from app.schemas.requests import LoanRequest, LoanStatusEnum, LoanUpdateRequest
from app.schemas.responses import LoanResponse, LoanResponsePersonalizated, UserResponse
from typing import List

from app.services.crud_investment import InvestmentCRUD

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
    async def list_loans(db: AsyncSession) -> List[LoanResponsePersonalizated]:
        try:
            result = await db.execute(
                select(Loan, Borrower, User, RiskProfile)
                .join(Borrower, Loan.borrower_id == Borrower.borrower_id)
                .join(User, Borrower.user_id == User.user_id)
                .join(RiskProfile, RiskProfile.borrower_id == Borrower.borrower_id)
            )
            loans = result.all()

            return [
                LoanResponsePersonalizated(
                    loan_id=loan.Loan.loan_id,
                    borrower_id=loan.Loan.borrower_id,
                    amount=loan.Loan.amount,
                    interest_rate=loan.Loan.interest_rate,
                    duration=loan.Loan.duration,
                    status=loan.Loan.status,
                    goals=loan.Loan.goals,
                    risk_score=loan.RiskProfile.risk_score,
                    user=UserResponse(
                        user_id=loan.User.user_id,
                        name=loan.User.name,
                        email=loan.User.email,
                        cpf=loan.User.cpf,
                    )
                )
                for loan in loans
            ]
        
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

    @staticmethod
    async def list_user_loans(db: AsyncSession, user_id: int) -> List[LoanResponse]:
        try:
            
            result = await db.execute(select(Borrower).where(Borrower.user_id == user_id))
            borrower = result.scalar_one_or_none()

            if not borrower:
                raise HTTPException(status_code=404, detail="Borrower not found")

            
            result = await db.execute(select(Loan).where(Loan.borrower_id == borrower.borrower_id))
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
        
        except HTTPException:
            raise
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error retrieving user loans")

    @staticmethod
    async def update_loan_status(db: AsyncSession, loan_id: int, new_status: LoanStatusEnum) -> LoanResponse:
        try:
            # Buscar o empréstimo pelo ID
            result = await db.execute(select(Loan).where(Loan.loan_id == loan_id))
            loan = result.scalar_one_or_none()
            
            if not loan:
                raise HTTPException(status_code=404, detail="Loan not found")
            
            # Atualizar o status do empréstimo
            loan.status = new_status.value

            # Commit para persistir a atualização do status
            await db.commit()
            await db.refresh(loan)

            # Verificar se o novo status é 'payed' para gerar contrato e pagamentos
            if new_status == LoanStatusEnum.payed:
                # Buscar o investimento relacionado a este empréstimo
                result_investment = await db.execute(select(Investment).where(Investment.loan_id == loan_id))
                investment_in = result_investment.scalar_one_or_none()
                if not investment_in:
                    raise HTTPException(status_code=404, detail="Investment not found")

                result_investor = await db.execute(select(Investor).where(Investor.investor_id == investment_in.investor_id))
                investor = result_investor.scalar_one_or_none()
                if not investor:
                    raise HTTPException(status_code=404, detail="Investor not found")

                # Gerar contrato
                await InvestmentCRUD.generate_contract(db, loan, investor)

                # Gerar pagamentos
                await InvestmentCRUD.generate_payments(db, loan, investment_in.amount)

            return LoanResponse.from_orm(loan)
        
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Error updating loan status") 