import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@/api/client'
import { useAuthStore } from './store'

type Credentials = { email: string; password: string }
type Registration = { email: string; password: string; full_name?: string }

export function useMe() {
  const isAuthed = useAuthStore(
    (state) => state.accessToken !== null || state.refreshToken !== null,
  )
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const { data, error } = await api.GET('/api/v1/auth/me')
      if (error) throw error
      return data
    },
    enabled: isAuthed,
    retry: false,
    staleTime: 5 * 60 * 1000,
  })
}

export function useLogin() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ email, password }: Credentials) => {
      const { data, error } = await api.POST('/api/v1/auth/login', {
        // `scope` is required by the OAuth2 form schema; empty is correct here.
        body: { username: email, password, scope: '' },
        // OAuth2 password flow is form-encoded, not JSON.
        bodySerializer: (body) =>
          new URLSearchParams(body as Record<string, string>).toString(),
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      if (error) throw error
      return data
    },
    onSuccess: async (data) => {
      useAuthStore.getState().setTokens(data.access_token, data.refresh_token)
      await queryClient.invalidateQueries({ queryKey: ['me'] })
    },
  })
}

export function useRegister() {
  return useMutation({
    mutationFn: async ({ email, password, full_name }: Registration) => {
      const { data, error } = await api.POST('/api/v1/auth/register', {
        body: { email, password, full_name },
      })
      if (error) throw error
      return data
    },
  })
}

export function useLogout() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      await api.POST('/api/v1/auth/logout')
    },
    // Clear locally regardless of the network result — the token is gone either way.
    onSettled: () => {
      useAuthStore.getState().clear()
      queryClient.clear()
    },
  })
}
