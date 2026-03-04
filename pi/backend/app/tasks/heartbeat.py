"""
Background heartbeat loop.
Posts printer states to the cloud admin API every HEARTBEAT_INTERVAL seconds.
Failures are silently swallowed — a missed heartbeat is not fatal.
"""
import asyncio
import logging

from app.config import settings
from app.services.cloud_api import post_heartbeat
from app.services.cups_service import get_printer_states

logger = logging.getLogger(__name__)


async def heartbeat_loop() -> None:
    while True:
        try:
            states = await get_printer_states()
            await post_heartbeat(states)
        except Exception as exc:
            logger.warning("Heartbeat failed: %s", exc)
        await asyncio.sleep(settings.heartbeat_interval)
