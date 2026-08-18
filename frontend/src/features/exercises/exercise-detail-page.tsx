import { useNavigate } from '@tanstack/react-router'
import { Pencil, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import { useMe } from '@/auth/useAuth'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataError } from '@/components/data-error'
import { FadeIn } from '@/components/fade-in'
import { PageBreadcrumb } from '@/components/page-breadcrumb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { ExerciseFormDialog } from './exercise-form-dialog'
import { useDeleteExercise, useExercise } from './hooks'

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="space-y-1">
      <dt className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
        {label}
      </dt>
      <dd className="text-sm">{children}</dd>
    </div>
  )
}

export function ExerciseDetailPage({ id }: { id: number }) {
  const navigate = useNavigate()
  const { data: me } = useMe()
  const { data: exercise, isLoading, isError, error } = useExercise(id)
  const deleteExercise = useDeleteExercise()
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)

  const canManage =
    me !== undefined &&
    exercise !== undefined &&
    (exercise.owner_id === me.id || me.is_superuser)

  const confirmDelete = () => {
    deleteExercise.mutate(id, {
      onSuccess: () => {
        toast.success('Exercise deleted')
        navigate({ to: '/exercises' })
      },
      onError: (deleteError) => toast.error(getErrorMessage(deleteError)),
    })
  }

  return (
    <FadeIn className="space-y-6">
      <PageBreadcrumb
        items={[
          { label: 'Home', to: '/' },
          { label: 'Exercises', to: '/exercises' },
          ...(exercise ? [{ label: exercise.name }] : []),
        ]}
      />

      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : isError || exercise === undefined ? (
        <DataError error={error} />
      ) : (
        <>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <h1 className="text-2xl font-semibold tracking-tight">{exercise.name}</h1>
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
            <CardHeader>
              <CardTitle className="text-base">Details</CardTitle>
            </CardHeader>
            <CardContent>
              <dl className="grid gap-6 sm:grid-cols-3">
                <Field label="Type">
                  <Badge variant="secondary">{exercise.exercise_type?.name}</Badge>
                </Field>
                <Field label="Level">{exercise.level?.name}</Field>
                <Field label="Body part">{exercise.target_body_part?.name}</Field>
              </dl>
              {exercise.description ? (
                <div className="mt-6 space-y-1">
                  <dt className="text-xs font-medium tracking-wide text-muted-foreground uppercase">
                    Description
                  </dt>
                  <dd className="text-sm whitespace-pre-wrap">
                    {exercise.description}
                  </dd>
                </div>
              ) : null}
            </CardContent>
          </Card>

          <ExerciseFormDialog
            open={formOpen}
            onOpenChange={setFormOpen}
            exercise={exercise}
          />
          <ConfirmDialog
            open={deleteOpen}
            onOpenChange={setDeleteOpen}
            title="Delete exercise?"
            description={`"${exercise.name}" will be permanently removed.`}
            onConfirm={confirmDelete}
            isPending={deleteExercise.isPending}
          />
        </>
      )}
    </FadeIn>
  )
}
