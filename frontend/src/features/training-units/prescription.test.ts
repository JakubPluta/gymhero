import { describe, expect, it } from 'vitest'
import type { PrescribedSet, TrainingUnitExercise } from '@/api/types'
import { formatPrescription } from './prescription'

const set = (
  set_number: number,
  reps: number | null,
  weight: number | null,
): PrescribedSet => ({ set_number, reps, weight })

const link = (sets: PrescribedSet[]): TrainingUnitExercise => ({
  exercise: { id: 1, name: 'Bench Press', owner_id: 1 },
  sets,
})

describe('formatPrescription', () => {
  it('formats a ramp of sets as reps×weight', () => {
    expect(
      formatPrescription(
        link([set(1, 12, 80), set(2, 10, 90), set(3, 10, 90), set(4, 8, 100)]),
      ),
    ).toBe('12×80, 10×90, 10×90, 8×100')
  })

  it('formats a reps-only set', () => {
    expect(formatPrescription(link([set(1, 12, null)]))).toBe('12')
  })

  it('formats a weight-only set', () => {
    expect(formatPrescription(link([set(1, null, 80)]))).toBe('@80')
  })

  it('returns a dash when there are no sets', () => {
    expect(formatPrescription(link([]))).toBe('—')
  })
})
