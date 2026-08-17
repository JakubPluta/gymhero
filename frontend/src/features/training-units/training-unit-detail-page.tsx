import { Link, useNavigate } from '@tanstack/react-router'
import { ArrowLeft, Dumbbell, Pencil, Plus, Trash2, X } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import { useMe } from '@/auth/useAuth'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataError } from '@/components/data-error'
import { EmptyState } from '@/components/empty-state'
import { FadeIn } from '@/components/fade-in'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AddExerciseDialog } from './add-exercise-dialog'
import {
  useDeleteTrainingUnit,
  useRemoveExerciseFromUnit,
  useTrainingUnit,
} from './hooks'
import { UnitFormDialog } from './unit-form-dialog'

export function TrainingUnitDetailPage({ id }: { id: number }) {
  const navigate = useNavigate()
  const { data: me } = useMe()
  const { data: unit, isLoading, isError, error } = useTrainingUnit(id)
  const deleteUnit = useDeleteTrainingUnit()
  const removeExercise = useRemoveExerciseFromUnit(id)
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [addOpen, setAddOpen] = useState(false)

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

  return (
    <FadeIn className="space-y-6">
      <Button asChild variant="ghost" size="sm" className="-ml-2 w-fit">
        <Link to="/training-units">
          <ArrowLeft className="mr-2 size-4" />
          Back to training units
        </Link>
      </Button>

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
                  {(unit.exercises ?? []).map((exercise) => (
                    <li
                      key={exercise.id}
                      className="flex items-center justify-between py-2.5"
                    >
                      <Link
                        to="/exercises/$exerciseId"
                        params={{ exerciseId: String(exercise.id) }}
                        className="text-sm font-medium hover:underline"
                      >
                        {exercise.name}
                      </Link>
                      {canManage ? (
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Remove ${exercise.name}`}
                          disabled={removeExercise.isPending}
                          onClick={() => handleRemoveExercise(exercise.id)}
                        >
                          <X className="size-4" />
                        </Button>
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
            existingIds={(unit.exercises ?? []).map((exercise) => exercise.id)}
            open={addOpen}
            onOpenChange={setAddOpen}
          />
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
