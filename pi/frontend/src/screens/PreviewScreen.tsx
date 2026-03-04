import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { confirmPrint, getJobStatus } from '../api/piBackend'
import type { StartPrintResponse } from '../api/piBackend'

interface Props {
  job: StartPrintResponse
  onConfirm: () => void
  onError: (msg: string) => void
}

const FILE_ICONS: Record<string, string> = {
  pdf:  '📄',
  docx: '📝',
  xlsx: '📊',
  pptx: '📑',
  ppt:  '📑',
  jpg:  '🖼️',
  jpeg: '🖼️',
  png:  '🖼️',
}

const PRINTER_LABEL: Record<string, string> = {
  COLOR_PHOTO:     'Color Photo Printer',
  LASER_DOCUMENT:  'Laser Document Printer',
}

export default function PreviewScreen({ job, onConfirm, onError }: Props) {
  const [ready, setReady] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Poll until status = READY (download + convert done)
  useEffect(() => {
    intervalRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(job.job_id)
        if (status.status === 'READY') {
          clearInterval(intervalRef.current!)
          setReady(true)
        } else if (status.status === 'FAILED') {
          clearInterval(intervalRef.current!)
          onError('Failed to prepare your file. Please try again or contact staff.')
        }
      } catch {
        // transient network error — keep polling
      }
    }, 2000)

    return () => clearInterval(intervalRef.current!)
  }, [job.job_id, onError])

  const handleConfirm = async () => {
    setConfirming(true)
    try {
      await confirmPrint(job.job_id)
      onConfirm()
    } catch {
      onError('Failed to start printing. Please contact staff.')
    }
  }

  const icon = FILE_ICONS[job.file_type?.toLowerCase() ?? ''] ?? '📄'
  const printerLabel = PRINTER_LABEL[job.printer_type] ?? job.printer_type

  return (
    <motion.div
      key="preview"
      initial={{ opacity: 0, x: 60 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -60 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className="w-full h-full flex flex-col bg-surface"
    >
      {/* Header */}
      <div className="px-8 pt-6 pb-2">
        <h1 className="text-center text-kiosk-xl font-bold text-slate-100">Your Print Job</h1>
        <p className="text-center text-kiosk-sm text-slate-400 mt-1">
          {ready ? 'Ready to print!' : 'Preparing your file…'}
        </p>
      </div>

      {/* File card */}
      <div className="flex-1 flex flex-col items-center justify-center px-10 gap-6">
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.1 }}
          className="w-full max-w-xl bg-surface-card rounded-3xl p-8 shadow-xl border border-slate-700/50"
        >
          {/* File icon + name */}
          <div className="flex items-center gap-5 mb-6">
            <span className="text-[3.5rem]">{icon}</span>
            <div className="flex-1 min-w-0">
              <p className="text-kiosk-md font-bold text-slate-100 truncate">
                {job.original_filename}
              </p>
              <p className="text-kiosk-sm text-slate-400 uppercase tracking-wide mt-1">
                {job.file_type?.toUpperCase()}
              </p>
            </div>
          </div>

          {/* Divider */}
          <div className="h-px bg-slate-700 mb-6" />

          {/* Print options */}
          <div className="grid grid-cols-2 gap-4">
            <InfoRow label="Copies" value={String(job.options?.copies ?? 1)} />
            <InfoRow label="Paper"  value={job.options?.paper_size ?? 'A4'} />
            <InfoRow label="Color"  value={job.options?.color ? 'Color' : 'Black & White'} />
            <InfoRow label="Printer" value={printerLabel} />
          </div>
        </motion.div>

        {/* Status / button */}
        {!ready ? (
          <div className="flex items-center gap-4 text-kiosk-md text-slate-400">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}
              className="w-8 h-8 border-4 border-slate-600 border-t-accent rounded-full"
            />
            Downloading your file…
          </div>
        ) : (
          <motion.button
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            whileTap={{ scale: 0.96 }}
            onClick={handleConfirm}
            disabled={confirming}
            className="
              w-full max-w-xl
              bg-accent hover:bg-accent-hover
              text-slate-950 font-black
              text-kiosk-lg py-6 rounded-2xl
              transition-all duration-150
              shadow-lg shadow-accent/30
              touch-target
            "
          >
            {confirming ? 'Starting…' : 'Print Now →'}
          </motion.button>
        )}
      </div>
    </motion.div>
  )
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface rounded-xl px-5 py-4">
      <p className="text-kiosk-sm text-slate-500 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-kiosk-md font-bold text-slate-100 truncate">{value}</p>
    </div>
  )
}
