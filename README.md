# Feste Italia

Monorepo per un portale italiano dedicato alla scoperta di eventi, manifestazioni e idee per gite.

## Stack

- Frontend: Next.js, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, Pydantic
- Database: PostgreSQL + PostGIS
- Infrastructure: Docker + Docker Compose

## Quick start

1. Copy `.env.example` to `.env`
2. Ensure Docker Desktop is running with the Linux engine enabled
3. Run `docker compose up --build`
4. Open the frontend at `http://localhost:3000`
5. Open the API at `http://localhost:8000/docs`

### Local checks without Docker

The API uses Python 3.12. From `apps/api`, activate the repository virtual environment and run `uvicorn app.main:app --reload`.

The frontend uses Node.js 24 and can be checked from the repository root with `npm --workspace apps/web run typecheck`, `npm --workspace apps/web run lint`, and `npm --workspace apps/web run build`.

## Workspace structure

- `apps/web`: Next.js frontend
- `apps/api`: FastAPI backend
- `docs`: project documentation
- `infrastructure`: deployment and environment helpers

## Status

The foundation and first homepage MVP are ready. Database-backed features still require the Docker Postgres/PostGIS service to be running.
