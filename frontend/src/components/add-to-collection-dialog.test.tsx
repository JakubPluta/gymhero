import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import { AddToCollectionDialog } from './add-to-collection-dialog'

const items = [
  { id: 1, name: 'Alpha' },
  { id: 2, name: 'Beta' },
  { id: 3, name: 'Gamma' },
]

function renderDialog(onAdd: (ids: number[]) => void, existingIds: number[] = []) {
  return render(
    <AddToCollectionDialog
      open
      onOpenChange={vi.fn()}
      title="Add items"
      description="Pick some."
      placeholder="Search…"
      emptyText="Nothing found."
      existingIds={existingIds}
      isPending={false}
      onAdd={onAdd}
      items={items}
    />,
  )
}

describe('AddToCollectionDialog', () => {
  it('starts with an empty, disabled add button', () => {
    renderDialog(vi.fn())
    expect(screen.getByRole('button', { name: 'Add (0)' })).toBeDisabled()
  })

  it('hides already-added options', () => {
    renderDialog(vi.fn(), [2])
    expect(screen.getByText('Alpha')).toBeInTheDocument()
    expect(screen.queryByText('Beta')).not.toBeInTheDocument()
  })

  it('accumulates a multi-selection and adds the chosen ids', async () => {
    const onAdd = vi.fn()
    renderDialog(onAdd)
    await userEvent.click(screen.getByText('Alpha'))
    await userEvent.click(screen.getByText('Gamma'))
    const addButton = screen.getByRole('button', { name: 'Add (2)' })
    expect(addButton).toBeEnabled()
    await userEvent.click(addButton)
    expect(onAdd).toHaveBeenCalledWith([1, 3])
  })
})
