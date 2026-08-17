import { Check } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '@/components/ui/command'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

type Option = { id: number; name: string }

type AddToCollectionDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  title: string
  description: string
  placeholder: string
  emptyText: string
  existingIds: number[]
  isPending: boolean
  onAdd: (ids: number[]) => void
  // Server-search mode: pass all three. The parent fetches `results` for `query`.
  query?: string
  onQueryChange?: (query: string) => void
  results?: Option[]
  // Client-search mode: pass `items`; cmdk filters them locally.
  items?: Option[]
}

// Searchable, multi-select picker shared by "add exercises to unit" (server
// search over the catalog) and "add units to plan" (client search over a small
// owned list). Selection accumulates; the parent's onAdd fires the mutations.
export function AddToCollectionDialog({
  open,
  onOpenChange,
  title,
  description,
  placeholder,
  emptyText,
  existingIds,
  isPending,
  onAdd,
  query,
  onQueryChange,
  results,
  items,
}: AddToCollectionDialogProps) {
  const [selected, setSelected] = useState<Set<number>>(new Set())

  useEffect(() => {
    setSelected(new Set())
  }, [open])

  const isServerMode = onQueryChange !== undefined
  const options = isServerMode ? (results ?? []) : (items ?? [])
  const available = options.filter((option) => !existingIds.includes(option.id))

  const toggle = (id: number) => {
    setSelected((current) => {
      const next = new Set(current)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="gap-0 p-0 sm:max-w-lg">
        <DialogHeader className="px-6 pt-6">
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <Command shouldFilter={!isServerMode} className="mt-2">
          <CommandInput
            placeholder={placeholder}
            value={isServerMode ? query : undefined}
            onValueChange={onQueryChange}
          />
          <CommandList>
            <CommandEmpty>{emptyText}</CommandEmpty>
            <CommandGroup>
              {available.map((option) => (
                <CommandItem
                  key={option.id}
                  value={option.name}
                  onSelect={() => toggle(option.id)}
                >
                  <Check
                    className={cn(
                      'mr-2 size-4',
                      selected.has(option.id) ? 'opacity-100' : 'opacity-0',
                    )}
                  />
                  {option.name}
                </CommandItem>
              ))}
            </CommandGroup>
          </CommandList>
        </Command>
        <DialogFooter className="px-6 pb-6">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => onAdd([...selected])}
            disabled={selected.size === 0 || isPending}
          >
            Add ({selected.size})
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
