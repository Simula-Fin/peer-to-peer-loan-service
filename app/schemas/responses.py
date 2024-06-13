from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import List


class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class AccessTokenResponse(BaseResponse):
    token_type: str = "Bearer"
    access_token: str
    expires_at: int
    refresh_token: str
    refresh_token_expires_at: int

class LoanResponse(BaseModel):
    loan_id: int
    borrower_id: int
    amount: float
    interest_rate: float
    duration: int
    status: str
    goals: str
    
    class from_attributes:
        orm_mode = True


class InvestmentResponse(BaseModel):
    investment_id: int
    loan_id: int
    investor_id: int
    amount: float

    class from_attributes:
        orm_mode = True

class PaymentResponse(BaseModel):
    payment_id: int
    loan_id: int
    borrower_id: int
    installment_number: int
    amount: float
    due_date: date
    status: str

    class from_attributes:
        orm_mode = True
