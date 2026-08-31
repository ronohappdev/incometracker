from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

# An in-memory SQLite database normally exists only for one connection. StaticPool
# makes every test session share the same connection created by setup_function.
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False)


def db_override():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = db_override
client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def auth(email="person@example.com"):
    response = client.post("/auth/register", json={"email": email, "password": "a-secure-password"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_income_crud_and_dashboard_updates():
    headers = auth()
    made = client.post(
        "/income",
        headers=headers,
        json={
            "amount": "15000.00",
            "transaction_date": "2026-08-10",
            "source": "Freelancing",
            "category": "Freelancing",
        },
    )
    assert made.status_code == 201
    income_id = made.json()["id"]
    assert (
        client.patch(f"/income/{income_id}", headers=headers, json={"amount": "20000.00"}).json()[
            "amount"
        ]
        == "20000.00"
    )
    assert client.get("/income", headers=headers).json()["total"] == 1
    assert client.delete(f"/income/{income_id}", headers=headers).status_code == 204
    assert client.get("/income", headers=headers).json()["total"] == 0


def test_user_cannot_access_another_users_income():
    a, b = auth("a@example.com"), auth("b@example.com")
    income_id = client.post(
        "/income",
        headers=a,
        json={
            "amount": "10",
            "transaction_date": "2026-01-01",
            "source": "Other",
            "category": "Other",
        },
    ).json()["id"]
    assert client.get(f"/income/{income_id}", headers=b).status_code == 404


def test_invalid_income_and_unauthenticated_are_rejected():
    assert client.get("/income").status_code == 401
    assert (
        client.post(
            "/income",
            headers=auth(),
            json={
                "amount": "0",
                "transaction_date": "2026-01-01",
                "source": "Other",
                "category": "Other",
            },
        ).status_code
        == 422
    )


def test_dashboard_returns_authoritative_gap_and_surplus():
    headers = auth()
    today = date.today()
    client.patch(
        "/benchmark",
        headers=headers,
        json={
            "name": "Career Benchmark",
            "employment_start_date": today.replace(day=1).isoformat(),
            "monthly_income": "100.00",
            "currency": "KES",
        },
    )
    client.post(
        "/income",
        headers=headers,
        json={
            "amount": "1000.00",
            "transaction_date": today.isoformat(),
            "source": "Contract",
            "category": "Contract",
        },
    )
    response = client.get("/dashboard", headers=headers)
    assert response.status_code == 200
    dashboard = response.json()
    assert dashboard["my_total_income"] == "1000.00"
    assert dashboard["gap"] == "0.00"
    assert float(dashboard["surplus"]) > 0
    assert float(dashboard["progress_percentage"]) > 100


def test_adjustment_crud():
    headers = auth("adjust@example.com")
    # create adjustment
    made = client.post(
        "/benchmark/adjustments",
        headers=headers,
        json={
            "adjustment_date": "2026-08-01",
            "amount": "100.00",
            "adjustment_type": "bonus",
            "description": "Initial bonus",
        },
    )
    assert made.status_code == 201
    aid = made.json()["id"]

    # update adjustment
    updated = client.patch(
        f"/benchmark/adjustments/{aid}", headers=headers, json={"amount": "150.00"}
    )
    assert updated.status_code == 200
    assert updated.json()["amount"] == "150.00"

    # delete adjustment
    assert client.delete(f"/benchmark/adjustments/{aid}", headers=headers).status_code == 204

    # deleting again returns 404
    assert client.delete(f"/benchmark/adjustments/{aid}", headers=headers).status_code == 404


def test_salary_history_no_overlap():
    headers = auth("salary@example.com")
    # create initial period
    made = client.post(
        "/benchmark/salary-history",
        headers=headers,
        json={"effective_from": "2026-01-01", "effective_to": "2026-06-30", "monthly_income": "1000.00"},
    )
    assert made.status_code == 201

    # overlapping start
    overlap = client.post(
        "/benchmark/salary-history",
        headers=headers,
        json={"effective_from": "2026-06-01", "effective_to": "2026-12-31", "monthly_income": "1100.00"},
    )
    assert overlap.status_code == 422

    # non-overlapping after
    ok = client.post(
        "/benchmark/salary-history",
        headers=headers,
        json={"effective_from": "2026-07-01", "effective_to": "2026-12-31", "monthly_income": "1100.00"},
    )
    assert ok.status_code == 201

    # update existing to overlap should fail
    pid = ok.json()["id"]
    conflict = client.patch(
        f"/benchmark/salary-history/{pid}",
        headers=headers,
        json={"effective_from": "2026-05-01"},
    )
    assert conflict.status_code == 422


def test_analytics_endpoints():
    headers = auth("analytics@example.com")
    # create incomes across months and years
    client.post(
        "/income",
        headers=headers,
        json={"amount": "100.00", "transaction_date": "2025-12-15", "source": "A", "category": "X"},
    )
    client.post(
        "/income",
        headers=headers,
        json={"amount": "200.00", "transaction_date": "2026-01-10", "source": "B", "category": "Y"},
    )
    client.post(
        "/income",
        headers=headers,
        json={"amount": "300.00", "transaction_date": "2026-01-20", "source": "C", "category": "Y"},
    )

    resp_monthly = client.get(
        "/analytics/monthly", headers=headers, params={"start": "2025-12-01", "end": "2026-01-31"}
    )
    assert resp_monthly.status_code == 200
    items = resp_monthly.json()["items"]
    assert any(i["period"] == "2025-12" and float(i["total"]) == 100.0 for i in items)
    assert any(i["period"] == "2026-01" and float(i["total"]) == 500.0 for i in items)

    resp_yearly = client.get(
        "/analytics/yearly", headers=headers, params={"start": "2025-01-01", "end": "2026-12-31"}
    )
    assert resp_yearly.status_code == 200
    yitems = resp_yearly.json()["items"]
    assert any(i["period"] == "2025" for i in yitems)
    assert any(i["period"] == "2026" for i in yitems)
