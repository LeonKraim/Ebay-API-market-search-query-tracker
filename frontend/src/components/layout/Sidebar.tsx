import {
  LayoutDashboard,
  Search,
  List,
  BarChart2,
  Clock,
  Settings,
  Activity,
  ScrollText,
  Loader2,
} from 'lucide-react'
import { cn } from '@/lib/cn'
import { useItemsEvaluated } from '@/api/hooks'
import type { Page } from '@/App'

const NAV: { id: Page; label: string; icon: React.FC<{ className?: string }> }[] = [
  { id: 'dashboard',  label: 'Dashboard',  icon: LayoutDashboard },
  { id: 'queries',    label: 'Queries',    icon: Search },
  { id: 'listings',   label: 'Listings',   icon: List },
  { id: 'stats',      label: 'Stats',      icon: BarChart2 },
  { id: 'scheduler',  label: 'Scheduler',  icon: Clock },
  { id: 'logs',       label: 'Logs',       icon: ScrollText },
  { id: 'settings',   label: 'Settings',   icon: Settings },
]

interface SidebarProps {
  activePage: Page
  onNavigate: (page: Page) => void
}

export function Sidebar({ activePage, onNavigate }: SidebarProps) {
  const { data: evaluated } = useItemsEvaluated()

  return (
    <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col py-4 gap-1 shrink-0">
      <nav className="flex-1 px-2 gap-0.5 flex flex-col">
        {NAV.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={cn(
              'flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors w-full text-left',
              activePage === id
                ? 'bg-blue-600 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800',
            )}
          >
            <Icon className="w-4 h-4 shrink-0" />
            {label}
          </button>
        ))}
      </nav>

      <div className="px-3 pb-2 border-t border-gray-800 pt-3">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <Activity className="w-3 h-3 text-green-400" />
          <span>
            {evaluated
              ? `${evaluated.total.toLocaleString()} unique items evaluated`
              : '— unique items evaluated'}
          </span>
        </div>
        {evaluated?.scheduler_running && (
          <div className="flex items-center gap-1.5 mt-1 text-xs text-green-400">
            <Loader2 className="w-3 h-3 animate-spin shrink-0" />
            Scheduler running
          </div>
        )}
        <a href="https://github.com/LeonKraim" target="_blank" rel="noopener noreferrer" className="mt-3 text-[11px] text-gray-500 hover:text-gray-300 underline underline-offset-2 transition-colors block">
          Made by Leon Kraim
        </a>
      </div>
    </aside>
  )
}
