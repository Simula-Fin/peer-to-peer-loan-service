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
    
    class from_attributes:
        orm_mode = True

class LoanUpdateRequest(BaseModel):
    amount: float
    interest_rate: float
    duration: int
    status: str
    goals: str
    
    class from_attributes:
        orm_mode = True    

class InvestmentRequest(BaseModel):
    loan_id: int
    amount: float

    class from_attributes:
        orm_mode = True            

class PaymentUpdateRequest(BaseModel):
    status: str

