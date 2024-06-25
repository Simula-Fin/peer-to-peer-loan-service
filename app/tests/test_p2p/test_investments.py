from datetime import date
from fastapi import HTTPException, status
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
from app.models import Investor, Loan, Payment, User
from app.schemas.requests import InvestmentRequest
from app.schemas.responses import InvestmentResponse
from app.services.crud_investment import InvestmentCRUD

@pytest.mark.asyncio
async def test_create_investment(
    client: AsyncClient,
    session: AsyncSession,
    default_user: User,
    default_loan: Loan,
    default_investor: Investor
) -> None:
    # Create an investment request
    investment_request = InvestmentRequest(
        loan_id=default_loan.loan_id,
        amount=5000.0
    )

    investment_response = await InvestmentCRUD.create_investment(
        db=session, investment_in=investment_request, user=default_user
    )

    assert isinstance(investment_response, InvestmentResponse)
    assert investment_response.loan_id == investment_request.loan_id
    assert investment_response.investor_id == default_investor.investor_id
    assert investment_response.amount == investment_request.amount


@pytest.mark.asyncio
async def test_generate_payments(
    session: AsyncSession,
    default_loan: Loan
) -> None:
    
    await InvestmentCRUD.generate_payments(db=session, loan=default_loan, investment_amount=5000.0)

    payments = await session.execute(
        select(Payment).where(Payment.loan_id == default_loan.loan_id)
    )
    generated_payments = payments.fetchall()

    assert len(generated_payments) == default_loan.duration

    for payment in generated_payments:
        assert payment[0].amount > 0
        assert payment[0].status == "pending"