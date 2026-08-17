import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import type { ListParams, TrainingPlanCreate, TrainingPlanUpdate } from '@/api/types'

const planKeys = {
  all: ['training-plans'] as const,
  list: (params: ListParams) => ['training-plans', 'list', params] as const,
  detail: (id: number) => ['training-plans', 'detail', id] as const,
}

export function useTrainingPlans({ scope, skip, limit, q }: ListParams) {
  return useQuery({
    queryKey: planKeys.list({ scope, skip, limit, q }),
    queryFn: async () => {
      const query = { skip, limit, q: q ? q : undefined }
      if (scope === 'my') {
        const { data, error } = await api.GET('/api/v1/training-plans/all/my', {
          params: { query },
        })
        if (error) throw error
        return data
      }
      const { data, error } = await api.GET('/api/v1/training-plans/all', {
        params: { query },
      })
      if (error) throw error
      return data
    },
  })
}

export function useTrainingPlan(id: number) {
  return useQuery({
    queryKey: planKeys.detail(id),
    queryFn: async () => {
      const { data, error } = await api.GET(
        '/api/v1/training-plans/{training_plan_id}',
        {
          params: { path: { training_plan_id: id } },
        },
      )
      if (error) throw error
      return data
    },
  })
}

export function useCreateTrainingPlan() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: TrainingPlanCreate) => {
      const { data, error } = await api.POST('/api/v1/training-plans/', { body })
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: planKeys.all }),
  })
}

export function useUpdateTrainingPlan(id: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (body: TrainingPlanUpdate) => {
      const { data, error } = await api.PUT(
        '/api/v1/training-plans/{training_plan_id}',
        {
          params: { path: { training_plan_id: id } },
          body,
        },
      )
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: planKeys.all }),
  })
}

export function useDeleteTrainingPlan() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      const { error } = await api.DELETE('/api/v1/training-plans/{training_plan_id}', {
        params: { path: { training_plan_id: id } },
      })
      if (error) throw error
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: planKeys.all }),
  })
}

export function useAddUnitToPlan(planId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (unitId: number) => {
      const { data, error } = await api.PUT(
        '/api/v1/training-plans/{training_plan_id}/training-units/{training_unit_id}',
        { params: { path: { training_plan_id: planId, training_unit_id: unitId } } },
      )
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: planKeys.all }),
  })
}

export function useRemoveUnitFromPlan(planId: number) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (unitId: number) => {
      const { data, error } = await api.DELETE(
        '/api/v1/training-plans/{training_plan_id}/training-units/{training_unit_id}',
        { params: { path: { training_plan_id: planId, training_unit_id: unitId } } },
      )
      if (error) throw error
      return data
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: planKeys.all }),
  })
}
