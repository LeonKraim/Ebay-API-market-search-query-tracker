import { ExternalLink } from 'lucide-react'
import { type SoldRecord } from '@/api/client'
import { fmtPrice, fmtDate } from '@/lib/format'
import { Throbber } from '@/components/ui/Throbber'

interface SoldTableProps {
  records: SoldRecord[]
  isLoading?: boolean
}

export function SoldTable({ records, isLoading }: SoldTableProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Throbber size={28} />
      </div>
    )
  }

  if (records.length === 0) {
    return <div className="text-center text-gray-500 py-16 text-sm">No sold records found.</div>
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800">
      <table className="w-full text-sm text-left">
        <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wider">
          <tr>
            <th className="px-4 py-3">Title</th>
            <th className="px-4 py-3">Sold price</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">Sold date</th>
            <th className="px-4 py-3">Link</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {records.map((r) => (
            <tr key={r.id} className="hover:bg-gray-800/50 transition-colors">
              <td className="px-4 py-3 max-w-xs">
                <span className="line-clamp-2 text-gray-100">{r.title}</span>
              </td>
              <td className="px-4 py-3 text-amber-300 font-mono tabular-nums">
                {fmtPrice(r.sold_price, r.currency ?? undefined)}
              </td>
              <td className="px-4 py-3 text-gray-400">{r.listing_type ?? '—'}</td>
              <td className="px-4 py-3 text-gray-400 text-xs">{fmtDate(r.sold_date)}</td>
              <td className="px-4 py-3">
                {r.item_url && (
                  <a
                    href={r.item_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </a>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
