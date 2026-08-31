from contextlib import asynccontextmanager
from datetime import date

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select

from app.database import Base, engine
from app.dependencies import CurrentUser, Db
from app.models import (
    BenchmarkAdjustment,
    BenchmarkProfile,
    BenchmarkSalaryHistory,
    IncomeTransaction,
    User,
)
from app.schemas import (
    AdjustmentCreate,
    AdjustmentOut,
    AdjustmentUpdate,
    BenchmarkOut,
    BenchmarkUpdate,
    DashboardOut,
    IncomeCreate,
    IncomeOut,
    IncomePage,
    IncomeUpdate,
    LoginRequest,
    SalaryHistoryCreate,
    SalaryHistoryOut,
    SalaryHistoryUpdate,
    AnalyticsOut,
    Token,
    UserCreate,
    UserOut,
)
from app.security import create_access_token, hash_password, verify_password
from app.services import dashboard
from app.services import monthly_analytics, yearly_analytics


@asynccontextmanager
async def lifespan(_: FastAPI):
    # PostgreSQL schema changes are always applied through Alembic migrations.
    # SQLite remains convenient for a local first run and API test harnesses.
    if str(engine.url).startswith("sqlite"):
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Income Gap Tracker API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Db):
    if db.scalar(select(User).where(User.email == payload.email.lower())):
        raise HTTPException(status_code=409, detail="An account with this email already exists")
    user = User(email=payload.email.lower(), password_hash=hash_password(payload.password))
    db.add(user)
    db.flush()
    db.add(
        BenchmarkProfile(
            user_id=user.id,
            name="Career Benchmark",
            employment_start_date=date(2022, 1, 1),
            monthly_income=50000,
            currency="KES",
        )
    )
    db.commit()
    return Token(access_token=create_access_token(user.id))


@app.post("/auth/login", response_model=Token)
def login(payload: LoginRequest, db: Db):
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.id))


@app.get("/users/me", response_model=UserOut)
def me(user: CurrentUser):
    return user


@app.get("/income", response_model=IncomePage)
def list_income(
    user: CurrentUser,
    db: Db,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    search: str | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    oldest: bool = False,
):
    query = select(IncomeTransaction).where(IncomeTransaction.user_id == user.id)
    if search:
        query = query.where(IncomeTransaction.description.ilike(f"%{search}%"))
    if category:
        query = query.where(IncomeTransaction.category == category)
    if start_date:
        query = query.where(IncomeTransaction.transaction_date >= start_date)
    if end_date:
        query = query.where(IncomeTransaction.transaction_date <= end_date)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    order = (
        IncomeTransaction.transaction_date.asc()
        if oldest
        else IncomeTransaction.transaction_date.desc()
    )
    items = db.scalars(query.order_by(order).offset((page - 1) * page_size).limit(page_size)).all()
    return IncomePage(items=items, total=total, page=page, page_size=page_size)


@app.post("/income", response_model=IncomeOut, status_code=status.HTTP_201_CREATED)
def create_income(payload: IncomeCreate, user: CurrentUser, db: Db):
    item = IncomeTransaction(user_id=user.id, **payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def owned_income(income_id: str, user: User, db: Db) -> IncomeTransaction:
    item = db.scalar(
        select(IncomeTransaction).where(
            IncomeTransaction.id == income_id, IncomeTransaction.user_id == user.id
        )
    )
    if not item:
        raise HTTPException(status_code=404, detail="Income transaction not found")
    return item


@app.get("/income/{income_id}", response_model=IncomeOut)
def get_income(income_id: str, user: CurrentUser, db: Db):
    return owned_income(income_id, user, db)


@app.patch("/income/{income_id}", response_model=IncomeOut)
def update_income(income_id: str, payload: IncomeUpdate, user: CurrentUser, db: Db):
    item = owned_income(income_id, user, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/income/{income_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_income(income_id: str, user: CurrentUser, db: Db):
    db.delete(owned_income(income_id, user, db))
    db.commit()


@app.get("/benchmark", response_model=BenchmarkOut)
def get_benchmark(user: CurrentUser, db: Db):
    return db.scalar(select(BenchmarkProfile).where(BenchmarkProfile.user_id == user.id))


@app.patch("/benchmark", response_model=BenchmarkOut)
def update_benchmark(payload: BenchmarkUpdate, user: CurrentUser, db: Db):
    profile = db.scalar(select(BenchmarkProfile).where(BenchmarkProfile.user_id == user.id))
    for field, value in payload.model_dump().items():
        setattr(profile, field, value)
    db.commit()
    db.refresh(profile)
    return profile


def user_benchmark(user: User, db: Db) -> BenchmarkProfile:
    return db.scalar(select(BenchmarkProfile).where(BenchmarkProfile.user_id == user.id))


@app.get("/benchmark/salary-history", response_model=list[SalaryHistoryOut])
def list_salary_history(user: CurrentUser, db: Db):
    profile = user_benchmark(user, db)
    return db.scalars(
        select(BenchmarkSalaryHistory)
        .where(BenchmarkSalaryHistory.benchmark_profile_id == profile.id)
        .order_by(BenchmarkSalaryHistory.effective_from)
    ).all()


@app.post(
    "/benchmark/salary-history",
    response_model=SalaryHistoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_salary_history(payload: SalaryHistoryCreate, user: CurrentUser, db: Db):
    if payload.effective_to and payload.effective_to < payload.effective_from:
        raise HTTPException(status_code=422, detail="End date cannot be before start date")
    profile = user_benchmark(user, db)
    # Prevent overlapping salary-history periods for this benchmark profile
    def _overlaps(a_from, a_to, b_from, b_to):
        a_to_eff = a_to or date.max
        b_to_eff = b_to or date.max
        return a_from <= b_to_eff and b_from <= a_to_eff

    existing = db.scalars(
        select(BenchmarkSalaryHistory).where(BenchmarkSalaryHistory.benchmark_profile_id == profile.id)
    ).all()
    for p in existing:
        if _overlaps(payload.effective_from, payload.effective_to, p.effective_from, p.effective_to):
            raise HTTPException(status_code=422, detail="Salary history periods cannot overlap")

    period = BenchmarkSalaryHistory(benchmark_profile_id=profile.id, **payload.model_dump())
    db.add(period)
    db.commit()
    db.refresh(period)
    return period


def owned_salary_history(
    period_id: str, profile: BenchmarkProfile, db: Db
) -> BenchmarkSalaryHistory:
    period = db.scalar(
        select(BenchmarkSalaryHistory).where(
            BenchmarkSalaryHistory.id == period_id,
            BenchmarkSalaryHistory.benchmark_profile_id == profile.id,
        )
    )
    if not period:
        raise HTTPException(status_code=404, detail="Salary history entry not found")
    return period


@app.patch("/benchmark/salary-history/{period_id}", response_model=SalaryHistoryOut)
def update_salary_history(period_id: str, payload: SalaryHistoryUpdate, user: CurrentUser, db: Db):
    period = owned_salary_history(period_id, user_benchmark(user, db), db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(period, field, value)
    if period.effective_to and period.effective_to < period.effective_from:
        raise HTTPException(status_code=422, detail="End date cannot be before start date")
    # Validate no overlap with other salary history entries
    def _overlaps(a_from, a_to, b_from, b_to):
        a_to_eff = a_to or date.max
        b_to_eff = b_to or date.max
        return a_from <= b_to_eff and b_from <= a_to_eff

    other = db.scalars(
        select(BenchmarkSalaryHistory).where(
            BenchmarkSalaryHistory.benchmark_profile_id == period.benchmark_profile_id,
            BenchmarkSalaryHistory.id != period.id,
        )
    ).all()
    for p in other:
        if _overlaps(period.effective_from, period.effective_to, p.effective_from, p.effective_to):
            raise HTTPException(status_code=422, detail="Salary history periods cannot overlap")
    db.commit()
    db.refresh(period)
    return period


@app.delete("/benchmark/salary-history/{period_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_salary_history(period_id: str, user: CurrentUser, db: Db):
    db.delete(owned_salary_history(period_id, user_benchmark(user, db), db))
    db.commit()


@app.get("/benchmark/adjustments", response_model=list[AdjustmentOut])
def list_adjustments(user: CurrentUser, db: Db):
    profile = user_benchmark(user, db)
    return db.scalars(
        select(BenchmarkAdjustment)
        .where(BenchmarkAdjustment.benchmark_profile_id == profile.id)
        .order_by(BenchmarkAdjustment.adjustment_date.desc())
    ).all()


@app.post(
    "/benchmark/adjustments",
    response_model=AdjustmentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_adjustment(payload: AdjustmentCreate, user: CurrentUser, db: Db):
    profile = user_benchmark(user, db)
    adjustment = BenchmarkAdjustment(benchmark_profile_id=profile.id, **payload.model_dump())
    db.add(adjustment)
    db.commit()
    db.refresh(adjustment)
    return adjustment


def owned_adjustment(adjustment_id: str, profile: BenchmarkProfile, db: Db) -> BenchmarkAdjustment:
    adjustment = db.scalar(
        select(BenchmarkAdjustment).where(
            BenchmarkAdjustment.id == adjustment_id,
            BenchmarkAdjustment.benchmark_profile_id == profile.id,
        )
    )
    if not adjustment:
        raise HTTPException(status_code=404, detail="Benchmark adjustment not found")
    return adjustment


@app.patch("/benchmark/adjustments/{adjustment_id}", response_model=AdjustmentOut)
def update_adjustment(adjustment_id: str, payload: "AdjustmentUpdate", user: CurrentUser, db: Db):
    profile = user_benchmark(user, db)
    adj = owned_adjustment(adjustment_id, profile, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(adj, field, value)
    db.commit()
    db.refresh(adj)
    return adj


@app.delete("/benchmark/adjustments/{adjustment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_adjustment(adjustment_id: str, user: CurrentUser, db: Db):
    profile = user_benchmark(user, db)
    db.delete(owned_adjustment(adjustment_id, profile, db))
    db.commit()


@app.get("/dashboard", response_model=DashboardOut)
def get_dashboard(user: CurrentUser, db: Db):
    profile = db.scalar(select(BenchmarkProfile).where(BenchmarkProfile.user_id == user.id))
    return dashboard(db, user.id, profile)


@app.get("/analytics/monthly", response_model=AnalyticsOut)
def analytics_monthly(
    user: CurrentUser,
    db: Db,
    start: date | None = None,
    end: date | None = None,
):
    today = date.today()
    if not end:
        end = today
    if not start:
        # default to 12 months back (same month last year)
        start = date(end.year - 1, end.month, 1)
    items = monthly_analytics(db, user.id, start, end)
    return AnalyticsOut(items=items)


@app.get("/analytics/yearly", response_model=AnalyticsOut)
def analytics_yearly(user: CurrentUser, db: Db, start: date | None = None, end: date | None = None):
    today = date.today()
    if not end:
        end = today
    if not start:
        start = date(end.year - 5, 1, 1)
    items = yearly_analytics(db, user.id, start, end)
    return AnalyticsOut(items=items)
