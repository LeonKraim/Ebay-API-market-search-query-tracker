import { Play, Pencil, Trash2, Loader2, Square } from 'lucide-react'
import { type SearchQuery } from '@/api/client'
import { fmtDatetime } from '@/lib/format'

interface QueryCardProps {
  query: SearchQuery
  onRunNow?: (id: number) => void
  onStopPoll?: (id: number) => void
  onEdit?: (query: SearchQuery) => void
  onDelete?: (id: number) => void
  onOpen?: (query: SearchQuery) => void
  onToggleEnabled?: (id: number, enabled: boolean) => void
  running?: boolean
  polling?: boolean
  deleting?: boolean
}

export function QueryCard({
  query,
  onRunNow,
  onStopPoll,
  onEdit,
  onDelete,
  onOpen,
  onToggleEnabled,
  running,
  polling,
  deleting,
}: QueryCardProps) {
  return (
    <div
      role="button"
      tabIndex={0}
      onClick={() => onOpen?.(query)}
      onKeyDown={(event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault()
          onOpen?.(query)
        }
      }}
      className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex flex-col gap-3 cursor-pointer transition-colors hover:border-blue-500/40"
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className="font-semibold text-white truncate">{query.keyword}</p>
          <p className="text-xs text-gray-400 mt-0.5 truncate">
            {query.site_id}
            {query.category_id ? ` • Category ${query.category_id}` : ' • All categories'}
          </p>
        </div>
        <label
          className="flex items-center gap-1.5 cursor-pointer select-none shrink-0"
          onClick={(e) => e.stopPropagation()}
        >
          <input
            type="checkbox"
            checked={query.enabled}
            onChange={(e) => {
              e.stopPropagation()
              onToggleEnabled?.(query.id, e.target.checked)
            }}
            className="w-4 h-4 rounded accent-blue-500 cursor-pointer"
          />
          <span className={`text-xs font-medium ${query.enabled ? 'text-green-400' : 'text-gray-500'}`}>
            {query.enabled ? 'Enabled' : 'Disabled'}
          </span>
        </label>
      </div>

      <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs text-gray-400">
        <span>Site: <span className="text-gray-200">{query.site_id}</span></span>
        <span>Interval: <span className="text-gray-200">{query.interval_minutes}m</span></span>
        <span>Snapshots: <span className="text-gray-200">{query.total_snapshots}</span></span>
        <span className="col-span-2">
          Last polled: <span className="text-gray-200">{fmtDatetime(query.last_polled_at)}</span>
        </span>
      </div>

      <div className="flex gap-2 pt-1">
        {polling ? (
          <button
            onClick={(event) => {
              event.stopPropagation()
              onStopPoll?.(query.id)
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-amber-500/20 hover:bg-amber-500/35 text-amber-200 transition-colors"
          >
            <Square className="w-3 h-3" />
            Stop
          </button>
        ) : (
          <button
            onClick={(event) => {
              event.stopPropagation()
              onRunNow?.(query.id)
            }}
            disabled={running}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 transition-colors"
          >
            <Play className="w-3 h-3" />
            Run now
          </button>
        )}
        <button
          onClick={(event) => {
            event.stopPropagation()
            onEdit?.(query)
          }}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-700 hover:bg-gray-600 text-gray-200 transition-colors"
        >
          <Pencil className="w-3 h-3" />
          Edit
        </button>
        <button
          onClick={(event) => {
            event.stopPropagation()
            onDelete?.(query.id)
          }}
          disabled={deleting}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-red-600/20 hover:bg-red-600/40 text-red-300 transition-colors ml-auto disabled:opacity-50"
        >
          {deleting ? (
            <Loader2 className="w-3 h-3 animate-spin" />
          ) : (
            <Trash2 className="w-3 h-3" />
          )}
        </button>
      </div>
    </div>
  )
}
