import aiosqlite
from pathlib import Path

DB_PATH = str(Path(__file__).parent.parent / "jobs.db")


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS print_jobs (
                id                TEXT PRIMARY KEY,
                code              TEXT NOT NULL,
                status            TEXT NOT NULL,
                file_path         TEXT,
                file_type         TEXT,
                original_filename TEXT,
                printer_type      TEXT,
                options           TEXT,
                error_msg         TEXT,
                created_at        TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at        TEXT NOT NULL DEFAULT (datetime('now'))
            )
        """)
        await db.commit()


async def create_job(
    job_id: str,
    code: str,
    file_type: str,
    original_filename: str,
    printer_type: str,
    options: str,
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO print_jobs (id, code, status, file_type, original_filename, printer_type, options)
            VALUES (?, ?, 'DOWNLOADING', ?, ?, ?, ?)
            """,
            (job_id, code, file_type, original_filename, printer_type, options),
        )
        await db.commit()


async def update_job(
    job_id: str,
    status: str,
    *,
    error_msg: str | None = None,
    file_path: str | None = None,
) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            UPDATE print_jobs
            SET status    = ?,
                error_msg = COALESCE(?, error_msg),
                file_path = COALESCE(?, file_path),
                updated_at = datetime('now')
            WHERE id = ?
            """,
            (status, error_msg, file_path, job_id),
        )
        await db.commit()


async def get_job(job_id: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM print_jobs WHERE id = ?", (job_id,)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_in_flight_jobs() -> list[dict]:
    """Return jobs that were mid-process when the Pi last restarted."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT * FROM print_jobs
            WHERE status IN ('DOWNLOADING', 'CONVERTING', 'READY', 'PRINTING')
            """
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]
