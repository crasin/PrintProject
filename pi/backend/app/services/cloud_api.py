"""
Thin wrapper around the cloud REST API.
All calls include the per-store API key header for auth.
"""
import httpx
from app.config import settings

_HEADERS = {"X-Store-Api-Key": settings.store_api_key}


async def validate_code(code: str) -> dict | None:
    """
    Ask the cloud to validate a print code.

    Returns job details dict on success, None if the code is invalid/expired/already used.
    Raises httpx.HTTPError on unexpected server errors.

    Expected response shape:
    {
        "job_id": "uuid",
        "download_url": "https://s3.signed-url...",
        "file_type": "pdf",          # extension: pdf | docx | xlsx | pptx | jpg | png
        "original_filename": "doc.pdf",
        "printer_type": "LASER_DOCUMENT",   # or COLOR_PHOTO
        "options": {
            "copies": 1,
            "paper_size": "A4",      # A4 | Letter | 4x6 | 5x7
            "color": false
        }
    }
    """
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            f"{settings.cloud_api_url}/api/jobs/validate-code",
            json={"code": code},
            headers=_HEADERS,
        )
        if response.status_code in (404, 410):
            return None
        response.raise_for_status()
        return response.json()


async def update_job_status(job_id: str, status: str) -> None:
    """
    Report a job's final status (DONE or FAILED) back to the cloud.
    Cloud deletes the S3 file on DONE.
    Fire-and-forget safe — caller should wrap in try/except.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.patch(
            f"{settings.cloud_api_url}/api/jobs/{job_id}/status",
            json={"status": status},
            headers=_HEADERS,
        )
        response.raise_for_status()


async def post_heartbeat(printer_states: dict) -> None:
    """
    Send printer health to the cloud admin API.
    printer_states = {"PrinterName": "idle" | "printing" | "offline"}
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{settings.cloud_api_url}/api/stores/{settings.store_id}/heartbeat",
            json={"printer_states": printer_states},
            headers=_HEADERS,
        )
        response.raise_for_status()
