# Income Gap Tracker

A private, mobile-first tool for tracking personal income against a configurable financial benchmark. The comparison is presented as neutral financial progress—not a measure of personal worth.

## Run locally

1. Optionally copy `.env.example` to `.env` and set a real `SECRET_KEY`. Docker uses development defaults when this file is absent.
2. Start PostgreSQL and the API with `docker compose up --build`. The API container applies Alembic migrations before it starts.
3. In a separate terminal, `cd mobile && npm install && npx expo start`.
4. Set `EXPO_PUBLIC_API_URL` to your reachable API address (for a physical device, use your computer's LAN IP, not `localhost`).

Run backend checks with `cd backend && python3 -m pip install -e '.[dev]' && pytest -q && ruff check .`.

For host-run migrations against Docker PostgreSQL, start the database first with `docker compose up -d db`, then run `cd backend && .venv/bin/python -m alembic upgrade head`. Without a root `.env`, Alembic uses the local SQLite development database (`backend/income_gap.db`).

See [architecture](docs/architecture.md), [API](docs/api.md), and [calculations](docs/calculations.md).
