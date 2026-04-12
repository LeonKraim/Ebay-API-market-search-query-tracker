import { useState } from 'react'
import { useAppConfig, useEbaySites, useUpdateEbaySite } from '@/api/hooks'
import { FullPageSpinner } from '@/components/ui/Throbber'

export function SettingsPage() {
  const { data: config, isLoading } = useAppConfig()
  const { data: sites } = useEbaySites()
  const updateSiteMutation = useUpdateEbaySite()
  const [siteMsg, setSiteMsg] = useState<string | null>(null)

  if (isLoading) return <FullPageSpinner />

  const currentSiteId = (config as any)?.ebay?.site_id ?? 'EBAY-GB'

  const handleSiteChange = async (newSite: string) => {
    setSiteMsg(null)
    try {
      const res = await updateSiteMutation.mutateAsync(newSite)
      setSiteMsg(`Switched to ${res.site_name} (${res.site_id})`)
    } catch (e: unknown) {
      setSiteMsg(`Error: ${(e as Error).message}`)
    }
  }

  return (
    <div className="max-w-2xl mx-auto space-y-8">
      <h1 className="text-2xl font-bold text-white">Settings</h1>

      {/* eBay Marketplace Selector */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
        <h2 className="text-sm font-semibold text-white">Default eBay Marketplace</h2>
        <p className="text-xs text-gray-500">
          Select the eBay regional site used as the default for new queries.
        </p>
        <select
          className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-blue-500"
          value={currentSiteId}
          onChange={(e) => handleSiteChange(e.target.value)}
          disabled={updateSiteMutation.isPending}
        >
          {sites?.map((s) => (
            <option key={s.id} value={s.id}>
              {s.name} ({s.id})
            </option>
          ))}
          {/* fallback if sites haven't loaded yet */}
          {!sites && <option value={currentSiteId}>{currentSiteId}</option>}
        </select>
        {siteMsg && (
          <p className={`text-xs ${siteMsg.startsWith('Error') ? 'text-red-400' : 'text-green-400'}`}>
            {siteMsg}
          </p>
        )}
      </div>

      {/* Default Interval */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-3">
        <h2 className="text-sm font-semibold text-white">Default Poll Interval</h2>
        <p className="text-xs text-gray-500">
          New queries will use this interval by default.
        </p>
        <div className="text-sm text-gray-100">
          <span className="text-gray-400">Current default: </span>
          <span className="font-semibold">60 minutes</span>
        </div>
        <p className="text-[11px] text-gray-600">
          To change the default interval, edit the scheduler configuration in the backend settings or set it per-query when creating.
        </p>
      </div>

      {/* General config display */}
      <div className="bg-gray-900 border border-gray-800 rounded-xl divide-y divide-gray-800">
        {config &&
          Object.entries(config).map(([key, value]) => (
            <div key={key} className="flex items-start justify-between px-5 py-3 gap-4">
              <span className="text-sm text-gray-400 font-mono">{key}</span>
              <span className="text-sm text-gray-100 text-right max-w-xs break-all">
                {Array.isArray(value)
                  ? value.join(', ')
                  : typeof value === 'boolean'
                  ? value ? '✓ true' : '✗ false'
                  : typeof value === 'object' && value !== null
                  ? JSON.stringify(value)
                  : String(value)}
              </span>
            </div>
          ))}
        {!config && (
          <p className="px-5 py-4 text-sm text-gray-500">Could not load config.</p>
        )}
      </div>

      <p className="text-xs text-gray-600">
        These values reflect the current server configuration (non-secret fields only).
        To change them, edit <code className="font-mono">backend/config.toml</code> and restart the server.
      </p>
    </div>
  )
}
