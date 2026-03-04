"""
Downloads a file from a pre-signed S3 URL to a local temp directory.
Uses streaming to handle large files (up to 50 MB) without loading into RAM.
"""
import aiofiles
import httpx
from pathlib import Path
from app.config import settings


async def download_file(url: str, job_id: str, file_type: str) -> Path:
    """
    Stream-download the file into /tmp/printjobs/<job_id>/original.<ext>.
    Returns the local Path of the downloaded file.
    """
    job_dir = Path(settings.temp_dir) / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    file_path = job_dir / f"original.{file_type}"

    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in response.aiter_bytes(chunk_size=65_536):
                    await f.write(chunk)

    return file_path
