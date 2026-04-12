import { useQueries, useItemsEvaluated, useSchedulerStatus } from '@/api/hooks'
import { FullPageSpinner } from '@/components/ui/Throbber'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { fmtDatetime } from '@/lib/format'

interface DashboardProps {
  onOpenQuery?: (queryId: number) => void
}

export function Dashboard({ onOpenQuery }: DashboardProps) {
  const { data: queriesData, isLoading: loadingQueries } = useQueries(1, 5)
  const { data: evaluated } = useItemsEvaluated()
  const { data: schedulerStatus } = useSchedulerStatus()

  if (loadingQueries) return <FullPageSpinner />

  const queries = queriesData?.items ?? []

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-white">Dashboard</h1>
        <p className="text-gray-400 text-sm mt-1">Overview of your eBay market intelligence platform</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard
          label="Unique Items Evaluated"
          value={evaluated?.total.toLocaleString() ?? '…'}
          sub={evaluated?.since ? `Since ${fmtDatetime(evaluated.since)}` : undefined}
        />
        <StatCard
          label="Total Queries"
          value={queriesData?.total?.toString() ?? '…'}
          sub={`${queries.filter((q) => q.enabled).length} enabled`}
        />
        <StatCard
          label="Scheduler"
          value={
            schedulerStatus
              ? schedulerStatus.paused
                ? 'Paused'
                : schedulerStatus.running
                  ? 'Running'
                  : 'Idle'
              : '…'
          }
          sub={schedulerStatus
            ? schedulerStatus.active_schedules > 0
              ? `${schedulerStatus.active_schedules} scheduled`
              : 'No active queries'
            : undefined}
          accent={schedulerStatus?.running && !schedulerStatus.paused ? 'green' : 'gray'}
        />
      </div>

      {/* Recent queries */}
      <div>
        <h2 className="text-lg font-semibold text-white mb-3">Recent Queries</h2>
        <div className="space-y-2">
          {queries.length === 0 && (
            <p className="text-gray-500 text-sm">No queries yet. Go to Queries to add one.</p>
          )}
          {queries.map((q) => (
            <div
              key={q.id}
              role="button"
              tabIndex={0}
              onClick={() => onOpenQuery?.(q.id)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault()
                  onOpenQuery?.(q.id)
                }
              }}
              className="flex items-center justify-between bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 cursor-pointer transition-colors hover:border-blue-500/40"
            >
              <div>
                <p className="text-sm font-medium text-white">{q.keyword}</p>
                <p className="text-xs text-gray-500">{q.site_id}{q.category_id ? ` • Category ${q.category_id}` : ''}</p>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs text-gray-500">{fmtDatetime(q.last_polled_at)}</span>
                <StatusBadge status={q.enabled ? 'enabled' : 'disabled'} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  label,
  value,
  sub,
  accent = 'blue',
}: {
  label: string
  value: string
  sub?: string
  accent?: 'blue' | 'green' | 'gray'
}) {
  const accent_colour = {
    blue:  'text-blue-400',
    green: 'text-green-400',
    gray:  'text-gray-400',
  }[accent]

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${accent_colour}`}>{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
    </div>
  )
}
