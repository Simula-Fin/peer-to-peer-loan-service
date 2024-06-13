import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models import User, Contract, Borrower, Investor
from app.schemas.responses import ContractResponse
from typing import List

class ContractCRUD:

    @staticmethod
    async def get_all_contracts(db: AsyncSession) -> List[ContractResponse]:
        try:
            contracts = await db.execute(select(Contract))
            contracts = contracts.scalars().all()
            return [ContractResponse.from_orm(contract) for contract in contracts]
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error fetching contracts")

    @staticmethod
    async def get_user_contracts(db: AsyncSession, user: User) -> List[ContractResponse]:
        try:
            result = await db.execute(
                select(Contract)
                .outerjoin(Borrower, Contract.borrower_id == Borrower.borrower_id)
                .outerjoin(Investor, Contract.investor_id == Investor.investor_id)
                .where((Borrower.user_id == user["user_id"]) | (Investor.user_id == user["user_id"]))
            )
            contracts = result.scalars().all()
            return [ContractResponse.from_orm(contract) for contract in contracts]
        
        except SQLAlchemyError as e:
            raise HTTPException(status_code=500, detail="Database error occurred")
        
        except Exception as e:
            raise HTTPException(status_code=400, detail="Error fetching user contracts")