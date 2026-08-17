import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { ExerciseCreate, ExerciseListParams, ExerciseUpdate } from '@/api/types'

const exerciseKeys = {
  all: ['exercises'] as const,
  list: (params: ExerciseListParams) => ['exercises', 'list', params] as const,
  detail: (id: number) => ['exercises', 'detail', id] as const,
}

export function useExercises(params: ExerciseListParams) {
  const { scope, skip, limit, q, exercise_type_id, level_id, target_body_part_id } =
    params
  return useQuery({
    queryKey: exerciseKeys.list(params),
    queryFn: async () => {
      const query = {
        skip,
        limit,
        q: q ? q : undefined,
        exercise_type_id,
        level_id,
        target_body_part_id,
      }
      if (scope === 'my') {
        const { data, error } = await api.GET('/api/v1/exercises/my', {
          params: { query },
        })
        if (error) throw error
        return data
      }
      const { data, error } = await api.GET('/api/v1/exercises/all', {
        params: { query },
      })
      if (error) throw error
      return data
    },
  })
}

export function useExercise(id: number) {
  return useQuery({
    queryKey: exerciseKeys.detail(id),
    queryFn: async () => {
      const { data, error } = await api.GET('/api/v1/exercises/{exercise_id}', {
        params: { path: { exercise_id: id } },
      })
      if (error) throw error
      return data
    },
  })
}

export function useCreateExercise() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: ExerciseCreate) => {
      const { data, error } = await api.POST('/api/v1/exercises/', { body })
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: exerciseKeys.all }),
  })
}

export function useUpdateExercise(id: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: ExerciseUpdate) => {
      const { data, error } = await api.PATCH('/api/v1/exercises/{exercise_id}', {
        params: { path: { exercise_id: id } },
        body,
      })
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: exerciseKeys.all }),
  })
}

export function useDeleteExercise() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      const { error } = await api.DELETE('/api/v1/exercises/{exercise_id}', {
        params: { path: { exercise_id: id } },
      })
      if (error) throw error
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: exerciseKeys.all }),
  })
}
