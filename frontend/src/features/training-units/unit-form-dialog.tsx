import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import type { TrainingUnit } from '@/api/types'
import {
  EntityFormDialog,
  type NameDescriptionPayload,
} from '@/components/entity-form-dialog'
import { useCreateTrainingUnit, useUpdateTrainingUnit } from './hooks'

type UnitFormDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  unit?: TrainingUnit
}

export function UnitFormDialog({ open, onOpenChange, unit }: UnitFormDialogProps) {
  const isEdit = unit !== undefined
  const createUnit = useCreateTrainingUnit()
  const updateUnit = useUpdateTrainingUnit(unit?.id ?? 0)

  const handleSubmit = (payload: NameDescriptionPayload) => {
    const mutation = isEdit ? updateUnit : createUnit
    mutation.mutate(payload, {
      onSuccess: () => {
        toast.success(isEdit ? 'Training unit updated' : 'Training unit created')
        onOpenChange(false)
      },
      onError: (error) => toast.error(getErrorMessage(error)),
    })
  }

  return (
    <EntityFormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={isEdit ? 'Edit training unit' : 'New training unit'}
      description="A training unit groups exercises into a single workout."
      namePlaceholder="Push day"
      submitLabel={isEdit ? 'Save changes' : 'Create'}
      initialName={unit?.name ?? ''}
      initialDescription={unit?.description ?? ''}
      isPending={createUnit.isPending || updateUnit.isPending}
      onSubmit={handleSubmit}
    />
  )
}
