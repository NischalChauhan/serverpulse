
import asyncio
import logging
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.permissions import router as permissions_router
from app.api.routes.servers import router as servers_router
from app.api.routes.metrics import router as metrics_router
from app.api.routes.alerts import router as alerts_router

from app.db.session import SessionLocal
from app.services.server_monitor import update_server_statuses


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONITOR_INTERVAL_SECONDS = 15


def run_server_status_check():
    db = SessionLocal()

    try:
        updated_count = update_server_statuses(db)

        if updated_count:
            logger.warning(
                "Marked %s server(s) offline due to missed heartbeats",
                updated_count,
            )

    finally:
        db.close()


async def offline_monitor_loop():
    logger.info("Server offline monitor started")

    while True:
        try:
            await asyncio.to_thread(run_server_status_check)

        except Exception:
            logger.exception("Server offline monitor check failed")

        await asyncio.sleep(MONITOR_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI):
    monitor_task = asyncio.create_task(offline_monitor_loop())

    try:
        yield
    finally:
        monitor_task.cancel()

        with suppress(asyncio.CancelledError):
            await monitor_task

        logger.info("Server offline monitor stopped")


app = FastAPI(
    title="OpsPulse API",
    description="Linux Server Monitoring and Observability Platform",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "OpsPulse API",
    }


# Register API routers
app.include_router(auth_router, prefix="/api")
app.include_router(permissions_router, prefix="/api")
app.include_router(servers_router, prefix="/api")
app.include_router(metrics_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
