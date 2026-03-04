import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'

const WORDS = ['SELF', 'SECURE', 'FAST']
const INTERVAL_MS = 2500

export default function SlideShow() {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const id = setInterval(() => setIndex(i => (i + 1) % WORDS.length), INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  return (
    <div className="flex flex-col items-center leading-none select-none">
      {/* Row 1 — cycling word */}
      <div className="relative flex items-center justify-center" style={{ minHeight: '1.1em' }}>
        <AnimatePresence mode="wait">
          <motion.span
            key={WORDS[index]}
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.45, ease: 'easeInOut' }}
            className="text-hero font-black tracking-tight text-accent"
            style={{ lineHeight: 1 }}
          >
            {WORDS[index]}
          </motion.span>
        </AnimatePresence>
      </div>

      {/* Row 2 — always "Print" */}
      <span
        className="text-hero font-black tracking-tight text-slate-100"
        style={{ lineHeight: 1 }}
      >
        Print
      </span>
    </div>
  )
}
