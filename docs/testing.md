# Testing

Backend tests cover benchmark January, February, full-year, and current-month calendar accrual; income CRUD; invalid input; authentication; and user isolation. Run `pytest -q` from `backend` after installing development dependencies. Run `ruff check .` for linting.

Mobile test tooling is scaffolded in `package.json`; component tests are the next feature once the authentication/onboarding flow is implemented.
