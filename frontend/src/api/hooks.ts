import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, type QueryCreate, type QueryUpdate, type SchedulerStatus, type ItemsEvaluated } from '@/api/client'

export const QUERY_KEYS = {
  queries: (page = 1, pageSize = 20) => ['queries', page, pageSize] as const,
  query: (id: number) => ['query', id] as const,
  snapshots: (queryId?: number, page = 1) => ['snapshots', queryId, page] as const,
  listings: (params: object) => ['listings', params] as const,
  sold: (params: object) => ['sold', params] as const,
  priceTrend: (qid: number, gran: string) => ['priceTrend', qid, gran] as const,
  soldTrend: (qid: number, gran: string) => ['soldTrend', qid, gran] as const,
  summary: (qid: number) => ['summary', qid] as const,
  itemsEvaluated: () => ['itemsEvaluated'] as const,
  schedulerStatus: () => ['schedulerStatus'] as const,
  config: () => ['config'] as const,
  ebayCategorySuggestions: (siteId: string, q: string) => ['ebayCategorySuggestions', siteId, q] as const,
  logsRecent: (lines: number) => ['logsRecent', lines] as const,
}

// ── Queries ────────────────────────────────────────────────────────────────

export function useQueries(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: QUERY_KEYS.queries(page, pageSize),
    queryFn: () => api.queries.list(page, pageSize),
  })
}

export function useQuery_(id: number) {
  return useQuery({
    queryKey: QUERY_KEYS.query(id),
    queryFn: () => api.queries.get(id),
    enabled: id > 0,
  })
}

export function useCreateQuery() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: QueryCreate) => api.queries.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['queries'] })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
    },
  })
}

export function useUpdateQuery() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: QueryUpdate }) =>
      api.queries.update(id, data),
    onSuccess: (_res, { id }) => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.query(id) })
      qc.invalidateQueries({ queryKey: ['queries'] })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
    },
  })
}

export function useDeleteQuery() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.queries.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['queries'] })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
    },
  })
}

export function useRunQueryNow() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.queries.runNow(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['snapshots'] })
      qc.invalidateQueries({ queryKey: ['queries'] })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
    },
  })
}

// ── Snapshots ──────────────────────────────────────────────────────────────

export function useSnapshots(queryId?: number, page = 1) {
  return useQuery({
    queryKey: QUERY_KEYS.snapshots(queryId, page),
    queryFn: () => api.snapshots.list(queryId, page),
    refetchInterval: 15_000, // auto-refresh to pick up running snapshots
  })
}

// ── Listings ───────────────────────────────────────────────────────────────

export function useListings(
  params: Record<string, string | number | boolean | undefined>,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: QUERY_KEYS.listings(params),
    queryFn: () => api.listings.list(params),
    enabled: options?.enabled !== false,
  })
}

export function useItemHistory(itemId: string) {
  return useQuery({
    queryKey: ['itemHistory', itemId],
    queryFn: () => api.listings.itemHistory(itemId),
    enabled: !!itemId,
  })
}

// ── Sold ───────────────────────────────────────────────────────────────────

export function useSold(params: Record<string, string | number | undefined>) {
  return useQuery({
    queryKey: QUERY_KEYS.sold(params),
    queryFn: () => api.sold.list(params),
  })
}

// ── Stats ──────────────────────────────────────────────────────────────────

export function usePriceTrend(queryId: number, granularity = 'week') {
  return useQuery({
    queryKey: QUERY_KEYS.priceTrend(queryId, granularity),
    queryFn: () => api.stats.priceTrend(queryId, granularity),
    enabled: queryId > 0,
  })
}

export function useSoldTrend(queryId: number, granularity = 'week') {
  return useQuery({
    queryKey: QUERY_KEYS.soldTrend(queryId, granularity),
    queryFn: () => api.stats.soldTrend(queryId, granularity),
    enabled: queryId > 0,
  })
}

export function useSummary(queryId: number) {
  return useQuery({
    queryKey: QUERY_KEYS.summary(queryId),
    queryFn: () => api.stats.summary(queryId),
    enabled: queryId > 0,
  })
}

export function useItemsEvaluated() {
  return useQuery({
    queryKey: QUERY_KEYS.itemsEvaluated(),
    queryFn: () => api.stats.itemsEvaluated(),
    refetchInterval: 10_000,
  })
}

// ── Scheduler ─────────────────────────────────────────────────────────────

export function useSchedulerStatus() {
  return useQuery({
    queryKey: QUERY_KEYS.schedulerStatus(),
    queryFn: () => api.scheduler.status(),
    refetchInterval: 5_000,
  })
}

export function usePauseScheduler() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api.scheduler.pause(),
    onMutate: async () => {
      await qc.cancelQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
      const prev = qc.getQueryData<SchedulerStatus>(QUERY_KEYS.schedulerStatus())
      qc.setQueryData<SchedulerStatus>(QUERY_KEYS.schedulerStatus(), old =>
        old ? { ...old, paused: true } : old,
      )
      qc.setQueryData<ItemsEvaluated>(QUERY_KEYS.itemsEvaluated(), old =>
        old ? { ...old, scheduler_running: false } : old,
      )
      return { prev }
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev !== undefined) {
        qc.setQueryData(QUERY_KEYS.schedulerStatus(), ctx.prev)
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.itemsEvaluated() })
    },
  })
}

export function useResumeScheduler() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api.scheduler.resume(),
    onMutate: async () => {
      await qc.cancelQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
      const prev = qc.getQueryData<SchedulerStatus>(QUERY_KEYS.schedulerStatus())
      qc.setQueryData<SchedulerStatus>(QUERY_KEYS.schedulerStatus(), old =>
        old ? { ...old, paused: false } : old,
      )
      qc.setQueryData<ItemsEvaluated>(QUERY_KEYS.itemsEvaluated(), old =>
        old ? { ...old, scheduler_running: true } : old,
      )
      return { prev }
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.prev !== undefined) {
        qc.setQueryData(QUERY_KEYS.schedulerStatus(), ctx.prev)
      }
    },
    onSettled: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.itemsEvaluated() })
    },
  })
}

export function useRunAllNow() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => api.scheduler.runAll(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['snapshots'] })
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
    },
  })
}

// ── Config ─────────────────────────────────────────────────────────────────

export function useAppConfig() {
  return useQuery({
    queryKey: QUERY_KEYS.config(),
    queryFn: () => api.config.get(),
    staleTime: Infinity, // config rarely changes at runtime
  })
}

export function useEbaySites() {
  return useQuery({
    queryKey: ['ebaySites'] as const,
    queryFn: () => api.config.sites(),
    staleTime: Infinity,
  })
}

export function useEbayCategorySuggestions(
  siteId: string,
  query: string,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: QUERY_KEYS.ebayCategorySuggestions(siteId, query),
    queryFn: () => api.config.categorySuggestions(siteId, query),
    enabled: options?.enabled !== false && !!siteId && query.trim().length > 0,
    staleTime: 60_000,
  })
}

export function useUpdateEbaySite() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (site_id: string) => api.config.updateSite(site_id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.config() })
    },
  })
}

export function useUpdateSettings() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: import('@/api/client').SettingsUpdate) => api.config.updateSettings(body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.config() })
    },
  })
}

export function useStopQueryPoll() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: number) => api.queries.stop(id),
    onSettled: () => {
      qc.invalidateQueries({ queryKey: QUERY_KEYS.schedulerStatus() })
      qc.invalidateQueries({ queryKey: ['queries'] })
    },
  })
}

// ── Logs ────────────────────────────────────────────────────────────────────

export function useRecentLogs(lines = 200) {
  return useQuery({
    queryKey: QUERY_KEYS.logsRecent(lines),
    queryFn: () => api.logs.recent(lines),
    refetchInterval: 3_000,
  })
}
