import { useDeferredValue, useState } from 'react'
import { Plus, X } from 'lucide-react'
import {
  useQueries,
  useCreateQuery,
  useDeleteQuery,
  useRunQueryNow,
  useSchedulerStatus,
  useStopQueryPoll,
  useUpdateQuery,
  useEbayCategorySuggestions,
  useEbaySites,
} from '@/api/hooks'
import { QueryCard } from '@/components/ui/QueryCard'
import { FullPageSpinner } from '@/components/ui/Throbber'
import type { SearchQuery, QueryCreate } from '@/api/client'

interface QueriesPageProps {
  onOpenQuery?: (queryId: number) => void
}

export function QueriesPage({ onOpenQuery }: QueriesPageProps) {
  const [page, _setPage] = useState(1)
  const { data, isLoading } = useQueries(page)
  const { data: sites } = useEbaySites()
  const { data: schedulerStatus } = useSchedulerStatus()
  const createMutation = useCreateQuery()
  const deleteMutation = useDeleteQuery()
  const runMutation = useRunQueryNow()
  const stopMutation = useStopQueryPoll()
  const updateMutation = useUpdateQuery()

  const [showForm, setShowForm] = useState(false)
  const [editTarget, setEditTarget] = useState<SearchQuery | null>(null)
  const defaultForm: QueryCreate = {
    keyword: '',
    category_id: null,
    site_id: 'EBAY-DE',
    enabled: true,
    include_sold: false,
  }
  const [form, setForm] = useState<QueryCreate>(defaultForm)
  const [error, setError] = useState<string | null>(null)
  const [runningIds, setRunningIds] = useState<Set<number>>(new Set())
  const [stoppedIds, setStoppedIds] = useState<Set<number>>(new Set())
  const [pageError, setPageError] = useState<string | null>(null)
  const deferredKeyword = useDeferredValue(form.keyword ?? '')
  const categorySearch = deferredKeyword.trim()
  const canSuggestCategories = categorySearch.length >= 2 && !!form.site_id
  const { data: categorySuggestionData, isLoading: categoryLoading } = useEbayCategorySuggestions(
    form.site_id ?? 'EBAY-DE',
    categorySearch,
    { enabled: canSuggestCategories },
  )
  const categorySuggestions = categorySuggestionData?.items ?? []
  const selectedCategoryMissing = !!form.category_id && !categorySuggestions.some(
    (category) => category.category_id === form.category_id,
  )
  const pollingIds = new Set(
    [...(schedulerStatus?.running_query_ids ?? []), ...runningIds].filter(
      (id) => !stoppedIds.has(id),
    ),
  )

  const handleSubmit = async () => {
    setError(null)
    if (!form.keyword.trim()) {
      setError('Keyword is required.')
      return
    }
    try {
      if (editTarget) {
        await updateMutation.mutateAsync({ id: editTarget.id, data: form })
      } else {
        await createMutation.mutateAsync(form)
      }
      setShowForm(false)
      setEditTarget(null)
      setForm(defaultForm)
    } catch (e: unknown) {
      setError((e as Error).message ?? 'Failed to save query')
    }
  }

  const handleRunNow = async (id: number) => {
    setPageError(null)
    setRunningIds((prev) => new Set(prev).add(id))
    try {
      await runMutation.mutateAsync(id)
    } catch (e: unknown) {
      setPageError((e as Error).message ?? 'Failed to start query poll')
    } finally {
      setRunningIds((prev) => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const handleStopPoll = (id: number) => {
    setPageError(null)
    setStoppedIds((prev) => new Set(prev).add(id))
    stopMutation.mutate(id, {
      onSuccess: () => {
        setStoppedIds((prev) => {
          const next = new Set(prev)
          next.delete(id)
          return next
        })
      },
      onError: (err) => {
        setStoppedIds((prev) => {
          const next = new Set(prev)
          next.delete(id)
          return next
        })
        setPageError(err instanceof Error ? err.message : 'Failed to stop query poll')
      },
    })
  }

  const handleToggleEnabled = (id: number, enabled: boolean) => {
    setPageError(null)
    updateMutation.mutate(
      { id, data: { enabled } },
      {
        onError: (err) => {
          setPageError(err instanceof Error ? err.message : 'Failed to update query')
        },
      },
    )
  }

  if (isLoading) return <FullPageSpinner />

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {pageError && (
        <div className="flex items-center justify-between gap-3 bg-red-900/40 border border-red-700/60 text-red-300 text-sm rounded-lg px-4 py-3">
          <span>{pageError}</span>
          <button onClick={() => setPageError(null)} className="text-red-400 hover:text-red-200 shrink-0">✕</button>
        </div>
      )}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Queries</h1>
        <button
          onClick={() => { setShowForm(true); setEditTarget(null); setForm(defaultForm) }}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Query
        </button>
      </div>

      {/* Inline form */}
      {showForm && (
        <div className="bg-gray-900 border border-gray-700 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between mb-1">
            <h2 className="text-sm font-semibold text-white">{editTarget ? 'Edit Query' : 'New Query'}</h2>
            <button onClick={() => setShowForm(false)} className="text-gray-500 hover:text-gray-300">
              <X className="w-4 h-4" />
            </button>
          </div>
          {error && <p className="text-red-400 text-xs">{error}</p>}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <label className="flex flex-col gap-1">
              <span className="text-xs text-gray-400">Search query *</span>
              <input
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                value={form.keyword}
                onChange={(e) => setForm((f) => ({ ...f, keyword: e.target.value, category_id: null }))}
                placeholder="nintendo switch"
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs text-gray-400">Site ID</span>
              <select
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                value={form.site_id ?? 'EBAY-DE'}
                onChange={(e) => setForm((f) => ({ ...f, site_id: e.target.value, category_id: null }))}
              >
                {sites?.map((s) => (
                  <option key={s.id} value={s.id}>
                    {s.name} ({s.id})
                  </option>
                ))}
                {!sites && <option value={form.site_id ?? 'EBAY-DE'}>{form.site_id ?? 'EBAY-DE'}</option>}
              </select>
            </label>
            <label className="flex flex-col gap-1 sm:col-span-2">
              <span className="text-xs text-gray-400">Category</span>
              <select
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-60"
                value={form.category_id ?? ''}
                disabled={!canSuggestCategories}
                onChange={(e) => setForm((f) => ({
                  ...f,
                  category_id: e.target.value ? e.target.value : null,
                }))}
              >
                <option value="">All categories</option>
                {selectedCategoryMissing && form.category_id && (
                  <option value={form.category_id}>Saved category ({form.category_id})</option>
                )}
                {categorySuggestions.map((category) => (
                  <option key={category.category_id} value={category.category_id}>
                    {category.category_path}
                  </option>
                ))}
              </select>
              <span className="text-[11px] text-gray-500">
                {!canSuggestCategories
                  ? 'Type at least 2 characters to load eBay category suggestions.'
                  : categoryLoading
                    ? 'Loading category suggestions from eBay...'
                    : categorySuggestions.length > 0
                      ? 'Optional category filter for this search query.'
                      : 'No category suggestions found for the current query.'}
              </span>
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs text-gray-400">Min Price</span>
              <input
                type="number"
                min="0"
                step="0.01"
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                value={form.min_price ?? ''}
                onChange={(e) => setForm((f) => ({ ...f, min_price: e.target.value ? parseFloat(e.target.value) : null }))}
                placeholder="e.g., 50.00"
              />
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs text-gray-400">Max Price</span>
              <input
                type="number"
                min="0"
                step="0.01"
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                value={form.max_price ?? ''}
                onChange={(e) => setForm((f) => ({ ...f, max_price: e.target.value ? parseFloat(e.target.value) : null }))}
                placeholder="e.g., 300.00"
              />
              {!form.min_price && !form.max_price && (
                <span className="text-[11px] text-yellow-500 mt-1">
                  ⚠️ Warning: Without a price range, this query may consume a large number of eBay API requests.
                </span>
              )}
            </label>
            <label className="flex flex-col gap-1">
              <span className="text-xs text-gray-400">Interval (minutes)</span>
              <input
                type="number"
                min={5}
                max={10080}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
                value={form.interval_minutes ?? 60}
                onChange={(e) => setForm((f) => ({ ...f, interval_minutes: parseInt(e.target.value) || 60 }))}
              />
            </label>
          </div>

          <div className="flex gap-2 justify-end">
            <button
              onClick={() => setShowForm(false)}
              className="px-4 py-2 text-sm text-gray-400 hover:text-white transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSubmit}
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium disabled:opacity-50 transition-colors"
            >
              {editTarget ? 'Save' : 'Create'}
            </button>
          </div>
        </div>
      )}

      {/* Query cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {(data?.items ?? []).map((q) => (
          <QueryCard
            key={q.id}
            query={q}
            onOpen={(query) => onOpenQuery?.(query.id)}
            running={runningIds.has(q.id)}
            polling={pollingIds.has(q.id)}
            onRunNow={handleRunNow}
            onStopPoll={handleStopPoll}
            onToggleEnabled={handleToggleEnabled}
            onEdit={(query) => {
              setEditTarget(query)
              setForm({
                keyword: query.keyword,
                category_id: query.category_id,
                site_id: query.site_id,
                interval_minutes: query.interval_minutes,
                enabled: query.enabled,
                include_sold: query.include_sold,
              })
              setShowForm(true)
            }}
            deleting={deleteMutation.isPending && deleteMutation.variables === q.id}
            onDelete={(id) => deleteMutation.mutate(id, {
              onError: (err) => setPageError(err instanceof Error ? err.message : 'Failed to delete query'),
            })}
          />
        ))}
      </div>

      {data?.total === 0 && (
        <p className="text-gray-500 text-sm text-center py-8">No queries yet. Create one above.</p>
      )}
    </div>
  )
}
