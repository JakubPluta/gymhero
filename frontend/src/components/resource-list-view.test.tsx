import { render, screen } from '@testing-library/react'
import { Dumbbell } from 'lucide-react'
import { describe, expect, it, vi } from 'vitest'
import type { ListParams, Paged } from '@/api/types'
import { ResourceListView, type Column } from './resource-list-view'

type Item = { id: number; name: string; owner_id: number }

type ListResult = {
  data: Paged<Item> | undefined
  isLoading: boolean
  isError: boolean
  error: unknown
}

const columns: Column<Item>[] = [{ header: 'Name', cell: (item) => item.name }]

function makeProps(
  useList: (params: ListParams) => ListResult,
  canManage: (item: Item) => boolean = () => true,
) {
  return {
    title: 'Widgets',
    description: 'Manage widgets',
    icon: Dumbbell,
    newLabel: 'New widget',
    entityLabel: 'widget',
    emptyTitle: 'No widgets yet',
    emptyDescription: 'Create your first widget.',
    useList,
    columns,
    getRowId: (item: Item) => item.id,
    getRowName: (item: Item) => item.name,
    canManage,
    onNew: vi.fn(),
    onEdit: vi.fn(),
    onDelete: vi.fn(),
    isDeleting: false,
  }
}

const oneItem: Paged<Item> = {
  items: [{ id: 1, name: 'Alpha', owner_id: 1 }],
  total: 1,
  skip: 0,
  limit: 10,
}

describe('ResourceListView', () => {
  it('renders the header and a create action', () => {
    const useList = () => ({
      data: oneItem,
      isLoading: false,
      isError: false,
      error: null,
    })
    render(<ResourceListView<Item> {...makeProps(useList)} />)
    expect(screen.getByRole('heading', { name: 'Widgets' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /new widget/i })).toBeInTheDocument()
  })

  it('shows the empty state when there are no items', () => {
    const empty: Paged<Item> = { items: [], total: 0, skip: 0, limit: 10 }
    const useList = () => ({
      data: empty,
      isLoading: false,
      isError: false,
      error: null,
    })
    render(<ResourceListView<Item> {...makeProps(useList)} />)
    expect(screen.getByText('No widgets yet')).toBeInTheDocument()
    expect(screen.queryByText('Alpha')).not.toBeInTheDocument()
  })

  it('renders a flattened error message', () => {
    const useList = () => ({
      data: undefined,
      isLoading: false,
      isError: true,
      error: { detail: 'boom' },
    })
    render(<ResourceListView<Item> {...makeProps(useList)} />)
    expect(screen.getByText('boom')).toBeInTheDocument()
  })

  it('renders rows with a row-actions menu when the user can manage', () => {
    const useList = () => ({
      data: oneItem,
      isLoading: false,
      isError: false,
      error: null,
    })
    render(<ResourceListView<Item> {...makeProps(useList)} />)
    expect(screen.getByText('Alpha')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Actions' })).toBeInTheDocument()
  })

  it('hides row actions when the user cannot manage', () => {
    const useList = () => ({
      data: oneItem,
      isLoading: false,
      isError: false,
      error: null,
    })
    render(<ResourceListView<Item> {...makeProps(useList, () => false)} />)
    expect(screen.getByText('Alpha')).toBeInTheDocument()
    expect(screen.queryByRole('button', { name: 'Actions' })).not.toBeInTheDocument()
  })
})
