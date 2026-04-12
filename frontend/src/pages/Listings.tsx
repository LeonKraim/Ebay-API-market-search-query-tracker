import { useEffect, useMemo, useState } from 'react'
import { ChevronRight, ChevronDown, LayoutGrid, List } from 'lucide-react'
import { useQueries, useListings } from '@/api/hooks'
import { ListingTable } from '@/components/ui/ListingTable'
import { Throbber } from '@/components/ui/Throbber'
import type { SearchQuery } from '@/api/client'
import type { MarketMode } from '@/App'
import { SoldBrowser } from '@/pages/Sold'

type ListingsViewMode = 'list' | 'grid'

interface ListingsPageProps {
  marketMode: MarketMode
  selectedQueryId: number | null
  onMarketModeChange: (mode: MarketMode) => void
}

export function ListingsPage({ marketMode, selectedQueryId, onMarketModeChange }: ListingsPageProps) {
  const { data: queriesData, isLoading: queriesLoading } = useQueries(1, 100)
  const queries = queriesData?.items ?? []
  const [viewMode, setViewMode] = useState<ListingsViewMode>('list')
  const orderedQueries = useMemo(() => {
    if (!selectedQueryId) {
      return queries
    }

    const selectedQuery = queries.find((query) => query.id === selectedQueryId)
    if (!selectedQuery) {
      return queries
    }

    return [selectedQuery, ...queries.filter((query) => query.id !== selectedQueryId)]
  }, [queries, selectedQueryId])

  if (queriesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Throbber size={28} />
      </div>
    )
  }

  if (!queries.length) {
    return (
      <div className="max-w-6xl mx-auto">
        <h1 className="text-2xl font-bold text-white mb-6">Listings</h1>
        <p className="text-gray-500 text-sm">No queries yet. Create a query to start tracking listings.</p>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-4">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-2xl font-bold text-white">Listings</h1>
          <p className="text-sm text-gray-500 mt-1">
            Browse live and sold results in one place.
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          <div className="inline-flex items-center rounded-xl border border-gray-700 bg-gray-900 p-1">
            <button
              onClick={() => onMarketModeChange('live')}
              className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                marketMode === 'live' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Live
            </button>
            <button
              onClick={() => onMarketModeChange('sold')}
              className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                marketMode === 'sold' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
              }`}
            >
              Sold
            </button>
          </div>
          {marketMode === 'live' && (
            <div className="inline-flex items-center rounded-xl border border-gray-700 bg-gray-900 p-1">
              <button
                onClick={() => setViewMode('list')}
                className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                  viewMode === 'list' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <List className="w-4 h-4" />
                List
              </button>
              <button
                onClick={() => setViewMode('grid')}
                className={`inline-flex items-center gap-2 rounded-lg px-3 py-2 text-sm transition-colors ${
                  viewMode === 'grid' ? 'bg-blue-600 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <LayoutGrid className="w-4 h-4" />
                Grid
              </button>
            </div>
          )}
        </div>
      </div>
      {marketMode === 'live' ? (
        orderedQueries.map((query) => (
          <QueryGroup
            key={query.id}
            query={query}
            viewMode={viewMode}
            selected={query.id === selectedQueryId}
          />
        ))
      ) : (
        <SoldBrowser embedded queryId={selectedQueryId} />
      )}
    </div>
  )
}

function QueryGroup({
  query,
  viewMode,
  selected,
}: {
  query: SearchQuery
  viewMode: ListingsViewMode
  selected: boolean
}) {
  const [expanded, setExpanded] = useState(selected)
  const [page, setPage] = useState(1)

  const { data, isLoading } = useListings(
    { query_id: query.id, page, page_size: 25 },
    { enabled: expanded },
  )

  const total = data?.total ?? 0
  const lastPage = data ? Math.ceil(data.total / data.page_size) : 1

  useEffect(() => {
    if (selected) {
      setExpanded(true)
      setPage(1)
    }
  }, [selected])

  return (
    <div className={`border rounded-xl overflow-hidden ${selected ? 'border-blue-500/40' : 'border-gray-700'}`}>
      <button
        className={`w-full flex items-center justify-between px-4 py-3 text-left transition-colors ${selected ? 'bg-blue-950/20 hover:bg-blue-950/30' : 'bg-gray-800 hover:bg-gray-750'}`}
        onClick={() => {
          setExpanded((e) => !e)
          setPage(1)
        }}
      >
        <div className="flex items-center gap-3 min-w-0">
          {expanded ? (
            <ChevronDown className="w-4 h-4 text-gray-400 flex-shrink-0" />
          ) : (
            <ChevronRight className="w-4 h-4 text-gray-400 flex-shrink-0" />
          )}
          <div className="min-w-0">
            <span className="block font-medium text-white truncate">{query.keyword}</span>
            <span className="block text-xs text-gray-500 truncate">
              {query.site_id}
              {query.category_id ? ` • Category ${query.category_id}` : ' • All categories'}
            </span>
          </div>
        </div>
        {expanded && total > 0 && (
          <span className="text-xs text-gray-500 flex-shrink-0 ml-2">
            {total.toLocaleString()} listings
          </span>
        )}
      </button>

      {expanded && (
        <div className="bg-gray-900">
          <ListingTable listings={data?.items ?? []} isLoading={isLoading} variant={viewMode} />
          {data && data.total > data.page_size && (
            <div className="flex items-center justify-center gap-2 py-3 border-t border-gray-800">
              <button
                onClick={() => setPage((p) => p - 1)}
                disabled={page === 1}
                className="px-3 py-1.5 text-sm rounded bg-gray-800 hover:bg-gray-700 text-gray-300 disabled:opacity-40"
              >
                ← Prev
              </button>
              <span className="text-xs text-gray-500">
                Page {page} / {lastPage}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= lastPage}
                className="px-3 py-1.5 text-sm rounded bg-gray-800 hover:bg-gray-700 text-gray-300 disabled:opacity-40"
              >
                Next →
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
