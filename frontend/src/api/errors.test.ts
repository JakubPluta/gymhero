import { describe, expect, it } from 'vitest'
import { getErrorMessage } from './errors'

describe('getErrorMessage', () => {
  it('returns the message from an Error', () => {
    expect(getErrorMessage(new Error('boom'))).toBe('boom')
  })

  it('returns a string error as-is', () => {
    expect(getErrorMessage('plain error')).toBe('plain error')
  })

  it('flattens FastAPI { detail: string }', () => {
    expect(getErrorMessage({ detail: 'Not found' })).toBe('Not found')
  })

  it('flattens FastAPI validation { detail: [{ msg }] }', () => {
    const error = { detail: [{ msg: 'field required', loc: ['body', 'name'] }] }
    expect(getErrorMessage(error)).toBe('field required')
  })

  it('falls back for unrecognized shapes', () => {
    expect(getErrorMessage({ unexpected: true })).toBe('Something went wrong')
    expect(getErrorMessage(null)).toBe('Something went wrong')
  })

  it('uses a custom fallback', () => {
    expect(getErrorMessage(undefined, 'Login failed')).toBe('Login failed')
  })
})
