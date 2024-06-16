import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import Loan, User, Contract, Borrower, Investor
from app.schemas.responses import ContractResponse, LoanResponsePersonalizated, UserResponse
from typing import List

class ContractCRUD:

    @staticmethod
    async def get_all_contracts(db: AsyncSession) -> List[ContractResponse]:
        try:
            borrower_user_alias = aliased(User)
            investor_user_alias = aliased(User)

            result = await db.execute(
                select(Contract, Loan, Borrower, borrower_user_alias, Investor, investor_user_alias)
                .outerjoin(Borrower, Contract.borrower_id == Borrower.borrower_id)
                .outerjoin(Investor, Contract.investor_id == Investor.investor_id)
                .outerjoin(Loan, Contract.loan_id == Loan.loan_id)
                .outerjoin(borrower_user_alias, Borrower.user_id == borrower_user_alias.user_id)
                .outerjoin(investor_user_alias, Investor.user_id == investor_user_alias.user_id)
            )
            contracts = result.all()

            return [
                ContractResponse(
                    contract_id=contract[0].contract_id,
                    loan_id=contract[0].loan_id,
                    investor_id=contract[0].investor_id,
                    borrower_id=contract[0].borrower_id,
                    status=contract[0].status,
                    date_signed=contract[0].date_signed,
                    investor_signature_digital_uuid=contract[0].investor_signature_digital_uuid,
                    borrower_signature_digital_uuid=contract[0].borrower_signature_digital_uuid,
                    loan=LoanResponsePersonalizated(
                        loan_id=contract[1].loan_id,
                        borrower_id=contract[1].borrower_id,
                        amount=contract[1].amount,
                        interest_rate=contract[1].interest_rate,
                        duration=contract[1].duration,
                        status=contract[1].status,
                        goals=contract[1].goals,
                        risk_score=30,
                        user = UserResponse(
                            user_id=contract[3].user_id,
                            name=contract[3].name,
                            email=contract[3].email,
                            cpf=contract[3].cpf
                        )
                    ),
                    borrower_user=UserResponse(
                        user_id=contract[3].user_id,
                        name=contract[3].name,
                        email=contract[3].email,
                        cpf=contract[3].cpf
                    ),
                    investor_user=UserResponse(
                        user_id=contract[5].user_id,
                        name=contract[5].name,
                        email=contract[5].email,
                        cpf=contract[5].cpf
                    )
                )
                for contract in contracts
            ]
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error fetching contracts")

    @staticmethod
    async def get_user_contracts(db: AsyncSession, user: User) -> List[ContractResponse]:
        try:
            borrower_user_alias = aliased(User)
            investor_user_alias = aliased(User)

            result = await db.execute(
                select(Contract, Loan, Borrower, borrower_user_alias, Investor, investor_user_alias)
                .outerjoin(Borrower, Contract.borrower_id == Borrower.borrower_id)
                .outerjoin(Investor, Contract.investor_id == Investor.investor_id)
                .outerjoin(Loan, Contract.loan_id == Loan.loan_id)
                .outerjoin(borrower_user_alias, Borrower.user_id == borrower_user_alias.user_id)
                .outerjoin(investor_user_alias, Investor.user_id == investor_user_alias.user_id)
                .where((Borrower.user_id == user["user_id"]) | (Investor.user_id == user["user_id"]))
            )
            contracts = result.all()

            return [
                ContractResponse(
                    contract_id=contract[0].contract_id,
                    loan_id=contract[0].loan_id,
                    investor_id=contract[0].investor_id,
                    borrower_id=contract[0].borrower_id,
                    status=contract[0].status,
                    date_signed=contract[0].date_signed,
                    investor_signature_digital_uuid=contract[0].investor_signature_digital_uuid,
                    borrower_signature_digital_uuid=contract[0].borrower_signature_digital_uuid,
                    loan=LoanResponsePersonalizated(
                        loan_id=contract[1].loan_id,
                        borrower_id=contract[1].borrower_id,
                        amount=contract[1].amount,
                        interest_rate=contract[1].interest_rate,
                        duration=contract[1].duration,
                        status=contract[1].status,
                        goals=contract[1].goals,
                        risk_score=30,
                        user = UserResponse(
                            user_id=contract[3].user_id,
                            name=contract[3].name,
                            email=contract[3].email,
                            cpf=contract[3].cpf
                        )
                    ),
                    borrower_user=UserResponse(
                        user_id=contract[3].user_id,
                        name=contract[3].name,
                        email=contract[3].email,
                        cpf=contract[3].cpf
                    ),
                    investor_user=UserResponse(
                        user_id=contract[5].user_id,
                        name=contract[5].name,
                        email=contract[5].email,
                        cpf=contract[5].cpf
                    )
                )
                for contract in contracts
            ]

        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred")

        except Exception as e:
            print(e)
            raise HTTPException(status_code=400, detail="Error fetching user contracts")