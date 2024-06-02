from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime, date
from enum import Enum

class BaseRequest(BaseModel):
    # may define additional fields or config shared across requests
    pass


class RefreshTokenRequest(BaseRequest):
    refresh_token: str


class UserUpdatePasswordRequest(BaseRequest):
    password: str
 



