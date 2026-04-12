import { format, parseISO } from 'date-fns'

/** Format an ISO datetime string to a human-readable local string. */
export function fmtDatetime(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(parseISO(iso), 'dd MMM yyyy HH:mm')
  } catch {
    return iso
  }
}

/** Format an ISO date string to a short date. */
export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return '—'
  try {
    return format(parseISO(iso), 'dd MMM yyyy')
  } catch {
    return iso
  }
}

/** Format a price as a locale currency string. */
export function fmtPrice(
  price: number | string | null | undefined,
  currency = 'GBP',
): string {
  if (price == null) return '—'
  const num = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(num)) return '—'
  try {
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency,
      minimumFractionDigits: 2,
    }).format(num)
  } catch {
    return `${currency} ${num.toFixed(2)}`
  }
}

/** Clamp a number to [min, max]. */
export function clamp(value: number, min: number, max: number): number {
  return Math.min(Math.max(value, min), max)
}

/** Pluralise a word. */
export function pluralise(count: number, word: string, plural = `${word}s`): string {
  return count === 1 ? `1 ${word}` : `${count} ${plural}`
}
