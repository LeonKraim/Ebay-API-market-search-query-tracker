/**
 * Typed API client that wraps fetch with NProgress integration,
 * consistent error handling, and request logging.
 */
import NProgress from 'nprogress'
import { logger } from '@/lib/logger'

const BASE = '/api/v1'

// ── Types ──────────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface SearchQuery {
  id: number
  name: string
  keyword: string
  category_id: string | null
  site_id: string
  min_price: number | null
  max_price: number | null
  interval_minutes: number
  enabled: boolean
  include_sold: boolean
  created_at: string
  last_polled_at: string | null
  total_snapshots: number
}

export interface QueryCreate {
  name?: string
  keyword: string
  category_id?: string | null
  site_id?: string
  min_price?: number | null
  max_price?: number | null
  interval_minutes?: number
  enabled?: boolean
  include_sold?: boolean
}

export interface QueryUpdate extends Partial<QueryCreate> {}

export interface Snapshot {
  id: number
  query_id: number
  started_at: string
  finished_at: string | null
  items_found: number
  items_new: number
  items_updated: number
  status: 'running' | 'complete' | 'error'
  error_message: string | null
}

export interface ListingRecord {
  id: number
  snapshot_id: number
  query_id: number
  item_id: string
  title: string
  image_url: string | null
  current_price: string | null
  currency: string | null
  buy_it_now: boolean
  listing_type: string | null
  watch_count: number | null
  bid_count: number | null
  selling_state: string | null
  country: string | null
  end_time: string | null
  item_url: string | null
  gallery_url: string | null
  first_seen_at: string
  last_seen_at: string
}

export interface SoldRecord {
  id: number
  query_id: number
  item_id: string
  title: string
  sold_price: string | null
  currency: string | null
  sold_date: string | null
  listing_type: string | null
  image_url: string | null
  item_url: string | null
  scraped_at: string
}

export interface PriceTrendPoint {
  date: string
  avg_price: number | null
  min_price: number | null
  max_price: number | null
  count: number
}

export interface SoldTrendPoint {
  date: string
  avg_sold_price: number | null
  count: number
}

export interface QuerySummary {
  query_id: number
  total_live: number
  total_sold: number
  avg_live_price: number | null
  avg_sold_price: number | null
  median_sold_price: number | null
  price_delta: number | null
}

export interface ItemsEvaluated {
  total: number
  since: string | null
  scheduler_running: boolean
}

export interface SchedulerStatus {
  running: boolean
  paused: boolean
  active_schedules: number
  running_jobs: number
  running_query_ids: number[]
}

export interface AppConfig {
  app_title: string
  app_debug: boolean
  auth_enabled: boolean
  cors_origins: string[]
  ebay?: {
    site_id: string
    max_pages: number
  }
  scheduler?: {
    default_interval_minutes: number
    max_concurrent_polls: number
  }
  scraper?: {
    enabled: boolean
    completed_days: number
  }
  // Legacy flat keys for backward compatibility
  ebay_site_id?: string
  ebay_max_pages?: number
  scheduler_default_interval_minutes?: number
  scheduler_max_concurrent_polls?: number
}

export interface SettingsUpdate {
  scheduler_default_interval_minutes?: number
  scheduler_max_concurrent_polls?: number
  ebay_max_pages?: number
  scraper_enabled?: boolean
  scraper_completed_days?: number
}

export interface EbaySite {
  id: string
  name: string
}

export interface EbayCategorySuggestion {
  category_id: string
  category_name: string
  category_path: string
}

export interface EbayCategorySuggestionList {
  items: EbayCategorySuggestion[]
}

export interface LogLine {
  raw: string
  timestamp: string | null
  level: string | null
  message: string | null
}

export interface RecentLogsResponse {
  lines: LogLine[]
  total_available: number
}

// ── Core fetch wrapper ─────────────────────────────────────────────────────

let _pendingRequests = 0

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE}${path}`

  _pendingRequests++
  NProgress.start()
  logger.debug('API →', options.method ?? 'GET', url)

  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...options.headers },
      ...options,
    })

    if (!res.ok) {
      let detail = res.statusText
      try {
        const body = await res.json()
        detail = body?.detail ?? detail
      } catch { /* ignore parse error */ }
      logger.error('API error', res.status, url, detail)
      throw new ApiError(res.status, detail, url)
    }

    const data: T = res.status === 204 ? (null as T) : await res.json()
    logger.debug('API ←', res.status, url)
    return data
  } finally {
    _pendingRequests--
    if (_pendingRequests <= 0) {
      _pendingRequests = 0
      NProgress.done()
    }
  }
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly url: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// ── Queries ────────────────────────────────────────────────────────────────

export const api = {
  queries: {
    list: (page = 1, pageSize = 20) =>
      apiFetch<PaginatedResponse<SearchQuery>>(`/queries?page=${page}&page_size=${pageSize}`),
    get: (id: number) => apiFetch<SearchQuery>(`/queries/${id}`),
    create: (data: QueryCreate) =>
      apiFetch<SearchQuery>('/queries', { method: 'POST', body: JSON.stringify(data) }),
    update: (id: number, data: QueryUpdate) =>
      apiFetch<SearchQuery>(`/queries/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
    delete: (id: number) => apiFetch<null>(`/queries/${id}`, { method: 'DELETE' }),
    runNow: (id: number) => apiFetch<{ message: string }>(`/queries/${id}/run`, { method: 'POST' }),
    stop: (id: number) => apiFetch<{ message: string; query_id: number }>(`/queries/${id}/stop`, { method: 'POST' }),
  },

  snapshots: {
    list: (queryId?: number, page = 1, pageSize = 20) =>
      apiFetch<PaginatedResponse<Snapshot>>(
        `/snapshots?${queryId ? `query_id=${queryId}&` : ''}page=${page}&page_size=${pageSize}`,
      ),
    get: (id: number) => apiFetch<Snapshot>(`/snapshots/${id}`),
  },

  listings: {
    list: (params: Record<string, string | number | boolean | undefined> = {}) => {
      const qs = Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
      return apiFetch<PaginatedResponse<ListingRecord>>(`/listings${qs ? '?' + qs : ''}`)
    },
    itemHistory: (itemId: string) =>
      apiFetch<ListingRecord[]>(`/listings/item/${encodeURIComponent(itemId)}`),
  },

  sold: {
    list: (params: Record<string, string | number | undefined> = {}) => {
      const qs = Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== '')
        .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`)
        .join('&')
      return apiFetch<PaginatedResponse<SoldRecord>>(`/sold${qs ? '?' + qs : ''}`)
    },
  },

  stats: {
    priceTrend: (queryId: number, granularity = 'week') =>
      apiFetch<PriceTrendPoint[]>(`/stats/price-trend?query_id=${queryId}&granularity=${granularity}`),
    soldTrend: (queryId: number, granularity = 'week') =>
      apiFetch<SoldTrendPoint[]>(`/stats/sold-trend?query_id=${queryId}&granularity=${granularity}`),
    summary: (queryId: number) =>
      apiFetch<QuerySummary>(`/stats/summary?query_id=${queryId}`),
    itemsEvaluated: () => apiFetch<ItemsEvaluated>('/stats/items-evaluated'),
  },

  scheduler: {
    status: () => apiFetch<SchedulerStatus>('/scheduler/status'),
    pause: () => apiFetch<{ message: string }>('/scheduler/pause', { method: 'POST' }),
    resume: () => apiFetch<{ message: string }>('/scheduler/resume', { method: 'POST' }),
    runAll: () => apiFetch<{ message: string }>('/scheduler/run-all', { method: 'POST' }),
  },

  config: {
    get: () => apiFetch<AppConfig>('/config'),
    sites: () => apiFetch<EbaySite[]>('/config/ebay-sites'),
    categorySuggestions: (site_id: string, q: string) =>
      apiFetch<EbayCategorySuggestionList>(
        `/config/ebay-category-suggestions?site_id=${encodeURIComponent(site_id)}&q=${encodeURIComponent(q)}`,
      ),
    updateSite: (site_id: string) =>
      apiFetch<{ site_id: string; site_name: string }>('/config/ebay-site', {
        method: 'PUT',
        body: JSON.stringify({ site_id }),
      }),
    updateSettings: (body: SettingsUpdate) =>
      apiFetch<Record<string, unknown>>('/config/settings', {
        method: 'PATCH',
        body: JSON.stringify(body),
      }),
  },

  logs: {
    recent: (lines = 200) => apiFetch<RecentLogsResponse>(`/logs/recent?lines=${lines}`),
  },
}
