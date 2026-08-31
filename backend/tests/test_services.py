from datetime import date
from decimal import Decimal

from app.models import BenchmarkAdjustment, BenchmarkProfile, BenchmarkSalaryHistory
from app.services import benchmark_total


def profile(start=date(2022, 1, 1), income=Decimal("50000")):
    return BenchmarkProfile(
        employment_start_date=start,
        monthly_income=income,
        name="Benchmark",
        currency="KES",
        user_id="u",
    )


def test_january_benchmark_is_one_month():
    assert benchmark_total(profile(), date(2022, 1, 31)) == Decimal("50000.00")


def test_february_benchmark_is_two_months():
    assert benchmark_total(profile(), date(2022, 2, 28)) == Decimal("100000.00")


def test_full_year_benchmark_is_600k():
    assert benchmark_total(profile(), date(2022, 12, 31)) == Decimal("600000.00")


def test_current_month_uses_calendar_day_accrual():
    assert benchmark_total(profile(), date(2022, 2, 14)) == Decimal("75000.00")


def test_salary_history_and_adjustment_change_benchmark_total():
    benchmark = profile()
    benchmark.salary_history = [
        BenchmarkSalaryHistory(
            effective_from=date(2022, 2, 1),
            monthly_income=Decimal("65000"),
        )
    ]
    benchmark.adjustments = [
        BenchmarkAdjustment(
            adjustment_date=date(2022, 2, 15),
            amount=Decimal("10000"),
            adjustment_type="Bonus",
        )
    ]
    assert benchmark_total(benchmark, date(2022, 2, 28)) == Decimal("125000.00")
