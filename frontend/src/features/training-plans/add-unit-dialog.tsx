import { useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import { AddToCollectionDialog } from '@/components/add-to-collection-dialog'
import { useTrainingUnits } from '@/features/training-units/hooks'
import { useAddUnitToPlan } from './hooks'

type AddUnitDialogProps = {
  planId: number
  existingIds: number[]
  open: boolean
  onOpenChange: (open: boolean) => void
}

const UNITS_LIMIT = 100

export function AddUnitDialog({
  planId,
  existingIds,
  open,
  onOpenChange,
}: AddUnitDialogProps) {
  // Only your own units can be attached (backend scopes membership to the owner).
  const units = useTrainingUnits({ scope: 'my', skip: 0, limit: UNITS_LIMIT })
  const addUnit = useAddUnitToPlan(planId)
  const [isPending, setIsPending] = useState(false)

  const handleAdd = async (ids: number[]) => {
    setIsPending(true)
    try {
      await Promise.all(ids.map((id) => addUnit.mutateAsync(id)))
      toast.success(
        ids.length === 1 ? 'Training unit added' : `${ids.length} units added`,
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
      title="Add training units"
      description="Pick one or more of your training units."
      placeholder="Search your units…"
      emptyText="No training units found."
      existingIds={existingIds}
      items={units.data?.items}
      isPending={isPending}
      onAdd={handleAdd}
    />
  )
}
