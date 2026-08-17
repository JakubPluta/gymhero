import { create } from 'zustand'
import { persist } from 'zustand/middleware'

type AuthState = {
  // Access token lives in memory only; refresh token is persisted so a reload
  // can silently re-mint an access token instead of forcing re-login.
  accessToken: string | null
  refreshToken: string | null
  setTokens: (accessToken: string, refreshToken: string) => void
  clear: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      accessToken: null,
      refreshToken: null,
      setTokens: (accessToken, refreshToken) => set({ accessToken, refreshToken }),
      clear: () => set({ accessToken: null, refreshToken: null }),
    }),
    {
      name: 'gymhero-auth',
      partialize: (state) => ({ refreshToken: state.refreshToken }),
    },
  ),
)

export function hasSession(): boolean {
  const { accessToken, refreshToken } = useAuthStore.getState()
  return accessToken !== null || refreshToken !== null
}
