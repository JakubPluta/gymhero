import { Link, useNavigate } from '@tanstack/react-router'
import { ChevronRight, ListChecks, Pencil, Plus, Trash2, X } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'sonner'
import { getErrorMessage } from '@/api/errors'
import { useMe } from '@/auth/useAuth'
import { ConfirmDialog } from '@/components/confirm-dialog'
import { DataError } from '@/components/data-error'
import { EmptyState } from '@/components/empty-state'
import { FadeIn } from '@/components/fade-in'
import { PageBreadcrumb } from '@/components/page-breadcrumb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { formatPrescription } from '@/features/training-units/prescription'
import { cn } from '@/lib/utils'
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
  const [expanded, setExpanded] = useState<Set<number>>(() => new Set())

  const canManage =
    me !== undefined &&
    plan !== undefined &&
    (plan.owner_id === me.id || me.is_superuser)

  const toggle = (unitId: number) =>
    setExpanded((current) => {
      const next = new Set(current)
      if (next.has(unitId)) next.delete(unitId)
      else next.add(unitId)
      return next
    })

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

  const units = plan?.training_units ?? []

  return (
    <FadeIn className="space-y-6">
      <PageBreadcrumb
        items={[
          { label: 'Home', to: '/' },
          { label: 'Training plans', to: '/training-plans' },
          ...(plan ? [{ label: plan.name }] : []),
        ]}
      />

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
                Training units ({units.length})
              </CardTitle>
              {canManage ? (
                <Button size="sm" variant="outline" onClick={() => setAddOpen(true)}>
                  <Plus className="mr-2 size-4" />
                  Add unit
                </Button>
              ) : null}
            </CardHeader>
            <CardContent>
              {units.length === 0 ? (
                <EmptyState
                  icon={ListChecks}
                  title="No training units"
                  description="Add training units to build out this plan."
                />
              ) : (
                <ul className="divide-y">
                  {units.map((unit) => {
                    const isOpen = expanded.has(unit.id)
                    const exercises = unit.exercises ?? []
                    return (
                      <li key={unit.id} className="py-1">
                        <div className="flex items-center justify-between gap-2">
                          <button
                            type="button"
                            onClick={() => toggle(unit.id)}
                            aria-expanded={isOpen}
                            className="flex flex-1 items-center gap-2 py-1.5 text-left"
                          >
                            <ChevronRight
                              className={cn(
                                'size-4 shrink-0 text-muted-foreground transition-transform',
                                isOpen && 'rotate-90',
                              )}
                            />
                            <span className="text-sm font-medium">{unit.name}</span>
                            <Badge variant="secondary">
                              {exercises.length} exercises
                            </Badge>
                          </button>
                          <div className="flex shrink-0 items-center gap-1">
                            <Button asChild variant="ghost" size="sm">
                              <Link
                                to="/training-units/$unitId"
                                params={{ unitId: String(unit.id) }}
                              >
                                Manage
                              </Link>
                            </Button>
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
                          </div>
                        </div>
                        {isOpen ? (
                          exercises.length === 0 ? (
                            <p className="pb-2 pl-6 text-sm text-muted-foreground">
                              No exercises in this unit yet.
                            </p>
                          ) : (
                            <ul className="space-y-1 pb-2 pl-6">
                              {exercises.map((link) => (
                                <li
                                  key={link.exercise.id}
                                  className="flex items-baseline justify-between gap-3 text-sm"
                                >
                                  <span className="font-medium">
                                    {link.exercise.name}
                                  </span>
                                  <span className="text-muted-foreground">
                                    {formatPrescription(link)}
                                  </span>
                                </li>
                              ))}
                            </ul>
                          )
                        ) : null}
                      </li>
                    )
                  })}
                </ul>
              )}
            </CardContent>
          </Card>

          <PlanFormDialog open={formOpen} onOpenChange={setFormOpen} plan={plan} />
          <AddUnitDialog
            planId={id}
            existingIds={units.map((unit) => unit.id)}
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
