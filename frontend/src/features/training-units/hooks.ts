import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type {
  ListParams,
  PrescriptionUpdate,
  TrainingUnitCreate,
  TrainingUnitUpdate,
} from '@/api/types'

const unitKeys = {
  all: ['training-units'] as const,
  list: (params: ListParams) => ['training-units', 'list', params] as const,
  detail: (id: number) => ['training-units', 'detail', id] as const,
}

export function useTrainingUnits({ scope, skip, limit, q }: ListParams) {
  return useQuery({
    queryKey: unitKeys.list({ scope, skip, limit, q }),
    queryFn: async () => {
      const query = { skip, limit, q: q ? q : undefined }
      if (scope === 'my') {
        const { data, error } = await api.GET('/api/v1/training-units/all/my', {
          params: { query },
        })
        if (error) throw error
        return data
      }
      const { data, error } = await api.GET('/api/v1/training-units/all', {
        params: { query },
      })
      if (error) throw error
      return data
    },
  })
}

export function useTrainingUnit(id: number) {
  return useQuery({
    queryKey: unitKeys.detail(id),
    queryFn: async () => {
      const { data, error } = await api.GET(
        '/api/v1/training-units/{training_unit_id}',
        {
          params: { path: { training_unit_id: id } },
        },
      )
      if (error) throw error
      return data
    },
  })
}

export function useCreateTrainingUnit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: TrainingUnitCreate) => {
      const { data, error } = await api.POST('/api/v1/training-units/', { body })
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: unitKeys.all }),
  })
}

export function useUpdateTrainingUnit(id: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: TrainingUnitUpdate) => {
      const { data, error } = await api.PUT(
        '/api/v1/training-units/{training_unit_id}',
        {
          params: { path: { training_unit_id: id } },
          body,
        },
      )
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: unitKeys.all }),
  })
}

export function useDeleteTrainingUnit() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      const { error } = await api.DELETE('/api/v1/training-units/{training_unit_id}', {
        params: { path: { training_unit_id: id } },
      })
      if (error) throw error
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: unitKeys.all }),
  })
}

export function useAddExerciseToUnit(unitId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (exerciseId: number) => {
      const { data, error } = await api.PUT(
        '/api/v1/training-units/{training_unit_id}/exercises/{exercise_id}',
        { params: { path: { training_unit_id: unitId, exercise_id: exerciseId } } },
      )
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: unitKeys.all }),
  })
}

export function useRemoveExerciseFromUnit(unitId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (exerciseId: number) => {
      const { data, error } = await api.DELETE(
        '/api/v1/training-units/{training_unit_id}/exercises/{exercise_id}',
        { params: { path: { training_unit_id: unitId, exercise_id: exerciseId } } },
      )
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: unitKeys.all }),
  })
}

export function useSetPrescription(unitId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({
      exerciseId,
      prescription,
    }: {
      exerciseId: number
      prescription: PrescriptionUpdate
    }) => {
      const { data, error } = await api.PATCH(
        '/api/v1/training-units/{training_unit_id}/exercises/{exercise_id}',
        {
          params: { path: { training_unit_id: unitId, exercise_id: exerciseId } },
          body: prescription,
        },
      )
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: unitKeys.all }),
  })
}
