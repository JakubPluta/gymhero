import { useQuery } from '@tanstack/react-query'
import { api } from '@/api/client'

// Reference catalogs are small and rarely change → fetch the full first page
// and cache it long. Used to populate the exercise form's selects.
const REFERENCE_LIMIT = 100
const STALE_TIME = 10 * 60 * 1000

export function useBodyParts() {
  return useQuery({
    queryKey: ['body-parts'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/v1/body-parts/all', {
        params: { query: { skip: 0, limit: REFERENCE_LIMIT } },
      })
      if (error) throw error
      return data.items
    },
    staleTime: STALE_TIME,
  })
}

export function useExerciseTypes() {
  return useQuery({
    queryKey: ['exercise-types'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/v1/exercise-types/all', {
        params: { query: { skip: 0, limit: REFERENCE_LIMIT } },
      })
      if (error) throw error
      return data.items
    },
    staleTime: STALE_TIME,
  })
}

export function useLevels() {
  return useQuery({
    queryKey: ['levels'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/v1/levels/all', {
        params: { query: { skip: 0, limit: REFERENCE_LIMIT } },
      })
      if (error) throw error
      return data.items
    },
    staleTime: STALE_TIME,
  })
}
