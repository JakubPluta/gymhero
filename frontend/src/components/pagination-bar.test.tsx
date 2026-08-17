import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { PaginationBar } from './pagination-bar'

describe('PaginationBar', () => {
  it('shows the current range', () => {
    render(<PaginationBar skip={0} limit={10} total={25} onSkipChange={vi.fn()} />)
    expect(screen.getByText('1–10 of 25')).toBeInTheDocument()
  })

  it('shows a zero range when there is nothing', () => {
    render(<PaginationBar skip={0} limit={10} total={0} onSkipChange={vi.fn()} />)
    expect(screen.getByText('0–0 of 0')).toBeInTheDocument()
  })

  it('disables Previous on the first page', () => {
    render(<PaginationBar skip={0} limit={10} total={25} onSkipChange={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Previous' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Next' })).toBeEnabled()
  })

  it('disables Next on the last page', () => {
    render(<PaginationBar skip={20} limit={10} total={25} onSkipChange={vi.fn()} />)
    expect(screen.getByRole('button', { name: 'Next' })).toBeDisabled()
  })

  it('advances by one page on Next', async () => {
    const onSkipChange = vi.fn()
    render(<PaginationBar skip={0} limit={10} total={25} onSkipChange={onSkipChange} />)
    await userEvent.click(screen.getByRole('button', { name: 'Next' }))
    expect(onSkipChange).toHaveBeenCalledWith(10)
  })

  it('goes back a page on Previous', async () => {
    const onSkipChange = vi.fn()
    render(
      <PaginationBar skip={20} limit={10} total={25} onSkipChange={onSkipChange} />,
    )
    await userEvent.click(screen.getByRole('button', { name: 'Previous' }))
    expect(onSkipChange).toHaveBeenCalledWith(10)
  })
})
