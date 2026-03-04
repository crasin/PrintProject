import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import get_in_flight_jobs, init_db, update_job
from app.routers import print_jobs
from app.services.cloud_api import update_job_status
from app.tasks.heartbeat import heartbeat_loop

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    await init_db()
    logger.info("Database initialised")

    # Recover jobs that were in-flight when the Pi last crashed/restarted.
    # The cloud code is already CLAIMED, so mark them FAILED and let the
    # store admin reset from the dashboard if needed.
    in_flight = await get_in_flight_jobs()
    if in_flight:
        logger.warning("Found %d in-flight jobs from before restart — marking FAILED", len(in_flight))
        for job in in_flight:
            await update_job(job["id"], "FAILED", error_msg="Pi restarted mid-job")
            try:
                await update_job_status(job["id"], "FAILED")
            except Exception as exc:
                logger.warning("Could not notify cloud for job %s: %s", job["id"], exc)

    # Start heartbeat as a background task
    hb_task = asyncio.create_task(heartbeat_loop())
    logger.info("Heartbeat started (interval=%ds)", 60)

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    hb_task.cancel()
    try:
        await hb_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="PrintProject Pi Backend",
    description="Local backend running on Raspberry Pi — validates print codes and controls CUPS printers.",
    version="0.1.0",
    lifespan=lifespan,
)

# Only the local kiosk frontend needs to reach this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["*"],
)

app.include_router(print_jobs.router)


@app.get("/health", tags=["meta"])
async def health():
    return {"status": "ok"}
