# Deployment

Use a managed PostgreSQL instance, a long random `SECRET_KEY`, HTTPS, restrictive CORS origins, and Alembic migrations during deployment. Never use the default development key or commit `.env`. Set the Expo API URL to the public HTTPS API origin.
