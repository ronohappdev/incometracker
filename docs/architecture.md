# Architecture

The repository has a React Native/Expo Router mobile app and a FastAPI API. The mobile client uses TanStack Query for server data and invalidates the dashboard and transaction queries after a write. JWT tokens are intended for Expo SecureStore; passwords are Argon2-hashed on the API.

The API uses SQLAlchemy 2.x models, PostgreSQL NUMERIC(14,2) monetary columns, and `Decimal` for all financial calculations. Route handlers own transport/authentication only; `app/services.py` owns financial calculations. PostgreSQL schema evolution is through Alembic migrations; the startup schema creation is strictly a local-development convenience.

Implemented entities are `users`, `benchmark_profiles`, and `income_transactions`. All transaction reads and mutations scope by authenticated user ID.
