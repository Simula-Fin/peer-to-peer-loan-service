import asyncio
from datetime import date, datetime
import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
import sqlalchemy
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
)

from app.core import database_session
from app.core.config import get_settings
from app.main import app as fastapi_app
from app.models import Base, Contract, Loan, User, Borrower, Investor

default_user_id = "b75365d9-7bf9-4f54-add5-aeab333a087b"
default_user_email = "geralt@wiedzmin.pl"
default_user_password = "geralt"
default_user_telephone = "48123456789"
default_user_name = "Geralt of Rivia"
default_user_monthly_income = 5000.0
default_user_cpf = "12345678901"
default_user_birth_date = date(1990, 1, 1)
default_user_pix_key = "1234567890"
default_user_is_admin = False
default_user_birth_date_string = "1990-01-01"
default_user_access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJteS1hcHAiLCJzdWIiOiI3NTdjZTdmMy1hZDhlLTQ2MmItODY2ZC1jYTRkY2U3OTEyMTkiLCJleHAiOjE3MTkxNjA3NTcsImlhdCI6MTcxOTA3NDM1N30.RGahkIaBQpsIRgQiF9zT0k-ptOMSP3wncJ2Qv3INbj8"

default_investor_id = 1
default_borrower_id = 1

import bcrypt

from app.core.config import get_settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(
        password.encode(),
        bcrypt.gensalt(get_settings().security.password_bcrypt_rounds),
    ).decode()


DUMMY_PASSWORD = get_password_hash("")

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def fixture_setup_new_test_database() -> None:
    worker_name = os.getenv("PYTEST_XDIST_WORKER", "gw0")
    test_db_name = f"test_db_{worker_name}"

    # create new test db using connection to current database
    conn = await database_session._ASYNC_ENGINE.connect()
    await conn.execution_options(isolation_level="AUTOCOMMIT")
    await conn.execute(sqlalchemy.text(f"DROP DATABASE IF EXISTS {test_db_name}"))
    await conn.execute(sqlalchemy.text(f"CREATE DATABASE {test_db_name}"))
    await conn.close()

    session_mpatch = pytest.MonkeyPatch()
    session_mpatch.setenv("DATABASE__DB", test_db_name)
    session_mpatch.setenv("SECURITY__PASSWORD_BCRYPT_ROUNDS", "4")

    # force settings to use now monkeypatched environments
    get_settings.cache_clear()

    # monkeypatch test database engine
    engine = database_session.new_async_engine(get_settings().sqlalchemy_database_uri)

    session_mpatch.setattr(
        database_session,
        "_ASYNC_ENGINE",
        engine,
    )
    session_mpatch.setattr(
        database_session,
        "_ASYNC_SESSIONMAKER",
        async_sessionmaker(engine, expire_on_commit=False),
    )

    # create app tables in test database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def fixture_clean_get_settings_between_tests() -> AsyncGenerator[None, None]:
    yield

    get_settings.cache_clear()


@pytest_asyncio.fixture(name="default_hashed_password", scope="session")
async def fixture_default_hashed_password() -> str:
    return get_password_hash(default_user_password)


@pytest_asyncio.fixture(name="session", scope="function")
async def fixture_session_with_rollback(
    monkeypatch: pytest.MonkeyPatch,
) -> AsyncGenerator[AsyncSession, None]:
    # we want to monkeypatch get_async_session with one bound to session
    # that we will always rollback on function scope

    connection = await database_session._ASYNC_ENGINE.connect()
    transaction = await connection.begin()

    session = AsyncSession(bind=connection, expire_on_commit=False)

    monkeypatch.setattr(
        database_session,
        "get_async_session",
        lambda: session,
    )

    yield session

    await session.close()
    await transaction.rollback()
    await connection.close()


@pytest_asyncio.fixture(name="client", scope="function")
async def fixture_client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=fastapi_app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as aclient:
        aclient.headers.update({"Host": "localhost"})
        yield aclient


@pytest_asyncio.fixture(name="default_user", scope="function")
async def fixture_default_user(
    session: AsyncSession, default_hashed_password: str
) -> dict:
    default_user = User(
        user_id=default_user_id,
        email=default_user_email,
        hashed_password=default_hashed_password,
        name=default_user_name,
        telephone=default_user_telephone,
        monthly_income=default_user_monthly_income,
        cpf=default_user_cpf,
        birth_date=default_user_birth_date,
        pix_key=default_user_pix_key,
    )
    session.add(default_user)
    await session.commit()
    await session.refresh(default_user)

    def user_to_dict(user: User) -> dict:
        return {
            "user_id": user.user_id,
            "email": user.email,
            "hashed_password": user.hashed_password,
            "name": user.name,
            "telephone": user.telephone,
            "monthly_income": user.monthly_income,
            "cpf": user.cpf,
            "birth_date": user.birth_date,
            "pix_key": user.pix_key,
        }

    return user_to_dict(default_user)


@pytest.fixture(name="default_user_headers", scope="function")
def fixture_default_user_headers(default_user: User) -> dict[str, str]:
    return {"Authorization": f"Bearer {default_user_access_token}"}

@pytest_asyncio.fixture(name="default_investor", scope="function")
async def fixture_default_investor(
    session: AsyncSession, default_user: User
) -> Investor:
    default_investor = Investor(
        investor_id=default_investor_id,
        user_id=default_user["user_id"]
    )
    session.add(default_investor)
    await session.commit()
    await session.refresh(default_investor)
    return default_investor


@pytest_asyncio.fixture(name="default_borrower", scope="function")
async def fixture_default_borrower(
    session: AsyncSession, default_user: User
) -> Borrower:
    default_borrower = Borrower(
        borrower_id=default_borrower_id,
        user_id=default_user["user_id"]
    )
    session.add(default_borrower)
    await session.commit()
    await session.refresh(default_borrower)
    return default_borrower


@pytest_asyncio.fixture(name="default_loan", scope="function")
async def default_loan(session: AsyncSession, default_borrower: Borrower) -> Loan:
    loan = Loan(
        borrower_id=default_borrower.borrower_id,
        amount=10000.0,
        interest_rate=5.0,
        duration=12,
        status="pending",
        goals="compras",
        bank_profit=500.0,
        investor_profit=300.0
    )
    session.add(loan)
    await session.commit()
    await session.refresh(loan)
    return loan

@pytest_asyncio.fixture(name="default_contract", scope="function")
async def default_contract(session: AsyncSession, default_loan: Loan, default_borrower: Borrower, default_investor: Investor) -> Contract:
    contract = Contract(
        loan_id=default_loan.loan_id,
        borrower_id=default_borrower.borrower_id,
        investor_id=default_investor.investor_id,
        status="active",
        date_signed=datetime.now(),
        investor_signature_digital_uuid="uuid",
        borrower_signature_digital_uuid="uuid"
    )
    session.add(contract)
    await session.commit()
    await session.refresh(contract)
    return contract