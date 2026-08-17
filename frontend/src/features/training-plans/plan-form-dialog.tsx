import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import type { TrainingPlan } from '@/api/types'
import {
  EntityFormDialog,
  type NameDescriptionPayload,
} from '@/components/entity-form-dialog'
import { useCreateTrainingPlan, useUpdateTrainingPlan } from './hooks'

type PlanFormDialogProps = {
  open: boolean
  onOpenChange: (open: boolean) => void
  plan?: TrainingPlan
}

export function PlanFormDialog({ open, onOpenChange, plan }: PlanFormDialogProps) {
  const isEdit = plan !== undefined
  const createPlan = useCreateTrainingPlan()
  const updatePlan = useUpdateTrainingPlan(plan?.id ?? 0)

  const handleSubmit = (payload: NameDescriptionPayload) => {
    const mutation = isEdit ? updatePlan : createPlan
    mutation.mutate(payload, {
      onSuccess: () => {
        toast.success(isEdit ? 'Training plan updated' : 'Training plan created')
        onOpenChange(false)
      },
      onError: (error) => toast.error(getErrorMessage(error)),
    })
  }

  return (
    <EntityFormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={isEdit ? 'Edit training plan' : 'New training plan'}
      description="A training plan organizes training units into a program."
      namePlaceholder="12-week strength"
      submitLabel={isEdit ? 'Save changes' : 'Create'}
      initialName={plan?.name ?? ''}
      initialDescription={plan?.description ?? ''}
      isPending={createPlan.isPending || updatePlan.isPending}
      onSubmit={handleSubmit}
    />
  )
}
