import { useState } from 'react'
import { useQueries, usePriceTrend, useSummary } from '@/api/hooks'
import { PriceTrendChart } from '@/components/ui/PriceTrendChart'
import { FullPageSpinner } from '@/components/ui/Throbber'
import { fmtPrice } from '@/lib/format'

const GRAN = ['day', 'week', 'month'] as const
type Granularity = (typeof GRAN)[number]

export function StatsPage() {
  const { data: queriesData, isLoading: loadingQueries } = useQueries(1, 100)
  const [selectedId, setSelectedId] = useState<number>(0)
  const [granularity, setGranularity] = useState<Granularity>('week')

  const queryId = selectedId || queriesData?.items?.[0]?.id || 0

  const { data: priceTrend, isLoading: loadingPrice } = usePriceTrend(queryId, granularity)
  const { data: summary, isLoading: loadingSummary } = useSummary(queryId)

  if (loadingQueries) return <FullPageSpinner />

  const queries = queriesData?.items ?? []

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="flex items-start justify-between flex-wrap gap-4">
        <h1 className="text-2xl font-bold text-white">Stats</h1>

        <div className="flex gap-2 flex-wrap">
          {/* Query selector */}
          <select
            className="bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
            value={queryId}
            onChange={(e) => setSelectedId(parseInt(e.target.value))}
          >
            {queries.map((q) => (
              <option key={q.id} value={q.id}>{q.keyword}</option>
            ))}
          </select>

          {/* Granularity tabs */}
          <div className="flex bg-gray-900 border border-gray-700 rounded-lg overflow-hidden">
            {GRAN.map((g) => (
              <button
                key={g}
                onClick={() => setGranularity(g)}
                className={`px-3 py-2 text-sm transition-colors ${
                  granularity === g
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-white'
                }`}
              >
                {g}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Summary cards */}
      {!loadingSummary && summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <SummaryCard label="Live listings" value={summary.total_live.toLocaleString()} />
          <SummaryCard label="Sold records" value={summary.total_sold.toLocaleString()} />
          <SummaryCard label="Avg live price" value={fmtPrice(summary.avg_live_price)} accent="blue" />
          <SummaryCard label="Median sold" value={fmtPrice(summary.median_sold_price)} accent="amber" />
        </div>
      )}

      {/* Price trend chart */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
        <h2 className="text-sm font-semibold text-gray-300 mb-4">Live Price Trend</h2>
        <PriceTrendChart data={priceTrend ?? []} isLoading={loadingPrice} />
      </div>
    </div>
  )
}

function SummaryCard({
  label,
  value,
  accent = 'white',
}: {
  label: string
  value: string
  accent?: 'white' | 'blue' | 'amber'
}) {
  const colour = { white: 'text-white', blue: 'text-blue-400', amber: 'text-amber-400' }[accent]
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className={`text-xl font-bold mt-1 ${colour}`}>{value}</p>
    </div>
  )
}
