from calendar import monthrange
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    BenchmarkProfile,
    IncomeTransaction,
)

ZERO = Decimal("0.00")
MONEY = Decimal("0.01")


def money(value: Decimal | int | None) -> Decimal:
    return Decimal(value or 0).quantize(MONEY, rounding=ROUND_HALF_UP)


def monthly_benchmark_income(profile: BenchmarkProfile, month: date) -> Decimal:
    """Return the salary history rate active on a calendar date, or the profile default."""
    matching_periods = [
        period
        for period in profile.salary_history
        if period.effective_from <= month
        and (period.effective_to is None or period.effective_to >= month)
    ]
    if not matching_periods:
        return Decimal(profile.monthly_income)
    # The newest applicable period wins if historic data accidentally overlaps.
    return Decimal(max(matching_periods, key=lambda period: period.effective_from).monthly_income)


def benchmark_total(profile: BenchmarkProfile, as_of: date) -> Decimal:
    """Completed prior months plus calendar-day accrual for the current month.

    If the benchmark starts part-way through a month, its first month is prorated.
    This makes start dates and the current period consistent and avoids 30-day assumptions.
    """
    if as_of < profile.employment_start_date:
        return ZERO
    total = ZERO
    cursor = profile.employment_start_date.replace(day=1)
    while cursor <= as_of.replace(day=1):
        days = monthrange(cursor.year, cursor.month)[1]
        start_day = (
            profile.employment_start_date.day
            if cursor.year == profile.employment_start_date.year
            and cursor.month == profile.employment_start_date.month
            else 1
        )
        end_day = as_of.day if cursor.year == as_of.year and cursor.month == as_of.month else days
        if end_day >= start_day:
            total += (
                monthly_benchmark_income(profile, cursor)
                * Decimal(end_day - start_day + 1)
                / Decimal(days)
            )
        cursor = date(
            cursor.year + (cursor.month == 12), 1 if cursor.month == 12 else cursor.month + 1, 1
        )
    adjustments = sum(
        (
            Decimal(adjustment.amount)
            for adjustment in profile.adjustments
            if adjustment.adjustment_date <= as_of
        ),
        ZERO,
    )
    return money(total + adjustments)


def dashboard(
    db: Session, user_id: str, profile: BenchmarkProfile, as_of: date | None = None
) -> dict:
    today = as_of or date.today()
    total = money(
        db.scalar(
            select(func.coalesce(func.sum(IncomeTransaction.amount), 0)).where(
                IncomeTransaction.user_id == user_id
            )
        )
    )
    monthly = money(
        db.scalar(
            select(func.coalesce(func.sum(IncomeTransaction.amount), 0)).where(
                IncomeTransaction.user_id == user_id,
                IncomeTransaction.transaction_date >= today.replace(day=1),
                IncomeTransaction.transaction_date <= today,
            )
        )
    )
    yearly = money(
        db.scalar(
            select(func.coalesce(func.sum(IncomeTransaction.amount), 0)).where(
                IncomeTransaction.user_id == user_id,
                IncomeTransaction.transaction_date >= date(today.year, 1, 1),
                IncomeTransaction.transaction_date <= today,
            )
        )
    )
    first_date = db.scalar(
        select(func.min(IncomeTransaction.transaction_date)).where(
            IncomeTransaction.user_id == user_id
        )
    )
    previous_month_end = today.replace(day=1) - __import__("datetime").timedelta(days=1)
    current_gap = max(ZERO, benchmark_total(profile, today) - total)
    prior_total = money(
        db.scalar(
            select(func.coalesce(func.sum(IncomeTransaction.amount), 0)).where(
                IncomeTransaction.user_id == user_id,
                IncomeTransaction.transaction_date <= previous_month_end,
            )
        )
    )
    prior_gap = max(ZERO, benchmark_total(profile, previous_month_end) - prior_total)
    elapsed_months = max(
        1,
        (today.year - profile.employment_start_date.year) * 12
        + today.month
        - profile.employment_start_date.month
        + 1,
    )
    benchmark = benchmark_total(profile, today)
    return {
        "my_total_income": total,
        "benchmark_total": benchmark,
        "gap": current_gap,
        "surplus": max(ZERO, total - benchmark),
        "progress_percentage": money((total / benchmark * 100) if benchmark else ZERO),
        "monthly_income": monthly,
        "yearly_income": yearly,
        "average_monthly_income": money(total / elapsed_months),
        "gap_change": money(prior_gap - current_gap),
        "benchmark_start_date": profile.employment_start_date,
        "tracking_start_date": first_date,
    }


def monthly_analytics(db: Session, user_id: str, start: date, end: date) -> list[dict]:
    """Return list of {period: 'YYYY-MM', total, count} between start and end inclusive."""
    rows = db.execute(
        select(
            func.extract("year", IncomeTransaction.transaction_date).label("y"),
            func.extract("month", IncomeTransaction.transaction_date).label("m"),
            func.coalesce(func.sum(IncomeTransaction.amount), 0).label("total"),
            func.count(IncomeTransaction.id).label("count"),
        )
        .where(
            IncomeTransaction.user_id == user_id,
            IncomeTransaction.transaction_date >= start,
            IncomeTransaction.transaction_date <= end,
        )
        .group_by("y", "m")
        .order_by("y", "m")
    )
    result = []
    for r in rows:
        year = int(r.y)
        month = int(r.m)
        result.append({"period": f"{year:04d}-{month:02d}", "total": money(r.total), "count": int(r.count)})
    return result


def yearly_analytics(db: Session, user_id: str, start: date, end: date) -> list[dict]:
    """Return list of {period: 'YYYY', total, count} between start and end inclusive."""
    rows = db.execute(
        select(
            func.extract("year", IncomeTransaction.transaction_date).label("y"),
            func.coalesce(func.sum(IncomeTransaction.amount), 0).label("total"),
            func.count(IncomeTransaction.id).label("count"),
        )
        .where(
            IncomeTransaction.user_id == user_id,
            IncomeTransaction.transaction_date >= start,
            IncomeTransaction.transaction_date <= end,
        )
        .group_by("y")
        .order_by("y")
    )
    result = []
    for r in rows:
        year = int(r.y)
        result.append({"period": f"{year:04d}", "total": money(r.total), "count": int(r.count)})
    return result
