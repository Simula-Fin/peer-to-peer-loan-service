from datetime import date
from fastapi import HTTPException, status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from app.models import Loan, RiskProfile, User, Borrower
from app.schemas.requests import LoanRequest, LoanUpdateRequest
from app.schemas.responses import LoanResponse
from app.services.p2p import LoanCRUD


@pytest.mark.asyncio
async def test_create_loan_creates_record_in_db(
    client: AsyncClient,
    session: AsyncSession,
    default_user: User,
    default_borrower: Borrower,
) -> None:
    loan_request = {
        "amount": 10000.0,
        "interest_rate": 5.0,
        "duration": 12,
        "goals": "compras"
    }

    loan_in = LoanRequest(**loan_request)
    loan_response = await LoanCRUD.create_loan(db=session, loan_in=loan_in, user=default_user)

    loan_count = await session.scalar(
        select(func.count()).where(Loan.borrower_id == default_borrower.borrower_id)
    )
    assert loan_count == 1

    assert isinstance(loan_response, LoanResponse)
    assert loan_response.amount == loan_request["amount"]
    assert loan_response.interest_rate == loan_request["interest_rate"]
    assert loan_response.duration == loan_request["duration"]
    assert loan_response.goals == loan_request["goals"]

@pytest.mark.asyncio
async def test_create_loan_with_nonexistent_borrower(
    client: AsyncClient,
    session: AsyncSession,
    default_user: User,
) -> None:
    loan_request = {
        "amount": 10000.0,
        "interest_rate": 5.0,
        "duration": 12,
        "goals": "compras"
    }

    loan_in = LoanRequest(**loan_request)

    borrower = await session.scalar(select(Borrower).where(Borrower.user_id == default_user["user_id"]))
    if borrower:
        await session.delete(borrower)
        await session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await LoanCRUD.create_loan(db=session, loan_in=loan_in, user=default_user)

    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc_info.value.detail == "Error creating loan"

@pytest.mark.asyncio
async def test_list_loans(session: AsyncSession, default_user: User, default_borrower: Borrower, default_loan: Loan) -> None:
    
    risk_profile = RiskProfile(
        borrower_id=default_borrower.borrower_id,
        risk_score=5
    )
    session.add(risk_profile)
    await session.commit()

    
    loans = await LoanCRUD.list_loans(db=session)

    assert len(loans) == 1
    loan_response = loans[0]
    assert loan_response.loan_id == default_loan.loan_id
    assert loan_response.borrower_id == default_borrower.borrower_id
    assert loan_response.amount == default_loan.amount
    assert loan_response.interest_rate == default_loan.interest_rate
    assert loan_response.duration == default_loan.duration
    assert loan_response.status == default_loan.status
    assert loan_response.goals == default_loan.goals
    assert loan_response.risk_score == 5
    assert loan_response.user.user_id == default_user["user_id"]

@pytest.mark.asyncio
async def test_delete_loan(session: AsyncSession, default_loan: Loan) -> None:
    
    await LoanCRUD.delete_loan(db=session, loan_id=default_loan.loan_id)

    
    loan_count = await session.scalar(
        select(func.count()).where(Loan.loan_id == default_loan.loan_id)
    )
    assert loan_count == 0

@pytest.mark.asyncio
async def test_delete_loan_nonexistent(session: AsyncSession) -> None:
    
    with pytest.raises(HTTPException) as exc_info:
        await LoanCRUD.delete_loan(db=session, loan_id=9999)

    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error deleting loan"

@pytest.mark.asyncio
async def test_update_loan(session: AsyncSession, default_loan: Loan) -> None:
    loan_update_request = LoanUpdateRequest(
        amount=20000.0,
        interest_rate=4.5,
        duration=24,
        status="approved",
        goals="compras"
    )

    
    updated_loan = await LoanCRUD.update_loan(db=session, loan_id=default_loan.loan_id, loan_in=loan_update_request)

    assert updated_loan.loan_id == default_loan.loan_id
    assert updated_loan.amount == loan_update_request.amount
    assert updated_loan.interest_rate == loan_update_request.interest_rate
    assert updated_loan.duration == loan_update_request.duration
    assert updated_loan.status == loan_update_request.status
    assert updated_loan.goals == loan_update_request.goals

@pytest.mark.asyncio
async def test_update_loan_nonexistent(session: AsyncSession) -> None:
    loan_update_request = LoanUpdateRequest(
        amount=20000.0,
        interest_rate=4.5,
        duration=24,
        status="approved",
        goals="renovação"
    )

    with pytest.raises(HTTPException) as exc_info:
        await LoanCRUD.update_loan(db=session, loan_id=9999, loan_in=loan_update_request)

    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Error updating loan"    
