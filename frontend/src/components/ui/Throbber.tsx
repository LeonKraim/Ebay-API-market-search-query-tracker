import { Loader2 } from 'lucide-react'

interface ThrobberProps {
  size?: number
  className?: string
}

export function Throbber({ size = 16, className = '' }: ThrobberProps) {
  return (
    <Loader2
      className={`animate-spin text-blue-400 ${className}`}
      style={{ width: size, height: size }}
    />
  )
}

export function FullPageSpinner() {
  return (
    <div className="flex items-center justify-center h-full w-full min-h-[200px]">
      <Throbber size={32} />
    </div>
  )
}
