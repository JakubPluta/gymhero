import type { components } from './schema'

type Schemas = components['schemas']

// Shared list/pagination shapes used by the resource hooks and the generic list view.
export type Scope = 'all' | 'my'
export type ListParams = { scope: Scope; skip: number; limit: number; q?: string }
export type Paged<T> = { items: T[]; total: number; skip: number; limit: number }

// Exercises additionally support server-side filtering by reference ids.
export type ExerciseListParams = ListParams & {
  exercise_type_id?: number
  level_id?: number
  target_body_part_id?: number
}

export type CurrentUser = Schemas['CurrentUser']

export type Exercise = Schemas['ExerciseInDB']
export type ExerciseSummary = Schemas['ExerciseSummary']
export type ExerciseCreate = Schemas['ExerciseCreate']
export type ExerciseUpdate = Schemas['ExerciseUpdate']

export type TrainingUnit = Schemas['TrainingUnitInDB']
export type TrainingUnitCreate = Schemas['TrainingUnitCreate']
export type TrainingUnitUpdate = Schemas['TrainingUnitUpdate']

export type TrainingPlan = Schemas['TrainingPlanInDB']
export type TrainingPlanCreate = Schemas['TrainingPlanCreate']
export type TrainingPlanUpdate = Schemas['TrainingPlanUpdate']

// Reference lookups are listed via their `*InDB` schemas (id + name).
export type BodyPart = Schemas['BodyPartInDB']
export type ExerciseType = Schemas['ExerciseTypeInDB']
export type Level = Schemas['LevelInDB']
