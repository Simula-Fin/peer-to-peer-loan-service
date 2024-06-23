from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from typing import List, Optional


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
    investor_profit: Optional[float]
    
    class Config:
        from_attributes = True


class InvestmentResponse(BaseModel):
    investment_id: int
    loan_id: int
    investor_id: int
    amount: float

    class Config:
        from_attributes = True

class PaymentResponse(BaseModel):
    payment_id: int
    loan_id: int
    borrower_id: int
    installment_number: int
    amount: float
    due_date: datetime
    status: str
    status_payment_investor: str
    investor_profit: Optional[float]

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    cpf: str

    class Config:
        from_attributes = True

class LoanResponsePersonalizated(BaseModel):
    loan_id: int
    borrower_id: int
    amount: float
    interest_rate: float
    duration: int
    status: str
    goals: str
    user: UserResponse
    risk_score: Optional[int]
    investor_profit: Optional[float]

    class Config:
        from_attributes = True


class InvestmentResponsePersonalizated(BaseModel):
    investment_id: int
    loan_id: int
    investor_id: int
    amount: float
    risk_score: Optional[int]
    loan: LoanResponse
    borrower_user: UserResponse
    investor_user: UserResponse

    class Config:
        from_attributes = True

class InvestmentResponseDetailed(BaseModel):
    investment_id: int
    amount: float
    loan: LoanResponsePersonalizated
    investor: UserResponse

    class Config:
        from_attributes = True


class ContractResponse(BaseModel):
    contract_id: int
    loan_id: int
    investor_id: int
    borrower_id: int
    status: str
    date_signed: datetime
    investor_signature_digital_uuid: str
    borrower_signature_digital_uuid: str
    loan: LoanResponsePersonalizated
    borrower_user: UserResponse
    investor_user: UserResponse

    class Config:
        from_attributes = True


class PaymentResponseDetailed(BaseModel):
    payment_id: int
    loan_id: int
    borrower_id: int
    installment_number: int
    amount: float
    due_date: datetime
    status: str
    status_payment_investor: str
    investor_profit: Optional[float]
    loan: Optional[LoanResponsePersonalizated]
    investment: Optional[InvestmentResponse]

    class Config:
        from_attributes = True