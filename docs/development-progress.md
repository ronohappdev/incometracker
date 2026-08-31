# Development progress

## Feature: foundation, authenticated income CRUD, benchmark dashboard

**Requirements:** project setup; users, income, benchmark; authentication; income CRUD; benchmark engine; dashboard API; initial mobile dashboard and add-income flow.

**Files created/modified:** backend API, initial Alembic migration, Expo mobile shell, Docker Compose, environment template, and documentation.

**Database changes:** initial `users`, `benchmark_profiles`, and `income_transactions` tables with UUID IDs, foreign keys, indexes, and a positive income check.

**API/UI changes:** JWT registration/login; protected user, income, benchmark, and dashboard endpoints. Mobile dashboard renders authoritative API data; history and add-income form invalidate cached queries after saving.

**Tests added:** service tests for benchmark periods/current-month accrual and API tests for CRUD, validation, and ownership isolation.

**Test results:** Python source compilation and whitespace validation passed. The test/lint dependencies could not complete installation in the supplied execution environment (the package download process is interrupted before install), so pytest and Ruff remain to be run locally using the documented command.

**Design decisions:** use Decimal/NUMERIC; only the active benchmark month is prorated by calendar days; `gap` is never negative and `surplus` is separate.

**Remaining limitations:** salary history/adjustments, analytics charts, catch-up projections, milestones, CSV export, onboarding, offline queue, and complete mobile authentication are planned follow-on features. The current app must authenticate externally before accessing protected mobile views.

## Feature: benchmark history, adjustments, and mobile access

**Requirements:** support benchmark salary changes and dated adjustments; provide dashboard calculation coverage; require mobile sign-in before protected data loads.

**Files created/modified:** benchmark models/schemas/services/routes, Alembic revision `0002_benchmark_history`, backend tests, mobile authentication and onboarding routes, API/calculation documentation.

**Database changes:** adds `benchmark_salary_history` (effective dates and monthly income) and `benchmark_adjustments` (dated signed amounts). Both are profile-owned, indexed, and constrained by the migration.

**API/UI changes:** salary-history and adjustment list/create routes plus salary-history update/delete. Mobile now stores JWTs only in SecureStore, redirects unauthenticated users to sign in, lets new users configure the benchmark, and provides sign-out.

**Tests added:** benchmark total with salary history and bonus adjustment; dashboard API response with total income, zero gap, surplus, and progress above 100%.

**Test results:** the user-confirmed suite passes (9 tests), Ruff passes, and a clean local SQLite database was migrated through revision `0002_benchmark_history`.

**Design decisions:** salary history is date-based and falls back to the profile rate when no period matches. Adjustments can be positive or negative, enabling bonuses and unpaid/employment-gap corrections.

**Remaining limitations:** overlap prevention for salary-history entries, edit/delete APIs for adjustments, analytics charts, catch-up projections, milestones, export, and offline queueing.
