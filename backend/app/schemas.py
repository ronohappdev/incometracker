from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(UserCreate):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: EmailStr


class IncomeBase(BaseModel):
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    transaction_date: date
    source: str = Field(min_length=1, max_length=80)
    category: str = Field(min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=1000)
    project_client: str | None = Field(default=None, max_length=160)
    recurring: bool = False
    currency: str = Field(default="KES", min_length=3, max_length=3)


class IncomeCreate(IncomeBase):
    pass


class IncomeUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    transaction_date: date | None = None
    source: str | None = Field(default=None, min_length=1, max_length=80)
    category: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=1000)
    project_client: str | None = Field(default=None, max_length=160)
    recurring: bool | None = None


class IncomeOut(IncomeBase):
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime


class IncomePage(BaseModel):
    items: list[IncomeOut]
    total: int
    page: int
    page_size: int


class BenchmarkBase(BaseModel):
    name: str = Field(default="Career Benchmark", min_length=1, max_length=100)
    employment_start_date: date
    monthly_income: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    currency: str = Field(default="KES", min_length=3, max_length=3)


class BenchmarkUpdate(BenchmarkBase):
    pass


class BenchmarkOut(BenchmarkBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class SalaryHistoryBase(BaseModel):
    effective_from: date
    effective_to: date | None = None
    monthly_income: Decimal = Field(gt=0, max_digits=14, decimal_places=2)


class SalaryHistoryCreate(SalaryHistoryBase):
    pass


class SalaryHistoryUpdate(BaseModel):
    effective_from: date | None = None
    effective_to: date | None = None
    monthly_income: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)


class SalaryHistoryOut(SalaryHistoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class AdjustmentBase(BaseModel):
    adjustment_date: date
    amount: Decimal = Field(max_digits=14, decimal_places=2)
    adjustment_type: str = Field(min_length=1, max_length=40)
    description: str | None = Field(default=None, max_length=1000)

    @field_validator("amount")
    @classmethod
    def amount_must_not_be_zero(cls, value: Decimal) -> Decimal:
        if value == 0:
            raise ValueError("Amount must not be zero")
        return value


class AdjustmentCreate(AdjustmentBase):
    pass


class AdjustmentOut(AdjustmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: str


class AdjustmentUpdate(BaseModel):
    adjustment_date: date | None = None
    amount: Decimal | None = Field(default=None, max_digits=14, decimal_places=2)
    adjustment_type: str | None = Field(default=None, min_length=1, max_length=40)
    description: str | None = Field(default=None, max_length=1000)


class DashboardOut(BaseModel):
    my_total_income: Decimal
    benchmark_total: Decimal
    gap: Decimal
    surplus: Decimal
    progress_percentage: Decimal
    monthly_income: Decimal
    yearly_income: Decimal
    average_monthly_income: Decimal
    gap_change: Decimal
    benchmark_start_date: date
    tracking_start_date: date | None


class AnalyticsPoint(BaseModel):
    period: str
    total: Decimal
    count: int


class AnalyticsOut(BaseModel):
    items: list[AnalyticsPoint]
