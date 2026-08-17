import { Link } from '@tanstack/react-router'
import { ListChecks } from 'lucide-react'
import { useState } from 'react'
import type { TrainingUnit } from '@/api/types'
import { useMe } from '@/auth/useAuth'
import { ResourceListView, type Column } from '@/components/resource-list-view'
import { Badge } from '@/components/ui/badge'
import { useDeleteTrainingUnit, useTrainingUnits } from './hooks'
import { UnitFormDialog } from './unit-form-dialog'

export function TrainingUnitsPage() {
  const { data: me } = useMe()
  const deleteUnit = useDeleteTrainingUnit()
  const [editing, setEditing] = useState<TrainingUnit | undefined>(undefined)
  const [formOpen, setFormOpen] = useState(false)

  const openCreate = () => {
    setEditing(undefined)
    setFormOpen(true)
  }
  const openEdit = (unit: TrainingUnit) => {
    setEditing(unit)
    setFormOpen(true)
  }

  const columns: Column<TrainingUnit>[] = [
    {
      header: 'Name',
      className: 'font-medium',
      cell: (unit) => (
        <Link
          to="/training-units/$unitId"
          params={{ unitId: String(unit.id) }}
          className="hover:underline"
        >
          {unit.name}
        </Link>
      ),
    },
    {
      header: 'Exercises',
      cell: (unit) => (
        <Badge variant="secondary">{(unit.exercises ?? []).length}</Badge>
      ),
    },
  ]

  return (
    <>
      <ResourceListView<TrainingUnit>
        title="Training units"
        description="Reusable workouts built from exercises."
        icon={ListChecks}
        newLabel="New unit"
        entityLabel="training unit"
        emptyTitle="No training units yet"
        emptyDescription="Create a unit and start adding exercises."
        defaultScope="my"
        useList={useTrainingUnits}
        columns={columns}
        getRowId={(unit) => unit.id}
        getRowName={(unit) => unit.name}
        canManage={(unit) =>
          me !== undefined && (unit.owner_id === me.id || me.is_superuser)
        }
        onNew={openCreate}
        onEdit={openEdit}
        onDelete={(id, callbacks) => deleteUnit.mutate(id, callbacks)}
        isDeleting={deleteUnit.isPending}
        searchPlaceholder="Search units…"
      />
      <UnitFormDialog open={formOpen} onOpenChange={setFormOpen} unit={editing} />
    </>
  )
}
