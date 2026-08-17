import createClient, { type Middleware } from 'openapi-fetch'
import { useAuthStore } from '@/auth/store'
import type { paths } from './schema'

// Empty in dev → hits same-origin `/api/...` through the Vite proxy.
// Set VITE_API_URL in prod to the backend origin.
const BASE_URL = import.meta.env.VITE_API_URL ?? ''

// These never carry a token and must not trigger a refresh-retry loop.
const AUTH_FREE = [
  '/api/v1/auth/login',
  '/api/v1/auth/refresh',
  '/api/v1/auth/register',
]

function isAuthFree(pathname: string): boolean {
  return AUTH_FREE.some((path) => pathname.endsWith(path))
}

// Keep an unconsumed clone of every outgoing request so a 401 can be retried
// even for requests that carried a body (the original body stream is spent).
const pendingClones = new WeakMap<Request, Request>()

// Single-flight: concurrent 401s share one refresh call instead of stampeding.
let refreshInFlight: Promise<string | null> | null = null

async function runRefresh(): Promise<string | null> {
  const { refreshToken, setTokens, clear } = useAuthStore.getState()
  if (refreshToken === null) return null
  try {
    const response = await fetch(`${BASE_URL}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })
    if (!response.ok) {
      clear()
      return null
    }
    const data = (await response.json()) as {
      access_token: string
      refresh_token: string
    }
    setTokens(data.access_token, data.refresh_token)
    return data.access_token
  } catch {
    clear()
    return null
  }
}

function refreshOnce(): Promise<string | null> {
  refreshInFlight ??= runRefresh().finally(() => {
    refreshInFlight = null
  })
  return refreshInFlight
}

const authMiddleware: Middleware = {
  onRequest({ request }) {
    if (isAuthFree(new URL(request.url).pathname)) return request
    pendingClones.set(request, request.clone())
    const token = useAuthStore.getState().accessToken
    if (token !== null) request.headers.set('Authorization', `Bearer ${token}`)
    return request
  },
  async onResponse({ request, response }) {
    if (response.status !== 401) return response
    if (isAuthFree(new URL(request.url).pathname)) return response

    const token = await refreshOnce()
    const retryable = pendingClones.get(request)
    if (token === null || retryable === undefined) {
      useAuthStore.getState().clear()
      return response
    }
    retryable.headers.set('Authorization', `Bearer ${token}`)
    return fetch(retryable)
  },
}

export const api = createClient<paths>({ baseUrl: BASE_URL })
api.use(authMiddleware)
