# API

All protected endpoints require `Authorization: Bearer <JWT>`.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/auth/register` | Create account and default Career Benchmark (Jan 2022, KSh 50,000) |
| POST | `/auth/login` | Return JWT |
| GET | `/users/me` | Current account |
| GET/POST | `/income` | Paginated history/create transaction |
| GET/PATCH/DELETE | `/income/{id}` | A user-owned income transaction |
| GET/PATCH | `/benchmark` | Configurable benchmark |
| GET/POST | `/benchmark/salary-history` | List/add salary-rate periods |
| PATCH/DELETE | `/benchmark/salary-history/{id}` | Change/remove a salary-rate period |
| GET/POST | `/benchmark/adjustments` | List/add dated benchmark adjustments |
| GET | `/dashboard` | Authoritative totals and metrics |

`GET /income` supports `page`, `page_size`, `search`, `category`, `start_date`, `end_date`, and `oldest` query parameters.

Salary-history periods select the newest applicable rate for each calendar date. Adjustments are dated positive or negative amounts, suitable for bonuses, allowances, unpaid months, and employment gaps.
