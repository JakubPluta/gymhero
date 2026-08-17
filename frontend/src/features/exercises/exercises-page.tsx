import { Link } from '@tanstack/react-router'
import { Dumbbell } from 'lucide-react'
import { useState } from 'react'
import type { Exercise, ExerciseListParams } from '@/api/types'
import { useMe } from '@/auth/useAuth'
import { ResourceListView, type Column } from '@/components/resource-list-view'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useBodyParts, useExerciseTypes, useLevels } from '@/features/reference/hooks'
import { ExerciseFormDialog } from './exercise-form-dialog'
import { useDeleteExercise, useExercises } from './hooks'

type FilterSelectProps = {
  value: number | undefined
  onChange: (value: number | undefined) => void
  placeholder: string
  options: { id: number; name: string }[] | undefined
}

function FilterSelect({ value, onChange, placeholder, options }: FilterSelectProps) {
  return (
    <Select
      value={value === undefined ? 'all' : String(value)}
      onValueChange={(next) => onChange(next === 'all' ? undefined : Number(next))}
    >
      <SelectTrigger className="w-[150px]">
        <SelectValue placeholder={placeholder} />
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="all">{placeholder}</SelectItem>
        {options?.map((option) => (
          <SelectItem key={option.id} value={String(option.id)}>
            {option.name}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  )
}

export function ExercisesPage() {
  const { data: me } = useMe()
  const deleteExercise = useDeleteExercise()
  const bodyParts = useBodyParts()
  const types = useExerciseTypes()
  const levels = useLevels()

  const [editing, setEditing] = useState<Exercise | undefined>(undefined)
  const [formOpen, setFormOpen] = useState(false)
  const [typeId, setTypeId] = useState<number | undefined>(undefined)
  const [levelId, setLevelId] = useState<number | undefined>(undefined)
  const [bodyPartId, setBodyPartId] = useState<number | undefined>(undefined)

  const openCreate = () => {
    setEditing(undefined)
    setFormOpen(true)
  }
  const openEdit = (exercise: Exercise) => {
    setEditing(exercise)
    setFormOpen(true)
  }

  const columns: Column<Exercise>[] = [
    {
      header: 'Name',
      className: 'font-medium',
      cell: (exercise) => (
        <Link
          to="/exercises/$exerciseId"
          params={{ exerciseId: String(exercise.id) }}
          className="hover:underline"
        >
          {exercise.name}
        </Link>
      ),
    },
    {
      header: 'Type',
      cell: (exercise) => (
        <Badge variant="secondary">{exercise.exercise_type?.name}</Badge>
      ),
    },
    {
      header: 'Level',
      className: 'text-muted-foreground',
      cell: (exercise) => exercise.level?.name,
    },
    {
      header: 'Body part',
      className: 'text-muted-foreground',
      cell: (exercise) => exercise.target_body_part?.name,
    },
  ]

  const toolbar = (
    <>
      <FilterSelect
        value={typeId}
        onChange={setTypeId}
        placeholder="Type"
        options={types.data}
      />
      <FilterSelect
        value={levelId}
        onChange={setLevelId}
        placeholder="Level"
        options={levels.data}
      />
      <FilterSelect
        value={bodyPartId}
        onChange={setBodyPartId}
        placeholder="Body part"
        options={bodyParts.data}
      />
    </>
  )

  return (
    <>
      <ResourceListView<Exercise, ExerciseListParams>
        title="Exercises"
        description="Browse the shared catalog or manage your own."
        icon={Dumbbell}
        newLabel="New exercise"
        entityLabel="exercise"
        emptyTitle="No exercises found"
        emptyDescription="Try a different search or filters, or create a new exercise."
        defaultScope="all"
        useList={useExercises}
        columns={columns}
        getRowId={(exercise) => exercise.id}
        getRowName={(exercise) => exercise.name}
        canManage={(exercise) =>
          me !== undefined && (exercise.owner_id === me.id || me.is_superuser)
        }
        onNew={openCreate}
        onEdit={openEdit}
        onDelete={(id, callbacks) => deleteExercise.mutate(id, callbacks)}
        isDeleting={deleteExercise.isPending}
        searchPlaceholder="Search exercises…"
        toolbar={toolbar}
        extraParams={{
          exercise_type_id: typeId,
          level_id: levelId,
          target_body_part_id: bodyPartId,
        }}
      />
      <ExerciseFormDialog
        open={formOpen}
        onOpenChange={setFormOpen}
        exercise={editing}
      />
    </>
  )
}
