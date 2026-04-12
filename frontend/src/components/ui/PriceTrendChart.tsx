import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'
import { type PriceTrendPoint } from '@/api/client'
import { Throbber } from '@/components/ui/Throbber'

interface PriceTrendChartProps {
  data: PriceTrendPoint[]
  isLoading?: boolean
  currency?: string
}

export function PriceTrendChart({ data, isLoading, currency = 'GBP' }: PriceTrendChartProps) {
  const symbol = currency === 'GBP' ? '£' : currency === 'USD' ? '$' : '€'

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Throbber size={28} />
      </div>
    )
  }

  if (!data.length) {
    return <div className="flex items-center justify-center h-64 text-gray-500 text-sm">No data yet.</div>
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
        <XAxis
          dataKey="date"
          tick={{ fill: '#9ca3af', fontSize: 11 }}
          tickFormatter={(v) => {
            const d = new Date(v)
            return isNaN(d.getTime()) ? v : d.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' })
          }}
        />
        <YAxis
          tick={{ fill: '#9ca3af', fontSize: 11 }}
          tickFormatter={(v) => `${symbol}${v}`}
        />
        <Tooltip
          contentStyle={{ background: '#111827', border: '1px solid #374151', borderRadius: 8 }}
          labelStyle={{ color: '#f9fafb' }}
          labelFormatter={(v) => {
            const d = new Date(v)
            return isNaN(d.getTime()) ? v : d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
          }}
          formatter={(v) => {
            const num = typeof v === 'number' ? v : parseFloat(String(v))
            return [isNaN(num) ? '—' : `${symbol}${num.toFixed(2)}`, '']
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="avg_price"
          name="Avg price"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 5 }}
        />
        <Line
          type="monotone"
          dataKey="min_price"
          name="Min"
          stroke="#6ee7b7"
          strokeWidth={1.5}
          strokeDasharray="4 2"
          dot={false}
        />
        <Line
          type="monotone"
          dataKey="max_price"
          name="Max"
          stroke="#f87171"
          strokeWidth={1.5}
          strokeDasharray="4 2"
          dot={false}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
