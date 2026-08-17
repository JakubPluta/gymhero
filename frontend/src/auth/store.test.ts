import { beforeEach, describe, expect, it } from 'vitest'
import { hasSession, useAuthStore } from './store'

beforeEach(() => {
  useAuthStore.getState().clear()
  localStorage.clear()
})

describe('useAuthStore', () => {
  it('starts without a session', () => {
    expect(hasSession()).toBe(false)
    expect(useAuthStore.getState().accessToken).toBeNull()
  })

  it('setTokens stores both tokens and opens a session', () => {
    useAuthStore.getState().setTokens('access', 'refresh')
    const state = useAuthStore.getState()
    expect(state.accessToken).toBe('access')
    expect(state.refreshToken).toBe('refresh')
    expect(hasSession()).toBe(true)
  })

  it('clear removes both tokens', () => {
    useAuthStore.getState().setTokens('access', 'refresh')
    useAuthStore.getState().clear()
    expect(hasSession()).toBe(false)
    expect(useAuthStore.getState().accessToken).toBeNull()
  })

  it('persists only the refresh token to localStorage', () => {
    useAuthStore.getState().setTokens('access-secret', 'refresh-secret')
    const raw = localStorage.getItem('gymhero-auth')
    expect(raw).not.toBeNull()
    const persisted = JSON.parse(raw ?? '{}')
    expect(persisted.state.refreshToken).toBe('refresh-secret')
    // The access token must never be written to storage.
    expect(persisted.state.accessToken).toBeUndefined()
  })
})
