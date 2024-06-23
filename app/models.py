# SQL Alchemy models declaration.
# https://docs.sqlalchemy.org/en/20/orm/quickstart.html#declare-models
# mapped_column syntax from SQLAlchemy 2.0.

# https://alembic.sqlalchemy.org/en/latest/tutorial.html
# Note, it is used by alembic migrations logic, see `alembic/env.py`

# Alembic shortcuts:
# # create migration
# alembic revision --autogenerate -m "migration_name"

# # apply all migrations
# alembic upgrade head


import uuid
from datetime import datetime, date

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, Uuid, func, Float, Enum, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    create_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    update_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Base):
    __tablename__ = "user_account"

    user_id: Mapped[str] = mapped_column(Uuid(as_uuid=False), primary_key=True, default=lambda _: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(256), nullable=False, unique=True, index=True)
    telephone: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    monthly_income: Mapped[float] = mapped_column(Float, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), nullable=False)
    pix_key: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(back_populates="user")
    investor: Mapped["Investor"] = relationship("Investor", back_populates="user", uselist=False)
    borrower: Mapped["Borrower"] = relationship("Borrower", back_populates="user", uselist=False)
    loan_simulations: Mapped[list["LoanSimulation"]] = relationship("LoanSimulation", back_populates="user")
    consortium_simulations: Mapped[list["ConsortiumSimulation"]] = relationship("ConsortiumSimulation", back_populates="user")
    financing_simulations: Mapped[list["FinancingSimulation"]] = relationship("FinancingSimulation", back_populates="user")
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)

class RefreshToken(Base):
    __tablename__ = "refresh_token"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    refresh_token: Mapped[str] = mapped_column(String(512), nullable=False, unique=True, index=True)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exp: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.user_id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="refresh_tokens")

class Investor(Base):
    __tablename__ = "investor"

    investor_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.user_id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User", back_populates="investor")
    investments: Mapped[list["Investment"]] = relationship("Investment", back_populates="investor")
    contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="investor")

class Borrower(Base):
    __tablename__ = "borrower"

    borrower_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.user_id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship("User", back_populates="borrower")
    loan_applications: Mapped[list["Loan"]] = relationship("Loan", back_populates="borrower")
    risk_profile: Mapped["RiskProfile"] = relationship("RiskProfile", back_populates="borrower")
    contracts: Mapped[list["Contract"]] = relationship("Contract", back_populates="borrower")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="borrower")

class Loan(Base):
    __tablename__ = "loan"

    loan_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    borrower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('borrower.borrower_id'), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False)
    duration: Mapped[int] = mapped_column(BigInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    goals: Mapped[str] = mapped_column(Enum('viagem', 'compras', 'negocios', name='loan_objective'), nullable=False)
    bank_profit: Mapped[float] = mapped_column(Float, nullable=True)
    investor_profit: Mapped[float] = mapped_column(Float, nullable=True)
    investments: Mapped[list["Investment"]] = relationship("Investment", back_populates="loan")
    contract: Mapped["Contract"] = relationship("Contract", back_populates="loan")
    payments: Mapped[list["Payment"]] = relationship("Payment", back_populates="loan")
    borrower: Mapped["Borrower"] = relationship("Borrower", back_populates="loan_applications")

class RiskProfile(Base):
    __tablename__ = "risk_profile"

    profile_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    borrower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('borrower.borrower_id'), nullable=False)
    risk_score: Mapped[int] = mapped_column(BigInteger, nullable=False)
    borrower: Mapped[Borrower] = relationship("Borrower", back_populates="risk_profile")

class Investment(Base):
    __tablename__ = "investment"

    investment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('loan.loan_id'), nullable=False)
    investor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('investor.investor_id'), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    loan: Mapped[Loan] = relationship("Loan", back_populates="investments")
    investor: Mapped[Investor] = relationship("Investor", back_populates="investments")

class Contract(Base):
    __tablename__ = "contract"

    contract_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('loan.loan_id'), nullable=False)
    investor_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('investor.investor_id'), nullable=False)
    borrower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('borrower.borrower_id'), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    date_signed: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    investor_signature_digital_uuid: Mapped[str] = mapped_column(String(36), nullable=True, default=str(uuid.uuid4()))
    borrower_signature_digital_uuid: Mapped[str] = mapped_column(String(36), nullable=True, default=str(uuid.uuid4()))
    loan: Mapped["Loan"] = relationship("Loan", back_populates="contract")
    investor: Mapped["Investor"] = relationship("Investor", back_populates="contracts")
    borrower: Mapped["Borrower"] = relationship("Borrower", back_populates="contracts")

class Payment(Base):
    __tablename__ = "payment"

    payment_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    loan_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('loan.loan_id'), nullable=False)
    borrower_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('borrower.borrower_id'), nullable=False)
    installment_number: Mapped[int] = mapped_column(BigInteger, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    bank_profit: Mapped[float] = mapped_column(Float, nullable=True)
    investor_profit: Mapped[float] = mapped_column(Float, nullable=True)
    loan: Mapped[Loan] = relationship("Loan", back_populates="payments")
    borrower: Mapped[Borrower] = relationship("Borrower", back_populates="payments")
    status_payment_investor: Mapped[str] = mapped_column(String(50), nullable=True, default="pending")

class Bank(Base):
    __tablename__ = "bank"

    bank_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(14), nullable=False)
    telephone: Mapped[str] = mapped_column(String(20), nullable=False)
    juros_emprestimo: Mapped[float] = mapped_column(Float, nullable=False)
    juros_consortium: Mapped[float] = mapped_column(Float, nullable=False)
    juros_financiamento: Mapped[float] = mapped_column(Float, nullable=False)

class LoanSimulation(Base):
    __tablename__ = "loan_simulation"

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.user_id", ondelete="CASCADE"))
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False)
    duration_months: Mapped[int] = mapped_column(BigInteger, nullable=False)
    monthly_payment: Mapped[float] = mapped_column(Float, nullable=False)
    bank_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('bank.bank_id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    user: Mapped[User] = relationship("User", back_populates="loan_simulations")
    bank: Mapped[Bank] = relationship("Bank")

class ConsortiumSimulation(Base):
    __tablename__ = "consortium_simulation"

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.user_id", ondelete="CASCADE"))
    total_value: Mapped[float] = mapped_column(Float, nullable=False)
    monthly_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    duration_months: Mapped[int] = mapped_column(BigInteger, nullable=False)
    bank_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('bank.bank_id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    user: Mapped[User] = relationship("User", back_populates="consortium_simulations")
    bank: Mapped[Bank] = relationship("Bank")

class FinancingSimulation(Base):
    __tablename__ = "financing_simulation"

    simulation_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("user_account.user_id", ondelete="CASCADE"))
    total_value: Mapped[float] = mapped_column(Float, nullable=False)
    down_payment: Mapped[float] = mapped_column(Float, nullable=False)
    interest_rate: Mapped[float] = mapped_column(Float, nullable=False)
    duration_months: Mapped[int] = mapped_column(BigInteger, nullable=False)
    monthly_payment: Mapped[float] = mapped_column(Float, nullable=False)
    bank_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('bank.bank_id'), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    user: Mapped[User] = relationship("User", back_populates="financing_simulations")
    bank: Mapped[Bank] = relationship("Bank")