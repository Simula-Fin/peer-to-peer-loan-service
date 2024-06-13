import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import Loan, Borrower, User, Investment, Investor, Payment, Contract
from app.schemas.requests import InvestmentRequest
from app.schemas.responses import InvestmentResponse
from typing import List

from datetime import datetime, timedelta

class InvestmentCRUD:

    @staticmethod
    async def create_investment(db: AsyncSession, investment_in: InvestmentRequest, user: User) -> InvestmentResponse:
        try:
            # Verificar se o investidor é válido
            investor = await db.scalar(select(Investor).where(Investor.user_id == user["user_id"]))
            if not investor:
                raise HTTPException(status_code=404, detail="Investor not found")

            # Verificar se o empréstimo é válido
            loan = await db.scalar(select(Loan).where(Loan.loan_id == investment_in.loan_id, Loan.status == "pending"))
            if not loan:
                raise HTTPException(status_code=404, detail="Loan not found")

            # Criar nova instância de Investment
            investment = Investment(
                loan_id=investment_in.loan_id,
                investor_id=investor.investor_id,
                amount=investment_in.amount
            )
            db.add(investment)

            # Atualizar o status do empréstimo para "done"
            loan.status = "done"
            db.add(loan)

            # Gerar contrato
            await InvestmentCRUD.generate_contract(db, loan, investor)

            # Gerar pagamentos
            await InvestmentCRUD.generate_payments(db, loan, investment_in.amount)

            await db.commit()
            await db.refresh(investment)

            # Retornar a resposta
            return InvestmentResponse(
                investment_id=investment.investment_id,
                loan_id=investment.loan_id,
                investor_id=investment.investor_id,
                amount=investment.amount
            )
        
        except SQLAlchemyError as e:
            print(e)
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Error creating investment")

    @staticmethod
    async def generate_payments(db: AsyncSession, loan: Loan, investment_amount: float):
        try:
            # Calcular o valor de cada parcela
            monthly_payment = investment_amount / loan.duration

            for i in range(loan.duration):
                due_date = datetime.now() + timedelta(days=30 * (i + 1))
                payment = Payment(
                    loan_id=loan.loan_id,
                    borrower_id=loan.borrower_id,
                    installment_number=i + 1,
                    amount=monthly_payment,
                    due_date=due_date,
                    status="pending"
                )
                db.add(payment)
            
            await db.commit()
        
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error generating payments")

    async def list_investments(db: AsyncSession) -> List[InvestmentResponse]:
        try:
            result = await db.execute(select(Investment))
            investments = result.scalars().all()
            return [InvestmentResponse(
                investment_id=investment.investment_id,
                loan_id=investment.loan_id,
                investor_id=investment.investor_id,
                amount=investment.amount
            ) for investment in investments]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error retrieving investments")

    @staticmethod
    async def generate_contract(db: AsyncSession, loan: Loan, investor: Investor):
        try:
            contract = Contract(
                loan_id=loan.loan_id,
                investor_id=investor.investor_id,
                borrower_id=loan.borrower_id,
                status="active",
                date_signed=datetime.now(),
                investor_signature_digital_uuid=str(uuid.uuid4()),
                borrower_signature_digital_uuid=str(uuid.uuid4())
            )
            db.add(contract)

            await db.commit()
        
        except SQLAlchemyError as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Error generating contract")

    @staticmethod
    async def list_user_investments(db: AsyncSession, user_id: int) -> List[InvestmentResponse]:
        try:
            # Verificar se o usuário é um investidor válido
            investor = await db.scalar(select(Investor).where(Investor.user_id == user_id))
            if not investor:
                raise HTTPException(status_code=404, detail="Investor not found")

            # Consultar os investimentos do usuário
            result = await db.execute(select(Investment).where(Investment.investor_id == investor.investor_id))
            investments = result.scalars().all()

            return [InvestmentResponse(
                investment_id=investment.investment_id,
                loan_id=investment.loan_id,
                investor_id=investment.investor_id,
                amount=investment.amount
            ) for investment in investments]
        
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error retrieving user investments")       