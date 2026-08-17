import { Link, useNavigate } from '@tanstack/react-router'
import { ArrowLeft, ListChecks, Pencil, Plus, Trash2, X } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import { useMe } from '@/auth/useAuth'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataError } from '@/components/data-error'
import { EmptyState } from '@/components/empty-state'
import { FadeIn } from '@/components/fade-in'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AddUnitDialog } from './add-unit-dialog'
import { useDeleteTrainingPlan, useRemoveUnitFromPlan, useTrainingPlan } from './hooks'
import { PlanFormDialog } from './plan-form-dialog'

export function TrainingPlanDetailPage({ id }: { id: number }) {
  const navigate = useNavigate()
  const { data: me } = useMe()
  const { data: plan, isLoading, isError, error } = useTrainingPlan(id)
  const deletePlan = useDeleteTrainingPlan()
  const removeUnit = useRemoveUnitFromPlan(id)
  const [formOpen, setFormOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [addOpen, setAddOpen] = useState(false)

  const canManage =
    me !== undefined &&
    plan !== undefined &&
    (plan.owner_id === me.id || me.is_superuser)

  const confirmDelete = () => {
    deletePlan.mutate(id, {
      onSuccess: () => {
        toast.success('Training plan deleted')
        navigate({ to: '/training-plans' })
      },
      onError: (deleteError) => toast.error(getErrorMessage(deleteError)),
    })
  }

  const handleRemoveUnit = (unitId: number) => {
    removeUnit.mutate(unitId, {
      onSuccess: () => toast.success('Training unit removed'),
      onError: (removeError) => toast.error(getErrorMessage(removeError)),
    })
  }

  return (
    <FadeIn className="space-y-6">
      <Button asChild variant="ghost" size="sm" className="-ml-2 w-fit">
        <Link to="/training-plans">
          <ArrowLeft className="mr-2 size-4" />
          Back to training plans
        </Link>
      </Button>

      {isLoading ? (
        <Skeleton className="h-64 w-full" />
      ) : isError || plan === undefined ? (
        <DataError error={error} />
      ) : (
        <>
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="space-y-1">
              <h1 className="text-2xl font-semibold tracking-tight">{plan.name}</h1>
              {plan.description ? (
                <p className="text-sm text-muted-foreground">{plan.description}</p>
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
                Training units ({(plan.training_units ?? []).length})
              </CardTitle>
              {canManage ? (
                <Button size="sm" variant="outline" onClick={() => setAddOpen(true)}>
                  <Plus className="mr-2 size-4" />
                  Add unit
                </Button>
              ) : null}
            </CardHeader>
            <CardContent>
              {(plan.training_units ?? []).length === 0 ? (
                <EmptyState
                  icon={ListChecks}
                  title="No training units"
                  description="Add training units to build out this plan."
                />
              ) : (
                <ul className="divide-y">
                  {(plan.training_units ?? []).map((unit) => (
                    <li
                      key={unit.id}
                      className="flex items-center justify-between py-2.5"
                    >
                      <div className="flex items-center gap-3">
                        <Link
                          to="/training-units/$unitId"
                          params={{ unitId: String(unit.id) }}
                          className="text-sm font-medium hover:underline"
                        >
                          {unit.name}
                        </Link>
                        <Badge variant="secondary">
                          {(unit.exercises ?? []).length} exercises
                        </Badge>
                      </div>
                      {canManage ? (
                        <Button
                          variant="ghost"
                          size="icon"
                          aria-label={`Remove ${unit.name}`}
                          disabled={removeUnit.isPending}
                          onClick={() => handleRemoveUnit(unit.id)}
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

          <PlanFormDialog open={formOpen} onOpenChange={setFormOpen} plan={plan} />
          <AddUnitDialog
            planId={id}
            existingIds={(plan.training_units ?? []).map((unit) => unit.id)}
            open={addOpen}
            onOpenChange={setAddOpen}
          />
          <ConfirmDialog
            open={deleteOpen}
            onOpenChange={setDeleteOpen}
            title="Delete training plan?"
            description={`"${plan.name}" will be permanently removed.`}
            onConfirm={confirmDelete}
            isPending={deletePlan.isPending}
          />
        </>
      )}
    </FadeIn>
  )
}
