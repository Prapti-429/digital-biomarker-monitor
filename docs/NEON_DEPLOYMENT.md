# NUVYRA — Neon production database

NUVYRA uses PostgreSQL through the `DATABASE_URL` environment variable. The database URL belongs only on the backend hosting service and must never be committed to Git or exposed to the frontend.

## Production sequence

1. Keep the existing database until a backup is safely stored.
2. Create/verify the Neon production database.
3. Run the repository's Alembic migrations against Neon.
4. Set the backend's `DATABASE_URL` to the Neon PostgreSQL connection string.
5. Redeploy the backend.
6. Verify the health endpoint.
7. Test registration, login, logout, check-in persistence, dashboard history and AI analysis.
8. Only after successful verification should the old database be retired.

## Security

Never place `DATABASE_URL` in frontend environment variables. Never commit database credentials. Use the provider's secret/environment-variable settings for production credentials.
