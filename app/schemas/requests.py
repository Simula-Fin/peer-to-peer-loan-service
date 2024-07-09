from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, date
from enum import Enum
from typing import List
class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str

class LoanRequest(BaseModel):
    amount: float
    interest_rate: float
    duration: int
    goals: str
    
    class Config:
        from_attributes = True

class LoanUpdateRequest(BaseModel):
    amount: float
    interest_rate: float
    duration: int
    status: str
    goals: str
    
    class Config:
        from_attributes = True    

class InvestmentRequest(BaseModel):
    loan_id: int
    amount: float

    class Config:
        from_attributes = True            

class PaymentUpdateRequest(BaseModel):
    status: str

class LoanStatusEnum(str, Enum):
    pending = "pending"
    solicited = "solicited"
    approved = "approved"
    payed = "payed"
    done = "done"

# Schema para atualizar status do empréstimo
class UpdateLoanStatusRequest(BaseModel):
    status: LoanStatusEnum

    class Config:
        from_attributes = True

class RSAEncryptRequest(BaseModel):
    message: str
    public_key: str

class RSADecryptRequest(BaseModel):
    message: str
    private_key: str

class ChatBotRequest(BaseModel):
    prompt: str
    model: str = "gpt-3.5-turbo"
    max_tokens: int = 2048
    temperature: float = 0.5