// FastAPI errors are either `{ detail: string }` or, for 422 validation,
// `{ detail: [{ msg, loc, ... }] }`. Flatten either into a human string.
export function getErrorMessage(
  error: unknown,
  fallback = 'Something went wrong',
): string {
  if (error instanceof Error) return error.message
  if (typeof error === 'string') return error
  if (typeof error === 'object' && error !== null && 'detail' in error) {
    const { detail } = error as { detail: unknown }
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail) && detail.length > 0) {
      const first: unknown = detail[0]
      if (
        typeof first === 'object' &&
        first !== null &&
        'msg' in first &&
        typeof (first as { msg: unknown }).msg === 'string'
      ) {
        return (first as { msg: string }).msg
      }
    }
  }
  return fallback
}
