# Database

UUID strings are primary keys. `income_transactions.amount` and `benchmark_profiles.monthly_income` are `NUMERIC(14,2)`. Income has a positive-value database check in the initial Alembic migration. Indexes cover email, profile user ID, income user ID, and transaction date.

Run `cd backend && alembic upgrade head` after creating the database. Migration `0001_initial` creates the initial schema.
