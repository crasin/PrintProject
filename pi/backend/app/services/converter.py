"""
Converts Office documents (DOCX, XLSX, PPTX) to PDF using LibreOffice headless.
PDF, JPG, and PNG pass through unchanged.
"""
import asyncio
from pathlib import Path

# File types that CUPS accepts natively — no conversion needed
_PASSTHROUGH = {"pdf", "jpg", "jpeg", "png"}


async def convert_to_pdf_if_needed(file_path: Path, file_type: str) -> Path:
    """
    Returns a Path to the file ready for CUPS submission.
    For Office formats, runs LibreOffice and returns the converted PDF path.
    For passthrough types, returns file_path unchanged.
    """
    if file_type.lower() in _PASSTHROUGH:
        return file_path

    return await _libreoffice_convert(file_path)


async def _libreoffice_convert(file_path: Path) -> Path:
    output_dir = file_path.parent

    proc = await asyncio.create_subprocess_exec(
        "libreoffice",
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_dir),
        str(file_path),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise RuntimeError(
            f"LibreOffice conversion failed (exit {proc.returncode}): {stderr.decode().strip()}"
        )

    pdf_path = output_dir / (file_path.stem + ".pdf")
    if not pdf_path.exists():
        raise FileNotFoundError(
            f"LibreOffice did not produce expected output: {pdf_path}"
        )

    return pdf_path
