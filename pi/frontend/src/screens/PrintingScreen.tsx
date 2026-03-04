import { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import PrinterAnimation from '../components/PrinterAnimation'
import { getJobStatus } from '../api/piBackend'

interface Props {
  jobId: string
  printerType: string
  onDone: () => void
  onError: (msg: string) => void
}

export default function PrintingScreen({ jobId, printerType, onDone, onError }: Props) {
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const label = printerType === 'COLOR_PHOTO' ? 'photo' : 'document'

  useEffect(() => {
    intervalRef.current = setInterval(async () => {
      try {
        const status = await getJobStatus(jobId)
        if (status.status === 'DONE') {
          clearInterval(intervalRef.current!)
          onDone()
        } else if (status.status === 'FAILED') {
          clearInterval(intervalRef.current!)
          onError(`Printing failed. Please collect your receipt and contact staff.`)
        }
      } catch {
        // transient — keep polling
      }
    }, 2000)

    return () => clearInterval(intervalRef.current!)
  }, [jobId, onDone, onError])

  return (
    <motion.div
      key="printing"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
      className="w-full h-full flex flex-col items-center justify-center gap-8 bg-surface"
    >
      <PrinterAnimation />

      <motion.p
        className="text-kiosk-xl font-bold text-slate-100 text-center px-8"
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ repeat: Infinity, duration: 2, ease: 'easeInOut' }}
      >
        Printing your {label}…
      </motion.p>

      <p className="text-kiosk-md text-slate-500 text-center px-8">
        Please wait — collect your print from the tray
      </p>
    </motion.div>
  )
}
