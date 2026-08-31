# BUILD SPECIFICATION — PERSONAL INCOME GAP TRACKER

## Project Name

**Income Gap Tracker**

Build a production-quality mobile application that helps me track my personal cumulative income from the present onward against a predefined income benchmark representing what a friend has earned since they became employed.

The purpose of this application is motivation, accountability, financial progress tracking, and visualization.

The application must NOT treat the comparison as a judgment of personal worth. It should present the friend's income as a configurable financial benchmark and focus the user interface primarily on:

1. How much I have earned.
2. How much the benchmark has accumulated.
3. The current gap.
4. How much I need to earn to close the gap.
5. My progress toward closing the gap.
6. How my recent income is changing the gap.
7. What income rate would allow me to eventually catch up.

---

# 1. TECHNOLOGY STACK

Use the following architecture unless there is a compelling technical reason to change something.

## Mobile

- React Native
- Expo
- TypeScript
- Expo Router
- TanStack Query
- React Hook Form
- Zod where appropriate
- A reliable charting library compatible with React Native/Expo
- AsyncStorage or SecureStore for appropriate local persistence
- Jest + React Native Testing Library for frontend tests

## Backend

- Python
- FastAPI
- Pydantic
- SQLAlchemy 2.x
- Alembic
- PostgreSQL
- Pytest
- HTTPX for API testing

## Authentication

Implement simple authentication so the application can eventually be used securely.

Use:

- JWT access tokens
- Secure password hashing
- SecureStore on mobile for tokens

Do not store passwords in plaintext.

## Development

Use:

- Git
- GitHub
- ESLint
- Prettier
- Ruff
- Black
- mypy where practical
- `.env` configuration
- Docker/Docker Compose for local PostgreSQL and backend development

---

# 2. IMPORTANT DEVELOPMENT RULE

This project MUST be developed incrementally.

DO NOT build the entire application at once.

Implement ONE feature at a time.

For every feature:

1. Analyze the requirement.
2. Design the data model/API/UI needed.
3. Implement the feature.
4. Write automated tests.
5. Run the tests.
6. Fix all failures.
7. Run linting/type checks.
8. Manually verify the feature where appropriate.
9. Document what was implemented.
10. Only then move to the next feature.

Never proceed to the next feature while the current feature has failing tests or known critical bugs.

Maintain a development document:

`docs/development-progress.md`

After every completed feature, update this document with:

- Feature name
- Requirements
- Files created/modified
- Database changes
- API changes
- UI changes
- Tests added
- Test results
- Bugs discovered
- Bugs fixed
- Design decisions
- Remaining limitations

Also maintain:

`docs/architecture.md`

and

`docs/api.md`

Keep documentation synchronized with the actual implementation.

---

# 3. CORE BUSINESS CONCEPT

There are two financial profiles:

## Benchmark

The benchmark represents my friend's cumulative theoretical earnings.

Initial assumptions:

- Employment start: January 2022
- Starting monthly salary: KSh 50,000
- Salary frequency: Monthly
- Benchmark salary is configurable.
- Benchmark income is calculated automatically.
- The benchmark should continue accumulating month by month.

For example:

January 2022 = KSh 50,000

February 2022 = KSh 50,000

March 2022 = KSh 50,000

etc.

Do NOT manually insert thousands of benchmark income records unless necessary.

Instead, create a benchmark configuration and calculate the expected cumulative income from:

`employment_start_date`

through the current date.

However, provide an option to override specific months later if the user wants to account for:

- Salary increases
- Bonuses
- Unpaid months
- Employment gaps
- Additional income
- Other adjustments

---

# 4. USER'S PERSONAL INCOME

My personal income begins from the date I start using the system.

I should be able to manually record income whenever I receive it.

An income record should support:

- Amount
- Date received
- Income source
- Category
- Description/notes
- Optional project/client
- Optional recurring flag
- Currency
- Created timestamp
- Updated timestamp

Examples:

- Freelancing — KSh 15,000
- Salary — KSh 40,000
- Contract — KSh 75,000
- Affiliate income — KSh 8,000
- Online work — KSh 20,000
- Business — KSh 12,500
- Other — KSh 5,000

Do NOT assume that my income is monthly.

I may earn:

- multiple times in one month
- once in several months
- irregular amounts
- large one-off payments
- recurring salary

The application must aggregate individual income transactions automatically.

---

# 5. IMPORTANT FINANCIAL CALCULATION RULES

Use exact decimal/numeric calculations.

DO NOT use floating-point arithmetic for monetary values.

PostgreSQL should use an appropriate `NUMERIC`/decimal type.

The backend should use Python `Decimal` for financial calculations.

The frontend should not independently perform authoritative financial calculations.

The backend is the source of truth.

---

# 6. BENCHMARK CALCULATION

Create a benchmark calculation service.

At minimum:

```text
benchmark_monthly_income = 50,000 KSh

benchmark_total =
number_of_completed/elapsed_benchmark_months
×
monthly_income
```

The exact treatment of the current month must be explicitly defined and consistent.

Prefer calculating the benchmark based on completed monthly periods plus the current month's accrued benchmark amount where appropriate.

Document the chosen calculation method.

Do not accidentally count the same month twice.

Use calendar-aware date calculations rather than assuming every month has 30 days.

---

# 7. CORE DASHBOARD

The first major screen should be a dashboard.

Display prominently:

### My Total Income

Example:

`KSh 125,500`

### Benchmark Total

Example:

`KSh 2,800,000`

### Current Gap

Example:

`KSh 2,674,500`

Formula:

```text
gap = benchmark_total - my_total
```

If my income exceeds the benchmark:

```text
gap = 0
surplus = my_total - benchmark_total
```

Do not display a negative "deficit".

Instead show:

`Ahead by KSh X`

### Progress Percentage

```text
progress = my_total / benchmark_total × 100
```

Cap the visual progress indicator at 100%, while still showing the actual amount.

### Income Required to Catch Up

Display the exact amount required.

### Benchmark Start Date

Display:

`January 2022`

### My Tracking Start Date

Display the date of the first personal income record or the configured tracking start date.

---

# 8. REAL-TIME / LIVE UPDATES

Whenever I add, edit, or delete an income record:

Immediately update:

- Total personal income
- Gap
- Progress percentage
- Monthly income
- Yearly income
- Charts
- Catch-up calculations
- Milestone progress

Use TanStack Query cache invalidation/refetching.

The UI should feel real-time even if actual server push/websocket functionality is not initially required.

Design the architecture so WebSockets or Server-Sent Events could be introduced later if needed.

---

# 9. INCOME ENTRY

Create an intuitive "Add Income" screen.

Fields:

### Amount

Required.

Must be greater than zero.

### Date

Required.

Default to today.

### Income source

Examples:

- Employment
- Freelancing
- Contract
- Business
- Affiliate
- Online work
- Investment
- Other

Allow custom categories later.

### Description

Optional.

### Currency

Default:

`KES`

Initially support KES properly.

Design the data model so additional currencies can be added later.

### Project/client

Optional.

### Recurring income

Optional.

Validate all fields.

Show clear validation errors.

After successful submission:

- save to backend
- update dashboard
- show success feedback
- return to appropriate screen

---

# 10. TRANSACTION HISTORY

Create an income history screen.

Show:

- Date
- Amount
- Source
- Category
- Description
- Running total if practical

Support:

- Search
- Filter by category
- Filter by date
- Filter by year
- Sort newest/oldest
- Edit
- Delete

Use pagination for scalability.

Do not load thousands of records unnecessarily.

---

# 11. MONTHLY BREAKDOWN

Create a monthly income screen.

For every month, show:

| Month | My Income | Benchmark | Gap |
|---|---:|---:|---:|

Example:

| Jan 2026 | KSh 10,000 | KSh 50,000 | KSh 40,000 |
| Feb 2026 | KSh 25,000 | KSh 50,000 | KSh 25,000 |
| Mar 2026 | KSh 60,000 | KSh 50,000 | Ahead |

This view should clearly show whether my monthly earnings are:

- below benchmark
- equal to benchmark
- above benchmark

---

# 12. YEARLY BREAKDOWN

Create yearly aggregation.

Example:

```text
2022
Benchmark: KSh 600,000
My income: KSh 0
Gap: KSh 600,000

2023
Benchmark: KSh 600,000
My income: KSh 0
Gap: KSh 1,200,000

...

2026
Benchmark: KSh X
My income: KSh X
Gap: KSh X
```

Allow tapping a year to view monthly details.

---

# 13. CUMULATIVE INCOME CHART

Create a chart showing cumulative income over time.

Two lines:

- My cumulative income
- Benchmark cumulative income

The chart should visually answer:

"How close am I?"

The X-axis should represent time.

The Y-axis should represent cumulative KSh.

Use a clean mobile-friendly design.

Allow selecting:

- All time
- 5 years
- 3 years
- 1 year
- 6 months
- Custom range

---

# 14. MONTHLY INCOME CHART

Create another chart comparing monthly income.

Show:

- My monthly income
- Benchmark monthly income

This should answer:

"Am I currently earning at the rate needed to catch up?"

---

# 15. GAP CHART

Create a gap-over-time chart.

Show:

`Benchmark cumulative income - My cumulative income`

This is important because I want to see whether the gap is:

- increasing
- stable
- decreasing

Label it clearly.

For example:

```text
Gap

Jan: KSh 2.4M
Feb: KSh 2.35M
Mar: KSh 2.20M
Apr: KSh 2.05M
```

The ideal direction is a declining gap.

---

# 16. CATCH-UP CALCULATOR

Build a dedicated catch-up calculator.

Inputs:

- Current personal cumulative income
- Current benchmark cumulative income
- Expected future monthly personal income
- Benchmark monthly income
- Optional expected monthly income growth

Calculate:

### Scenario A — Fixed Income

"If I earn KSh 50,000 every month, when will I catch up?"

### Scenario B — Higher Income

"If I earn KSh 100,000 every month, when will I catch up?"

### Scenario C — Aggressive Growth

Allow a monthly income growth assumption.

For example:

```text
Starting monthly income:
KSh 50,000

Monthly growth:
5%

Projected catch-up:
DATE
```

Clearly label projections as estimates.

Do not present projections as guaranteed outcomes.

---

# 17. REQUIRED MONTHLY INCOME TO CATCH UP

Calculate the monthly income required to catch up within:

- 1 year
- 2 years
- 3 years
- 5 years

Example:

```text
To catch up within 2 years:

Required average monthly income:
KSh 120,000
```

Explain the calculation.

If catch-up is mathematically impossible under the selected assumptions, clearly state why.

---

# 18. PROGRESS MILESTONES

Create milestones based on cumulative income.

Examples:

- KSh 100,000
- KSh 250,000
- KSh 500,000
- KSh 1,000,000
- 10% of benchmark
- 25%
- 50%
- 75%
- 100%

Allow custom milestones.

When a milestone is reached, display a subtle congratulatory message.

Do not make the app childish or overly gamified.

The design should feel like a serious personal finance/productivity application.

---

# 19. GAP REDUCTION METRIC

One of the most important metrics should be:

### Gap Reduced

Calculate how much the gap has decreased since tracking began.

Example:

```text
Starting gap:
KSh 2,700,000

Current gap:
KSh 2,500,000

Gap reduced:
KSh 200,000
```

Also show:

```text
Gap reduction: 7.4%
```

This should reinforce progress rather than only showing the absolute deficit.

---

# 20. MOMENTUM METRIC

Calculate recent income momentum.

For example:

### Last 3 Months

```text
Income: KSh 180,000
Average: KSh 60,000/month
```

Compare against benchmark:

```text
Benchmark: KSh 50,000/month
You're currently earning 20% above benchmark.
```

Also calculate:

- Last 30 days
- Last 90 days
- Last 12 months

---

# 21. PERSONAL BEST

Track my highest earning:

- Month
- Year
- Single transaction
- Rolling 3-month period

Example:

```text
Personal best month

July 2027
KSh 185,000
```

This should provide positive reinforcement.

---

# 22. STREAK / CONSISTENCY

Track whether I have recorded income consistently.

Example:

```text
Income recorded in:
6 consecutive months
```

Do not punish months where I genuinely earn nothing.

The goal is tracking and accountability, not artificial gamification.

---

# 23. MOTIVATIONAL INSIGHTS

Generate simple rule-based insights.

Examples:

```text
Your gap decreased by KSh 35,000 this month.

You earned KSh 15,000 more than the benchmark this month.

Your average monthly income over the last 3 months is KSh 62,000.

At your current average income, you're on track to reduce the gap by approximately KSh X per year.
```

Avoid manipulative or emotionally harmful messaging.

Never say things such as:

- "You're failing."
- "Your friend is ahead of you."
- "You're wasting your life."
- "You are behind everyone."

Use neutral financial language.

---

# 24. BENCHMARK SETTINGS

Create a Settings section where the benchmark can be configured.

Fields:

- Benchmark name
- Employment start date
- Monthly salary
- Currency
- Salary growth
- Additional income assumptions
- Employment status
- Optional monthly overrides

Default:

```text
Benchmark:
Friend

Start:
January 2022

Monthly income:
KSh 50,000
```

Allow renaming the benchmark to something less emotionally loaded, such as:

`Career Benchmark`

This should be encouraged in the UI.

---

# 25. SALARY INCREASES / BENCHMARK HISTORY

Create a benchmark salary history system.

Example:

```text
Jan 2022 – Dec 2024
KSh 50,000/month

Jan 2025 – Dec 2025
KSh 65,000/month

Jan 2026 –
KSh 80,000/month
```

The system should calculate cumulative benchmark income based on these periods.

This feature can initially be hidden behind advanced settings but the database should support it.

---

# 26. BENCHMARK ADJUSTMENTS

Support optional benchmark adjustments:

- Bonus
- Allowance
- Other income
- Unpaid month
- Employment gap

Example:

```text
December 2025
Salary: KSh 65,000
Bonus: KSh 100,000
Total: KSh 165,000
```

Keep salary and adjustment records separate.

---

# 27. DATA MODEL

Design a normalized PostgreSQL schema.

At minimum consider:

```text
users
income_transactions
income_categories
benchmark_profiles
benchmark_salary_history
benchmark_adjustments
milestones
user_settings
```

Use UUID primary keys.

Include:

- created_at
- updated_at

where appropriate.

Use foreign keys.

Use indexes on:

- user_id
- transaction_date
- category
- benchmark profile ID

Use database constraints to prevent invalid monetary values.

---

# 28. API DESIGN

Create RESTful APIs.

Examples:

```text
POST /auth/register
POST /auth/login

GET /users/me

GET /income
POST /income
GET /income/{id}
PATCH /income/{id}
DELETE /income/{id}

GET /dashboard

GET /analytics/monthly
GET /analytics/yearly
GET /analytics/cumulative
GET /analytics/gap

GET /benchmark
PATCH /benchmark

GET /benchmark/salary-history
POST /benchmark/salary-history
PATCH /benchmark/salary-history/{id}
DELETE /benchmark/salary-history/{id}

GET /milestones
POST /milestones
PATCH /milestones/{id}
DELETE /milestones/{id}

GET /projections/catch-up
```

Keep business calculations in dedicated service modules rather than putting complex financial logic directly inside route handlers.

---

# 29. BACKEND ARCHITECTURE

Use a clean structure similar to:

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── repositories/
│   ├── dependencies/
│   └── utils/
├── tests/
├── alembic/
├── alembic.ini
├── pyproject.toml
└── Dockerfile
```

Separate:

- API layer
- Business logic
- Database access
- Validation
- Authentication

---

# 30. MOBILE ARCHITECTURE

Use a structure similar to:

```text
mobile/
├── app/
│   ├── (auth)/
│   ├── (tabs)/
│   │   ├── index.tsx
│   │   ├── income.tsx
│   │   ├── analytics.tsx
│   │   └── settings.tsx
│   ├── income/
│   ├── benchmark/
│   └── projections/
├── components/
├── features/
├── hooks/
├── services/
├── api/
├── types/
├── utils/
├── constants/
└── tests/
```

Use feature-oriented architecture where practical.

Avoid creating one enormous component.

---

# 31. UI DESIGN

The UI should feel:

- clean
- mature
- focused
- motivating
- financial
- professional
- mobile-first

Avoid excessive gradients, childish gamification, or unnecessary animations.

The main dashboard should immediately communicate:

```text
YOUR TOTAL
KSh X

BENCHMARK
KSh X

CURRENT GAP
KSh X

PROGRESS
X%

AVERAGE MONTHLY INCOME
KSh X

CATCH-UP RATE
KSh X/month
```

Then show charts and recent activity.

---

# 32. DASHBOARD INFORMATION HIERARCHY

Top:

### "Your Financial Progress"

Then:

```text
My Income
KSh XXX

Benchmark
KSh XXX

Gap
KSh XXX
```

Then:

```text
Progress: XX%
```

Then:

### "Are You Closing the Gap?"

Display:

```text
Gap this month:
KSh X

Gap last month:
KSh Y

Change:
-KSh Z
```

Use clear visual indication that a decreasing gap is positive.

Then charts.

Then recent income.

Then catch-up projection.

---

# 33. EMPTY STATE

When there are no personal income records:

Do NOT display:

`You have earned KSh 0`

in a discouraging way.

Instead:

```text
Your journey starts here.

Your benchmark has already been accumulating since January 2022.

Add your first income to start tracking your progress.
```

Provide:

`+ Add Income`

button.

---

# 34. FIRST-RUN EXPERIENCE

On first launch:

1. Welcome screen.
2. Explain what the application tracks.
3. Configure benchmark.
4. Configure personal tracking start date.
5. Add first income or skip.
6. Show dashboard.

Make the benchmark assumptions editable.

---

# 35. OFFLINE SUPPORT

The app should remain usable if the network temporarily disappears.

At minimum:

- cache dashboard data
- cache recent transactions
- display last synchronized timestamp

Design the architecture so offline income entries can eventually be queued and synchronized.

If implementing offline writes, ensure duplicate transactions cannot be created during synchronization.

---

# 36. ERROR HANDLING

Implement proper error states.

Examples:

- Network unavailable
- Server unavailable
- Invalid amount
- Unauthorized
- Transaction not found
- Database error
- Authentication failure

Never expose raw Python exceptions to users.

Show human-readable messages.

Log technical details on the backend.

---

# 37. SECURITY

Implement:

- Password hashing
- JWT authentication
- Authorization checks
- Input validation
- SQL injection protection through SQLAlchemy
- Secure token storage
- Environment variables
- No secrets committed to Git
- CORS configuration
- Rate limiting where appropriate
- Secure production configuration

Every income transaction must belong to an authenticated user.

A user must NEVER be able to access another user's financial records.

---

# 38. DATABASE MIGRATIONS

Use Alembic.

Never manually modify production schema.

Every schema change should create an Alembic migration.

Test migrations from a clean database.

---

# 39. TESTING STRATEGY

Testing is mandatory.

## Backend unit tests

Test:

- benchmark calculations
- monthly aggregation
- yearly aggregation
- cumulative income
- gap calculations
- progress percentages
- salary changes
- benchmark adjustments
- catch-up projections
- milestone calculations
- edge cases

## API tests

Test:

- authentication
- CRUD income
- authorization
- dashboard endpoint
- analytics endpoints
- benchmark endpoints
- invalid inputs

## Frontend tests

Test:

- dashboard rendering
- income form validation
- adding income
- editing income
- deleting income
- loading/error states
- filters
- calculations displayed by API
- navigation

---

# 40. CRITICAL FINANCIAL TEST CASES

Create explicit tests for:

### Case 1

Friend starts January 2022.

Salary = KSh 50,000.

Verify January calculation.

### Case 2

Verify February calculation.

### Case 3

Verify one complete year.

Expected:

```text
12 × 50,000 = KSh 600,000
```

### Case 4

Verify multiple years.

### Case 5

Current month handling.

### Case 6

User earns nothing.

### Case 7

User earns multiple transactions in one month.

Example:

```text
KSh 10,000
KSh 20,000
KSh 15,000
```

Monthly total should be:

```text
KSh 45,000
```

### Case 8

User earns more than benchmark.

The system should display:

```text
Ahead by KSh X
```

### Case 9

Salary changes.

### Case 10

Bonus/adjustment.

### Case 11

Income transaction edited.

All totals must recalculate.

### Case 12

Income transaction deleted.

All totals must recalculate.

### Case 13

Different users.

User A must never see User B's income.

---

# 41. TEST DATA / SEEDING

Create development seed data.

Example:

Benchmark:

```text
Start: 2022-01-01
Salary: KSh 50,000
```

Personal income:

```text
2026-08-01 — KSh 10,000
2026-08-10 — KSh 15,000
2026-08-20 — KSh 25,000
```

Expected August personal income:

```text
KSh 50,000
```

Use this to verify dashboard calculations.

Do not use fake data in production.

---

# 42. DATA EXPORT

Implement CSV export.

Allow me to export:

- all personal income
- monthly summary
- yearly summary
- benchmark comparison

Example:

```text
date,source,category,amount,currency,description
```

Later consider PDF export.

---

# 43. BACKUP / DATA PORTABILITY

Design the system so personal income data can be backed up.

Provide:

- CSV export
- JSON export if practical

Do not lock the user's financial data into the application.

---

# 44. NOTIFICATIONS

Design optional reminders.

Examples:

### Monthly reminder

"Have you recorded all your income for this month?"

### Milestone

"You've reached KSh 500,000 in cumulative income."

### Progress

"Your gap decreased by KSh X this month."

Notifications must be optional.

Do not spam the user.

---

# 45. SETTINGS

Create settings for:

- Currency
- Benchmark
- Salary history
- Income categories
- Notifications
- Theme
- Export data
- Account
- Security
- Delete account

---

# 46. PRIVACY

Financial data is private.

The application should clearly communicate:

- Income data belongs to the user.
- Benchmark data is configurable.
- Data is not publicly visible.
- Authentication is required for stored data.

Do not expose financial information through analytics URLs or logs.

---

# 47. RESPONSIVE / ACCESSIBLE UI

Ensure:

- readable typography
- sufficient contrast
- large touch targets
- screen-reader-friendly labels
- accessible form controls
- proper keyboard behavior
- appropriate number input keyboard
- safe area handling

---

# 48. PERFORMANCE

Avoid unnecessary API requests.

Use:

- TanStack Query caching
- pagination
- memoization where useful
- database indexes
- server-side aggregation for large datasets

Do not fetch every transaction simply to calculate dashboard totals.

Create optimized backend aggregation queries.

---

# 49. IMPORTANT ARCHITECTURAL PRINCIPLE

The backend should be the source of truth for all financial calculations.

The frontend should primarily:

- request data
- render data
- collect user input
- send mutations

Do not duplicate complex financial calculations independently in React Native.

This prevents discrepancies between screens.

---

# 50. DOCUMENTATION

Create:

```text
README.md
docs/architecture.md
docs/development-progress.md
docs/database.md
docs/api.md
docs/calculations.md
docs/testing.md
docs/deployment.md
```

`docs/calculations.md` must explain every financial formula.

For example:

```text
gap
progress
monthly income
annual income
cumulative income
gap reduction
catch-up projection
required monthly income
```

---

# 51. DEVELOPMENT PHASES

Build the application in the following order.

## PHASE 1 — Project Setup

Create:

- React Native Expo project
- FastAPI project
- PostgreSQL
- Docker Compose
- Git repository
- Environment configuration
- linting
- formatting
- testing infrastructure

TEST BEFORE CONTINUING.

---

## PHASE 2 — Database

Implement:

- users
- income transactions
- benchmark profile

Create migrations.

Create seed data.

Test database operations.

TEST BEFORE CONTINUING.

---

## PHASE 3 — Authentication

Implement:

- registration
- login
- password hashing
- JWT
- authentication middleware
- protected routes

Test:

- valid login
- invalid login
- unauthorized requests
- user isolation

TEST BEFORE CONTINUING.

---

## PHASE 4 — Income CRUD

Implement:

- add income
- list income
- view income
- edit income
- delete income

Test every operation.

TEST BEFORE CONTINUING.

---

## PHASE 5 — Benchmark Engine

Implement benchmark calculation.

Default:

```text
January 2022
KSh 50,000/month
```

Test exact monthly and cumulative calculations.

TEST BEFORE CONTINUING.

---

## PHASE 6 — Dashboard API

Create the dashboard aggregation endpoint.

Return:

```text
my_total_income
benchmark_total
gap
surplus
progress_percentage
monthly_income
yearly_income
gap_change
average_monthly_income
```

Test extensively.

TEST BEFORE CONTINUING.

---

## PHASE 7 — Mobile Dashboard

Build the main dashboard.

Connect it to the backend.

Test:

- loading
- success
- error
- empty states
- refresh
- data updates

TEST BEFORE CONTINUING.

---

## PHASE 8 — Add Income UI

Build the income form.

Connect it to API.

After saving:

- invalidate relevant queries
- refresh dashboard
- update totals

TEST BEFORE CONTINUING.

---

## PHASE 9 — Transaction History

Build:

- list
- filters
- search
- edit
- delete

TEST BEFORE CONTINUING.

---

## PHASE 10 — Monthly Analytics

Implement monthly aggregation API and UI.

TEST BEFORE CONTINUING.

---

## PHASE 11 — Yearly Analytics

Implement yearly aggregation.

TEST BEFORE CONTINUING.

---

## PHASE 12 — Charts

Implement:

- cumulative comparison
- monthly comparison
- gap trend

TEST BEFORE CONTINUING.

---

## PHASE 13 — Catch-Up Calculator

Implement projection engine.

Test mathematical correctness extensively.

TEST BEFORE CONTINUING.

---

## PHASE 14 — Milestones

Implement milestones and achievement tracking.

TEST BEFORE CONTINUING.

---

## PHASE 15 — Benchmark Salary History

Implement salary changes.

TEST BEFORE CONTINUING.

---

## PHASE 16 — Benchmark Adjustments

Implement:

- bonuses
- allowances
- unpaid periods
- other adjustments

TEST BEFORE CONTINUING.

---

## PHASE 17 — Insights

Implement rule-based financial insights.

TEST BEFORE CONTINUING.

---

## PHASE 18 — Export

Implement CSV/JSON export.

TEST BEFORE CONTINUING.

---

## PHASE 19 — Notifications

Implement optional reminders.

TEST BEFORE CONTINUING.

---

## PHASE 20 — Offline/Caching Improvements

Improve caching and offline behavior.

TEST BEFORE CONTINUING.

---

## PHASE 21 — Security Audit

Review:

- authentication
- authorization
- database access
- secrets
- API validation
- token handling
- CORS
- logs
- data exposure

Fix issues.

TEST BEFORE CONTINUING.

---

## PHASE 22 — Performance Audit

Check:

- API response times
- database queries
- indexes
- unnecessary API calls
- React Native rendering
- chart performance

Optimize where necessary.

TEST BEFORE CONTINUING.

---

## PHASE 23 — End-to-End Testing

Run a complete scenario:

1. Register user.
2. Configure benchmark.
3. Add first income.
4. View dashboard.
5. Add multiple incomes.
6. Verify monthly totals.
7. Verify cumulative totals.
8. Verify gap.
9. Verify chart.
10. Edit transaction.
11. Verify recalculation.
12. Delete transaction.
13. Verify recalculation.
14. Change benchmark salary.
15. Verify recalculation.
16. Run catch-up projection.
17. Export data.

Everything must work.

---

# 52. FINAL ACCEPTANCE CRITERIA

The application is considered complete only when:

- A user can register/login.
- A benchmark can start from January 2022.
- The default benchmark is KSh 50,000/month.
- Benchmark income automatically accumulates.
- Personal income can be added at any time.
- Multiple income records per month are supported.
- Dashboard totals update immediately after changes.
- Current gap is accurately calculated.
- Progress percentage is accurately calculated.
- Monthly analytics work.
- Yearly analytics work.
- Cumulative charts work.
- Gap trend works.
- Catch-up projections work.
- Benchmark salary changes are supported.
- Benchmark adjustments are supported.
- Transactions can be edited/deleted.
- Financial calculations use decimal-safe arithmetic.
- Users cannot access each other's data.
- Automated tests pass.
- Linting passes.
- Type checks pass where configured.
- Database migrations work.
- Documentation is complete.
- No known critical bugs remain.

---

# 53. IMPORTANT UX PRINCIPLE

The application is being built as a motivational financial tracking tool.

The benchmark should provide pressure and accountability without making the application psychologically destructive.

The application should emphasize:

```text
"How much closer did I get?"

rather than:

"How far behind am I?"
```

Therefore the most important dashboard metric after the current gap should be:

### GAP REDUCED

For example:

```text
You've reduced the gap by KSh 240,000
since you started tracking.
```

Also show:

```text
Your average monthly income:
KSh 62,500

Benchmark:
KSh 50,000

Current rate:
125% of benchmark
```

This lets the application recognize when my income trajectory is improving even if the historical cumulative gap remains large.

---

# 54. FUTURE FEATURES — DO NOT IMPLEMENT YET

Keep the architecture extensible for:

- Multiple benchmarks
- Multiple currencies
- Net income vs gross income
- Expenses
- Savings
- Investments
- Net worth
- Tax tracking
- AI financial insights
- Income forecasting
- Web dashboard
- Desktop dashboard
- CSV import
- Bank integrations
- M-Pesa integration
- Recurring income automation
- Multiple financial goals

Do NOT implement these until the core income-vs-benchmark tracker is stable.

---

# 55. CODE QUALITY RULES

Write production-quality code.

Avoid:

- giant components
- duplicated logic
- hard-coded calculations
- hard-coded API URLs
- hard-coded secrets
- floating-point monetary calculations
- unnecessary dependencies
- premature abstraction
- duplicated business logic
- untested financial formulas

Use meaningful names.

Add comments only where they explain WHY something exists, not obvious code.

Prefer small, testable functions.

Keep financial calculation functions pure wherever possible.

---

# 56. CODEX WORKFLOW

When starting:

### Step 1

Inspect the repository.

If an existing project exists, understand it before changing anything.

Do not overwrite existing work without understanding it.

### Step 2

Create a plan.

### Step 3

Implement only PHASE 1.

### Step 4

Run all relevant tests.

### Step 5

Fix failures.

### Step 6

Update documentation.

### Step 7

Show me a concise summary:

```text
Completed:
Phase X — Feature

Files changed:
...

Tests:
X passed

Lint:
Passed

Type check:
Passed

Documentation:
Updated

Next:
Phase X+1
```

Then continue to the next phase only after the current phase is confirmed stable.

If you encounter an architectural decision, explain the tradeoff briefly and choose the option most appropriate for a production application.

---

# 57. FIRST TASK

Start by inspecting the current repository.

Determine whether this is:

- an empty repository
- an existing React Native project
- an existing Python backend
- an existing full-stack project

Do not immediately write application features.

First create:

```text
docs/architecture.md
docs/development-progress.md
docs/calculations.md
README.md
```

Then establish the project architecture and development environment.

Implement **PHASE 1 ONLY**.

Run the tests.

Fix all issues.

Document the result.

Do not proceed to Phase 2 until Phase 1 is fully tested and stable.