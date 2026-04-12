import { useState } from 'react'
import { useSold } from '@/api/hooks'
import { SoldTable } from '@/components/ui/SoldTable'

interface SoldBrowserProps {
  queryId?: number | null
  embedded?: boolean
}

export function SoldBrowser({ queryId = null, embedded = false }: SoldBrowserProps) {
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useSold({
    query_id: queryId ?? undefined,
    search: search || undefined,
    page,
    page_size: 25,
  })

  return (
    <div className={embedded ? 'space-y-6' : 'max-w-6xl mx-auto space-y-6'}>
      <div className="flex items-center justify-between">
        {embedded ? (
          <h2 className="text-xl font-semibold text-white">Sold Listings</h2>
        ) : (
          <h1 className="text-2xl font-bold text-white">Sold Listings</h1>
        )}
        <span className="text-xs text-gray-500">
          {data ? `${data.total.toLocaleString()} total` : ''}
        </span>
      </div>

      <input
        className="w-full max-w-sm bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
        placeholder="Search sold titles…"
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(1) }}
      />

      <SoldTable records={data?.items ?? []} isLoading={isLoading} />

      {data && data.total > data.page_size && (
        <div className="flex justify-center gap-2">
          <button
            onClick={() => setPage((p) => p - 1)}
            disabled={page === 1}
            className="px-3 py-1.5 text-sm rounded bg-gray-800 text-gray-300 disabled:opacity-40 hover:bg-gray-700"
          >
            ← Prev
          </button>
          <span className="text-xs text-gray-500 self-center">
            Page {page} / {Math.ceil(data.total / data.page_size)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= Math.ceil(data.total / data.page_size)}
            className="px-3 py-1.5 text-sm rounded bg-gray-800 text-gray-300 disabled:opacity-40 hover:bg-gray-700"
          >
            Next →
          </button>
        </div>
      )}
    </div>
  )
}

export function SoldPage() {
  return <SoldBrowser />
}
