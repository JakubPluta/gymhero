import { useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import { AddToCollectionDialog } from '@/components/add-to-collection-dialog'
import { useDebounce } from '@/hooks/use-debounce'
import { useExercises } from '@/features/exercises/hooks'
import { useAddExerciseToUnit } from './hooks'

type AddExerciseDialogProps = {
  unitId: number
  existingIds: number[]
  open: boolean
  onOpenChange: (open: boolean) => void
}

const RESULT_LIMIT = 20

export function AddExerciseDialog({
  unitId,
  existingIds,
  open,
  onOpenChange,
}: AddExerciseDialogProps) {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 250)
  const exercises = useExercises({
    scope: 'all',
    skip: 0,
    limit: RESULT_LIMIT,
    q: debouncedQuery,
  })
  const addExercise = useAddExerciseToUnit(unitId)
  const [isPending, setIsPending] = useState(false)

  const handleAdd = async (ids: number[]) => {
    setIsPending(true)
    try {
      await Promise.all(ids.map((id) => addExercise.mutateAsync(id)))
      toast.success(
        ids.length === 1 ? 'Exercise added' : `${ids.length} exercises added`,
      )
      onOpenChange(false)
    } catch (error) {
      toast.error(getErrorMessage(error))
    } finally {
      setIsPending(false)
    }
  }

  return (
    <AddToCollectionDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Add exercises"
      description="Search the catalog and add one or more to this unit."
      placeholder="Search exercises…"
      emptyText="No exercises found."
      existingIds={existingIds}
      query={query}
      onQueryChange={setQuery}
      results={exercises.data?.items}
      isPending={isPending}
      onAdd={handleAdd}
    />
  )
}
