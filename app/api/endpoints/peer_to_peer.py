from fastapi import APIRouter, Depends, status
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api import deps


router = APIRouter()
