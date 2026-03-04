const BASE: string = import.meta.env.VITE_PI_API_URL ?? 'http://localhost:8001'

export interface PrintOptions {
  copies: number
  paper_size: string
  color: boolean
}

export interface StartPrintResponse {
  job_id: string
  status: string
  original_filename: string
  file_type: string
  printer_type: string
  options: PrintOptions
}

export interface JobStatus {
  id: string
  status: 'DOWNLOADING' | 'CONVERTING' | 'READY' | 'PRINTING' | 'DONE' | 'FAILED'
  original_filename: string | null
  file_type: string | null
  printer_type: string | null
  options: string | null
  error_msg: string | null
  file_path: string | null
  created_at: string
  updated_at: string
}

export async function startPrint(code: string): Promise<StartPrintResponse> {
  const res = await fetch(`${BASE}/local/print`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ code }),
  })
  if (res.status === 404) throw new InvalidCodeError()
  if (!res.ok) throw new Error(`Server error: ${res.status}`)
  return res.json()
}

export async function confirmPrint(jobId: string): Promise<void> {
  const res = await fetch(`${BASE}/local/confirm/${jobId}`, { method: 'POST' })
  if (!res.ok) throw new Error(`Confirm failed: ${res.status}`)
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  const res = await fetch(`${BASE}/local/status/${jobId}`)
  if (!res.ok) throw new Error(`Status fetch failed: ${res.status}`)
  return res.json()
}

export async function getPrinters(): Promise<Record<string, string>> {
  const res = await fetch(`${BASE}/local/printers`)
  if (!res.ok) return {}
  const data = await res.json()
  return data.printers as Record<string, string>
}

export class InvalidCodeError extends Error {
  constructor() {
    super('Invalid or expired code')
  }
}
