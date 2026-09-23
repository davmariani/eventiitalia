import asyncio
import logging

from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import SessionLocal, initialize_database, test_database_connection
from app.refresh import refresh_demo_data
from app.routers.events import router as events_router

logger = logging.getLogger(__name__)


async def scheduled_db_refresh_worker() -> None:
    while True:
        now = datetime.now()
        next_run = datetime.combine(now.date(), time(1, 0))
        if now >= next_run:
            next_run += timedelta(days=1)
        sleep_seconds = (next_run - now).total_seconds()
        await asyncio.sleep(sleep_seconds)

        try:
            with SessionLocal() as session:
                count = refresh_demo_data(session)
            logger.info("Scheduled database refresh completed: %s events updated", count)
        except Exception as exc:  # pragma: no cover - runtime guard
            logger.exception("Scheduled database refresh failed: %s", exc)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    database_ready = test_database_connection()
    if database_ready:
        logger.info("Database connection successful")
    else:
        logger.warning("Database not reachable at startup; continuing in degraded mode.")

    task = asyncio.create_task(scheduled_db_refresh_worker())
    try:
        yield
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logger.info("Scheduled database refresh worker stopped.")


app = FastAPI(
    title="Feste Italia API",
    version="0.1.0",
    description="API per eventi, mappe e ricerca territoriale italiana.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Modificato da True a False
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events_router)


@app.get("/health")
def healthcheck() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "environment": settings.app_env,
    }


@app.get("/")
def root() -> dict:
    return {
        "message": "Feste Italia API",
        "docs": "/docs",
        "health": "/health",
    }
