import { useState } from 'react'
import { ImageOff } from 'lucide-react'
import { type ListingRecord } from '@/api/client'
import { fmtPrice, fmtDatetime } from '@/lib/format'
import { Throbber } from '@/components/ui/Throbber'

interface ListingTableProps {
  listings: ListingRecord[]
  isLoading?: boolean
  onItemClick?: (itemId: string) => void
  variant?: 'list' | 'grid'
}

export function ListingTable({ listings, isLoading, onItemClick, variant = 'list' }: ListingTableProps) {
  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-16">
        <Throbber size={28} />
      </div>
    )
  }

  if (listings.length === 0) {
    return (
      <div className="text-center text-gray-500 py-16 text-sm">No listings found.</div>
    )
  }

  if (variant === 'grid') {
    return (
      <div className="p-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {listings.map((listing) => (
          <article
            key={listing.id}
            className="group overflow-hidden rounded-2xl border border-gray-800 bg-gradient-to-b from-gray-900 to-gray-950 hover:border-blue-500/40 transition-colors"
            onClick={() => onItemClick?.(listing.item_id)}
          >
            <div className="p-3 pb-0">
              <ListingThumbnail listing={listing} layout="grid" />
            </div>
            <div className="p-4 space-y-3">
              {listing.item_url ? (
                <a
                  href={listing.item_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(event) => event.stopPropagation()}
                  className="line-clamp-2 text-sm font-medium text-blue-300 hover:text-blue-200 hover:underline"
                >
                  {listing.title}
                </a>
              ) : (
                <p className="line-clamp-2 text-sm font-medium text-gray-100">{listing.title}</p>
              )}

              <div className="flex items-center justify-between gap-3">
                <span className="text-lg font-semibold text-green-300 font-mono tabular-nums">
                  {fmtPrice(listing.current_price, listing.currency ?? undefined)}
                </span>
                <span className="text-xs text-gray-500">{listing.listing_type ?? '—'}</span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs text-gray-400">
                <span>State: <span className="text-gray-200">{listing.selling_state ?? '—'}</span></span>
                <span>Site: <span className="text-gray-200">{listing.country ?? '—'}</span></span>
                <span className="col-span-2">Last seen: <span className="text-gray-200">{fmtDatetime(listing.last_seen_at)}</span></span>
              </div>
            </div>
          </article>
        ))}
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800">
      <table className="w-full text-sm text-left">
        <thead className="bg-gray-900 text-gray-400 text-xs uppercase tracking-wider">
          <tr>
            <th className="px-4 py-3">Listing</th>
            <th className="px-4 py-3">Price</th>
            <th className="px-4 py-3">Type</th>
            <th className="px-4 py-3">State</th>
            <th className="px-4 py-3">Last seen</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {listings.map((l) => (
            <tr
              key={l.id}
              className="hover:bg-gray-800/50 transition-colors cursor-pointer"
              onClick={() => onItemClick?.(l.item_id)}
            >
              <td className="px-4 py-3 min-w-[320px] max-w-xl">
                <div className="flex items-start gap-3">
                  <ListingThumbnail listing={l} layout="list" />
                  <div className="min-w-0">
                    {l.item_url ? (
                      <a
                        href={l.item_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="line-clamp-2 text-blue-400 hover:text-blue-300 hover:underline"
                      >
                        {l.title}
                      </a>
                    ) : (
                      <span className="line-clamp-2 text-gray-100">{l.title}</span>
                    )}
                    <p className="mt-1 text-xs text-gray-500">
                      {l.country ?? 'Unknown location'}
                    </p>
                  </div>
                </div>
              </td>
              <td className="px-4 py-3 text-green-300 font-mono tabular-nums">
                {fmtPrice(l.current_price, l.currency ?? undefined)}
              </td>
              <td className="px-4 py-3 text-gray-400">{l.listing_type ?? '—'}</td>
              <td className="px-4 py-3 text-gray-400">{l.selling_state ?? '—'}</td>
              <td className="px-4 py-3 text-gray-500 text-xs">{fmtDatetime(l.last_seen_at)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function ListingThumbnail({
  listing,
  layout,
}: {
  listing: ListingRecord
  layout: 'list' | 'grid'
}) {
  const [failed, setFailed] = useState(false)
  const src = listing.image_url ?? listing.gallery_url
  const sizeClass = layout === 'grid' ? 'h-44 w-full' : 'h-16 w-16 flex-shrink-0'

  if (!src || failed) {
    return (
      <div className={`${sizeClass} flex items-center justify-center rounded-xl border border-dashed border-gray-700 bg-gray-900 text-gray-600`}>
        <ImageOff className="w-5 h-5" />
      </div>
    )
  }

  return (
    <img
      src={src}
      alt={listing.title}
      className={`${sizeClass} rounded-xl object-cover bg-gray-900`}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  )
}
