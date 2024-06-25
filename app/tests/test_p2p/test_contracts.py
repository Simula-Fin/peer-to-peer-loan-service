from fastapi import HTTPException, status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from app.models import Contract, Investor, Loan, RiskProfile, User, Borrower
from app.schemas.requests import LoanRequest, LoanUpdateRequest
from app.schemas.responses import ContractResponse, LoanResponse
from app.services.crud_contracts import ContractCRUD
from datetime import datetime
from app.main import app

@pytest.mark.asyncio
async def test_list_all_contracts(
    client: AsyncClient,
    session: AsyncSession,
    default_user_headers: dict[str, str]
) -> None:
    
    response = await client.get(app.url_path_for("list_all_contracts"),
                                headers=default_user_headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_user_contracts_no_contracts(
    client: AsyncClient,
    session: AsyncSession,
    default_user: User,
) -> None:
    
    contracts = await ContractCRUD.get_user_contracts(db=session, user=default_user)

    assert isinstance(contracts, list)
    assert len(contracts) == 0


@pytest.mark.asyncio
async def test_get_user_contracts_invalid_user(
    client: AsyncClient,
    session: AsyncSession,
) -> None:
    invalid_user = User(
        user_id=999,
        name="Invalid User",
        email="invalid@example.com",
        cpf="99999999999",
    )

    with pytest.raises(HTTPException) as exc_info:
        await ContractCRUD.get_user_contracts(db=session, user=invalid_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST