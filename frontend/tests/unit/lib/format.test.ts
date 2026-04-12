import { describe, it, expect } from 'vitest'
import { fmtPrice, fmtDate, fmtDatetime, pluralise } from '@/lib/format'

describe('fmtPrice', () => {
  it('formats GBP correctly', () => {
    expect(fmtPrice(9.99, 'GBP')).toMatch(/£9\.99/)
  })

  it('returns em-dash for null', () => {
    expect(fmtPrice(null)).toBe('—')
  })

  it('returns em-dash for undefined', () => {
    expect(fmtPrice(undefined)).toBe('—')
  })

  it('handles string numbers', () => {
    expect(fmtPrice('27.50', 'GBP')).toMatch(/27\.50/)
  })

  it('handles zero', () => {
    expect(fmtPrice(0, 'GBP')).toMatch(/0\.00/)
  })

  it('handles large numbers with grouping', () => {
    const result = fmtPrice(1299.99, 'GBP')
    expect(result).toMatch(/1[,.]?299/)
  })
})

describe('fmtDate', () => {
  it('formats ISO date string', () => {
    expect(fmtDate('2024-01-15')).toBe('15 Jan 2024')
  })

  it('returns em-dash for null', () => {
    expect(fmtDate(null)).toBe('—')
  })

  it('returns em-dash for empty string', () => {
    expect(fmtDate('')).toBe('—')
  })
})

describe('fmtDatetime', () => {
  it('formats ISO datetime', () => {
    const result = fmtDatetime('2024-06-01T10:30:00Z')
    expect(result).toMatch(/01 Jun 2024/)
  })

  it('returns em-dash for null', () => {
    expect(fmtDatetime(null)).toBe('—')
  })
})

describe('pluralise', () => {
  it('singular', () => {
    expect(pluralise(1, 'item')).toBe('1 item')
  })

  it('plural', () => {
    expect(pluralise(5, 'item')).toBe('5 items')
  })

  it('zero is plural', () => {
    expect(pluralise(0, 'item')).toBe('0 items')
  })

  it('custom plural', () => {
    expect(pluralise(2, 'query', 'queries')).toBe('2 queries')
  })
})
