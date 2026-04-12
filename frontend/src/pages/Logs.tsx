import { useEffect, useRef, useState } from 'react'
import { useRecentLogs } from '@/api/hooks'
import { Loader2, ArrowDownToLine, Pin } from 'lucide-react'
import { cn } from '@/lib/cn'
import type { LogLine } from '@/api/client'

const LEVEL_COLORS: Record<string, string> = {
  DEBUG:    'text-gray-500',
  INFO:     'text-blue-400',
  SUCCESS:  'text-green-400',
  WARNING:  'text-yellow-400',
  WARN:     'text-yellow-400',
  ERROR:    'text-red-400',
  CRITICAL: 'text-red-500',
}

const LEVEL_BG: Record<string, string> = {
  ERROR:    'bg-red-950/30',
  CRITICAL: 'bg-red-950/40',
  WARNING:  'bg-yellow-950/20',
  WARN:     'bg-yellow-950/20',
}

function levelColor(level: string | null) {
  if (!level) return 'text-gray-400'
  return LEVEL_COLORS[level.toUpperCase()] ?? 'text-gray-400'
}

function rowBg(level: string | null) {
  if (!level) return ''
  return LEVEL_BG[level.toUpperCase()] ?? ''
}

function LogRow({ line }: { line: LogLine }) {
  const bg = rowBg(line.level)
  const color = levelColor(line.level)

  if (!line.timestamp) {
    return (
      <div className="px-3 py-0.5 text-gray-600 font-mono text-xs whitespace-pre-wrap break-all">
        {line.raw || '\u00a0'}
      </div>
    )
  }

  return (
    <div className={cn('flex gap-2 px-3 py-0.5 hover:bg-white/5 font-mono text-xs', bg)}>
      <span className="text-gray-600 shrink-0 select-none">{line.timestamp}</span>
      <span className={cn('w-16 shrink-0 font-semibold', color)}>
        {line.level ?? ''}
      </span>
      <span className="text-gray-300 break-all whitespace-pre-wrap">{line.message}</span>
    </div>
  )
}

export function LogsPage() {
  const [lineCount, setLineCount] = useState(200)
  const [autoScroll, setAutoScroll] = useState(true)
  const [filter, setFilter] = useState('')
  const bottomRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const { data, isLoading, dataUpdatedAt } = useRecentLogs(lineCount)

  const lines = data?.lines ?? []
  const filtered = filter.trim()
    ? lines.filter(l =>
        l.raw.toLowerCase().includes(filter.toLowerCase()) ||
        l.message?.toLowerCase().includes(filter.toLowerCase()),
      )
    : lines

  // Auto-scroll to bottom when new data arrives
  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [dataUpdatedAt, autoScroll])

  function handleScroll() {
    const el = containerRef.current
    if (!el) return
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 40
    if (!atBottom && autoScroll) setAutoScroll(false)
  }

  const lastUpdated = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : null

  return (
    <div className="flex flex-col h-full">
      {/* Header toolbar */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-800 shrink-0 flex-wrap">
        <h1 className="text-lg font-bold text-white">Logs</h1>

        <input
          type="text"
          placeholder="Filter…"
          value={filter}
          onChange={e => setFilter(e.target.value)}
          className="ml-2 px-2 py-1 bg-gray-800 border border-gray-700 rounded text-xs text-gray-200 placeholder-gray-500 focus:outline-none focus:ring-1 focus:ring-blue-500 w-48"
        />

        <div className="flex items-center gap-1 ml-auto">
          {isLoading && <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-400" />}
          {lastUpdated && (
            <span className="text-[10px] text-gray-600 mr-2">updated {lastUpdated}</span>
          )}

          <select
            value={lineCount}
            onChange={e => setLineCount(Number(e.target.value))}
            className="text-xs bg-gray-800 border border-gray-700 text-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value={100}>Last 100 lines</option>
            <option value={200}>Last 200 lines</option>
            <option value={500}>Last 500 lines</option>
            <option value={1000}>Last 1000 lines</option>
          </select>

          <button
            onClick={() => {
              setAutoScroll(v => !v)
              if (!autoScroll && bottomRef.current) {
                bottomRef.current.scrollIntoView({ behavior: 'smooth' })
              }
            }}
            title={autoScroll ? 'Unpin auto-scroll' : 'Pin auto-scroll to bottom'}
            className={cn(
              'ml-1 p-1.5 rounded transition-colors',
              autoScroll
                ? 'bg-blue-600 text-white hover:bg-blue-500'
                : 'bg-gray-700 text-gray-400 hover:bg-gray-600',
            )}
          >
            {autoScroll ? (
              <Pin className="w-3.5 h-3.5" />
            ) : (
              <ArrowDownToLine className="w-3.5 h-3.5" />
            )}
          </button>
        </div>

        {data && (
          <span className="text-[10px] text-gray-600 w-full -mt-1">
            Showing {filtered.length.toLocaleString()} of {data.total_available.toLocaleString()} total log lines
          </span>
        )}
      </div>

      {/* Log output */}
      <div
        ref={containerRef}
        onScroll={handleScroll}
        className="flex-1 overflow-y-auto bg-gray-950 font-mono"
      >
        {isLoading && filtered.length === 0 && (
          <div className="flex items-center justify-center h-24 text-gray-600 text-sm gap-2">
            <Loader2 className="w-4 h-4 animate-spin" />
            Loading logs…
          </div>
        )}

        {!isLoading && filtered.length === 0 && (
          <div className="flex items-center justify-center h-24 text-gray-600 text-sm">
            {filter ? 'No lines match the filter.' : 'No log entries yet.'}
          </div>
        )}

        {filtered.map((line, i) => (
          <LogRow key={i} line={line} />
        ))}
        <div ref={bottomRef} />
      </div>
    </div>
  )
}
