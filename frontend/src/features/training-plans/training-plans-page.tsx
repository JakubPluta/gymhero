import { Link } from '@tanstack/react-router'
import { ClipboardList } from 'lucide-react'
import { useState } from 'react'
import type { TrainingPlan } from '@/api/types'
import { useMe } from '@/auth/useAuth'
import { ResourceListView, type Column } from '@/components/resource-list-view'
import { Badge } from '@/components/ui/badge'
import { useDeleteTrainingPlan, useTrainingPlans } from './hooks'
import { PlanFormDialog } from './plan-form-dialog'

export function TrainingPlansPage() {
  const { data: me } = useMe()
  const deletePlan = useDeleteTrainingPlan()
  const [editing, setEditing] = useState<TrainingPlan | undefined>(undefined)
  const [formOpen, setFormOpen] = useState(false)

  const openCreate = () => {
    setEditing(undefined)
    setFormOpen(true)
  }
  const openEdit = (plan: TrainingPlan) => {
    setEditing(plan)
    setFormOpen(true)
  }

  const columns: Column<TrainingPlan>[] = [
    {
      header: 'Name',
      className: 'font-medium',
      cell: (plan) => (
        <Link
          to="/training-plans/$planId"
          params={{ planId: String(plan.id) }}
          className="hover:underline"
        >
          {plan.name}
        </Link>
      ),
    },
    {
      header: 'Units',
      cell: (plan) => (
        <Badge variant="secondary">{(plan.training_units ?? []).length}</Badge>
      ),
    },
  ]

  return (
    <>
      <ResourceListView<TrainingPlan>
        title="Training plans"
        description="Programs built from your training units."
        icon={ClipboardList}
        newLabel="New plan"
        entityLabel="training plan"
        emptyTitle="No training plans yet"
        emptyDescription="Create a plan and organize your training units."
        defaultScope="my"
        useList={useTrainingPlans}
        columns={columns}
        getRowId={(plan) => plan.id}
        getRowName={(plan) => plan.name}
        canManage={(plan) =>
          me !== undefined && (plan.owner_id === me.id || me.is_superuser)
        }
        onNew={openCreate}
        onEdit={openEdit}
        onDelete={(id, callbacks) => deletePlan.mutate(id, callbacks)}
        isDeleting={deletePlan.isPending}
        searchPlaceholder="Search plans…"
      />
      <PlanFormDialog open={formOpen} onOpenChange={setFormOpen} plan={editing} />
    </>
  )
}
