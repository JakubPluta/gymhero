import { Link, useNavigate } from '@tanstack/react-router'
import { Dumbbell, Pencil, Plus, Trash2, X } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import type { PrescriptionUpdate, TrainingUnitExercise } from '@/api/types'
import { useMe } from '@/auth/useAuth'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataError } from '@/components/data-error'
import { EmptyState } from '@/components/empty-state'
import { FadeIn } from '@/components/fade-in'
import { PageBreadcrumb } from '@/components/page-breadcrumb'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AddExerciseDialog } from './add-exercise-dialog'
import {
  useDeleteTrainingUnit,
  useRemoveExerciseFromUnit,
  useSetPrescription,
  useTrainingUnit,
} from './hooks'
import { formatPrescription } from './prescription'
import { PrescriptionDialog } from './prescription-dialog'
import { UnitFormDialog } from './unit-form-dialog'

export function TrainingUnitDetailPage({ id }: { id: number }) {
  const navigate = useNavigate()
  const { data: me } = useMe()
  const { data: unit, isLoading, isError, error } = useTrainingUnit(id)
  const deleteUnit = useDeleteTrainingUnit()
  const removeExercise = useRemoveExerciseFromUnit(id)
  const setPrescription = useSetPrescription(id)
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [addOpen, setAddOpen] = useState(false)
  const [editingLink, setEditingLink] = useState<TrainingUnitExercise | null>(null)

  const canManage =
    me !== undefined &&
    unit !== undefined &&
    (unit.owner_id === me.id || me.is_superuser)

  const confirmDelete = () => {
    deleteUnit.mutate(id, {
      onSuccess: () => {
        toast.success('Training unit deleted')
        navigate({ to: '/training-units' })
      },
      onError: (deleteError) => toast.error(getErrorMessage(deleteError)),
    })
  }

  const handleRemoveExercise = (exerciseId: number) => {
    removeExercise.mutate(exerciseId, {
      onSuccess: () => toast.success('Exercise removed'),
      onError: (removeError) => toast.error(getErrorMessage(removeError)),
    })
  }

  const handleSavePrescription = (prescription: PrescriptionUpdate) => {
    if (editingLink === null) return
    setPrescription.mutate(
      { exerciseId: editingLink.exercise.id, prescription },
      {
        onSuccess: () => {
          toast.success('Prescription updated')
          setEditingLink(null)
        },
        onError: (saveError) => toast.error(getErrorMessage(saveError)),
      },
    )
  }

  return (
    <FadeIn className="space-y-6">
      <PageBreadcrumb
        items={[
          { label: 'Home', to: '/' },
          { label: 'Training units', to: '/training-units' },
          ...(unit ? [{ label: unit.name }] : []),
        ]}
      />

      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : isError || unit === undefined ? (
        <DataError error={error} />
      ) : (
        <>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-1">
              <h1 className="text-2xl font-semibold tracking-tight">{unit.name}</h1>
              {unit.description ? (
                <p className="text-sm text-muted-foreground">{unit.description}</p>
              ) : null}
            </div>
            {canManage ? (
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setFormOpen(true)}>
                  <Pencil className="mr-2 size-4" />
                  Edit
                </Button>
                <Button variant="outline" size="sm" onClick={() => setDeleteOpen(true)}>
                  <Trash2 className="mr-2 size-4" />
                  Delete
                </Button>
              </div>
            ) : null}
          </div>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0">
              <CardTitle className="text-base">
                Exercises ({(unit.exercises ?? []).length})
              </CardTitle>
              {canManage ? (
                <Button size="sm" variant="outline" onClick={() => setAddOpen(true)}>
                  <Plus className="mr-2 size-4" />
                  Add exercise
                </Button>
              ) : null}
            </CardHeader>
            <CardContent>
              {(unit.exercises ?? []).length === 0 ? (
                <EmptyState
                  icon={Dumbbell}
                  title="No exercises"
                  description="Add exercises to build out this unit."
                />
              ) : (
                <ul className="divide-y">
                  {(unit.exercises ?? []).map((link) => (
                    <li
                      key={link.exercise.id}
                      className="flex items-center justify-between gap-3 py-2.5"
                    >
                      <div className="min-w-0 space-y-0.5">
                        <Link
                          to="/exercises/$exerciseId"
                          params={{ exerciseId: String(link.exercise.id) }}
                          className="text-sm font-medium hover:underline"
                        >
                          {link.exercise.name}
                        </Link>
                        <p className="text-xs text-muted-foreground">
                          {formatPrescription(link)}
                        </p>
                      </div>
                      {canManage ? (
                        <div className="flex shrink-0 items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label={`Edit prescription for ${link.exercise.name}`}
                            onClick={() => setEditingLink(link)}
                          >
                            <Pencil className="size-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            aria-label={`Remove ${link.exercise.name}`}
                            disabled={removeExercise.isPending}
                            onClick={() => handleRemoveExercise(link.exercise.id)}
                          >
                            <X className="size-4" />
                          </Button>
                        </div>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>

          <UnitFormDialog open={formOpen} onOpenChange={setFormOpen} unit={unit} />
          <AddExerciseDialog
            unitId={id}
            existingIds={(unit.exercises ?? []).map((link) => link.exercise.id)}
            open={addOpen}
            onOpenChange={setAddOpen}
          />
          {editingLink !== null ? (
            <PrescriptionDialog
              open
              onOpenChange={(open) => {
                if (!open) setEditingLink(null)
              }}
              exerciseName={editingLink.exercise.name}
              initialSets={editingLink.sets ?? []}
              isPending={setPrescription.isPending}
              onSubmit={handleSavePrescription}
            />
          ) : null}
          <ConfirmDialog
            open={deleteOpen}
            onOpenChange={setDeleteOpen}
            title="Delete training unit?"
            description={`"${unit.name}" will be permanently removed.`}
            onConfirm={confirmDelete}
            isPending={deleteUnit.isPending}
          />
        </>
      )}
    </FadeIn>
  )
}
