from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core import database_session
import requests

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/access-token")
SERVICE_URL = get_settings().security.microservice_p2p_url.get_secret_value()


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with database_session.get_async_session() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    try:
        response = requests.get(f"{SERVICE_URL}/users/me", headers={"Authorization": f"Bearer {token}"})
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Token is invalid or expired")
        
        user_info = response.json()
        return user_info
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Failed to verify token")
