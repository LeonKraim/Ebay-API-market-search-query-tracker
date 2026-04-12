import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { StatusBadge } from '@/components/ui/StatusBadge'

describe('StatusBadge', () => {
  it('renders "running" status', () => {
    render(<StatusBadge status="running" />)
    expect(screen.getByText('running')).toBeInTheDocument()
  })

  it('renders "complete" status', () => {
    render(<StatusBadge status="complete" />)
    expect(screen.getByText('complete')).toBeInTheDocument()
  })

  it('renders "error" status', () => {
    render(<StatusBadge status="error" />)
    expect(screen.getByText('error')).toBeInTheDocument()
  })

  it('renders unknown status without crashing', () => {
    render(<StatusBadge status="something-new" />)
    expect(screen.getByText('something-new')).toBeInTheDocument()
  })

  it('shows spinner dot for running', () => {
    const { container } = render(<StatusBadge status="running" />)
    // The pulse dot is a span with animate-pulse
    const pulseDot = container.querySelector('.animate-pulse')
    expect(pulseDot).not.toBeNull()
  })

  it('does not show spinner for complete', () => {
    const { container } = render(<StatusBadge status="complete" />)
    const pulseDot = container.querySelector('.animate-pulse')
    expect(pulseDot).toBeNull()
  })
})
