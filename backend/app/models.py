import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def uuid_pk():
    return mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


class Timestamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class User(Timestamped, Base):
    __tablename__ = "users"
    id: Mapped[str] = uuid_pk()
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    incomes: Mapped[list["IncomeTransaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    benchmark: Mapped["BenchmarkProfile | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", uselist=False
    )


class IncomeTransaction(Timestamped, Base):
    __tablename__ = "income_transactions"
    id: Mapped[str] = uuid_pk()
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    transaction_date: Mapped[date] = mapped_column(Date, index=True)
    source: Mapped[str] = mapped_column(String(80))
    category: Mapped[str] = mapped_column(String(80), default="Other")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    project_client: Mapped[str | None] = mapped_column(String(160), nullable=True)
    recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    currency: Mapped[str] = mapped_column(String(3), default="KES")
    user: Mapped[User] = relationship(back_populates="incomes")


class BenchmarkProfile(Timestamped, Base):
    __tablename__ = "benchmark_profiles"
    id: Mapped[str] = uuid_pk()
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100), default="Career Benchmark")
    employment_start_date: Mapped[date] = mapped_column(Date)
    monthly_income: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="KES")
    user: Mapped[User] = relationship(back_populates="benchmark")
    salary_history: Mapped[list["BenchmarkSalaryHistory"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )
    adjustments: Mapped[list["BenchmarkAdjustment"]] = relationship(
        back_populates="profile", cascade="all, delete-orphan"
    )


class BenchmarkSalaryHistory(Timestamped, Base):
    __tablename__ = "benchmark_salary_history"
    id: Mapped[str] = uuid_pk()
    benchmark_profile_id: Mapped[str] = mapped_column(
        ForeignKey("benchmark_profiles.id"), index=True
    )
    effective_from: Mapped[date] = mapped_column(Date)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    monthly_income: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    profile: Mapped[BenchmarkProfile] = relationship(back_populates="salary_history")


class BenchmarkAdjustment(Timestamped, Base):
    __tablename__ = "benchmark_adjustments"
    id: Mapped[str] = uuid_pk()
    benchmark_profile_id: Mapped[str] = mapped_column(
        ForeignKey("benchmark_profiles.id"), index=True
    )
    adjustment_date: Mapped[date] = mapped_column(Date, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    adjustment_type: Mapped[str] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    profile: Mapped[BenchmarkProfile] = relationship(back_populates="adjustments")
