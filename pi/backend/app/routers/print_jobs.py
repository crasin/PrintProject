import json
import shutil
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.database import create_job, get_job, update_job
from app.services import cloud_api, cups_service
from app.services.converter import convert_to_pdf_if_needed
from app.services.downloader import download_file

router = APIRouter(prefix="/local", tags=["print"])


class PrintRequest(BaseModel):
    code: str


# ---------------------------------------------------------------------------
# POST /local/print
# Validates the code, returns file details immediately, then starts
# download + conversion in the background. STOPS at READY — does not
# submit to CUPS until the user explicitly confirms via POST /local/confirm.
# ---------------------------------------------------------------------------
@router.post("/print")
async def start_print(request: PrintRequest, background_tasks: BackgroundTasks):
    code = request.code.strip().upper()

    job = await cloud_api.validate_code(code)
    if job is None:
        raise HTTPException(status_code=404, detail="Invalid or expired code")

    job_id = job["job_id"]

    await create_job(
        job_id=job_id,
        code=code,
        file_type=job["file_type"],
        original_filename=job["original_filename"],
        printer_type=job["printer_type"],
        options=json.dumps(job["options"]),
    )

    background_tasks.add_task(_download_and_convert, job)

    # Return full job details so the frontend can show the preview immediately
    return {
        "job_id": job_id,
        "status": "DOWNLOADING",
        "original_filename": job["original_filename"],
        "file_type": job["file_type"],
        "printer_type": job["printer_type"],
        "options": job["options"],
    }


# ---------------------------------------------------------------------------
# POST /local/confirm/{job_id}
# Called by the kiosk UI when the user taps "Print Now" on the preview screen.
# Requires status == READY (download + convert already done).
# ---------------------------------------------------------------------------
@router.post("/confirm/{job_id}")
async def confirm_print(job_id: str, background_tasks: BackgroundTasks):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] != "READY":
        raise HTTPException(
            status_code=409,
            detail=f"Job is not ready for printing (status: {job['status']})",
        )

    printer_name = (
        settings.photo_printer_name
        if job["printer_type"] == "COLOR_PHOTO"
        else settings.document_printer_name
    )
    options = json.loads(job["options"]) if isinstance(job["options"], str) else job["options"]

    background_tasks.add_task(_submit_and_monitor, job_id, job["file_path"], printer_name, options)

    return {"job_id": job_id, "status": "PRINTING"}


# ---------------------------------------------------------------------------
# GET /local/status/{job_id}
# Kiosk UI polls this to drive screen transitions.
# Statuses: DOWNLOADING → CONVERTING → READY → PRINTING → DONE | FAILED
# ---------------------------------------------------------------------------
@router.get("/status/{job_id}")
async def get_status(job_id: str):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


# ---------------------------------------------------------------------------
# GET /local/printers
# Kiosk can check whether printers are online before showing the idle screen.
# ---------------------------------------------------------------------------
@router.get("/printers")
async def get_printers():
    states = await cups_service.get_printer_states()
    return {"printers": states}


# ---------------------------------------------------------------------------
# Background task: download file + convert to PDF, then stop at READY.
# ---------------------------------------------------------------------------
async def _download_and_convert(job: dict) -> None:
    job_id = job["job_id"]
    job_dir = Path(settings.temp_dir) / job_id

    try:
        file_path = await download_file(
            url=job["download_url"],
            job_id=job_id,
            file_type=job["file_type"],
        )
        await update_job(job_id, "CONVERTING", file_path=str(file_path))

        print_path = await convert_to_pdf_if_needed(file_path, job["file_type"])

        # Store the final print-ready path and mark READY — awaiting user confirm
        await update_job(job_id, "READY", file_path=str(print_path))

    except Exception as exc:
        await update_job(job_id, "FAILED", error_msg=str(exc))
        try:
            await cloud_api.update_job_status(job_id, "FAILED")
        except Exception:
            pass
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)


# ---------------------------------------------------------------------------
# Background task: submit to CUPS and monitor until terminal state.
# Triggered by POST /local/confirm.
# ---------------------------------------------------------------------------
async def _submit_and_monitor(
    job_id: str,
    file_path: str,
    printer_name: str,
    options: dict,
) -> None:
    job_dir = Path(settings.temp_dir) / job_id

    try:
        await update_job(job_id, "PRINTING")
        cups_job_id = await cups_service.submit_to_cups(file_path, printer_name, options)
        result = await cups_service.wait_for_cups_job(cups_job_id)

        final = "DONE" if result == "DONE" else "FAILED"
        await update_job(job_id, final)
        await cloud_api.update_job_status(job_id, final)

    except Exception as exc:
        await update_job(job_id, "FAILED", error_msg=str(exc))
        try:
            await cloud_api.update_job_status(job_id, "FAILED")
        except Exception:
            pass

    finally:
        if job_dir.exists():
            shutil.rmtree(job_dir, ignore_errors=True)
