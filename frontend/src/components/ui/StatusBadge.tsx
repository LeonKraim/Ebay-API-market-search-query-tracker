import { cn } from '@/lib/cn'

type Status = 'running' | 'complete' | 'error' | 'enabled' | 'disabled' | string

const COLOUR: Record<string, string> = {
  idle:     'bg-slate-500/20 text-slate-300 border-slate-500/40',
  running:  'bg-blue-500/20 text-blue-300 border-blue-500/40',
  complete: 'bg-green-500/20 text-green-300 border-green-500/40',
  error:    'bg-red-500/20 text-red-300 border-red-500/40',
  enabled:  'bg-green-500/20 text-green-300 border-green-500/40',
  disabled: 'bg-gray-500/20 text-gray-400 border-gray-600/40',
}

interface StatusBadgeProps {
  status: Status
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const colour = COLOUR[status] ?? 'bg-gray-500/20 text-gray-400 border-gray-600/40'
  return (
    <span
      className={cn(
        'inline-flex items-center px-2 py-0.5 text-xs font-medium rounded border',
        colour,
        className,
      )}
    >
      {status === 'running' && (
        <span className="mr-1.5 inline-block w-1.5 h-1.5 rounded-full bg-blue-400 animate-pulse" />
      )}
      {status}
    </span>
  )
}
