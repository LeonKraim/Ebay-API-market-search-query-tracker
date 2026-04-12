import { useEffect, useState } from 'react'
import { TopLoadingBar } from '@/components/layout/TopLoadingBar'
import { Sidebar } from '@/components/layout/Sidebar'
import { Dashboard } from '@/pages/Dashboard'
import { QueriesPage } from '@/pages/Queries'
import { ListingsPage } from '@/pages/Listings'
import { StatsPage } from '@/pages/Stats'
import { SchedulerPage } from '@/pages/Scheduler'
import { SettingsPage } from '@/pages/Settings'
import { LogsPage } from '@/pages/Logs'

export type Page = 'dashboard' | 'queries' | 'listings' | 'stats' | 'scheduler' | 'logs' | 'settings'
export type MarketMode = 'live' | 'sold'

interface NavigationState {
  page: Page
  marketMode: MarketMode
  selectedQueryId: number | null
}

const PAGES = new Set<Page>(['dashboard', 'queries', 'listings', 'stats', 'scheduler', 'logs', 'settings'])

function readNavigationState(): NavigationState {
  const url = new URL(window.location.href)
  const params = new URLSearchParams(url.search)
  const rawPage = params.get('page')
  const page = rawPage && PAGES.has(rawPage as Page) ? (rawPage as Page) : 'dashboard'
  const marketMode = params.get('market') === 'sold' ? 'sold' : 'live'
  const rawQueryId = Number.parseInt(params.get('queryId') ?? '', 10)
  const selectedQueryId = Number.isInteger(rawQueryId) && rawQueryId > 0 ? rawQueryId : null

  if (page !== 'listings') {
    return { page, marketMode: 'live', selectedQueryId: null }
  }

  return { page, marketMode, selectedQueryId }
}

function buildNavigationUrl(state: NavigationState): string {
  const url = new URL(window.location.href)
  const params = new URLSearchParams()
  params.set('page', state.page)

  if (state.page === 'listings') {
    params.set('market', state.marketMode)
    if (state.selectedQueryId) {
      params.set('queryId', String(state.selectedQueryId))
    }
  }

  const query = params.toString()
  return `${url.pathname}${query ? `?${query}` : ''}${url.hash}`
}

function normalizeNavigationState(state: NavigationState): NavigationState {
  if (state.page !== 'listings') {
    return { page: state.page, marketMode: 'live', selectedQueryId: null }
  }

  return state
}

export default function App() {
  const [navigation, setNavigation] = useState<NavigationState>(() => readNavigationState())

  useEffect(() => {
    const onPopState = () => {
      setNavigation(readNavigationState())
    }

    window.addEventListener('popstate', onPopState)

    return () => {
      window.removeEventListener('popstate', onPopState)
    }
  }, [])

  function navigate(nextState: NavigationState) {
    const normalized = normalizeNavigationState(nextState)
    const url = buildNavigationUrl(normalized)
    window.history.pushState({}, '', url)
    setNavigation(normalized)
  }

  function navigateToPage(page: Page) {
    navigate({
      page,
      marketMode: 'live',
      selectedQueryId: null,
    })
  }

  function openQueryInListings(queryId: number) {
    navigate({ page: 'listings', marketMode: 'live', selectedQueryId: queryId })
  }

  function renderPage() {
    switch (navigation.page) {
      case 'dashboard':
        return <Dashboard onOpenQuery={openQueryInListings} />
      case 'queries':
        return <QueriesPage onOpenQuery={openQueryInListings} />
      case 'listings':
        return (
          <ListingsPage
            marketMode={navigation.marketMode}
            selectedQueryId={navigation.selectedQueryId}
            onMarketModeChange={(marketMode) =>
              navigate({
                page: 'listings',
                marketMode,
                selectedQueryId: navigation.selectedQueryId,
              })
            }
          />
        )
      case 'stats':
        return <StatsPage />
      case 'scheduler':
        return <SchedulerPage />
      case 'logs':
        return <LogsPage />
      case 'settings':
        return <SettingsPage />
      default:
        return <Dashboard onOpenQuery={openQueryInListings} />
    }
  }

  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      <TopLoadingBar />
      <Sidebar activePage={navigation.page} onNavigate={navigateToPage} />
      <main className="flex-1 overflow-y-auto p-6">
        {renderPage()}
      </main>
    </div>
  )
}
