import { motion } from 'framer-motion'

// Allowed characters: A-F and 0-9 (code is always 6 chars, hex-like)
const ALPHA_KEYS = ['A', 'B', 'C', 'D', 'E', 'F']
const NUM_KEYS   = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
const CODE_LENGTH = 6

interface Props {
  value: string
  onChange: (val: string) => void
  shaking: boolean
  errorMsg: string
}

export default function CodeKeypad({ value, onChange, shaking, errorMsg }: Props) {
  const append = (ch: string) => {
    if (value.length < CODE_LENGTH) onChange(value + ch)
  }
  const del = () => onChange(value.slice(0, -1))
  const clear = () => onChange('')

  return (
    <div className="flex flex-col items-center gap-5 w-full max-w-lg mx-auto">
      {/* Code display — 6 boxes */}
      <motion.div
        animate={shaking ? { x: [0, -12, 12, -8, 8, 0] } : {}}
        transition={{ duration: 0.45 }}
        className="flex gap-3"
      >
        {Array.from({ length: CODE_LENGTH }).map((_, i) => (
          <div
            key={i}
            className={`
              w-16 h-20 rounded-xl flex items-center justify-center
              text-kiosk-xl font-black tracking-widest
              border-2 transition-colors duration-200
              ${i < value.length
                ? 'border-accent bg-surface-card text-accent'
                : 'border-slate-700 bg-surface-card text-slate-600'}
            `}
          >
            {value[i] ?? ''}
          </div>
        ))}
      </motion.div>

      {/* Error message */}
      <div className="h-8 flex items-center">
        {errorMsg && (
          <motion.p
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-kiosk-sm text-red-400 font-semibold"
          >
            {errorMsg}
          </motion.p>
        )}
      </div>

      {/* Letter keys: A B C / D E F */}
      <div className="flex flex-col gap-3 w-full">
        <div className="flex gap-3 justify-center">
          {ALPHA_KEYS.slice(0, 3).map(k => <Key key={k} label={k} onPress={append} />)}
        </div>
        <div className="flex gap-3 justify-center">
          {ALPHA_KEYS.slice(3).map(k => <Key key={k} label={k} onPress={append} />)}
        </div>

        {/* Divider */}
        <div className="h-px bg-slate-700 my-1" />

        {/* Number keys: 1–9 + 0 centred */}
        {[0, 3, 6].map(start => (
          <div key={start} className="flex gap-3 justify-center">
            {NUM_KEYS.slice(start, start + 3).map(k => <Key key={k} label={k} onPress={append} />)}
          </div>
        ))}
        <div className="flex gap-3 justify-center">
          <Key label="0" onPress={append} wide />
        </div>

        {/* Delete / Clear */}
        <div className="flex gap-3 justify-center mt-1">
          <Key label="⌫" onPress={del} accent />
          <Key label="✕ Clear" onPress={clear} accent wide />
        </div>
      </div>
    </div>
  )
}

function Key({
  label,
  onPress,
  accent = false,
  wide = false,
}: {
  label: string
  onPress: (v: string) => void
  accent?: boolean
  wide?: boolean
}) {
  return (
    <motion.button
      whileTap={{ scale: 0.88 }}
      onClick={() => onPress(label)}
      className={`
        ${wide ? 'w-40' : 'w-[4.5rem]'} h-16 rounded-xl
        text-kiosk-md font-bold
        transition-colors duration-100
        touch-target
        ${accent
          ? 'bg-slate-700 hover:bg-slate-600 text-slate-200'
          : 'bg-surface-raised hover:bg-slate-600 text-slate-100 active:bg-accent active:text-slate-950'}
      `}
    >
      {label}
    </motion.button>
  )
}
