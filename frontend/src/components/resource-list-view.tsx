import {
  MoreHorizontal,
  Pencil,
  Plus,
  Search,
  Trash2,
  type LucideIcon,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import type { ListParams, Paged, Scope } from '@/api/types'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataError } from '@/components/data-error'
import { EmptyState } from '@/components/empty-state'
import { FadeIn } from '@/components/fade-in'
import { PageHeader } from '@/components/page-header'
import { PaginationBar } from '@/components/pagination-bar'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useDebounce } from '@/hooks/use-debounce'

const PAGE_SIZE = 10

export type Column<T> = {
  header: string
  cell: (item: T) => React.ReactNode
  className?: string
}

type ListQuery<T> = {
  data: Paged<T> | undefined
  isLoading: boolean
  isError: boolean
  error: unknown
}

type DeleteCallbacks = { onSuccess: () => void; onError: (error: unknown) => void }

type ResourceListViewProps<T, P extends ListParams = ListParams> = {
  title: string
  description: string
  icon: LucideIcon
  newLabel: string
  entityLabel: string
  emptyTitle: string
  emptyDescription: string
  defaultScope?: Scope
  useList: (params: P) => ListQuery<T>
  columns: Column<T>[]
  getRowId: (item: T) => number
  getRowName: (item: T) => string
  canManage: (item: T) => boolean
  onNew: () => void
  onEdit: (item: T) => void
  onDelete: (id: number, callbacks: DeleteCallbacks) => void
  isDeleting: boolean
  // Opt-in name search box (only rendered when set); q is passed to useList.
  searchPlaceholder?: string
  // Entity-specific filter controls + their current values (merged into params).
  toolbar?: React.ReactNode
  extraParams?: Omit<P, keyof ListParams>
}

export function ResourceListView<T, P extends ListParams = ListParams>({
  title,
  description,
  icon: Icon,
  newLabel,
  entityLabel,
  emptyTitle,
  emptyDescription,
  defaultScope = 'all',
  useList,
  columns,
  getRowId,
  getRowName,
  canManage,
  onNew,
  onEdit,
  onDelete,
  isDeleting,
  searchPlaceholder,
  toolbar,
  extraParams,
}: ResourceListViewProps<T, P>) {
  const [scope, setScope] = useState<Scope>(defaultScope)
  const [skip, setSkip] = useState(0)
  const [deleting, setDeleting] = useState<T | undefined>(undefined)
  const [searchInput, setSearchInput] = useState('')
  const q = useDebounce(searchInput, 300)

  // base list params + entity-specific filters; the merge reassembles exactly P.
  const params = {
    scope,
    skip,
    limit: PAGE_SIZE,
    q: q ? q : undefined,
    ...(extraParams ?? {}),
  } as P
  const extraKey = JSON.stringify(extraParams ?? {})

  const { data, isLoading, isError, error } = useList(params)

  // A new search term or filter changes the result set — go back to page 1.
  useEffect(() => {
    setSkip(0)
  }, [q, extraKey])

  const handleScopeChange = (next: string) => {
    // TabsTrigger values are fixed to 'all' | 'my' below.
    setScope(next as Scope)
    setSkip(0)
  }

  const confirmDelete = () => {
    if (deleting === undefined) return
    const capitalized = entityLabel.charAt(0).toUpperCase() + entityLabel.slice(1)
    onDelete(getRowId(deleting), {
      onSuccess: () => {
        toast.success(`${capitalized} deleted`)
        setDeleting(undefined)
      },
      onError: (deleteError) => toast.error(getErrorMessage(deleteError)),
    })
  }

  return (
    <FadeIn className="space-y-6">
      <PageHeader
        title={title}
        description={description}
        action={
          <Button onClick={onNew}>
            <Plus className="mr-2 size-4" />
            {newLabel}
          </Button>
        }
      />

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <Tabs value={scope} onValueChange={handleScopeChange}>
          <TabsList>
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="my">Mine</TabsTrigger>
          </TabsList>
        </Tabs>
        {searchPlaceholder || toolbar ? (
          <div className="flex flex-wrap items-center gap-2">
            {searchPlaceholder ? (
              <div className="relative">
                <Search className="absolute top-2.5 left-2.5 size-4 text-muted-foreground" />
                <Input
                  value={searchInput}
                  onChange={(event) => setSearchInput(event.target.value)}
                  placeholder={searchPlaceholder}
                  className="w-full pl-8 sm:w-[240px]"
                />
              </div>
            ) : null}
            {toolbar}
          </div>
        ) : null}
      </div>

      {isLoading ? (
        <div className="space-y-2">
          {Array.from({ length: 5 }).map((_, index) => (
            <Skeleton key={index} className="h-12 w-full" />
          ))}
        </div>
      ) : isError ? (
        <DataError error={error} />
      ) : data === undefined || data.items.length === 0 ? (
        <EmptyState
          icon={Icon}
          title={emptyTitle}
          description={emptyDescription}
          action={
            <Button onClick={onNew} variant="outline">
              <Plus className="mr-2 size-4" />
              {newLabel}
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          <div className="rounded-lg border">
            <Table>
              <TableHeader>
                <TableRow>
                  {columns.map((column) => (
                    <TableHead key={column.header}>{column.header}</TableHead>
                  ))}
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.items.map((item) => (
                  <TableRow key={getRowId(item)}>
                    {columns.map((column) => (
                      <TableCell key={column.header} className={column.className}>
                        {column.cell(item)}
                      </TableCell>
                    ))}
                    <TableCell>
                      {canManage(item) ? (
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" aria-label="Actions">
                              <MoreHorizontal className="size-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => onEdit(item)}>
                              <Pencil className="mr-2 size-4" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem
                              variant="destructive"
                              onClick={() => setDeleting(item)}
                            >
                              <Trash2 className="mr-2 size-4" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      ) : null}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <PaginationBar
            skip={skip}
            limit={PAGE_SIZE}
            total={data.total}
            onSkipChange={setSkip}
          />
        </div>
      )}

      <ConfirmDialog
        open={deleting !== undefined}
        onOpenChange={(open) => {
          if (!open) setDeleting(undefined)
        }}
        title={`Delete ${entityLabel}?`}
        description={
          deleting === undefined
            ? undefined
            : `"${getRowName(deleting)}" will be permanently removed.`
        }
        onConfirm={confirmDelete}
        isPending={isDeleting}
      />
    </FadeIn>
  )
}
