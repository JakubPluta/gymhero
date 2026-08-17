import { useEffect, useState } from 'react'

// Returns `value` delayed by `delayMs`, resetting the timer on each change —
// used to avoid firing a query on every keystroke of a search box.
export function useDebounce<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs)
    return () => clearTimeout(timer)
  }, [value, delayMs])
  return debounced
}
