import { useState, useEffect } from 'react'
import { useAppConfig, useEbaySites, useUpdateEbaySite, useUpdateSettings } from '@/api/hooks'
import { FullPageSpinner } from '@/components/ui/Throbber'

function NumericField({
  label,
  description,
  value,
  min,
  max,
  onSave,
  saving,
}: {
  label: string
  description?: string
  value: number
  min?: number
  max?: number
  onSave: (v: number) => void
  saving?: boolean
}) {
  const [draft, setDraft] = useState(String(value))
  const [msg, setMsg] = useState<string | null>(null)
  useEffect(() => { setDraft(String(value)) }, [value])

  const handleSave = () => {
    const n = parseInt(draft)
    if (isNaN(n) || (min !== undefined && n < min) || (max !== undefined && n > max)) {
      setMsg(`Must be a number${min !== undefined ? ` ≥ ${min}` : ''}${max !== undefined ? ` ≤ ${max}` : ''}.`)
      return
    }
    setMsg(null)
    onSave(n)
  }

  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
      <h2 className="text-sm font-semibold text-white">{label}</h2>
      {description && <p className="text-xs text-gray-500">{description}</p>}
      <div className="flex gap-2 items-center">
        <input
          type="number"
          min={min}
          max={max}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          className="w-32 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={handleSave}
          disabled={saving || draft === String(value)}
          className="px-3 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-40 text-white rounded-lg text-sm font-medium transition-colors"
        >
          {saving ? 'Saving…' : 'Save'}
        </button>
      </div>
      {msg && <p className="text-xs text-red-400">{msg}</p>}
    </div>
  )
}

function ToggleField({
  label,
  description,
  value,
  onSave,
  saving,
}: {
  label: string
  description?: string
  value: boolean
  onSave: (v: boolean) => void
  saving?: boolean
}) {
  return (
    <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
      <div className="flex items-center justify-between gap-4">
        <div className="space-y-1">
          <h2 className="text-sm font-semibold text-white">{label}</h2>
          {description && <p className="text-xs text-gray-500">{description}</p>}
        </div>
        <button
          type="button"
          role="switch"
          aria-checked={value}
          disabled={saving}
          onClick={() => onSave(!value)}
          className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500/60 disabled:opacity-50 ${value ? 'bg-blue-600' : 'bg-gray-600'}`}
        >
          <span
            className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transition-transform ${value ? 'translate-x-5' : 'translate-x-0'}`}
          />
        </button>
      </div>
    </div>
  )
}

export function SettingsPage() {
  const { data: config, isLoading } = useAppConfig()
  const { data: sites } = useEbaySites()
  const updateSiteMutation = useUpdateEbaySite()
  const updateSettingsMutation = useUpdateSettings()
  const [siteMsg, setSiteMsg] = useState<string | null>(null)
  const [settingsMsg, setSettingsMsg] = useState<string | null>(null)

  if (isLoading) return <FullPageSpinner />

  const cfg = config as any
  const currentSiteId = cfg?.ebay?.site_id ?? 'EBAY-GB'
  const defaultInterval = cfg?.scheduler?.default_interval_minutes ?? 60
  const maxConcurrent = cfg?.scheduler?.max_concurrent_polls ?? 3
  const maxPages = cfg?.ebay?.max_pages ?? 10000
  const scraperEnabled = cfg?.scraper?.enabled ?? true
  const scraperDays = cfg?.scraper?.completed_days ?? 90

  const handleSiteChange = async (newSite: string) => {
    setSiteMsg(null)
    try {
      const res = await updateSiteMutation.mutateAsync(newSite)
      setSiteMsg(`Switched to ${res.site_name} (${res.site_id})`)
    } catch (e: unknown) {
      setSiteMsg(`Error: ${(e as Error).message}`)
    }
  }

  const handleUpdateSetting = async (patch: Parameters<typeof updateSettingsMutation.mutateAsync>[0]) => {
    setSettingsMsg(null)
    try {
      await updateSettingsMutation.mutateAsync(patch)
      setSettingsMsg('Saved.')
      setTimeout(() => setSettingsMsg(null), 2000)
    } catch (e: unknown) {
      setSettingsMsg(`Error: ${(e as Error).message}`)
    }
  }

  const saving = updateSettingsMutation.isPending

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      {settingsMsg && (
        <p className={`text-xs ${settingsMsg.startsWith('Error') ? 'text-red-400' : 'text-green-400'}`}>
          {settingsMsg}
        </p>
      )}

      {/* eBay Marketplace */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
        <h2 className="text-sm font-semibold text-white">Default eBay Marketplace</h2>
        <p className="text-xs text-gray-500">Select the eBay regional site used as the default for new queries.</p>
        <select
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
          value={currentSiteId}
          onChange={(e) => handleSiteChange(e.target.value)}
          disabled={updateSiteMutation.isPending}
        >
          {sites?.map((s) => (
            <option key={s.id} value={s.id}>{s.name} ({s.id})</option>
          ))}
          {!sites && <option value={currentSiteId}>{currentSiteId}</option>}
        </select>
        {siteMsg && (
          <p className={`text-xs ${siteMsg.startsWith('Error') ? 'text-red-400' : 'text-green-400'}`}>{siteMsg}</p>
        )}
      </div>

      {/* Scheduler */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-1">Scheduler</h2>
        <NumericField
          label="Default Poll Interval (minutes)"
          description="New queries will use this interval by default."
          value={defaultInterval}
          min={1}
          max={10080}
          saving={saving}
          onSave={(v) => handleUpdateSetting({ scheduler_default_interval_minutes: v })}
        />
        <NumericField
          label="Max Concurrent Polls"
          description="Maximum number of eBay polls that can run at the same time."
          value={maxConcurrent}
          min={1}
          max={20}
          saving={saving}
          onSave={(v) => handleUpdateSetting({ scheduler_max_concurrent_polls: v })}
        />
      </div>

      {/* eBay API */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-1">eBay API</h2>
        <NumericField
          label="Max Pages Per Poll"
          description="Maximum number of result pages fetched per query poll."
          value={maxPages}
          min={1}
          max={100000}
          saving={saving}
          onSave={(v) => handleUpdateSetting({ ebay_max_pages: v })}
        />
      </div>

      {/* Scraper */}
      <div className="space-y-3">
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wider px-1">Sold Listing Scraper</h2>
        <ToggleField
          label="Scraper Enabled"
          description="Scrape completed/sold listings from eBay."
          value={scraperEnabled}
          saving={saving}
          onSave={(v) => handleUpdateSetting({ scraper_enabled: v })}
        />
        <NumericField
          label="Completed Listings Lookback (days)"
          description="How many days back to include when scraping completed listings."
          value={scraperDays}
          min={1}
          max={365}
          saving={saving}
          onSave={(v) => handleUpdateSetting({ scraper_completed_days: v })}
        />
      </div>
    </div>
  )
}

